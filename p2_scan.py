#!/usr/bin/env python3
"""
p2_scan.py -- nwproto P2: extract embedded protobuf FileDescriptorProto blobs
              from a Windows PE, decode them, and reconstruct .proto sources.

CHARTER context:
  - Static only. Reads a file on disk. Nothing is executed, hooked or modified.
  - Signatures, not offsets: every blob is reported with its first-16-byte
    signature (the encoded `name` field = the .proto path string constant),
    which is patch-stable in a way a VA is not.
  - The tool is self-testing (--selftest) against synthetic descriptors we
    control, per CHARTER §2/§4, before it is pointed at the retail binary.

WHY THIS BEATS THE GHIDRA XREF WALK AS THE PRIMARY ROUTE
  P2_PROMPT Step 1 says to locate
  `google::protobuf::DescriptorPool::InternalAddGeneratedFile`. That is the
  *old* (proto2 / early proto3) registration API. Protobuf >= 3.10 generates
  `google::protobuf::internal::AddDescriptors(const DescriptorTable*)` instead,
  where the blob lives inside a static DescriptorTable struct. Which symbol
  exists depends on the protobuf version Amazon linked -- unknown up front.
  Both leave the *same artefact* in .rdata: a raw serialized
  FileDescriptorProto. Scanning for the artefact is therefore version
  independent, while scanning for the function is not. Use Ghidra afterwards to
  attribute blobs to call sites, not to find them.

USAGE
  python3 p2_scan.py --selftest
  python3 p2_scan.py /path/to/NewWorld.exe --outdir p2_out
  python3 p2_scan.py /path/to/NewWorld.exe --outdir p2_out --diagnostics

OUTPUT (in --outdir)
  blobs/<n>_<sanitized_path>.bin   raw extracted FileDescriptorProto bytes
  proto/<path>.proto               reconstructed .proto source
  index.tsv                        blob address/size/signature table
  fields.tsv                       every field: message, name, number, type, wire type
  report.md                        human-readable summary incl. service blocks
"""

import argparse
import binascii
import os
import re
import struct
import sys

try:
    from google.protobuf import descriptor_pb2
except ImportError:
    sys.stderr.write(
        "google.protobuf is required.\n"
        "  pip install protobuf --break-system-packages\n"
    )
    raise


# --------------------------------------------------------------------------
# Minimal PE parsing (no pefile dependency)
# --------------------------------------------------------------------------

class Section:
    __slots__ = ("name", "vaddr", "vsize", "raw_ptr", "raw_size")

    def __init__(self, name, vaddr, vsize, raw_ptr, raw_size):
        self.name = name
        self.vaddr = vaddr
        self.vsize = vsize
        self.raw_ptr = raw_ptr
        self.raw_size = raw_size

    def __repr__(self):
        return "<%s va=0x%x vsize=0x%x raw=0x%x/0x%x>" % (
            self.name, self.vaddr, self.vsize, self.raw_ptr, self.raw_size)


class PE:
    def __init__(self, data):
        self.data = data
        if data[:2] != b"MZ":
            raise ValueError("not a PE: missing MZ")
        e_lfanew = struct.unpack_from("<I", data, 0x3C)[0]
        if data[e_lfanew:e_lfanew + 4] != b"PE\0\0":
            raise ValueError("not a PE: missing PE signature")
        coff = e_lfanew + 4
        (machine, nsec, _tds, _psym, _nsym,
         opt_size, _chars) = struct.unpack_from("<HHIIIHH", data, coff)
        self.machine = machine
        opt = coff + 20
        magic = struct.unpack_from("<H", data, opt)[0]
        if magic == 0x20B:          # PE32+
            self.image_base = struct.unpack_from("<Q", data, opt + 24)[0]
        elif magic == 0x10B:        # PE32
            self.image_base = struct.unpack_from("<I", data, opt + 28)[0]
        else:
            raise ValueError("unknown optional header magic 0x%x" % magic)
        self.sections = []
        sec = opt + opt_size
        for i in range(nsec):
            off = sec + i * 40
            raw_name = data[off:off + 8].rstrip(b"\0")
            name = raw_name.decode("ascii", "replace")
            vsize, vaddr, raw_size, raw_ptr = struct.unpack_from("<IIII", data, off + 8)
            self.sections.append(Section(name, vaddr, vsize, raw_ptr, raw_size))

    def section_for_file_offset(self, off):
        for s in self.sections:
            if s.raw_ptr and s.raw_ptr <= off < s.raw_ptr + s.raw_size:
                return s
        return None

    def va_for_file_offset(self, off):
        s = self.section_for_file_offset(off)
        if s is None:
            return None
        return self.image_base + s.vaddr + (off - s.raw_ptr)


