# P2 — Extract the protobuf message schemas from the binary

> # ✅ DONE — 2026-09-04. Findings in STATE §17.9.
>
> **VERDICT: NEGATIVE — and the negative is the deliverable.**
>
> Protobuf is present in `NewWorld.exe` and **irrelevant to the world protocol**.
> A whole-binary scan recovered **3 `FileDescriptorProto` blobs**, none of them
> game protocol:
>
> | `.proto` | VA | size | what it is |
> |---|---|---|---|
> | `campfire_event_default.proto` | `0x1486f5b60` | 1407 | Amazon Campfire **telemetry** — 1 message, 1 nested context struct, 1 enum |
> | `google/protobuf/empty.proto` | `0x1495ab7c0` | 190 | stock well-known type |
> | `google/protobuf/descriptor.proto` | `0x1495b3330` | 6028 | stock — present *only* because `Reflection` requires it |
>
> **No Javelin descriptor. No `service` block. No message named
> `*Result`/`*Response`. `application/x-protobuf` = 0 against
> `application/json` = 236.**
>
> **All three predictions in this file are falsified**, including prediction 3,
> billed here as "the single most valuable find P2 can make." The chunk's value is
> the correction, not a schema:
>
> - **FIND-2 closed negative.** T1's flag rested on a single `GOOGLE_CHECK` assert
>   string, and `descriptor.proto`'s presence is the whole explanation for it.
> - **§17.5's "protobuf choke point" corrected** (STATE §13). The AWS SDK path is
>   **JSON** — which §16.15 had already demonstrated by reading queue-`Token`
>   fields out of the stock `JsonView` GetString helper. *The evidence was in
>   `STATE.md` before H2 wrote the claim.*
> - **OI-H2-3 answered, mundanely.** Response types are absent from RTTI because
>   AWS SDK `XResult` classes are non-polymorphic — no vtable, no RTTI. Not an
>   exotic inbound path.
> - **Track P retargeted onto P5** — GridMate `ReplicaChunk` marshalling, for
>   which we hold the source at `7d4f1ee6`. No capture, no client, and immune to
>   the 2027-01-31 sunset.
>
> **Residual: OI-P2-1** — the registration mechanism is unconfirmed, and it is the
> one definition-of-done bullet this chunk did not satisfy. Low priority: there is
> no Javelin descriptor to register regardless of what registers the three that
> exist. **OI-P2-2** — are the 10 Javelin types the same REST routes P0 already
> decoded on TCP/443?
>
> Instrument kept: **`p2_scan.py`** — scans for the `FileDescriptorProto`
> *artefact* rather than a registration *function*, so it is
> protobuf-version-independent. Validated against synthetic, 171 MB positive and
> 40 MB negative controls **before** it was pointed at retail (test #63); the
> controls caught two defects that would otherwise have run on the real binary.
> Tests #63–#65.
>
> **Claims below that this chunk falsified are struck through with their
> replacement beside them, per CHARTER §5. The body is otherwise verbatim.**

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are the
context. Do not act on a summary of either.**

Created 2026-09-04, out of the §15 work order (item 2) and FIND-2 (§10, §15).
Warmed by H2 (§17), which located the Javelin Gateway dispatch mechanism and
~~identified the AWS SDK serialization path as the protobuf choke point.~~
**FALSIFIED — there is no protobuf on that path; it is JSON. STATE §13, §17.9.**

P2 is **static, needs no login, no running client, no Proton, and has no
deadline.** It operates on `NewWorld.exe` b22469132 on disk. Nothing is injected
or modified. It reuses the warm Ghidra project from H2 (`nwly.gpr`, §5).

---

## The one thing this chunk does

**Extract the protobuf message schemas embedded in `NewWorld.exe` b22469132 —
specifically the `FileDescriptorProto` blobs flagged by T1 (FIND-2, §10) — and
produce a human-readable schema for every message type the client sends or
receives on the world stream.**

~~The deliverable is a set of `.proto` files (or equivalent structured output)
describing the wire format of the Javelin Gateway world messages identified by H2
(§17.5). These schemas are what Track P decodes and what S1a must speak.~~
**FALSIFIED. No such schemas exist.** Track P decodes GridMate `ReplicaChunk`
marshalling (P5) and S1a speaks JSON on the Javelin side. §17.9.

Why this is the right next chunk: H2 enumerated 10 Javelin Gateway message types
by RTTI and located the AWS SDK serialization path as the protobuf choke point
(§17.5), but it did not extract the schemas themselves. P2 finishes that job
statically. ~~The server→client direction is entirely absent from H2's RTTI findings
(OI-H2-3) — the embedded `FileDescriptorProto` blobs are the primary static route
into that direction.~~ **FALSIFIED on the second clause.** The direction *is*
absent from RTTI, but for a boring reason (non-polymorphic `XResult` types), and
the blobs are **not** a route into it — they contain no Javelin types at all. The
real routes are P0's already-decrypted auth traffic and the GridMate fork source.
§17.9.

---

## Why this is answerable statically

Three force-multipliers:

1. **`google::protobuf::Reflection` is present in `NewWorld.exe`** (T1, §10,
   FIND-2). This is the runtime reflection system, which requires the full
   `FileDescriptorProto` blob for every message type to be present in the binary
   at runtime. The blobs are not optional — they are the reflection system's data
   source. **TRUE BUT MISLEADING AS APPLIED.** It holds for every *protobuf-generated*
   type, which turned out to be one telemetry schema. It says nothing about game
   messages, because game messages are not protobuf. **The inference "protobuf is
   present, therefore the protocol is protobuf" is the error this chunk exposed.**

2. **Protobuf's self-describing binary format is well-documented.** A
   `FileDescriptorProto` is itself a protobuf message (field ids and wire types
   are known). Extracting it requires finding the blob in the binary and running
   `protoc --decode=google.protobuf.FileDescriptorProto` or equivalent — no
   reverse engineering of the encoding, just locating the data.

3. ~~**H2 gave us the entry points.** The Javelin Gateway model constructors
   (`FUN_146406a90` family, §17.5) embed named vftables for 10 message types.
   The protobuf descriptors for those types are registered at startup by
   `google::protobuf::DescriptorPool::InternalAddGeneratedFile` — a known, named
   function with a known call pattern. Its callers are the registration sites; its
   arguments are the raw `FileDescriptorProto` blobs.~~ **FALSIFIED TWICE.**
   (a) Those 10 types have **no** protobuf descriptors — they are JSON models.
   (b) `InternalAddGeneratedFile` is the **proto2 / early-proto3** API; protobuf
   ≥3.10 emits `internal::AddDescriptors(const DescriptorTable*)` instead, so
   "a known, named function" was not a safe assumption either. §17.9.

---

## Step 0 — confirm the instrument

```fish
set -g NW ~/Documents/nwly-pin/22469132/Bin64/NewWorld.exe
sha256sum $NW    # expect 8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e
```

Open the warm Ghidra project (`~/Documents/Ghidra-projects/nwly.gpr`, §5). Do
not re-import — analysis is already done.

Confirm the warm landmarks from §17 are present:
- `FUN_14644a070` (GameConnection state machine) resolves.
- `Aws::JavelinGatewayService` RTTI present (Symbol Table filter `JavelinGateway`
  matches ~99 symbols).
- `google::protobuf` strings present — in the Symbol Tree or via Search →
  Program Text for `google::protobuf`.

If the SHA doesn't match §5, stop (CHARTER §6.3).

---

## Step 1 — locate `InternalAddGeneratedFile`

> **SUPERSEDED — this whole step is the wrong route.** `InternalAddGeneratedFile`
> is the proto2/early-proto3 registration API and the linked version is unknown up
> front. **Scan for the artefact, not the function:** a serialized
> `FileDescriptorProto` in `.rdata` is version-independent, and its size can be
> recovered by walking its own top-level fields, so the caller's size constant is
> not needed — which frees that constant to serve as an *independent check*.
> `p2_scan.py` does this in ~2 s on a 171 MB PE. Ghidra is still worth using, for
> **attribution** (which call site registers which blob) rather than discovery.
> §17.9.

`google::protobuf::DescriptorPool::InternalAddGeneratedFile(const void* encoded_file_descriptor, int size)` is the registration function. Every protobuf message type compiled into a binary calls it at startup (via `AddDescriptors` / `protobuf_AddDesc_` generated functions), passing the raw serialised `FileDescriptorProto` blob and its byte length.

**Find it in the binary:**

In Ghidra, search for the string `google::protobuf` in the Symbol Tree or via
Search → Program Text. Alternatively, `InternalAddGeneratedFile` has a
characteristic call signature: it is called with two arguments (a pointer to a
byte blob in `.rdata` and an integer size), and the blobs it receives are
immediately recognisable as protobuf wire format starting with field tag `0x0a`
(field 1, wire type 2 = length-delimited — the `name` field of
`FileDescriptorProto`).

**Predict before searching:** ~~`InternalAddGeneratedFile` will have many callers
— one per `.proto` file compiled in.~~ **FALSIFIED — 3 descriptors exist in total,
2 of them stock.** Each caller is a small `AddDescriptors`
stub that passes a pointer into `.rdata` and a size constant. The size constants
will vary (each `.proto` file's descriptor is a different size) but the pattern
will be uniform. Record the prediction, then confirm.

---

## Step 2 — enumerate the registration call sites

Once `InternalAddGeneratedFile` is located, examine its XREF list. Each caller
is one registered `.proto` file. For each:

1. Record the blob address (the first argument — a pointer into `.rdata` or
   `.data`) and the size (the second argument — an integer constant).
2. Note the caller's name or address.
3. Identify whether the blob is for a Javelin Gateway type (look at the first
   few bytes — the `name` field will decode to a path like
   `"javelin_gateway_service.proto"` or similar).

**The goal is a complete list of all registered `.proto` file blobs**, with
their addresses and sizes. Prioritise blobs whose file paths (visible in the
first bytes of the decoded name field) reference Javelin, world, game, or
character namespaces.

---

## Step 3 — extract the blobs

For each blob identified in Step 2, extract the raw bytes from the binary. Two
approaches:

**Approach A — Ghidra memory export (preferred for individual blobs):**
In Ghidra, navigate to the blob address, select the byte range (size from Step 2),
right-click → Copy Special → Python Byte String (or use File → Export → Binary).
Paste the bytes into a file.

**Approach B — command-line extraction (preferred for bulk):**
```fish
# dd from the pinned binary at the file offset corresponding to the VA
# (subtract the image base, typically 0x140000000 for this PE)
set va 0x<blob_va>
set size <blob_size>
set image_base 0x140000000
set file_offset (math "$va - $image_base")
dd if=$NW of=/tmp/proto_blob_<n>.bin bs=1 skip=$file_offset count=$size
```

Verify each blob starts with `0x0a` (protobuf field 1, wire type 2) — if it
starts with anything else it is not a `FileDescriptorProto`.

---

## Step 4 — decode the schemas

For each extracted blob:

```fish
# Decode as FileDescriptorProto
cat /tmp/proto_blob_<n>.bin | protoc --decode=google.protobuf.FileDescriptorProto \
    google/protobuf/descriptor.proto

# Or, if protoc is not available, use Python:
python3 -c "
from google.protobuf import descriptor_pb2
with open('/tmp/proto_blob_<n>.bin', 'rb') as f:
    data = f.read()
fd = descriptor_pb2.FileDescriptorProto()
fd.ParseFromString(data)
print(fd)
"
```

If neither `protoc` nor the Python protobuf library is installed:
```fish
pip install protobuf --break-system-packages
```

For each decoded `FileDescriptorProto`, record:
- The `name` field (the `.proto` file path)
- The `package` field
- All `message_type` entries (message names and their fields)
- All `enum_type` entries
- All `dependency` entries (imported `.proto` files)

~~**Prioritise the Javelin Gateway types** from §17.5 — confirm that each of the
10 named message types (`PostGameWorldsWorldIdCharactersRequest`,
`GetLoginInfoRequest`, etc.) has a corresponding schema with field names and
types. These are the schemas Track P must decode.~~ **VACUOUS — none of the 10
has a protobuf schema. Their names are literal REST routes
(`POST /game/worlds/{worldId}/characters`), and the API is JSON. OI-P2-2.**

---

## Step 5 — reconstruct `.proto` files

From the decoded `FileDescriptorProto` data, write `.proto` files. These can be
reconstructed manually or with a tool:

```fish
# protoc can write .proto from a FileDescriptorSet
# First, build a FileDescriptorSet from the individual blobs
# Then use protoc --decode_raw or a proto-to-proto converter
```

Alternatively, the Python protobuf library's `descriptor_pb2.FileDescriptorProto`
output is sufficient — the field names, types, and numbers are all present and
readable. The `.proto` files do not need to be compilable, only accurate.

~~**For each message type in §17.5, record:**~~ **VACUOUS — no §17.5 type has a
descriptor. The list below was applied instead to `campfire_event_default.proto`,
the only non-stock schema in the binary. §17.9.**
- All field names, field numbers, and wire types
- Nested message types
- Enum types and values
- Whether it has a `oneof` (relevant for S1a's send-side)
- The `repeated` fields (these are lists — important for character and world list
  messages)

---

## Step 6 — the server→client direction (OI-H2-3)

~~H2 found no `Result`/`Response` RTTI types (§17.5, OI-H2-3). The
`FileDescriptorProto` blobs may contain the response message types even though
their RTTI is absent — protobuf descriptors are registered for all types in a
`.proto` file, not just the ones instantiated as RTTI objects.~~ **The reasoning
is sound and the premise is false: there are no Javelin blobs to contain them.**
**OI-H2-3 ANSWERED:** AWS SDK `XResult` classes are non-polymorphic value types,
so no vtable and no RTTI. Expected SDK shape, not an exotic inbound path. §17.9.

For each decoded schema, look for:
- Any message whose name ends in `Result`, `Response`, `Notification`, or `Event`
- Any message in a service definition's RPC `output_type`
- Any `service` definition (these describe the full RPC interface including both
  directions)

If the binary contains a `google::protobuf::ServiceDescriptor` (i.e. a `service`
block in the registered `.proto`), **that is the complete client→server and
server→client interface in one place**. Record it in full.

---

## Predictions — record before searching (CHARTER §4)

**ALL THREE FALSIFIED — see the DONE banner. Kept verbatim as the record.**

1. ~~**`InternalAddGeneratedFile` has 20–100 callers** — one per compiled `.proto`
   file. The Javelin Gateway service alone is likely split across several files
   (service definition, request types, response types, common types). The total
   blob count will exceed the 10 RTTI types H2 found.~~ **FALSIFIED — 3 total.**
2. ~~**Response/result types are present in the blobs even though absent from
   RTTI** — protobuf compiles both directions into the descriptor, and the server
   side types will be in the same `.proto` files as the request types.~~
   **FALSIFIED — no Javelin descriptor exists in any form.**
3. ~~**A `service JavelinGatewayService` block exists** in at least one registered
   `.proto`, listing the full RPC interface including method names, input types,
   and output types for both directions. This is the single most valuable find
   P2 can make.~~ **FALSIFIED — zero service blocks across all 3 descriptors.**

~~If prediction 3 is confirmed, that `service` block is the primary deliverable
and collapses most of Track P's work into a single read.~~

**Retrospective on the prediction set (CHARTER §4).** All three shared one
unstated assumption — *protobuf is present, therefore the protocol is protobuf* —
so they could not fail independently, and the set had far less discriminating
power than three predictions suggests. **`STATE.md` already contained the
disconfirming evidence** (§16.15: Javelin-family fields read out of a **JSON**
helper), and no prediction was aimed at it. **Lesson: when predictions share a
premise, the premise is the thing to predict about.**

---

## Definition of done

- ~~**`InternalAddGeneratedFile` located** with its call sites enumerated.~~
  **NOT SATISFIED → OI-P2-1.** The three blobs were located as *data*; nothing
  proves what registers them. All three candidate symbols matched 0 as literal
  strings, but a non-virtual free function's name need not appear in the binary,
  so the string test cannot answer it. Resolved by XREF on the three blob VAs.
  **Cannot change the verdict** — there is no Javelin descriptor to register.
- **All registered `.proto` blob addresses and sizes recorded** as signatures
  (blob address in `.rdata`, size constant in the caller).
- ~~**All Javelin Gateway schemas decoded** — field names, numbers, types for
  every message type in §17.5, plus any response/result types found.~~
  **VACUOUS — none exist.**
- **The server→client direction addressed** — either confirmed present in the
  blobs (with schemas), or confirmed absent (with a clear statement of what is
  and isn't there). **✅ SATISFIED via the second branch — confirmed absent, with
  evidence. This bullet's "or confirmed absent" clause is why P2 closes complete
  rather than partial.**
- ~~**`.proto` file content recorded** for all world-relevant message types —
  accurate enough for S1a to emit and Track P to decode against.~~ **VACUOUS —
  no world-relevant message type has a `.proto`.** Recorded instead: the full
  `campfire_event_default.proto`, with field numbers and wire types in
  `p2_out/fields.tsv`.
- **The `service` block recorded** if present — method names, input types,
  output types. **✅ SATISFIED — absent, in all 3 descriptors.**

---

## Non-goals and hard boundaries

- **Static only.** No execution, no hooking, no injection. CHARTER §3.
- **No anti-cheat, no EAC.** If any trace wanders into `EasyAntiCheat/`, stop.
- **Do not implement a decoder here.** P2 extracts schemas; decoding individual
  captured messages against those schemas is a later P-track chunk. The temptation
  to start decoding a blob that looks interesting is how this chunk becomes
  infinite.
- **Signatures, not offsets** (CHARTER §4). Every blob location is recorded as a
  scannable pattern (the first 8–16 bytes of the blob, which are the encoded
  `name` field of the `FileDescriptorProto` — patch-stable because the `.proto`
  file path is a string constant).
- **No world-stream capture, no pcap.** Pure static analysis.

---

## FINDINGS to record

P2's findings extend §17 (H2's world-message dispatch map) as a new subsection
**§17.9** (or a new **§18** if the schema content is substantial enough to stand
alone — judge by volume; the threshold is whether it makes §17 unwieldy). Include:

- The `InternalAddGeneratedFile` call-site enumeration (blob addresses and sizes).
- All decoded Javelin Gateway schemas — field names, numbers, wire types.
- The server→client direction: confirmed present or confirmed absent, with
  evidence either way.
- The `service` block if present.
- Any non-Javelin schemas found that are relevant to the world session (e.g.
  Carrier-level framing types, replica chunk types).
- Anything bearing on S1a (what the server must emit) and on Track P
  (prioritised decode list with field-level detail).

**Before closing (CHARTER §6.4):** tick P2's row in `CHUNKS.md`, add a DONE
banner to this file, and record any new open items in STATE §15. Note in the
Order section what P2 unblocks (Track P field-level decode; S1a's send-side
schema). **Router before ledger.**
