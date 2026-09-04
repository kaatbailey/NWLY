# P2 runbook — protobuf schema extraction

Companion to `P2_PROMPT.md`. Read `CHARTER.md` and `STATE.md` first.
Instrument: `p2_scan.py`, validated 2026-09-04 (see "Instrument validation").

---

## Premise correction, recorded before running (CHARTER §4)

§17.5 calls the AWS SDK model path "the protobuf choke point." The evidence
already in STATE points the other way:

- §16.15 read the queue-token deserializer and found fields pulled by the stock
  AWS-SDK **`JsonView` GetString** helper. `Aws::Utils::Json::JsonView` is JSON.
  That is the same SDK codegen family as the Javelin models.
- The 10 type names in §17.5 are REST routes, not stream messages:
  `PostGameWorldsWorldIdCharactersRequest` = `POST /game/worlds/{worldId}/characters`;
  `DeleteGameCharactersCharacterIdRequest` = `DELETE /game/characters/{characterId}`;
  plus `PatchCharacterRequest`, `GetLoginInfoRequest`, `ListWorldsRequest`.
  AWS SDK for C++ service clients serialize to JSON over HTTP.
- Those are plausibly **the same calls P0 already decoded in plaintext on
  TCP/443** (§16.2–16.4), i.e. the auth phase, not the world stream.

This also dissolves **OI-H2-3** without mystery. In AWS SDK C++, `XRequest`
derives from the polymorphic `AmazonSerializableWebServiceRequest` (→ RTTI),
while `XResult` classes are ordinary non-polymorphic value types (**no vtable →
no RTTI**). "No Response/Result types in RTTI" is the expected shape of the SDK,
not evidence that responses are deserialized exotically.

**This does not cancel P2.** FIND-2 is solid — `google::protobuf::Reflection` is
in `NewWorld.exe` and reflection requires descriptors. The question P2 answers is
*what protobuf is for*, and "confirmed absent, with a clear statement of what is
and isn't there" is already in P2's definition of done.

---

## Predictions — record before running

| ID | Prediction | Falsified by |
|---|---|---|
| **P2-A** | ≥1 `FileDescriptorProto` blob is recovered (FIND-2 holds). | Zero blobs → protobuf is linked but no generated messages; FIND-2 closes negative. |
| **P2-B** | **No `service JavelinGatewayService` block exists.** Contradicts P2_PROMPT prediction 3. | Any service block naming Javelin → my correction is wrong, P2_PROMPT prediction 3 stands, and it is the primary deliverable. Take it. |
| **P2-C** | Recovered packages are infrastructure (telemetry / metrics / analytics / EOS / Amazon-internal), **not** javelin / world / character namespaces. | A world- or character-namespaced descriptor. |
| **P2-D** | `JsonView` / `AmazonSerializableWebServiceRequest` / `application/json` counts vastly exceed any protobuf content-type marker. | Comparable or inverted counts. |
| **P2-E** | `InternalAddGeneratedFile` may be **absent**; `AddDescriptors` / `descriptor_table` present instead (protobuf ≥ 3.10). P2_PROMPT Step 1 as written then cannot succeed. | `InternalAddGeneratedFile` present with callers. |

P2_PROMPT prediction 1 ("20–100 callers") is untestable until P2-E resolves.

---

## Step 0 — confirm the instrument

```fish
set -g NW ~/Documents/nwly-pin/22469132/Bin64/NewWorld.exe
sha256sum $NW
# expect 8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e
```

Mismatch → stop (CHARTER §6.3). Use the **pin**, not the live Steam install.

```fish
python3 -c 'import google.protobuf; print(google.protobuf.__version__)'
# if missing: pip install protobuf --break-system-packages
```

---

## Step 1 — validate the instrument before pointing it at retail (CHARTER §2)

```fish
python3 p2_scan.py --selftest
```

Must print `SELF-TEST PASSED`. If it does not, fix the tool before believing
anything it says about `NewWorld.exe`.

