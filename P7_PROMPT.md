# P7 — Framing the Hub message: the wire format, and which registration the client sends

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are
the context. Do not act on a summary of either.**

Created 2026-09-05, out of P6 (§19). P6 recovered the Hub type vocabulary and
the registration mechanism but **did not reach Step 4** — the wire format is
still unread, and prediction 0's central question is still open.

P7 is **static. Source + Ghidra. No login, no running client, no Proton, no
capture, and no deadline.** Immune to the 2027-01-31 sunset (§16.0).

Instruments: the warm `nwly.gpr` on `NewWorld.exe` b22469132 from the pin, the
Lumberyard fork at **`7d4f1ee6`** for `AzCore`/GridMate, and P6's output —
`hub_vocabulary.csv` (3,509 identities) plus the session-layer table in §19.6.
**Hub itself is Amazon-proprietary and is NOT in the fork.**

---

## What P6 hands you, so you do not re-derive it

- **The registrar is `FUN_1407de270`.** Hub types register through it, not
  through `AZ::Uuid::CreateString`. 3,511 call sites. §19.4.
- **3,509 Hub identities** with literal address, hook function and handler
  vftable. `hub_vocabulary.csv`. §19.5.
- **Names exist for 311 types by design**; 3,199 register an explicitly empty
  string. Do not go looking for the missing names — they are not in the binary.
  §19.5.
- **The session-layer table**, §19.6 — every handshake type with UUID, hook and
  **handler vftable**. The handler vftable is your entry point.
- **Three dead routes, §19.8.** `.rdata` adjacency, `InstallRegistrationHook`
  RTTI descriptors, hook→vftable→COL. **Read that section before starting.**
  Re-deriving any of them costs a session.

---

## Step 1 — OI-P6-2, and do this first

**Which `RegistrationRequest` revision does b22469132 actually send?**

All three are registered; registration is not use.

| Type | UUID | Hook |
|---|---|---|
| `RegistrationRequestMsg` | `8673a3cc-2848-4c87-aa72-cc860589d1b5` | `1407f27f0` |
| `RegistrationRequestV2Msg` | `da4e5889-a65c-4480-8642-0278160125a7` | `1407f2a20` |
| `RegistrationRequestV3Msg` | `0b826b33-89f5-49e0-b8cb-fe4433427778` | `1407f2c50` |

The answer is in whichever **construction** site is reachable from the client's
connect path — cross-reference §17.3's 15-state `GameConnection` table and
**OI-H2-5** (`vtable+0xa8` on the REP driver object, the gate between state 10
and `WaitingForActorGameConnection`).

**This is what S1a needs first. If the chunk runs long, prefer it over
everything below.** Report it before doing anything else.

## Step 2 — OI-P6-1: which `FragmentUpdateMsg`

Two distinct types share the leaf name:

- `951ef3ed-c9a0-4e3d-a6fd-7fe0673d28d2` — hook `1407eeca0`, handler `147f44828`
- `62f68299-7bb2-4e0a-90d9-b664bd363dae` — hook `146ac5390`, handler `148578628`

`P6_PROMPT` attributed RTTI descriptor `14a134340` to
`ReplicateClient::FragmentUpdateMsg`, but **that attribution is unverified** and
the descriptor's only code xref (`1407c9370`) is neither hook. Settle it before
Step 3 names its target. Do not assume the lower address is the right one.

## Step 3 — frame one message end to end (OI-P6-3)

Work from the **handler vftable**, not from the type. `147f44828` has 4 entries
(`FUN_1407c7db0`, `FUN_1407c7df0`, `LAB_1407c7b40`, `LAB_1407c7b50`).

Establish:
- how a message is serialized and deserialized
- **whether the 16-byte UUID is written on the wire, or an index into a
  per-connection table negotiated at registration** (prediction 2, untested)
- how a fragment's payload is delimited
- **whether Hub messages ride inside GridMate replica chunks or beside them on
  the same Carrier** (prediction 4, untested — relates to OI-P5-2, OI-H2-1)

Note that P5 established GridMate's envelope lengths are **bit** counts and its
VLQ is not protobuf's varint (§18). If Hub rides beside GridMate rather than
inside it, none of that applies to Hub's own framing — check, do not inherit.

