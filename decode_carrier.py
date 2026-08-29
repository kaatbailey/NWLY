#!/usr/bin/env python3
"""
NWLY / T4 step 4 -- decode captured GridMate Carrier datagrams.

This is the step-4 completion check. The layout below was read out of
GridMate/Carrier/Carrier.cpp at fork commit 413ecaf -- NOT guessed from a
hexdump. Running it against a capture confirms source and wire agree.

Source of every field (Carrier.cpp line numbers at 413ecaf):

  kCarrierEndian = BigEndian                                   line 58
  WriteDataGramHeader: writes m_flowControl.m_sequenceNumber   line 2869-2873
  WriteMessageHeader:  flags, then dataSize, then optionals    line 3494-3541

  Message flag bits (Carrier.cpp lines 86-93):
    MF_RELIABLE         = 1 << 0   (0x01)
    MF_UNUSED           = 1 << 1   (0x02)   must be 0
    MF_CHUNKS           = 1 << 2   (0x04)
    MF_SQUENTIAL_ID     = 1 << 3   (0x08)
    MF_SQUENTIAL_REL_ID = 1 << 4   (0x10)
    MF_DATA_CHANNEL     = 1 << 5   (0x20)
    MF_UNUSED           = 1 << 6   (0x40)   must be 0
    MF_CONNECTING       = 1 << 7   (0x80)

  Per-message field order, all big-endian (WriteMessageHeader):
    flags        u8   always
    dataSize     u16  always
    channel      u8   only if MF_DATA_CHANNEL
    numChunks    u16  only if MF_CHUNKS
    sequenceNum  u16  only if NOT MF_SQUENTIAL_ID
    relSeqNum    u16  only if NOT MF_SQUENTIAL_REL_ID
    payload      dataSize bytes

  Note the inverted sense: the MF_SQUENTIAL_* flags mean "this value is
  implied by the previous message, so it is NOT on the wire". Reading them
  the obvious way round desynchronises the parse immediately.

Usage:
    ./decode_carrier.py build/carrier_plaintext.pcap
    ./decode_carrier.py build/carrier_plaintext.pcap --max 8

Needs tshark (wireshark-cli) to read the pcap.
"""

import argparse
import struct
import subprocess
import sys

MF = [
    (0x01, "RELIABLE"),
    (0x02, "UNUSED_1"),
    (0x04, "CHUNKS"),
    (0x08, "SEQUENTIAL_ID"),
    (0x10, "SEQUENTIAL_REL_ID"),
    (0x20, "DATA_CHANNEL"),
    (0x40, "UNUSED_6"),
    (0x80, "CONNECTING"),
]


def flag_names(f):
    return "|".join(n for b, n in MF if f & b) or "none"


def u16(b, o):
    return struct.unpack_from(">H", b, o)[0]


WAKEUP = 0x47   # 'G', AZ_SOCKET_WAKEUP_MSG_VALUE, SocketDriver.cpp:55

# DTLS record types (RFC 6347). Used only to recognise that a capture is
# encrypted rather than to parse it -- once epoch > 0 the body is ciphertext.
DTLS_RT = {20: "ChangeCipherSpec", 21: "Alert", 22: "Handshake", 23: "ApplicationData"}
DTLS_HS = {0: "HelloRequest", 1: "ClientHello", 2: "ServerHello",
           3: "HelloVerifyRequest", 11: "Certificate", 12: "ServerKeyExchange",
           13: "CertificateRequest", 14: "ServerHelloDone", 15: "CertificateVerify",
           16: "ClientKeyExchange", 20: "Finished"}


def as_dtls(b):
    """If b looks like a DTLS record, describe it. Header is 13 bytes:
    type u8 | version u16 (0xfeff=1.0, 0xfefd=1.2) | epoch u16 | seq u48 | len u16
    Matches the RecordHeader that SecureSocketDriver.cpp parses by hand."""
    if len(b) < 13 or b[0] not in DTLS_RT or b[1] != 0xFE:
        return None
    ver = {0xFF: "1.0", 0xFD: "1.2"}.get(b[2], hex(b[2]))
    epoch = int.from_bytes(b[3:5], "big")
    length = int.from_bytes(b[11:13], "big")
    d = f"DTLS{ver} {DTLS_RT[b[0]]} epoch={epoch} len={length}"
    if b[0] == 22 and epoch == 0 and len(b) > 13:
        d += f" {DTLS_HS.get(b[13], 'hs' + str(b[13]))}"
    return d