---

## Step 2 — scan

```fish
python3 p2_scan.py $NW --outdir ~/Documents/NWLY/p2_out --diagnostics
```

Runtime is ~2 s on a 171 MB PE. Outputs in `p2_out/`:

| File | Contents |
|---|---|
| `index.tsv` | one row per blob: `.proto` path, package, **VA**, file offset, size, section, message/enum/service counts, confidence, **first-16-byte signature** |
| `fields.tsv` | every field: message, name, number, type, label, **wire type** |
| `proto/*.proto` | reconstructed sources |
| `blobs/*.bin` | raw extracted bytes, byte-exact |
| `report.md` | summary, service blocks, server→client name candidates, diagnostics |

The signature column is P2's "signatures, not offsets" requirement: the first 16
bytes are the encoded `name` field, i.e. the `.proto` path string constant, which
survives a rebase.

### Why this replaces Steps 1–3 of `P2_PROMPT.md`

`InternalAddGeneratedFile` is the **old** (proto2 / early proto3) registration
API. Protobuf ≥ 3.10 generates
`google::protobuf::internal::AddDescriptors(const DescriptorTable*)` instead,
with the blob inside a static struct. Which symbol exists depends on the linked
version — unknown up front. **Both leave the same artefact in `.rdata`: a raw
serialized `FileDescriptorProto`.** Scanning for the artefact is version
independent; scanning for the function is not. The scanner also recovers each
blob's exact size by walking its top-level fields, so it does not need the
caller's size constant at all.

Ghidra is still worth using — for **attribution**, not discovery (Step 3 below).

---

## Step 3 — Ghidra cross-check (independent confirmation, CHARTER §4)

Open the warm project `~/Documents/Ghidra-projects/nwly.gpr`. **Do not
re-import.** Confirm §17 landmarks resolve (`FUN_14644a070`, `JavelinGateway`
RTTI ≈ 99 symbols).

1. Search → Program Text for `InternalAddGeneratedFile`, then `AddDescriptors`,
   then `descriptor_table`. **Record which exist.** That resolves P2-E.
2. If a registration function exists, take its XREF list. For each caller,
   record the blob pointer and the size constant.
3. **Cross-check:** every size constant must match the scanner's recovered size
   for the blob at that VA. Two independent derivations of the same number —
   that is the check. A disagreement means one of them is wrong and neither is
   trustworthy until resolved.
4. Any blob the scanner found with no registration call site is worth a note:
   it may be data the binary carries but never registers.

---

## Step 4 — decision tree

**(a) Javelin/world-namespaced descriptors found, service block present.**
My correction is wrong. P2_PROMPT prediction 3 confirmed — the service block is
the primary deliverable. Continue with P2_PROMPT Steps 5–6 as written. Record
the full service block; it collapses Track P.

**(b) Descriptors found, infrastructure-only (telemetry/metrics/EOS).**
The likely outcome. Then:
- FIND-2 closes as *present but not the world schema*.
- **§17.5's "protobuf choke point" claim needs a §13 correction row** — struck
  through, not deleted (CHARTER §5).
- **OI-H2-3 gets a real answer:** response types are absent from RTTI because
  AWS SDK `XResult` classes are non-polymorphic, not because responses are
  deserialized exotically.
- Track P retargets. Two live routes, both cheap:
  - **Javelin (auth phase) schemas come from JSON key strings**, exactly as
    §16.15 recovered the `Token` fields — the field names are `GetString` /
    `WithString` arguments in `.rdata`. And P0's captures already contain this
    traffic in plaintext, so the schema can be read off the wire.
  - **The world stream is GridMate `ReplicaChunk` marshalling**, not protobuf —
    `VTransformReplicaChunk`, `ScriptComponentReplicaChunk`, ~94
    `InitializeReplicatedFields` refs (§10). That is `DataSetBase` / `Marshaler`
    in the reference fork, which means **we have the source** (CHARTER §2) and
    it is readable without any capture.