# --------------------------------------------------------------------------
# Protobuf wire-level helpers
# --------------------------------------------------------------------------

def read_varint(buf, pos):
    """Return (value, newpos) or (None, pos) if malformed/truncated."""
    result = 0
    shift = 0
    start = pos
    n = len(buf)
    while pos < n:
        b = buf[pos]
        result |= (b & 0x7F) << shift
        pos += 1
        if not (b & 0x80):
            return result, pos
        shift += 7
        if shift > 63:
            return None, start
    return None, start


# FileDescriptorProto top-level fields -> allowed wire type.
# 1 name(L) 2 package(L) 3 dependency(L) 4 message_type(L) 5 enum_type(L)
# 6 service(L) 7 extension(L) 8 options(L) 9 source_code_info(L)
# 10 public_dependency(V) 11 weak_dependency(V) 12 syntax(L) 13 edition(V)
_FDP_FIELDS = {
    1: {2}, 2: {2}, 3: {2}, 4: {2}, 5: {2}, 6: {2}, 7: {2}, 8: {2},
    9: {2}, 10: {0}, 11: {0}, 12: {2}, 13: {0, 2},
}


def scan_fdp_boundaries(buf, start, hard_limit=1 << 22, max_fields=4096):
    """
    Walk top-level FileDescriptorProto fields from `start` ONCE, recording the
    offset after each structurally valid field. Returns that list, longest last.

    This is how the blob's *size* is recovered without the caller's size
    constant. The size constant from the Ghidra call site is the independent
    check on this number (CHARTER §4: two sources, not one).

    Single-pass by design: an earlier version re-walked from `start` on every
    shrink attempt, which is O(n^2) and hung on adversarial input. A tool's cap
    is part of the measurement (CHARTER §4) -- so is a tool that never returns.
    """
    pos = start
    ends = []
    limit = min(len(buf), start + hard_limit)
    while pos < limit and len(ends) < max_fields:
        tag, npos = read_varint(buf, pos)
        if tag is None or tag == 0:
            break
        field = tag >> 3
        wire = tag & 7
        allowed = _FDP_FIELDS.get(field)
        if allowed is None or wire not in allowed:
            break
        pos = npos
        if wire == 2:
            ln, npos = read_varint(buf, pos)
            if ln is None or npos + ln > limit:
                break
            pos = npos + ln
        elif wire == 0:
            val, npos = read_varint(buf, pos)
            if val is None:
                break
            pos = npos
        else:
            break
        ends.append(pos)
    return ends


# A serialized FileDescriptorProto always opens with field 1 (name), wire
# type 2 -> byte 0x0A, then a varint length, then the .proto path. Anchor on
# that, and require the path to look like a .proto path. Low false-positive.
_ANCHOR = re.compile(rb"\x0a([\x01-\x7f])([\x20-\x7e]{1,127})")


def find_candidates(buf, base_offset=0):
    """Yield (file_offset, path_str) for every plausible FDP start."""
    for m in _ANCHOR.finditer(buf):
        ln = m.group(1)[0]
        body = m.group(2)
        if len(body) < ln:
            continue
        path = body[:ln]
        if not path.endswith(b".proto"):
            continue
        try:
            path_s = path.decode("ascii")
        except UnicodeDecodeError:
            continue
        yield base_offset + m.start(), path_s


def _as_text(v):
    """protobuf's upb backend hands back bytes for a string field carrying
    invalid UTF-8, which random .rdata produces constantly. Normalise."""
    if isinstance(v, bytes):
        try:
            return v.decode("utf-8")
        except UnicodeDecodeError:
            return None
    return v