def decode(payload):
    """Returns (lines, ok). ok is False if the parse desynchronised."""
    out = []

    # Single 'G' addressed to the socket's own port: SocketDriver's self-wakeup,
    # sent by StopWaitForData() (SocketDriver.cpp:1449-1470) to break the recv
    # thread out of its blocking wait. Receive side drops it as an "internal
    # wake up message" (line 1423). Not Carrier protocol -- do not try to parse
    # it, and exclude it when diffing against retail.
    if len(payload) == 1 and payload[0] == WAKEUP:
        return ["  SocketDriver self-wakeup byte ('G') -- not a Carrier datagram"], True

    # A DTLS record means SecureSocketDriver is in use (T4 step 5). Records at
    # epoch 0 are the cleartext handshake; epoch >= 1 is ciphertext and there is
    # nothing further to decode without the session keys.
    d = as_dtls(payload)
    if d:
        return [f"  {d} -- encrypted, not plaintext Carrier"], True

    if len(payload) < 2:
        return ["  too short for a datagram header"], False

    seq = u16(payload, 0)
    out.append(f"  datagram seq = {seq}")
    o = 2
    n = 0

    while o < len(payload):
        if o + 3 > len(payload):
            out.append(f"  +{o}: {len(payload) - o} trailing byte(s), no room for a message header")
            return out, False
        flags = payload[o]
        if flags & 0x42:
            out.append(f"  +{o}: flags 0x{flags:02x} sets a reserved bit -- parse desynchronised")
            return out, False
        size = u16(payload, o + 1)
        p = o + 3
        parts = [f"size={size}"]

        if flags & 0x20:
            if p >= len(payload):
                return out + [f"  +{o}: truncated at channel"], False
            parts.append(f"channel={payload[p]}")
            p += 1
        if flags & 0x04:
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at numChunks"], False
            parts.append(f"chunks={u16(payload, p)}")
            p += 2
        if not (flags & 0x08):
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at seqNum"], False
            parts.append(f"msgSeq={u16(payload, p)}")
            p += 2
        if not (flags & 0x10):
            if p + 2 > len(payload):
                return out + [f"  +{o}: truncated at relSeqNum"], False
            parts.append(f"relSeq={u16(payload, p)}")
            p += 2

        if p + size > len(payload):
            out.append(f"  +{o}: msg {n} claims {size} payload bytes, only {len(payload) - p} left")
            return out, False

        data = payload[p:p + size]
        out.append(f"  msg {n}: flags=0x{flags:02x} [{flag_names(flags)}] " + " ".join(parts))
        out.append(f"          payload {data.hex(' ') if size else '(empty)'}")
        o = p + size
        n += 1

    out.append(f"  -> {n} message(s), consumed all {len(payload)} bytes")
    return out, True


def read_pcap(path):
    try:
        r = subprocess.run(
            # --disable-protocol dtls is REQUIRED. Without it tshark dissects
            # secure captures as DTLS and leaves data.data empty, so every real
            # frame vanishes and only the 1-byte wakeups survive. Plaintext
            # captures are unaffected (no dissector claims them).
            ["tshark", "-r", path, "--disable-protocol", "dtls",
             "-Y", "udp", "-T", "fields",
             "-e", "udp.srcport", "-e", "udp.dstport", "-e", "data.data"],
            capture_output=True, text=True, check=True)
    except FileNotFoundError:
        sys.exit("tshark not found. Install it: sudo pacman -S wireshark-cli")
    except subprocess.CalledProcessError as e:
        sys.exit(f"tshark failed:\n{e.stderr}")

    out = []
    for line in r.stdout.splitlines():
        f = line.split("\t")
        if len(f) < 3 or not f[2].strip():
            continue
        # tshark may emit several data fields for one frame; take the first.
        hexstr = f[2].split(",")[0].replace(":", "").strip()
        try:
            out.append((f[0], f[1], bytes.fromhex(hexstr)))
        except ValueError:
            continue
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("pcap")
    ap.add_argument("--max", type=int, default=6, help="datagrams to decode (default 6)")
    args = ap.parse_args()

    pkts = read_pcap(args.pcap)
    if not pkts:
        sys.exit("No UDP payloads found in that capture.")

    print(f"{len(pkts)} datagrams with payload\n")

    # Classify every datagram, not just the ones printed. Counting only the
    # printed window, or counting wakeup bytes as successes, produces a false
    # PASS on a capture where nothing real was decoded at all.
    n_wake = n_dtls = n_carrier = n_bad = 0
    for _, _, p in pkts:
        if len(p) == 1 and p[0] == WAKEUP:
            n_wake += 1
        elif as_dtls(p):
            n_dtls += 1
        elif decode(p)[1]:
            n_carrier += 1
        else:
            n_bad += 1

    for i, (sp, dp, payload) in enumerate(pkts[:args.max]):
        print(f"=== #{i}  {sp} -> {dp}  {len(payload)} bytes ===")
        print("  raw:", payload.hex(" "))
        print("\n".join(decode(payload)[0]))
        print()

    real = n_dtls + n_carrier + n_bad
    print(f"{len(pkts)} datagrams: {n_carrier} Carrier, {n_dtls} DTLS, "
          f"{n_wake} wakeup, {n_bad} undecodable")

    if real == 0:
        print()
        print("NOTHING REAL DECODED -- only wakeup bytes reached the decoder.")
        print("This is almost always tshark's dissector hiding the payload, not an")
        print("empty capture. Check the raw bytes are there:")
        print("  tshark -r <pcap> --disable-protocol dtls -T fields -e data.data | head")
        sys.exit(1)

    if n_bad:
        print()
        print(f"{n_bad} datagram(s) did not decode. Either the layout reading is wrong,")
        print("or they are a variant (compression hint / ack block) not covered here.")
        print("Record which, and check Carrier.cpp GenerateDataGram.")
        sys.exit(1)

    print()
    if n_dtls and not n_carrier:
        print("SECURE capture: every real datagram is a DTLS record and none parse as")
        print("Carrier framing. The transport is encrypted -- but confirm the payload")
        print("string is absent too; record type alone does not prove that.")
    elif n_carrier and not n_dtls:
        print("PLAINTEXT capture: every real datagram decodes against the layout read")
        print("from Carrier.cpp. Source and wire agree.")
    else:
        print("MIXED capture: both Carrier and DTLS framing present. Expected only")
        print("mid-handshake; otherwise check the drivers were set on both CarrierDescs.")


if __name__ == "__main__":
    main()