---

## Predictions — record before searching (CHARTER §4)

**P6's lesson, and why prediction 0 is worded this way.** P6 answered its step 1
correctly and then spent four passes anchored on the wrong mechanism, because
`CreateString` was used by 5,907 types and looked like the answer. **A mechanism
used by most types in the binary is not therefore the mechanism the layer you
care about uses.** That is the fourth form of `X is in the binary, therefore the
protocol is X` (§17.9, §18.0, §19.4).

0. **PREMISE: the handler vftable reached from the registrar is where
   serialization lives, and reading it yields the wire format.** **Falsified if**
   the handler is only a dispatch stub and serialization lives in a separate
   visitor/reflection pass; **or if** the wire format is produced by a generic
   fragment codec that never names the message type at all. **Explicitly allow a
   possibility not listed here, and say so plainly if the evidence points outside
   all of them.**
1. **The wire carries a negotiated index, not the full 16-byte UUID.** Carried
   forward from P6 prediction 2, still untested. 16 bytes per message across
   3,509 types is expensive, and `RegistrationRequestV3Msg` +
   `RegistrationResponseMsg` is the natural place to negotiate a compact map.
   Falsified if the UUID appears verbatim in the serializer.
2. **b22469132 sends V3.** Three revisions exist and the newest is usually live.
   Weak; stated so it can be wrong cheaply.
3. **Hub rides beside GridMate replicas on the same Carrier, not inside replica
   chunks.** Carried forward from P6 prediction 4, still untested.
   `Hub::TransportLayerGridMate::Connect/Listen` (§12, §17) suggests Hub owns its
   transport rather than borrowing GridMate's replica system.

Predictions 1–3 are independent; none rescues 0 if it fails.

---

## Definition of done

- **OI-P6-2 answered** — which registration revision b22469132 sends, with
  evidence, cross-referenced against §17.3.
- **OI-P6-1 answered** — which `FragmentUpdateMsg` is `ReplicateClient`'s.
- **One message framed end to end**, preferably that `FragmentUpdateMsg`.
- **Predictions 1 and 3 tested** — UUID or index on the wire; inside GridMate
  chunks or beside them.
- **Every claim carries its source** — file and symbol at the pinned commit, or
  VA in b22469132.

---

## Non-goals and hard boundaries

- **Static only.** No execution, no hooking, no injection. CHARTER §3.
- **No anti-cheat, no EAC.** `EasyAntiCheatTrait`, `EasyAntiCheatClientTrait` and
  `EOSAntiCheatClientTrait` are in the vocabulary. **Names only. Do not trace,
  do not decompile. If a trace wanders toward any of them, stop.** CHARTER §3.
- **Do not re-derive P6's vocabulary.** It is in `hub_vocabulary.csv` and §19.
- **Do not retry §19.8's three dead routes.**
- **Do not chase the missing 3,199 names.** They do not exist. §19.5.
- **Do not decode a capture here.** P7 documents the format.
- **Do not implement S1a here.** P7 feeds it.
- **Scope bound:** actor migration, persistence, routing, phasing and AOI remain
  **noticed, not pursued**. **OI-P6-5** records a naming-convention inference
  (`*ReplicatedState`, `ComponentClientFacet_*`, `ComponentServerFacet_*`) that
  would give P3 and P4 their targets by name — that is a different chunk.

---

## FINDINGS to record

New STATE section **§20** (or `### 19.x` if thin — judge by volume). Include:
the OI-P6-2 answer with evidence; the OI-P6-1 resolution; the message framing;
prediction outcomes; anything bearing on **S1a** (what the server must emit to
get a client into a world), **P3**, and **P4**.

**Before closing (CHARTER §6.4 — router before ledger):**
1. Tick P7's row in `CHUNKS.md` with verdict, date and a `STATE §` pointer,
   **rewriting the note in the same edit**.
2. DONE banner on this file; strike through — never delete — anything falsified.
3. Fold FINDINGS into `STATE.md`; add §13 rows for anything overturned; update
   §15.
4. Update STATE's freshness header — **all fields**.
5. **Run `python3 check_docs.py`**, then push, then fill the commit hash.
6. End the session with a **HANDOFF block**, ten lines maximum, nothing after it.