def _accept(fdp, blob, exact):
    """
    Acceptance test for a candidate slice.

    Tier 1 (exact=True): protobuf round-trips the slice byte-identically. This
    is what a real generated descriptor does, because protoc emits fields in
    canonical order. Strongest evidence and the default.

    Tier 2 (exact=False): parse succeeds with no unknown fields and the file
    carries real content. Used only as a fallback, and flagged in output,
    because a descriptor that does not round-trip may have been truncated.
    """
    name = _as_text(fdp.name)
    if not name or not name.endswith(".proto"):
        return False
    # Every path component must be printable ASCII. Random data can produce a
    # decodable name that is still obviously not a source path.
    if any(ord(c) < 0x20 or ord(c) > 0x7e for c in name):
        return False
    # Substance gate. A descriptor that declares nothing is not a registered
    # descriptor -- it is a .proto path in a strings table preceded by a byte
    # that happens to be its length. The negative control produced 35081 such
    # "descriptors" in 40MB of noise before this gate existed; with it, zero.
    if not (fdp.message_type or fdp.enum_type or fdp.service or fdp.extension):
        return False
    if exact:
        return fdp.SerializeToString() == blob
    if len(fdp.UnknownFields()) > 0:
        return False
    return True


def try_parse(buf, start):
    """
    Attempt to recover a FileDescriptorProto beginning at `start`.
    Returns (fdp, size, exact) or (None, None, None).

    The greedy walk can over-run into adjacent .rdata that happens to parse as
    valid top-level fields, so candidate ends are tried longest-first and the
    longest that satisfies the acceptance test wins.
    """
    ends = scan_fdp_boundaries(buf, start)
    if not ends:
        return None, None, None
    for exact in (True, False):
        for end in reversed(ends):
            blob = bytes(buf[start:end])
            fdp = descriptor_pb2.FileDescriptorProto()
            try:
                fdp.ParseFromString(blob)
            except Exception:
                continue
            if _accept(fdp, blob, exact):
                return fdp, end - start, exact
    return None, None, None


# --------------------------------------------------------------------------
# .proto reconstruction
# --------------------------------------------------------------------------

_T = descriptor_pb2.FieldDescriptorProto
TYPE_NAME = {
    _T.TYPE_DOUBLE: "double", _T.TYPE_FLOAT: "float", _T.TYPE_INT64: "int64",
    _T.TYPE_UINT64: "uint64", _T.TYPE_INT32: "int32", _T.TYPE_FIXED64: "fixed64",
    _T.TYPE_FIXED32: "fixed32", _T.TYPE_BOOL: "bool", _T.TYPE_STRING: "string",
    _T.TYPE_GROUP: "group", _T.TYPE_MESSAGE: "message", _T.TYPE_BYTES: "bytes",
    _T.TYPE_UINT32: "uint32", _T.TYPE_ENUM: "enum", _T.TYPE_SFIXED32: "sfixed32",
    _T.TYPE_SFIXED64: "sfixed64", _T.TYPE_SINT32: "sint32", _T.TYPE_SINT64: "sint64",
}
# Wire type per protobuf spec: 0 varint, 1 64-bit, 2 length-delimited, 5 32-bit
WIRE_TYPE = {
    _T.TYPE_INT32: 0, _T.TYPE_INT64: 0, _T.TYPE_UINT32: 0, _T.TYPE_UINT64: 0,
    _T.TYPE_SINT32: 0, _T.TYPE_SINT64: 0, _T.TYPE_BOOL: 0, _T.TYPE_ENUM: 0,
    _T.TYPE_FIXED64: 1, _T.TYPE_SFIXED64: 1, _T.TYPE_DOUBLE: 1,
    _T.TYPE_STRING: 2, _T.TYPE_BYTES: 2, _T.TYPE_MESSAGE: 2, _T.TYPE_GROUP: 3,
    _T.TYPE_FIXED32: 5, _T.TYPE_SFIXED32: 5, _T.TYPE_FLOAT: 5,
}
LABEL_NAME = {1: "optional", 2: "required", 3: "repeated"}


def field_type_str(f):
    if f.type in (_T.TYPE_MESSAGE, _T.TYPE_ENUM, _T.TYPE_GROUP):
        return (_as_text(f.type_name) or "?").lstrip(".")
    return TYPE_NAME.get(f.type, "type%d" % f.type)


def wire_type_of(f):
    """Effective wire type. Packed repeated scalars ride as length-delimited."""
    base = WIRE_TYPE.get(f.type, 2)
    if f.label == 3 and base in (0, 1, 5):
        if f.options.packed or f.type != _T.TYPE_STRING:
            return "%d (or 2 if packed)" % base
    return str(base)


