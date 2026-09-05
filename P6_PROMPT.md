# P6 — The Hub message layer: type vocabulary and fragment wire format

> **DONE (PARTIAL) 2026-09-05 — STATE §19.**
> Steps 1, 2, 3 and 5 complete; **Step 4 not started**.
> OI-P5-1 answered (`CreateString` — extraction, not computation).
> OI-P5-4 answered (vftable layout NOT uniform; §18.3 restated single-instance).
> Vocabulary: **3,509 Hub identities**, 311 named / 3,199 anonymous **by design**.
> Handshake set enumerated with UUIDs, hooks and handler tables — §19.6.
> Successor open items: **OI-P6-1 … OI-P6-5** (§15). Step 4 is OI-P6-3.
> **Two claims in this file were falsified before the work began — struck through
> below. Do not act on the struck text.**


**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are
the context. Do not act on a summary of either.**

Created 2026-09-04, out of P5 (§18). P5 set out to document GridMate's replica
format and found a **third layer above it** — `Amazon::Hub`, Amazon's own actor
and fragment replication framework — which is where the game's state actually
lives. P6 is the chunk that reads it.

P6 is **static. Source + Ghidra. No login, no running client, no Proton, no
capture, and no deadline.** It is immune to the 2027-01-31 sunset (§16.0).

Instruments: the warm `nwly.gpr` on `NewWorld.exe` b22469132 from the pin, and
the Lumberyard fork at **`7d4f1ee6`** for `AzCore` (`AZ::Uuid`, `AZ_TYPE_INFO`).
**Note: Hub itself is Amazon-proprietary and is NOT in the fork.** Only the
AzCore primitives it builds on are.

---

## The one thing this chunk does

**Recover the Hub type vocabulary — the mapping from type name to the 16-byte
on-wire identity — and document how a Hub fragment message is framed, accurately
enough that a later chunk can decode a captured `FragmentUpdateMsg` and S1a can
emit a `RegistrationResponseMsg`.**

Deliverable: the name↔UUID map (or a documented reason it cannot be built
wholesale), plus the wire framing of one message end to end.

---

## Step 1 — OI-P5-1, and stop here if it goes the hard way

**This single fact determines the shape of the entire chunk. Do it first and
report it before doing anything else.**

`FUN_1407fbe00` (the `ReplicateClient` type-identity accessor, §18.3) caches 16
bytes computed by:

```c
FUN_1413e84b0(local_18, &DAT_147f42168, 0)
```

`147f42168` is `147f42158 + 0x10` — **past `"ReplicateClient\0"`** (15 chars plus
terminator). So the input is the string *following* the type name.

1. **Read `DAT_147f42168`.** Goto it in the Listing. Is it a name string, or a
   literal ~~`"{XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX}"`~~ **— brace-delimited is
   NOT the universal form. Both braced and unbraced literals exist and both are
   parsed; `ReplicateClient` is unbraced. §19.2, §13.**
   **ANSWERED: a literal, `6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d`.**
2. **Decompile `FUN_1413e84b0`.** Compare against `AZ::Uuid::CreateString` and
   `AZ::Uuid::CreateName` in the fork
   (`dev/Code/Framework/AzCore/AzCore/Math/Uuid.*`). ~~CreateName is MD5 over the
   name~~ **— FALSE: `CreateName` is SHA-1 (`Uuid.cpp:285` → `CreateData` `:293–322`,
   `Sha1.h` at `:15`, version nibble `0x50`). `VER_NAME_MD5` is decode-only.
   §19.2, §13.** CreateString parses hex with brace/dash handling. **They look
   nothing alike** — a few lines of decompiler output should settle it.

| Outcome | What P6 becomes |
|---|---|
| **`CreateName`** | The vocabulary is **computable offline**. We already hold ~3,600 type names from the symbol dump. Implement the same digest, run the names through, emit the full name↔UUID map. Go to Step 2a. |
| **`CreateString`** | The UUIDs are **literals** in `.rdata`. Scan for the brace-delimited pattern and pair each with its adjacent name string (§18.3: name and vftable are adjacent per translation unit). Go to Step 2b. |

