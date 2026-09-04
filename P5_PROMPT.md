# P5 — The replica/chunk model: how world state reaches the wire

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are
the context. Do not act on a summary of either.**

Created 2026-09-04, immediately after P2 (§17.9) and **because of it**. P2 ruled
protobuf out as the world-stream encoding, which promotes P5 from a
late-and-blocked chunk to the Track P front.

P5 is **static and source-first. No login, no running client, no Proton, no
Ghidra required for the primary work, and no deadline.** Its main instrument is
the Lumberyard fork we already build from, pinned at **`7d4f1ee6`**. Confirmation
against `NewWorld.exe` b22469132 is secondary and static.

**Dependency corrected 2026-09-04: H4 is not a gate.** Reading GridMate's
marshalers needs no reflection reader. H4 would accelerate mapping *which* chunk
types a given build registers; it is not required to learn the wire format.

---

## The one thing this chunk does

**Document how GridMate serialises replicated object state onto the wire —
the `ReplicaChunk` framing, how a chunk type is identified on the wire, how
`DataSet` values and their dirty bits are encoded, and the exact quantization
scheme the transform marshalers use — accurately enough that a later chunk can
decode a captured epoch-1 payload and S1a can emit one.**

Deliverable: a byte-level description of the replica layer, derived from source,
with each claim carrying the file and symbol it came from.

Why this is the right next chunk: it is the largest remaining unknown on the
critical path, the source for it is in our hands (CHARTER §2), and unlike
everything in P-track that depends on captures, **it survives 31 Jan 2027**.

---

## Why this is answerable from source

1. **The transport is stock GridMate.** T5/§12B: retail's transport is
   structurally stock `SecureSocketDriver`, zero catalogued exceptions, and the
   reference build is a valid instrument for it. In stock GridMate, `Carrier`
   carries `ReplicaManager` traffic — so the replica layer is the natural
   occupant of epoch ≥ 1.
2. **The replica stack is present in retail.** T1/§10: `GridMatePeerReplica`,
   `GridMateReplicaStatus`, `VTransformReplicaChunk`, `VTriggerAreaReplicaChunk`,
   `ScriptComponentReplicaChunk`; P2/§17.9 counted **23 `ReplicaChunk`** and
   **94 `InitializeReplicatedFields`** references.
3. **CHARTER §4: prefer the source to the sample.** One capture describes one
   session; `ReplicaChunk.cpp` describes the protocol family. Here we have the
   source and, for now, no capture at all — so source is not merely preferred,
   it is the only route.

**Source pin.** `github.com/kaatbailey/lumberyard` @ **`7d4f1ee6`**, under
`dev/Code/Framework/GridMate/GridMate/`. Verified 2026-09-04 that
`Replica/ReplicaChunk.h`, `Serialize/MathMarshal.h` and
`Serialize/CompressionMarshal.h` are **byte-identical** between `413ecaf` and
`7d4f1ee6` — the `false_v<>` patch touched only `AzCore/RTTI/TypeInfo.h`, so §7's
source-reading facts (established against `413ecaf`) transfer unchanged.

---

## Predictions — record before reading (CHARTER §4)

**P2's retrospective lesson applies and is the reason for prediction 0.** P2's
three predictions shared one unstated premise — *protobuf is present, therefore
the protocol is protobuf* — so they could not fail independently and the set had
far less discriminating power than three predictions suggests. **Prediction 0 is
aimed at this chunk's premise itself.**

0. **PREMISE: the world stream (epoch ≥ 1) actually carries `ReplicaChunk`
   traffic.** This is the same shape of inference that failed in P2 — "X is in
   the binary, therefore the protocol is X" — and it gets tested first, not
   assumed. **Falsified if** the `ReplicaChunk` references in `NewWorld.exe` are
   not reachable from the network receive path, or if `REPConnection::OnRecv`
   (§17.2) feeds only the Javelin/JSON service layer with no replica path beside
   it. **Note the live strain:** H2 mapped `OnRecv → Aws::JavelinGatewayService`
   handlers (§17.4), and P2 proved that layer is JSON. Either REP carries both
   and H2 saw only one, or the replica traffic rides a different path. **This
   ambiguity is the single most important thing P5 resolves**, and it is related
   to OI-H2-1 (does LibUV wrap the DTLS path or a parallel service channel?).
1. **Chunk type is identified on the wire by `AZ::Crc32` of the chunk type
   name**, sent as a 32-bit value, not by a registration index. Falsified if the
   descriptor table is index-keyed.
2. **`DataSet` updates are dirty-bit gated**, so a chunk's payload carries only
   changed members, preceded by a bitmask or run-length marker whose width
   depends on the declared DataSet count. Falsified if every update is a full
   chunk rewrite.