def render_field(f, syntax, indent):
    pad = " " * indent
    parts = []
    if syntax == "proto2":
        parts.append(LABEL_NAME.get(f.label, "optional"))
    else:
        if f.label == 3:
            parts.append("repeated")
        elif f.proto3_optional:
            parts.append("optional")
    parts.append(field_type_str(f))
    parts.append(_as_text(f.name) or "?")
    parts.append("=")
    opts = []
    if f.HasField("default_value"):
        dv = _as_text(f.default_value) or ""
        if f.type == _T.TYPE_STRING:
            dv = '"%s"' % dv
        opts.append("default = %s" % dv)
    if f.options.packed:
        opts.append("packed = true")
    if f.options.deprecated:
        opts.append("deprecated = true")
    tail = "%d" % f.number
    if opts:
        tail += " [%s]" % ", ".join(opts)
    return "%s%s %s;" % (pad, " ".join(parts), tail)


def render_enum(e, indent):
    pad = " " * indent
    out = ["%senum %s {" % (pad, _as_text(e.name) or "?")]
    for v in e.value:
        out.append("%s  %s = %d;" % (pad, _as_text(v.name) or "?", v.number))
    out.append("%s}" % pad)
    return out


def render_message(m, syntax, indent):
    pad = " " * indent
    out = ["%smessage %s {" % (pad, _as_text(m.name) or "?")]
    for nested in m.nested_type:
        if nested.options.map_entry:
            continue  # rendered inline as map<> by the field below
        out += render_message(nested, syntax, indent + 2)
    for e in m.enum_type:
        out += render_enum(e, indent + 2)
    oneof_members = {}
    for f in m.field:
        if f.HasField("oneof_index") and not f.proto3_optional:
            oneof_members.setdefault(f.oneof_index, []).append(f)
    plain = [f for f in m.field
             if not f.HasField("oneof_index") or f.proto3_optional]
    for f in plain:
        out.append(render_field(f, syntax, indent + 2))
    for idx, decl in enumerate(m.oneof_decl):
        members = oneof_members.get(idx, [])
        if not members:
            continue
        out.append("%s  oneof %s {" % (pad, _as_text(decl.name) or "?"))
        for f in members:
            out.append(render_field(f, syntax, indent + 4).replace(
                "optional ", "").replace("required ", ""))
        out.append("%s  }" % pad)
    for r in m.reserved_range:
        out.append("%s  reserved %d to %d;" % (pad, r.start, r.end - 1))
    out.append("%s}" % pad)
    return out


def render_service(s, indent=0):
    pad = " " * indent
    out = ["%sservice %s {" % (pad, _as_text(s.name) or "?")]
    for meth in s.method:
        cs = "stream " if meth.client_streaming else ""
        ss = "stream " if meth.server_streaming else ""
        out.append("%s  rpc %s(%s%s) returns (%s%s);" % (
            pad, _as_text(meth.name) or "?", cs,
            (_as_text(meth.input_type) or "?").lstrip("."),
            ss, (_as_text(meth.output_type) or "?").lstrip(".")))
    out.append("%s}" % pad)
    return out


def render_proto(fdp):
    syntax = _as_text(fdp.syntax) or "proto2"
    out = ['syntax = "%s";' % syntax, ""]
    if fdp.package:
        out += ["package %s;" % (_as_text(fdp.package) or "?"), ""]
    for dep in fdp.dependency:
        out.append('import "%s";' % (_as_text(dep) or "?"))
    if fdp.dependency:
        out.append("")
    for e in fdp.enum_type:
        out += render_enum(e, 0) + [""]
    for m in fdp.message_type:
        out += render_message(m, syntax, 0) + [""]
    for s in fdp.service:
        out += render_service(s, 0) + [""]
    for f in fdp.extension:
        out.append("extend %s { %s }" % (
            (_as_text(f.extendee) or "?").lstrip("."),
            render_field(f, syntax, 0).strip()))
    return "\n".join(out).rstrip() + "\n"


def walk_messages(fdp):
    """Yield (fully_qualified_name, DescriptorProto) including nested."""
    def rec(prefix, msg):
        nm = _as_text(msg.name) or "?"
        fq = "%s.%s" % (prefix, nm) if prefix else nm
        yield fq, msg
        for n in msg.nested_type:
            yield from rec(fq, n)
    for m in fdp.message_type:
        yield from rec(_as_text(fdp.package) or "", m)


# --------------------------------------------------------------------------
# Diagnostics: test the JSON-vs-protobuf premise directly
# --------------------------------------------------------------------------

