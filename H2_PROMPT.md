# H2 — Map the inbound world-message path and its dispatch

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are the
context. Do not act on a summary of either.**

Created 2026-08-31, out of the Track H plan (STATE §3; CHUNKS Order item 3) and warmed
by **S0a** (STATE §16.15). S0a analysed the same retail binary the other way round — the
*auth/handoff* path, ending at the `RepAddress` the client dials. H2 picks up where the
client starts *talking to the world*: it walks the **receive** path forward from the
socket to the point where a decrypted world message is routed to a handler, and maps that
routing. It is the static half of Track H and the primary static source of protocol
structure for Track P and S1a.

It is **static, needs no login, no running client, no Proton, and has no deadline.** It
reuses S0a's analysed Ghidra project (RTTI already run on `NewWorld.exe` b22469132), so it
starts warm. Nothing here touches a live client or a pcap.

---

## The one thing this chunk does

**From the retail binary, map the inbound path `recvfrom → DTLS/SSL_read → GridMate
Carrier → message dispatch`, and identify the mechanism that routes a decrypted world
message to its handler — plus the enumerable set of message types that mechanism keys
on.**

The deliverable is a *map*, not a bit: the chain of functions from datagram to dispatch,
the **dispatch mechanism** (switch on a type id? a registered-handler table? a GridMate
marshaler vtable?), and the **message-type enumeration** as far as it is tractable — each
recorded as a scannable signature, not a bare offset (CHARTER §4).

Why this is the right next chunk: S0a proved the *design shape* of S0, but nothing yet
tells Track P **what the world messages are** or tells S1a **what the client expects to
receive first**. The dispatch table is the spine both hang off. Everything downstream —
decoding individual messages (P-chunks), and emitting messages the client accepts (S1a) —
needs this map. Scope it **ambitiously**: a primary source of protocol structure, not a
one-off hunt for a single hook point.

---

## Why this is answerable statically — and why it is unusually cheap here

Two force-multipliers make this far less blind than generic protocol RE:

1. **We have the reference source.** T5/§12B concluded retail transport is *structurally
   stock GridMate `SecureSocketDriver`* with zero catalogued exceptions, and §10 settled
   the engine as GridMate with a New-World transport wrapper (`TransportLayerGridMate`
   RTTI). GridMate is open source in the Lumberyard fork (STATE §5, `~/Documents/
   lumberyard`, built commit `7d4f1ee6`). So the *transport* layer of the retail receive
   path can be **matched against known source by name and structure** — this is a Rosetta
   stone, not a cold read. The New-World-specific *message* layer sitting on top is the
   part that is genuinely ours to recover, and isolating it from the stock GridMate below
   it is most of the work.
2. **The crypto boundary is already located.** §10 found `SSL_read`/`SSL_write`
   (statically linked OpenSSL). Decrypted world bytes emerge from `SSL_read`'s consumer —
   so the message layer is reachable by walking *forward from `SSL_read`*, skipping the
   entire DTLS record machinery. `recvfrom` is the other anchor (raw datagram in), useful
   for confirming the DTLS layer is stock, but `SSL_read` is the shortcut to the messages.

There are, in other words, **two anchors that converge** on the same dispatch: forward
from `SSL_read`, and outward from the `TransportLayerGridMate` vtable (§10). Both are in
`NewWorld.exe`; neither is in EAC.

---

## Step 0 — confirm the instrument is the warm S0a project

```fish
set -g NW ~/Documents/nwly-pin/22469132/Bin64/NewWorld.exe
sha256sum $NW    # expect 8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e
```

Open the **same Ghidra project S0a used** (do not re-import — RTTI and auto-analysis are
already done; §16.15). Confirm the warm landmarks are present before starting, so you know
you are in the right project and not a fresh one:

- `SSL_read` / `SSL_write` located (§10). If the project doesn't show them by name (static
  OpenSSL is stripped), that is itself the first sub-task — find `SSL_read`'s body by its
  callers or by FidDb, and record it as a signature.
- `recvfrom` (or `WSARecvFrom`) import present — Symbol Tree → Imports, filter `recv`.
- The §16.15 landmarks resolve: `FUN_14644a070` (GameConnection state machine),
  `PTR_s_Disconnected_1484f9ff0`, the REP driver object at conn+0x1000.