**Record the answer before proceeding.** It is OI-P5-1 and test #68's residual.

---

## ~~Step 2a — build the map by computation~~ **DEAD — `CreateString`, not `CreateName`.**

Implement `Uuid::CreateName` from the fork source, verify it reproduces the
cached 16 bytes at `_DAT_14a2e7750` for `ReplicateClient`, **then** run it over
the full name list. **Verify against a second and third type before trusting the
bulk output** (CHARTER §4 — a belief validated only against your own tooling is
not validated).

## Step 2b — build the map by extraction **— DONE, but not as written**

> The `.rdata` scan described below is **not** how the map was built. Hub types
> register through `FUN_1407de270` with the UUID parse **inlined**, so they have
> no `CreateString` call site. Walking `CreateString` yields the engine's
> `AZ_TYPE_INFO` map (5,907 types) which does **not** contain the session layer.
> See §19.3–19.5. Three dead routes recorded in §19.8 — do not retry them.

Scan `.rdata` for the UUID-literal pattern; pair each with the nearest preceding
name string. **Verify the pairing rule on `ReplicateClient` and `REPClient`
first** — their neighbourhoods are ~0x5A00 apart (§18.1), so a naive
nearest-neighbour rule may mis-pair across translation-unit boundaries. Report
the pairing failure rate honestly rather than a clean-looking map.

---

## Step 3 — confirm the vftable layout is uniform (OI-P5-4)

Every §18.3 claim rests on **one** worked example. Repeat the trace on
`REPClient`: name string `147f47b10`, RTTI descriptor `14a134e00`, and its
`REPClient::REPClient(void)` lambda at `14a134e60`. Find its vftable; compare
slot count and targets against `ReplicateClient`'s 8 slots at `0x147f42110`.

**If the layouts differ, §18.3 is a single-instance observation and must be
restated as such.**

---

## Step 4 — frame one message end to end

Target `ReplicateClient::FragmentUpdateMsg` (RTTI descriptor `14a134340`) — the
**inbound world-state update**, the server→client direction the project has been
chasing since OI-H2-3.

Find its vftable and work out, from the virtuals:
- how a message is serialized and deserialized
- whether the 16-byte UUID is written on the wire, or an index into a
  per-connection table negotiated at registration
- how a fragment's payload is delimited
- whether Hub messages ride *inside* GridMate replica chunks or beside them on
  the same Carrier (relates to OI-P5-2 and OI-H2-1)

**That last question is the one that ties Hub back to T5's transport findings.**

---

## Step 5 — the handshake, for S1a

Enumerate the wire form of the session-opening messages (§18.2):
`REPClient::RegistrationRequestMsg` / `V2Msg` / `V3Msg`,
`RegistrationResponseMsg`, `PingMsg`, `TimeSynchMsg`, and
`REPConnectionListener::ClientConnectionMsg` / `ClientDisconnectionMsg`.

**Which revision does b22469132 actually send?** Three versions exist; the client
uses one. Cross-reference against §17.3's 15-state GameConnection table.

**This is the most directly S1a-actionable part of the chunk.** If time runs
short, prefer it over Step 4.

---

## Predictions — record before searching (CHARTER §4)

**P5's lesson, and the reason prediction 0 is worded as it is.** P5's
prediction 0 was written to target its own premise and *still* failed, because
it enumerated only two answers — "the world stream is `ReplicaChunk`" or "it is
not" — and reality was a third layer neither option named. **A premise-targeting
prediction must leave room for "neither — it is something not yet named."**
This is now the third time in two chunks that *X is in the binary, therefore the
protocol is X* has cost the project a redirect (P2 → protobuf; P5 → GridMate).