**(c) Zero descriptors.** Protobuf is linked (reflection symbols present) but no
generated message types are compiled in — reflection arrived as a transitive
dependency. FIND-2 closes negative. Same retarget as (b).

Outcome (b) or (c) is **not a failed chunk.** It removes a wrong belief from
§17.5 and redirects Track P off a dead end, which is worth more than a schema.

---

## Definition of done — mapped to this runbook

- [ ] `InternalAddGeneratedFile` located **or confirmed absent** with the
      alternative named (Step 3.1) — resolves P2-E
- [ ] Registration call sites enumerated, or absence recorded (Step 3.2)
- [ ] All blob addresses + sizes recorded **as signatures** (`index.tsv`)
- [ ] Sizes cross-checked against caller constants (Step 3.3)
- [ ] All decoded schemas recorded — names, numbers, types, wire types
      (`fields.tsv`, `proto/`)
- [ ] Server→client direction addressed: present with schemas, **or** confirmed
      absent with evidence (`report.md`)
- [ ] Service block recorded if present
- [ ] Predictions P2-A…P2-E each marked confirmed or falsified

---

## Instrument validation (2026-09-04)

Run before the tool was pointed at anything real, per CHARTER §2/§4.

| Control | Target | Result |
|---|---|---|
| Positive, synthetic | Javelin-shaped descriptor: nested messages, `oneof`, enum, repeated, defaults, **service block with input/output types**; second proto2 file; both butted directly against adjacent `.rdata` with no separator | **2/2 recovered.** Exact offsets, exact VAs, exact sizes **without the caller's size constant**. Service block and all field numbers/types round-tripped. |
| Positive, at scale | 171 MB (matching `NewWorld.exe`), six **real** Google descriptors planted at known offsets, largest 13,452 bytes | **6/6 recovered**, all sizes exact, VAs correct, **2 s runtime** |
| Negative | 40 MB of random bytes + ASCII-heavy noise seeded with decoy `.proto` paths and hand-crafted anchors | **0 false positives** |

Two defects were found and fixed by these controls, which is the argument for
running them:

1. **O(n²) extent recovery** — the first version re-walked from the blob start
   on every shrink attempt and **hung** on adversarial input. Now single-pass.
   *A tool that never returns is a cap on the measurement (CHARTER §4).*
2. **35,081 false positives** on the negative control. Cause: a bare `.proto`
   path in a strings table, preceded by a byte that happens to be its length, is
   a structurally valid name-only `FileDescriptorProto`. Fixed with a substance
   gate — a descriptor must declare at least one message, enum, service or
   extension. Dropped 35,081 → 0 with no loss of recall.

**Known caps, stated up front:**
- Scans `.rdata` / `.data` / `.rodata` by default. Use `--all-sections` if a
  descriptor is suspected elsewhere.
- Finds descriptors **as data**; it does not prove any of them is *registered*.
  That is what the Ghidra XREF cross-check (Step 3) is for.
- A descriptor stored compressed or obfuscated would be invisible. Nothing in
  §10 suggests that, but absence of a hit is not proof of absence.
- Blobs accepted on the fallback tier are flagged `PARTIAL` in `index.tsv` and
  may be truncated. Treat those as leads, not findings.

---

## Before closing (CHARTER §6.4) — router before ledger

1. Tick P2's row in `CHUNKS.md`, pointing at the new STATE section.
2. DONE banner on `P2_PROMPT.md` with the verdict.
3. **Strike through, do not delete**, any P2_PROMPT claim this chunk falsified —
   prediction 3 and the Step 1 `InternalAddGeneratedFile` assumption are the
   likely candidates.
4. Fold findings into **§17.9**, or a new **§18** if the schema content is bulky.
5. If outcome (b) or (c): add the §13 correction row for §17.5's "protobuf choke
   point", and close/redirect OI-H2-3 and FIND-2 in §15.
6. Update the freshness header: date, commit, section count, test number,
   correction count.