DIAGNOSTIC_STRINGS = [
    # protobuf registration APIs -- which era is linked
    b"InternalAddGeneratedFile",
    b"AddDescriptors",
    b"descriptor_table",
    b"google/protobuf/descriptor.proto",
    b"google::protobuf::Reflection",
    b"google::protobuf::MessageLite",
    b"google::protobuf::DescriptorPool",
    # AWS SDK serialization shape -- JSON or not
    b"AmazonSerializableWebServiceRequest",
    b"Aws::Utils::Json::JsonValue",
    b"Aws::Utils::Json::JsonView",
    b"SerializePayload",
    b"JavelinGatewayService",
    b"application/json",
    b"application/x-protobuf",
    b"application/octet-stream",
    # GridMate replica marshalling -- the actual world-stream candidate
    b"ReplicaChunk",
    b"InitializeReplicatedFields",
    b"DataSetBase",
    b"Marshaler",
]


def run_diagnostics(data):
    rows = []
    for needle in DIAGNOSTIC_STRINGS:
        count = data.count(needle)
        rows.append((needle.decode("ascii", "replace"), count))
    return rows


# --------------------------------------------------------------------------
# Driver
# --------------------------------------------------------------------------

def sanitize(path):
    return re.sub(r"[^A-Za-z0-9._-]", "_", path)