- The `TransportLayerGridMate` RTTI string (§10) resolves to a class with a vtable.

If the SHA doesn't match §5, or the project is not the b22469132 build, stop (CHARTER
§6.3). The dispatch addresses only describe *this* binary.

---

## Step 1 — anchor the receive path (two ends, predict before tracing)

**Anchor A — forward from the socket.** Xref `recvfrom`/`WSARecvFrom`. The referencing
function is the GridMate `SocketDriver`/`SecureSocketDriver` read. Confirm it matches the
reference GridMate `SocketDriver::Receive` / `ProcessRead` in structure (Rosetta check).
This bounds the DTLS record layer as stock and gives the datagram-in entry.

**Anchor B — the plaintext boundary.** Xref `SSL_read`. Its consumer is where decrypted
application data (epoch-1 Carrier payload, §16.13) becomes available. **This is the head of
the message path** — everything H2 cares about is downstream of here.

**Anchor C — the game wrapper.** Navigate to the `TransportLayerGridMate` vtable (from its
RTTI). Its receive/handler slot is the New-World message entry, sitting above GridMate
Carrier. Walking *out* from here meets Anchor B's *forward* walk at the dispatch.

**Predict before following (CHARTER §4):** name, for each anchor, the next 1–2 functions
you expect and why (e.g. "SSL_read's consumer hands the buffer to a GridMate Carrier
packet processor that splits it into per-channel messages"). Record the prediction, then
trace. A prediction that survives is a finding; one that breaks is a *better* finding.

---

## Step 2 — separate the stock transport from the game message layer

Walk forward from Anchor B (and outward from Anchor C) until the two meet. Along the way,
classify each function as **stock GridMate** (matchable to Lumberyard source — Carrier
reliability, channels, ack, fragmentation, `ReadBuffer`/`WriteBuffer` marshaling) or
**New-World message layer** (no source match — the game's own dispatch). The boundary
between them is the important line: below it is transport we already understand from the
reference; above it is the protocol H2 exists to recover.

Use the reference deliberately: open the GridMate source in `~/Documents/lumberyard`
(`dev/Code/Framework/GridMate/...`) beside Ghidra and match by structure — a retail `FUN_`
whose control flow mirrors `CarrierImpl::ProcessIncoming` (or the local equivalent) *is*
that function, and gets named as a signature. Every match collapses a swath of the graph.

---

## Step 3 — the load-bearing find: the dispatch mechanism

At the top of the message layer, exactly one of these shapes routes an inbound message to
its handler. Identify which, and record it as a signature:

- **A type-keyed table / registration map** — a `messageId → handler` structure populated
  at init (look for a run of inserts, each pairing a constant id with a function pointer).
  If so, dump the table: the ids and their handler `FUN_`s **are** the message enumeration.
- **A switch on a leading type byte/word** — a jump table off the first field of each
  decoded message. If so, enumerate the cases and their targets.
- **A GridMate ReplicaManager / marshaler vtable dispatch** — replica chunks routed by a
  registered marshaler per type. If so, the registered types are the enumeration, and the
  boundary between "replica traffic" and "raw messages" is itself a finding.

**Predict (Step 1's prediction 2 below) which you expect, then confirm.** Whichever it is,
the goal of this step is the **enumeration**: the set of message types the client will
accept on the world stream, each paired with the handler that consumes it. This is what
Track P decodes and what S1a must speak.

---

## Step 4 — where protobuf enters (FIND-2)

§10 found `google::protobuf::Reflection` linked (FIND-2, owned by P2). On the inbound path,
find where a decoded message is handed to protobuf parsing — `MessageLite::ParseFromArray`,
`::MergeFromCodedStream`, or a Reflection call. This tells Track P **which** message types
are protobuf-encoded versus GridMate-native marshaled, which is the single most useful
split for prioritising P-chunks. Do not decode the protobuf schemas here — that is P2/FIND-2
(the `FileDescriptorProto` extraction). H2 only marks *where* protobuf is invoked and on
*which* dispatch branches.

---

## Predictions — record before tracing (CHARTER §4)

1. **The receive path is structurally stock GridMate down to the message boundary.** The
   `recvfrom` and `SSL_read` consumers match Lumberyard `SocketDriver`/`Carrier` source;
   the New-World-specific code begins only at the message-dispatch layer. **Load-bearing** —
   if the transport layer *doesn't* match source, T5/§12B's "structurally stock" conclusion
   is in tension and must be revisited, not papered over.
2. **Dispatch is a type-keyed handler table (or ReplicaManager marshaler map), not a giant
   hand-written switch** — GridMate-style registration, populated at session init.
3. **A non-trivial fraction of world messages are protobuf-encoded** (FIND-2), entering via
   a single choke point on the dispatch, with the remainder GridMate-native marshaling.

If prediction 1 is falsified, that is the most important result of the chunk and reshapes
Track T's settled conclusion — state it plainly with the mismatching call sites.

---

## Definition of done

- The inbound chain `recvfrom → SSL_read consumer → GridMate Carrier → message layer`
  recorded as a sequence of **signatures** (named where they match reference source).
- The **dispatch mechanism identified** (table / switch / marshaler map) with its site as a
  signature.
- The **message-type enumeration** captured as far as tractable: ids/types paired with
  handler functions. "As far as tractable" is honest — if the table is huge or partly
  runtime-populated, record what is statically recoverable and say what isn't.
- The **protobuf choke point(s)** on the inbound path marked, with the dispatch branches
  that reach them (feeds P2/FIND-2, does not do its job).
- The **stock/game boundary** stated: which layers are matched GridMate and which are
  New-World-specific.
- A one-paragraph handoff for **S1a** (what the client expects to receive first on epoch-1,
  given §16.13's Token-in-first-message finding) and for **Track P** (the prioritised list
  of message types worth decoding, protobuf ones flagged).

---

## Non-goals and hard boundaries

- **Static only. No execution, no hooking, no injection.** CHARTER §3. H2 reads the binary;
  H1 (reference-build hook) and H3 (retail injection, last resort) are separate chunks. If a
  question here genuinely needs a running client to settle, that is a *finding* that would
  escalate to H1/H3 — record it, do not do it.
- **No anti-cheat, no EAC.** The receive path lives in `NewWorld.exe`/GridMate. If any trace
  wanders into `EasyAntiCheat/`, an attestation, or an integrity/heartbeat routine, stop
  following it — off-charter permanently (CHARTER §3).
- **Do not decode message semantics here.** H2 maps *structure and dispatch* and *enumerates*
  types. Deep per-message decode is spun out as P-chunks; protobuf schema extraction is P2.
  The temptation to follow one interesting handler all the way down is how this chunk becomes
  infinite — resist it, record the handler as a signature, move on.
- **Signatures, not offsets** (CHARTER §4). Every landmark is a scannable byte/RTTI/source-
  match pattern that survives the next client patch. A raw `FUN_` offset is a finding with a
  built-in expiry.
- **No world-stream capture, no pcap.** Pure static analysis.

---

## FINDINGS to record

The material is a distinct deliverable (a dispatch map), not an extension of the auth-phase
findings — **so it most likely warrants a new `## 17` (e.g. "World-message dispatch map"),
which takes the freshness-header section count 19 → 20.** Confirm the count either way
(CHARTER §6.2). If it turns out thin, fold as a §16.16 instead. Include:

- The inbound chain and the stock/game boundary, as signatures.
- The dispatch mechanism and the message-type enumeration (ids ↔ handlers).
- The protobuf choke point(s) and which branches reach them (cross-ref FIND-2 / P2).
- The reference-source matches made (which retail `FUN_`s are which GridMate functions).
- Anything bearing on S1a (first-message expectation, §16.13) and on the prediction-1
  transport-match check (confirming or straining T5/§12B).

**Then, before closing (CHARTER §6.4):** tick H2's row in `CHUNKS.md`, add a DONE banner to
this file, strike any falsified claim, and record any new open items in STATE §15 (e.g.
runtime-populated dispatch entries that static analysis can't enumerate → a candidate H1
sub-task). Note in the Order section what H2 unblocks (Track P prioritisation; S1a's
send-side). **Router before ledger.**