0. **PREMISE: `Amazon::Hub` fragments are what the world stream carries, and the
   16-byte UUID is what identifies them on it.** **Falsified if** the UUID is
   used only for in-process type dispatch and the wire carries a negotiated
   small index instead; **or if** Hub proves to be a server-side-only framework
   whose client half is a thin stub, with the actual wire format belonging to
   yet another layer. **Explicitly allow a fourth possibility not listed here,
   and say so plainly if the evidence points outside all of them.**
1. **`FUN_1413e84b0` is `Uuid::CreateString`, not `CreateName`** — so the
   vocabulary must be extracted, not computed. Based on the 3-arg/`0`-length
   call shape and `AZ_TYPE_INFO`'s convention of a literal UUID beside the name.
   *This is the prediction the session most wants to be wrong.*
2. **The wire carries a negotiated index, not the full 16-byte UUID.** Sending
   16 bytes per message for ~3,600 types is expensive; `RegistrationRequestV3Msg`
   plus a `RegistrationResponseMsg` is the natural place to negotiate a compact
   mapping. Falsified if the UUID appears verbatim in the serializer.
3. **The vftable layout is uniform across Hub types** (8 slots, name / identity
   compare / visitor dispatch in slots 0–2). Falsified by `REPClient` differing.
4. **Hub rides beside GridMate replicas on the same Carrier, not inside replica
   chunks.** `Hub::TransportLayerGridMate::Connect/Listen` (§12, §17) suggests
   Hub owns its transport rather than borrowing GridMate's replica system.

Predictions 1–4 are independent; none rescues 0 if it fails.

---

## Definition of done

- **OI-P5-1 answered** — `CreateName` or `CreateString`, with evidence.
- **The type vocabulary produced** — the name↔UUID map, or a clear statement of
  what fraction could be recovered and why the rest could not.
- **OI-P5-4 answered** — vftable layout uniform, or §18.3 restated as
  single-instance.
- **One message framed end to end**, preferably `FragmentUpdateMsg`.
- **The handshake enumerated** with the revision b22469132 actually sends.
- **Every claim carries its source** — file and symbol at the pinned commit, or
  VA in b22469132.

---

## Non-goals and hard boundaries

- **Static only.** No execution, no hooking, no injection. CHARTER §3.
- **No anti-cheat, no EAC.** Note that `EasyAntiCheatClientTrait` and
  `EOSAntiCheatClientTrait` **appear in the Hub type list**. They are in scope
  *only* as names in the vocabulary. **Do not trace them, do not decompile them.
  If a trace wanders toward either, stop.** CHARTER §3.
- **Do not enumerate all ~3,600 types by hand.** The map is produced by tool or
  not at all.
- **Do not decode a capture here.** P6 documents the format.
- **Do not implement S1a here.** P6 feeds it.
- **Scope bound:** Hub is large — actors, traits, routing, persistence,
  migration, phasing, AOI. **P6 covers the type vocabulary, the fragment
  message framing, and the session handshake. Everything else is
  noticed-not-pursued.** The Hub type list alone contains actor migration,
  persistence and interest-management subsystems; they are a different chunk.

---

## FINDINGS to record

New STATE section **§19** (or `### 18.x` if thin — judge by volume). Include:
the OI-P5-1 answer with evidence; the vocabulary map or its failure mode; the
vftable uniformity result; the message framing; the handshake enumeration and
which revision is live; anything bearing on **S1a** (what the server must emit
to get a client into a world), **P3** (position messages), and **P4**.

**Before closing (CHARTER §6.4 — router before ledger):**
1. Tick P6's row in `CHUNKS.md` with verdict, date and a `STATE §` pointer,
   **rewriting the note in the same edit**.
2. DONE banner on this file; strike through — never delete — anything falsified.
3. Fold FINDINGS into `STATE.md`; add §13 rows for anything overturned; update
   §15.
4. Update STATE's freshness header — **all five fields**.
5. **Run `python3 check_docs.py`**, then push, then fill the commit hash.
6. End the session with a **HANDOFF block**, ten lines maximum, nothing after it.