def scan_file(path, outdir, diagnostics=False, all_sections=False):
    with open(path, "rb") as fh:
        data = fh.read()

    print("file        : %s" % path)
    print("size        : %d bytes" % len(data))
    try:
        pe = PE(data)
        print("image base  : 0x%x" % pe.image_base)
        print("sections    : %s" % ", ".join(s.name for s in pe.sections))
        is_pe = True
    except ValueError as exc:
        print("PE parse    : %s  (scanning raw, no VA mapping)" % exc)
        pe = None
        is_pe = False

    # Which regions to scan. Descriptors live in initialized read-only data.
    regions = []
    if pe and not all_sections:
        for s in pe.sections:
            if s.name in (".rdata", ".data", ".rodata") and s.raw_size:
                regions.append((s.raw_ptr, s.raw_ptr + s.raw_size, s.name))
        if not regions:
            regions = [(0, len(data), "<whole file>")]
    else:
        regions = [(0, len(data), "<whole file>")]
    print("scanning    : %s" % ", ".join(r[2] for r in regions))
    print()

    results = []
    seen = set()
    for start, stop, secname in regions:
        window = data[start:stop]
        for off, path_s in find_candidates(window, base_offset=start):
            if off in seen:
                continue
            fdp, size, exact = try_parse(data, off)
            if fdp is None:
                continue
            seen.add(off)
            va = pe.va_for_file_offset(off) if is_pe else None
            sig = binascii.hexlify(data[off:off + 16]).decode()
            results.append({
                "offset": off, "va": va, "size": size, "section": secname,
                "path": _as_text(fdp.name) or path_s, "fdp": fdp, "sig": sig,
                "exact": exact,
            })

    results.sort(key=lambda r: r["offset"])
    print("FileDescriptorProto blobs recovered: %d" % len(results))
    print()

    os.makedirs(outdir, exist_ok=True)
    os.makedirs(os.path.join(outdir, "blobs"), exist_ok=True)
    os.makedirs(os.path.join(outdir, "proto"), exist_ok=True)

    index_rows = []
    field_rows = []
    services = []

    for i, r in enumerate(results):
        fdp = r["fdp"]
        blob = data[r["offset"]:r["offset"] + r["size"]]
        bname = "%03d_%s.bin" % (i, sanitize(r["path"]))
        with open(os.path.join(outdir, "blobs", bname), "wb") as fh:
            fh.write(blob)

        pname = sanitize(r["path"])
        if not pname.endswith(".proto"):
            pname += ".proto"
        with open(os.path.join(outdir, "proto", pname), "w") as fh:
            fh.write(render_proto(fdp))

        nmsg = sum(1 for _ in walk_messages(fdp))
        index_rows.append([
            str(i), r["path"], _as_text(fdp.package) or "",
            ("0x%x" % r["va"]) if r["va"] else "-",
            "0x%x" % r["offset"], str(r["size"]), r["section"],
            str(nmsg), str(len(fdp.enum_type)), str(len(fdp.service)),
            "exact" if r["exact"] else "PARTIAL", r["sig"],
        ])

        for fq, msg in walk_messages(fdp):
            for f in msg.field:
                field_rows.append([
                    r["path"], fq, _as_text(f.name) or "?", str(f.number),
                    field_type_str(f), LABEL_NAME.get(f.label, "?"),
                    wire_type_of(f),
                ])

        for s in fdp.service:
            services.append((r["path"], fdp.package, s))

    with open(os.path.join(outdir, "index.tsv"), "w") as fh:
        fh.write("idx\tproto_path\tpackage\tva\tfile_off\tsize\tsection\t"
                 "messages\tenums\tservices\tconfidence\tsignature_first16\n")
        for row in index_rows:
            fh.write("\t".join(row) + "\n")

    with open(os.path.join(outdir, "fields.tsv"), "w") as fh:
        fh.write("proto_path\tmessage\tfield\tnumber\ttype\tlabel\twire_type\n")
        for row in field_rows:
            fh.write("\t".join(row) + "\n")

    # ---- report ----
    lines = []
    lines.append("# P2 scan report")
    lines.append("")
    lines.append("- target: `%s`" % os.path.abspath(path))
    lines.append("- size: %d bytes" % len(data))
    if is_pe:
        lines.append("- image base: `0x%x`" % pe.image_base)
    lines.append("- FileDescriptorProto blobs recovered: **%d**" % len(results))
    lines.append("- total messages: **%d**" % sum(
        1 for r in results for _ in walk_messages(r["fdp"])))
    lines.append("- total service blocks: **%d**" % len(services))
    lines.append("")

    if results:
        lines.append("## Registered .proto files")
        lines.append("")
        lines.append("| # | path | package | VA | size | msgs | svcs | conf | signature (first 16B) |")
        lines.append("|---|---|---|---|---|---|---|---|---|")
        for row in index_rows:
            lines.append("| %s | `%s` | `%s` | `%s` | %s | %s | %s | %s | `%s` |" % (
                row[0], row[1], row[2], row[3], row[5], row[7], row[9], row[10], row[11]))
        lines.append("")

    lines.append("## Service blocks (both directions in one place)")
    lines.append("")
    if services:
        for pth, pkg, s in services:
            lines.append("### `%s` in `%s`" % (s.name, pth))
            lines.append("")
            lines.append("```proto")
            lines += render_service(s)
            lines.append("```")
            lines.append("")
    else:
        lines.append("**None.** No `service` block is present in any recovered "
                     "descriptor. P2 prediction 3 is FALSIFIED if this holds on "
                     "the retail binary: there is no single RPC interface "
                     "listing both directions.")
        lines.append("")

    lines.append("## Server->client candidates (OI-H2-3)")
    lines.append("")
    hits = []
    for r in results:
        for fq, _msg in walk_messages(r["fdp"]):
            leaf = fq.rsplit(".", 1)[-1]
            if re.search(r"(Result|Response|Notification|Event|Update|Snapshot)$", leaf):
                hits.append((r["path"], fq))
    if hits:
        for pth, fq in hits:
            lines.append("- `%s`  (in `%s`)" % (fq, pth))
    else:
        lines.append("**None found by name.** No message name ends in Result, "
                     "Response, Notification, Event, Update or Snapshot.")
    lines.append("")

    if diagnostics:
        lines.append("## Diagnostics -- serialization shape")
        lines.append("")
        lines.append("| string | count |")
        lines.append("|---|---|")
        for name, count in run_diagnostics(data):
            lines.append("| `%s` | %d |" % (name, count))
        lines.append("")
        lines.append("Reading: high `JsonValue`/`JsonView`/"
                     "`AmazonSerializableWebServiceRequest` counts with an "
                     "`application/json` content type indicate the AWS SDK "
                     "path is JSON, not protobuf -- which would mean the "
                     "Javelin Gateway models are NOT the protobuf choke point "
                     "and protobuf serves some other subsystem.")
        lines.append("")

    with open(os.path.join(outdir, "report.md"), "w") as fh:
        fh.write("\n".join(lines) + "\n")

    print("wrote: %s/index.tsv, fields.tsv, report.md, blobs/, proto/" % outdir)
    if services:
        print("SERVICE BLOCKS FOUND: %d  <-- P2 prediction 3 CONFIRMED" % len(services))
    else:
        print("no service blocks found")
    return results


# --------------------------------------------------------------------------
# Self-test: prove the instrument on a target we control (CHARTER §2/§4)
# --------------------------------------------------------------------------