3. **Transform/position values are quantized, not raw IEEE floats** —
   `CompressionMarshal.h` / `MathMarshal.h` exist for this. **This prediction is
   load-bearing for P3:** a controlled-walk capture searched for a smoothly
   varying float triple will find nothing if the values are quantized ints.
4. **The chunk header is small and fixed** — on the order of a few bytes for
   chunk id plus type, not a self-describing envelope.

Predictions 1–4 are independent of each other and none of them rescues
prediction 0 if it fails. If prediction 0 fails, **stop and report** — the rest
of the chunk is describing a protocol the client does not speak.

---

## Steps

### Step 0 — confirm the instrument
Fetch from the pin, not from `master`; record the commit in FINDINGS. Confirm the
three files above hash-match what §5 records if a local copy is used
(`~/Documents/lumberyard`).

### Step 1 — test prediction 0 before anything else
From the retail side (static, Ghidra, warm `nwly.gpr`): is there a path from the
network receive path to `ReplicaManager` / `ReplicaChunk` code? Landmarks:
`REPConnection::OnRecv` thunk at `148591750` (§17.2), the `ReplicaChunk` and
`InitializeReplicatedFields` references (§10, §17.9), and `GridMatePeerReplica`.
**Report the answer plainly whichever way it goes.** OI-H2-2 (OnRecv body not
resolved statically) is a known obstacle — if it blocks, say so and mark
prediction 0 unresolved rather than assumed.

### Step 2 — the chunk framing
From `Replica/ReplicaChunk.h/.cpp`, `Replica/ReplicaMgr.*`,
`Replica/ReplicaChunkDescriptor.*`: how a chunk is identified, what precedes its
payload, how multiple chunks in one replica are delimited.

### Step 3 — DataSet encoding
From `Replica/DataSet.h`, `Replica/ReplicaChunk.h`: how a `DataSet` declares
itself, how dirty state is tracked and encoded, what a member's on-wire form is.

### Step 4 — the marshalers, and the quantization scheme
From `Serialize/MathMarshal.h`, `Serialize/CompressionMarshal.h`,
`Serialize/Buffer.h`, `Serialize/UtilityMarshal.h`: the exact bit layout for
floats, vectors, quaternions and transforms, including range and precision
parameters. **This is the highest-value output for P3 and S1a.**

### Step 5 — cross-check against retail
Confirm the source-derived structures are consistent with what §10/§17.9 counted
in `NewWorld.exe`, and record any divergence. **CHARTER §2: when the reference
and retail conflict, retail is the truth.**

---

## Definition of done

- **Prediction 0 answered** — replica traffic confirmed on the world stream, or
  confirmed absent, or explicitly marked unresolved with the reason.
- **Chunk framing documented** — identification, header, delimitation.
- **DataSet encoding documented** — dirty-bit scheme and per-member wire form.
- **Quantization scheme documented** — enough for P3 to know what to look for and
  for S1a to emit a valid transform.
- **Every claim carries its source** — file and symbol, at the pinned commit.
- **Retail cross-check recorded** — consistent, divergent, or not yet checkable.

---

## Non-goals and hard boundaries

- **Static and source-only.** No execution, no hooking, no injection. CHARTER §3.
- **No anti-cheat, no EAC.** CHARTER §3.
- **Do not decode a capture here.** P5 documents the format; decoding a real
  payload is P3/P4. **This is the boundary that keeps P5 finite** — the same
  temptation that P2's prompt warned about.
- **Do not map the full chunk-type inventory.** *Which* chunks New World
  registers is an H4/D-track question. P5 documents the *mechanism*.
- **Do not redesign the server.** S1a consumes this; it is not written here.
- **Scope bound, explicit:** GridMate's replica system is large. P5 covers chunk
  framing, chunk-type identification, DataSet encoding, and transform/position
  marshalling. **RPCs, interest management, and the session/peer lifecycle are
  out of scope** — note them in FINDINGS as noticed-not-pursued and stop.

---

## FINDINGS to record

New STATE section **§18** (P5's content is a wire format and will not fit inside
§17's dispatch map). Include: the source pin; prediction 0's answer with
evidence; the framing, DataSet and quantization findings with per-claim sources;
the retail cross-check; anything bearing on **P3** (what a position message looks
like), **P4** (what a full state dump looks like) and **S1a** (what the server
must emit); and new open items for §15.

**Before closing (CHARTER §6.4 — router before ledger):**
1. Tick P5's row in `CHUNKS.md` with verdict, date and a `STATE §18` pointer,
   **rewriting the note in the same edit**.
2. DONE banner on this file; strike through — never delete — anything it
   falsified.
3. Fold FINDINGS into `STATE.md`; add §13 correction rows for anything overturned;
   update §15.
4. Update STATE's freshness header — all four numbers.
5. **Run `python3 check_docs.py`**, then push.
6. End the session with a **HANDOFF block**, ten lines maximum, nothing after it.