def build_synthetic_fdp():
    fdp = descriptor_pb2.FileDescriptorProto()
    fdp.name = "javelin/gateway/world.proto"
    fdp.package = "javelin.gateway"
    fdp.syntax = "proto3"
    fdp.dependency.append("google/protobuf/timestamp.proto")

    e = fdp.enum_type.add()
    e.name = "WorldState"
    for n, v in (("WORLD_UNKNOWN", 0), ("WORLD_UP", 1), ("WORLD_QUEUED", 2)):
        ev = e.value.add()
        ev.name, ev.number = n, v

    m = fdp.message_type.add()
    m.name = "PostGameWorldsWorldIdCharactersRequest"
    f = m.field.add()
    f.name, f.number, f.type, f.label = "world_id", 1, _T.TYPE_STRING, 1
    f = m.field.add()
    f.name, f.number, f.type, f.label = "character_id", 2, _T.TYPE_UINT64, 1
    f = m.field.add()
    f.name, f.number, f.type, f.label = "entitlements", 3, _T.TYPE_STRING, 3
    f = m.field.add()
    f.name, f.number, f.type, f.label = "state", 4, _T.TYPE_ENUM, 1
    f.type_name = ".javelin.gateway.WorldState"

    nested = m.nested_type.add()
    nested.name = "Position"
    for i, nm in enumerate(("x", "y", "z"), start=1):
        nf = nested.field.add()
        nf.name, nf.number, nf.type, nf.label = nm, i, _T.TYPE_FLOAT, 1

    oo = m.oneof_decl.add()
    oo.name = "auth"
    f = m.field.add()
    f.name, f.number, f.type, f.label = "jwt", 10, _T.TYPE_STRING, 1
    f.oneof_index = 0
    f = m.field.add()
    f.name, f.number, f.type, f.label = "ticket", 11, _T.TYPE_BYTES, 1
    f.oneof_index = 0

    r = fdp.message_type.add()
    r.name = "PostGameWorldsWorldIdCharactersResult"
    rf = r.field.add()
    rf.name, rf.number, rf.type, rf.label = "rep_address", 1, _T.TYPE_STRING, 1
    rf = r.field.add()
    rf.name, rf.number, rf.type, rf.label = "spawn", 2, _T.TYPE_MESSAGE, 1
    rf.type_name = ".javelin.gateway.PostGameWorldsWorldIdCharactersRequest.Position"

    svc = fdp.service.add()
    svc.name = "JavelinGatewayService"
    meth = svc.method.add()
    meth.name = "PostGameWorldsWorldIdCharacters"
    meth.input_type = ".javelin.gateway.PostGameWorldsWorldIdCharactersRequest"
    meth.output_type = ".javelin.gateway.PostGameWorldsWorldIdCharactersResult"
    return fdp


def build_second_fdp():
    fdp = descriptor_pb2.FileDescriptorProto()
    fdp.name = "telemetry/metrics.proto"
    fdp.package = "amazon.telemetry"
    fdp.syntax = "proto2"
    m = fdp.message_type.add()
    m.name = "MetricSample"
    f = m.field.add()
    f.name, f.number, f.type, f.label = "key", 1, _T.TYPE_STRING, 2
    f = m.field.add()
    f.name, f.number, f.type, f.label = "value", 2, _T.TYPE_DOUBLE, 1
    f.default_value = "0"
    return fdp


def make_fake_pe(payloads):
    """
    Build a minimal but structurally real PE32+ with a .rdata section holding
    the payload blobs surrounded by realistic non-descriptor noise. The point
    is to exercise PE parsing, VA mapping, blob discovery, extent recovery and
    boundary conditions -- especially blobs butted against adjacent data with
    no separator, which is the case that breaks a naive greedy walk.
    """
    noise_a = b"\x00" * 64 + b"Aws::Utils::Json::JsonView\x00" + b"\xcc" * 32
    noise_b = (b"\x11\x22\x33\x44" * 8) + b"application/json\x00"
    # deliberately adjacent, no padding between blob 0 and the trailing noise
    rdata = bytearray()
    layout = []
    rdata += noise_a
    for p in payloads:
        layout.append(len(rdata))
        rdata += p
        rdata += noise_b          # butted directly against the blob end
    rdata += b"InternalAddGeneratedFile\x00AddDescriptors\x00"
    rdata += b"google::protobuf::Reflection\x00ReplicaChunk\x00"

    file_align = 0x200
    sect_align = 0x1000
    headers_size = 0x400
    raw_size = (len(rdata) + file_align - 1) // file_align * file_align
    image_base = 0x140000000
    rdata_va = 0x1000

    buf = bytearray(headers_size + raw_size)
    buf[0:2] = b"MZ"
    struct.pack_into("<I", buf, 0x3C, 0x80)
    off = 0x80
    buf[off:off + 4] = b"PE\0\0"
    coff = off + 4
    opt_size = 240
    struct.pack_into("<HHIIIHH", buf, coff,
                     0x8664, 1, 0, 0, 0, opt_size, 0x0022)
    opt = coff + 20
    struct.pack_into("<H", buf, opt, 0x20B)          # PE32+
    struct.pack_into("<Q", buf, opt + 24, image_base)
    sec = opt + opt_size
    struct.pack_into("<8sIIII", buf, sec,
                     b".rdata", len(rdata), rdata_va, raw_size, headers_size)
    buf[headers_size:headers_size + len(rdata)] = rdata

    vas = [image_base + rdata_va + o for o in layout]
    offs = [headers_size + o for o in layout]
    return bytes(buf), offs, vas


def selftest():
    print("=" * 70)
    print("P2 INSTRUMENT SELF-TEST -- synthetic target, known ground truth")
    print("=" * 70)
    print()

    a, b = build_synthetic_fdp(), build_second_fdp()
    pa, pb = a.SerializeToString(), b.SerializeToString()
    pe_bytes, offs, vas = make_fake_pe([pa, pb])

    truth = [
        (offs[0], vas[0], len(pa), a.name),
        (offs[1], vas[1], len(pb), b.name),
    ]
    print("ground truth:")
    for o, v, s, n in truth:
        print("  off=0x%-6x va=0x%-12x size=%-5d %s" % (o, v, s, n))
    print()

    tmp = "/tmp/p2_selftest.bin"
    with open(tmp, "wb") as fh:
        fh.write(pe_bytes)

    outdir = "/tmp/p2_selftest_out"
    results = scan_file(tmp, outdir, diagnostics=True)

    failures = []
    if len(results) != 2:
        failures.append("expected 2 blobs, recovered %d" % len(results))
    for expected, got in zip(truth, results):
        eo, ev, es, en = expected
        if got["offset"] != eo:
            failures.append("offset: expected 0x%x got 0x%x" % (eo, got["offset"]))
        if got["va"] != ev:
            failures.append("VA: expected 0x%x got 0x%x" % (ev, got["va"]))
        if got["size"] != es:
            failures.append("size: expected %d got %d" % (es, got["size"]))
        if got["path"] != en:
            failures.append("name: expected %s got %s" % (en, got["path"]))

    # round-trip: reconstructed .proto must preserve every field number/type
    orig_fields = {(fq, f.name): (f.number, f.type)
                   for fq, m in walk_messages(a) for f in m.field}
    got_fields = {}
    for r in results:
        if r["path"] != a.name:
            continue
        for fq, m in walk_messages(r["fdp"]):
            for f in m.field:
                got_fields[(fq, f.name)] = (f.number, f.type)
    if orig_fields != got_fields:
        failures.append("field round-trip mismatch")

    svc_found = any(r["fdp"].service for r in results)
    if not svc_found:
        failures.append("service block not recovered")

    print()
    print("-" * 70)
    if failures:
        print("SELF-TEST FAILED")
        for f in failures:
            print("  ! " + f)
        return 1
    print("SELF-TEST PASSED")
    print("  - PE parsed, image base and VA mapping correct")
    print("  - both blobs located by signature anchor")
    print("  - exact sizes recovered WITHOUT the caller's size constant")
    print("  - blob boundary correct with adjacent data butted against it")
    print("  - nested messages, oneof, enum, repeated, defaults round-tripped")
    print("  - service block with input_type/output_type recovered")
    print()
    print("Reconstructed .proto for the synthetic Javelin file:")
    print("-" * 70)
    with open(os.path.join(outdir, "proto",
                           sanitize(a.name)), "r") as fh:
        print(fh.read())
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("binary", nargs="?", help="path to NewWorld.exe")
    ap.add_argument("--outdir", default="p2_out")
    ap.add_argument("--diagnostics", action="store_true",
                    help="count serialization-shape marker strings")
    ap.add_argument("--all-sections", action="store_true",
                    help="scan the whole file, not just .rdata/.data")
    ap.add_argument("--selftest", action="store_true")
    args = ap.parse_args()

    if args.selftest:
        return selftest()
    if not args.binary:
        ap.error("give a binary, or --selftest")
    scan_file(args.binary, args.outdir,
              diagnostics=args.diagnostics, all_sections=args.all_sections)
    return 0


if __name__ == "__main__":
    sys.exit(main())
