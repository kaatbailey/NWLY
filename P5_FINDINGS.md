# P5 FINDINGS — paste into `STATE.md`

**These are paste-in blocks, not a regenerated `STATE.md`.** The session's copy of
`STATE.md` predates the commit-hash edit made after the P2 fold, so regenerating
it would silently clobber that and anything else changed since. Apply the blocks
below by hand, in the order given (CHARTER §5, append-only).

**Filed as a new `## 18`, not a `###` under §17.** P5's content is a wire format
across two engines plus a newly discovered third layer; it does not belong inside
H2's dispatch map. **This changes the `## ` section count from 20 to 21** — the
freshness header must be updated accordingly.

---

## 1. New section — append at end of `STATE.md`

### 18. FINDINGS — P5 (replica/chunk model, source-first) — 2026-09-04

**Status:** DONE with a major redirect. Source read from the pinned Lumberyard
fork; retail cross-check performed statically in the warm `nwly.gpr`. No
execution, no hooking, no capture, no login. Opens OI-P5-1…4 and a new chunk
**P6**. Two §13 corrections, one of them against P2's own §17.9.

**Source pin:** `github.com/kaatbailey/lumberyard` @ **`7d4f1ee6`**, under
`dev/Code/Framework/GridMate/GridMate/` and `.../AzFramework/Network/`. Verified
2026-09-04 that `Replica/ReplicaChunk.h`, `Serialize/MathMarshal.h` and
`Serialize/CompressionMarshal.h` are **byte-identical** between `413ecaf` and
`7d4f1ee6`, so §7's source facts (established against `413ecaf`) transfer
unchanged.

**Retail instrument:** `NewWorld.exe` b22469132 from the pin, warm `nwly.gpr`.

#### 18.0 The headline: there is a THIRD layer, and the game state is in it

P5 set out to document GridMate's replica wire format on the assumption that the
world stream is GridMate `ReplicaChunk` marshalling. **That assumption was
wrong, and so was the alternative the prompt offered against it.**

| Layer | What it is | Status in retail |
|---|---|---|
| **GridMate replicas** | Stock Lumberyard `ReplicaChunk` / `DataSet` marshalling | **Present and stock.** `AzFramework::NetworkContextChunkDescriptor` verbatim from source. Bound chunk types visible: `TransformReplicaChunk`, `TriggerAreaReplicaChunk` — **both stock engine components**, not game content. |
| **Javelin (AWS SDK)** | JSON REST over HTTP | Auth phase. Settled by P2, §17.9. |
| **`Amazon::Hub`** ← **NEW** | Amazon's own actor/fragment replication framework, built **above** GridMate and using it only for transport | **Where the game's state actually lives.** ~3,600 registered types. |

**P5's prediction 0 asked the wrong question.** It offered two answers — "the
world stream carries `ReplicaChunk` traffic" or "it does not" — and the truth is
a third option the prompt never contemplated: GridMate replicas are present but
carry *engine* components, while every game-state type (`MB::*ReplicatedState`,
`Javelin::*ReplicatedState`) is a **Hub fragment**.

**This is the same error class as P2's, for the third time in two chunks:**
*X is in the binary, therefore the protocol is X.* Prediction 0 existed
specifically to catch it and did not, because it enumerated only two
possibilities. **Lesson for future prediction sets: a premise-targeting
prediction must include "neither — it is something not yet named."**

#### 18.1 Amazon::Hub — structure

**Hub is entirely inlined. There is not one named Hub function in the binary.**

| Query | Result |
|---|---|
| Symbols matching `Amazon::Hub` | **3,629 — all `Label`, zero `Function`** |
| Symbols matching `InstallRegistrationHook` | **3,482 — all `Label`, zero `Function`** |
| Functions with `Hub::` in the name | **0** |

Every `InstallRegistrationHook<T>` is inlined into a static initializer. What
survives is the RTTI descriptor of the type-erased lambda each hook builds:

```
`bool __cdecl Amazon::Hub::InstallRegistrationHook<T>(void)'::__l2::<lambda_1>::RTTI_Type_Descriptor
```

`?1` / `__l2` marks a function-local magic static. **Consequence: the hook bodies
cannot be found by name, and XREFs on the descriptors and name strings are the
only doors into the layer.** (Test #66.)

**Two distinct address regions, two different orderings:**

- **RTTI descriptors — contiguous, in LINK order** from `14a1340c0` upward,
  spaced 0x60–0x90 apart. Link order mirrors translation-unit order, which is
  why related services cluster.
- **Name strings — scattered, per translation unit.** `s_ReplicateClient` at
  `147f42158`, `s_REPClient` at `147f47b10` (~0x5A00 away),
  `s_Amazon::Hub::ActorRef` at `14803e230` (a third neighbourhood entirely).
  **A single contiguous dump will not enumerate the vocabulary.**

**The registration shape is uniform:** each service registers `X`, then
`X::State`, then each `X::*Msg`. A service, its state fragment, its messages.

#### 18.2 The world-session surface — one contiguous 0xA00-byte neighbourhood

The entire replication and session surface sits together in link order:

| VA | Type |
|---|---|
| `14a134340` | `ReplicateClient::FragmentUpdateMsg` |
| `14a1343c0` | `ReplicateClient::State` |
| `14a134430` | `ReplicateClient` |
| `14a134498` | `ReplicateClient::ReplicateClient(void)` ← ctor lambda |
| `14a1344e0` | `Replicate::UnregisterProxyMsg` |
| `14a134560` | `Replicate::UnregisterFragmentAccessMsg` |
| `14a1345e0` | `Replicate::RegisterFragmentAccessMsg` |
| `14a134660` | `Replicate::State` |
| `14a1346d0` | `Replicate` |
| `14a134730` | `Amazon::Hub::ASC_UnregisterAllFragmentsAccess` |
| `14a1347b0` | `Amazon::Hub::ASC_RegisterAllFragmentsAccess` |
| `14a134870` | `REPConnectionListener::ClientDisconnectionMsg` |
| `14a134900` | `REPConnectionListener::ClientConnectionMsg` |
| `14a134980` | `REPConnectionListener::State` |
| `14a1349f0` | `REPConnectionListener` |
| `14a134ab0` | `REPClient::RegistrationRequestV3Msg` |
| `14a134b30` | `REPClient::RegistrationRequestV2Msg` |
| `14a134bb0` | `REPClient::RegistrationRequestMsg` |
| `14a134c30` | `REPClient::PingMsg` |
| `14a134ca0` | `REPClient::RegistrationResponseMsg` |
| `14a134d20` | `REPClient::TimeSynchMsg` |
| `14a134d90` | `REPClient::State` |
| `14a134e00` | `REPClient` |
| `14a134e60` | `REPClient::REPClient(void)` ← ctor lambda |

**`Replicate` / `ReplicateClient` are a server/client service pair**, and
`ReplicateClient::FragmentUpdateMsg` is the **inbound world-state update** — the
server→client direction the project has been chasing since OI-H2-3.

**For S1a this is the most concrete target the project has ever had:** the world
handshake enumerated by name, in three versioned revisions
(`RegistrationRequestMsg` / `V2` / `V3`), plus `RegistrationResponseMsg`,
`PingMsg`, `TimeSynchMsg`, and the connection lifecycle
(`REPConnectionListener::ClientConnection/DisconnectionMsg`). This maps directly
onto §17.3's 15-state GameConnection table.

**Both `REPClient` and `ReplicateClient` constructors carry lambda descriptors** —
so these services register something at construction time as well as via the
static hooks.

#### 18.3 Hub type identity — a 16-byte `AZ::Uuid`, source UNRESOLVED

Worked example, `ReplicateClient` (test #67):

**vftable at `0x147f42110`, 8 slots**, ending `147f42148`; `DAT_147f42150`
begins the next structure. Slots reach their targets through MSVC **adjustor
thunks** (`MOVSXD RAX,[RCX-4]; SUB RCX,RAX; JMP …`) — multiple inheritance.

| Slot | Thunk | Target | What it does |
|---|---|---|---|
| `147f42120` | `LAB_1407c4b28` | `1407f9b60` | `return "ReplicateClient";` — **the type's own name** |
| `147f42128` | `LAB_1407c4b34` | `FUN_1407f9f30` | identity compare — two 8-byte halves, i.e. **16 bytes** |
| `147f42130` | `LAB_1407c4b40` | `FUN_1407f98d0` | visitor / apply, dispatches through a function pointer |
| `147f42138`, `147f42140` | `LAB_1407c4b58` | (shared) | — |
| `147f42148` | — | `FUN_1407c2fd0` | — |

**The vftable and the type's name strings are adjacent** (`0x147f42110` vs
`0x147f42158`) — which is why name strings cluster per translation unit rather
than in one table.

**`FUN_1407fbe00` produces the identity.** TLS-guarded magic static
(`_tls_index`, `DAT_14a2e7760`, `_Init_thread_footer`): computes **four
`undefined4` = 16 bytes** once, caches at `_DAT_14a2e7750`, returns its address.
Both slot-1 and slot-2 call it. **16 bytes is `AZ::Uuid`.**

```c
puVar1 = (undefined4 *)FUN_1413e84b0(local_18, &DAT_147f42168, 0);
```

**UNRESOLVED, and it is the highest-value open question in the project
(OI-P5-1).** `147f42168` is `147f42158 + 0x10` — i.e. **past** `"ReplicateClient\0"`
(15 chars + terminator). So the hash input is **the string that follows the type
name, not the type name itself.** Two readings, with opposite consequences:

| If `FUN_1413e84b0` is… | Then `DAT_147f42168` is… | Consequence |
|---|---|---|
| `AZ::Uuid::CreateName` | a name string | **The vocabulary is computable offline.** We hold ~3,600 type names; run them through the same algorithm and the full name↔UUID map falls out. No extraction needed. |
| `AZ::Uuid::CreateString` | a **literal** `"{XXXXXXXX-XXXX-…}"` from `AZ_TYPE_INFO` | **Not computable.** ~3,600 literal UUIDs must be extracted from `.rdata` individually. |

The 3-argument call with a `0` third parameter fits `CreateString(str, len=0)`.
**The session initially recorded the optimistic `CreateName` reading as fact and
then withdrew it before writing** — recorded here because the withdrawal is the
finding, not the guess. **Resolved by reading `DAT_147f42168` and decompiling
`FUN_1413e84b0`. That is P6 step 1.**

**Worked example of an inlined hook body: `FUN_1407f3720`.** TLS magic static
(`DAT_14a2e7790`); builds `"ReplicateClient"` inline as an `AZStd::string` —
`0x746163696c706552` / `0x696c4365` / `0x6e65` / `0x74` / `\0`, with length and
capacity both `0xf` — then loops over `(&DAT_147f42168)[i]`, the same following
string. **This is one of the `InstallRegistrationHook` bodies that has no symbol.**

#### 18.4 GridMate replica wire format — documented, and it is not the game's

Read from the pin; correct as far as it goes, but see §18.0 — this describes the
layer carrying **engine** components, not game state.

**Replica envelope** (`Replica/Replica.cpp:541`, `Replica::Marshal`):

```
ReplicaId
payloadLen            VLQ, in BITS          ← PackedSize
chunkManifest         VLQ u64 bitmask       ← which chunk slots follow
  per set bit:
    chunkLen          VLQ, in BITS
    chunkPayload:
      [ChunkTypeId : AZ::Crc32]             ← only when IncludeCtorData
      changebits    VLQ u32                 ← dirty DataSet mask
      dirty DataSets, in index order
      RPCs
```

**`PackedSize` is bit-granular, not byte-granular** (`Serialize/PackedSize.h`:
`m_totalBits`). `Marshaler<PackedSize>` writes **the bit count**, VLQ-encoded.
**A decoder reading these as byte lengths desyncs immediately** — the single
most dangerous gotcha in the format.

**GridMate's VLQ is not protobuf's varint.** Length is signalled by the high
bits of the *first* byte; payload bits pack low-first across the remainder
(`Serialize/CompressionMarshal.h:345`):

| First byte | Total bytes | Value bits |
|---|---|---|
| `< 0x80` | 1 | 7 |
| `0x80–0xBF` | 2 | 14 |
| `0xC0–0xDF` | 3 | 21 |
| `0xE0–0xEF` | 4 | 28 |
| `0xF0+` | 5 | 32 |

**Chunk type id is `AZ::Crc32`** — `typedef AZ::Crc32 ReplicaChunkClassId`
(`Replica/ReplicaDefs.h`). *Prediction 1 confirmed.*

**DataSets are dirty-bit gated** — VLQ-encoded changebits mask, only set members
written (`Replica/ReplicaChunk.cpp:339`, `MarshalDataSets`). *Prediction 2
confirmed.*

**Reserved command IDs** (`ReplicaDefs.h`): `Cmd_Greetings`, `Cmd_NewProxy`,
`Cmd_DestroyProxy`, `Cmd_NewOwner`, `Cmd_Heartbeat`, `RepId_SessionInfo`. Note
the encoding trick recorded in the source: *a CmdId above
`Max_Reserved_Cmd_Or_Id` is implicitly `UpdateReplica`, saving a byte per update.*

**Prediction 3 FALSIFIED — transforms are NOT quantized by default.**
`Marshaler<AZ::Vector3>` writes **three raw IEEE floats, 12 bytes**;
`Marshaler<AZ::Transform>` is four Vector3s, **48 bytes uncompressed**
(`Serialize/MathMarshal.h:59,186`). Quantization exists — `Float16Marshaler`,
`Vec3CompRangeMarshaler`, `QuatCompNormQuantizedMarshaler`,
`TransformCompressor`, `IntegerQuantizationMarshaler` — but is **opt-in per
DataSet declaration**, not the default. **This bears directly on P3:** a
controlled-walk capture should look for a smoothly varying **raw float triple**.
Whether New World opted into compression is a per-DataSet question this chunk
could not answer.

#### 18.5 What P5 unblocks and redirects

- **P6 opens** — the Hub message layer. Everything in §18.1–18.3.
- **Track P retargets again**, off GridMate replicas and onto Hub.
- **For S1a:** the world handshake is now enumerated by name (§18.2). The
  server→client state update has a name: `ReplicateClient::FragmentUpdateMsg`.
- **For P3:** look for raw float triples, not quantized ints (§18.4).
- **§17.9's Track P retarget is superseded** — see §13.

#### 18.6 Instrument notes and caps

- Ghidra 11.3+ replaced the Jython console with **PyGhidra**; launch via
  `/opt/ghidra/support/pyghidraRun`, not `ghidraRun`.
- **The PyGhidra console mangles multi-line pastes** (eats indentation, strands
  the prompt at `...`). Run scripts from `~/ghidra_scripts` via Script Manager
  instead. `hub_probe.py` is the one used here.
- **The Symbol Tree shows namespaces (`{}` icons), not functions.** Symbols
  matching a template name may be `Label` only. **Use the Symbol Table and check
  the Type column** — the session lost time to this.
- Whole-symbol-table sweeps take 1–5 minutes on this binary.
- **Cap:** every §18.1–18.3 finding is from one worked example
  (`ReplicateClient`) plus symbol-table aggregates. The vftable layout is
  assumed uniform across Hub types **and has not been checked against a second
  type** — OI-P5-4.

---

## 2. §13 — two correction rows to append

| Old claim | Where | Correction |
|---|---|---|
| "`InitializeReplicatedFields` **94** — matches T1/§10's independently-derived ~94, an instrument cross-check that passed" and, in the retarget, "The world stream is **GridMate `ReplicaChunk` marshalling** (`ReplicaChunk` 23, `InitializeReplicatedFields` 94 …)" | **§17.9** (P2, 2026-09-04) | **WRONG — `InitializeReplicatedFields` is not a GridMate symbol.** It is a virtual on `Javelin::*ComponentServerFacet` classes, i.e. **`Amazon::Hub`**, and is absent from all of `dev/Code/Framework` (AzCore + AzFramework + GridMate) at the pinned commit. The count matching T1's ~94 was a real cross-check of the *count*, but the *attribution* was inherited from §10 and never verified. **The 94 references are evidence for Hub, not for GridMate replicas.** The retarget conclusion was therefore right by accident and for the wrong reason: Track P did need to leave protobuf, but its destination is Hub (§18), not GridMate replica marshalling. **Lesson: an instrument cross-check that confirms a number does not confirm what the number is about.** §18.0, §18.1. |
| "Note P3 depends on this: GridMate's transform marshalers **quantize**, so a raw float triple is the wrong thing to look for." | `CHUNKS.md`, P5 stub (2026-09-04) | **FALSE for the defaults.** `Marshaler<AZ::Vector3>` writes three **raw IEEE floats** (12 B) and `Marshaler<AZ::Transform>` four of those (48 B), uncompressed, at `Serialize/MathMarshal.h:59,186`. Quantizing marshalers exist but are **opt-in per DataSet**. P3 should search for a smoothly varying raw float triple after all. Whether New World opts in per-DataSet is unresolved. §18.4. |

---

## 3. §14 — tests 66–68 to append

| 66 | **P5** whole-symbol-table sweep of `NewWorld.exe` b22469132 for `InstallRegistrationHook`, `REPClient`, `ReplicateClient`, `Amazon::Hub`, via `hub_probe.py` in PyGhidra. | P5 planned to decompile a registration hook and read how types are identified. Expect hooks to exist as functions. | **They do not exist as functions at all.** `Amazon::Hub` **3,629 symbols, 100% `Label`**; `InstallRegistrationHook` **3,482, 100% `Label`**; **functions with `Hub::` in the name: 0.** Every hook is inlined into a static initializer; only the type-erased lambda's RTTI descriptor survives. **The planned approach was impossible and the sweep is what revealed the Hub layer's existence.** §18.1. |
| 67 | **P5** XREF trace from the `"ReplicateClient"` name string (`147f42158`) and the `FragmentUpdateMsg` RTTI descriptor (`14a134340`) through to real code. | If Hub is inlined, XREFs on data are the only route in; expect them to reach a shared registration routine. | **Reached the type's vftable, not a registry.** vftable `0x147f42110`, **8 slots**, MSVC adjustor thunks. Slot 0 → `1407f9b60` = `return "ReplicateClient"`. Slot 1 → `FUN_1407f9f30` = **16-byte identity compare**. Slot 2 → `FUN_1407f98d0` = visitor dispatch. Both call `FUN_1407fbe00`, a TLS magic static caching a **16-byte `AZ::Uuid`**. Also recovered `FUN_1407f3720`, an **inlined hook body** building `"ReplicateClient"` as a 15-char inline `AZStd::string`. §18.3. |
| 68 | **P5** identify the source of the 16-byte Hub type identity: decompile `FUN_1407fbe00` and locate its hash input. | Determines whether the ~3,600-type wire vocabulary is computable offline or must be extracted literal by literal. | **UNRESOLVED — OI-P5-1, and the withdrawal is the finding.** `FUN_1407fbe00` calls `FUN_1413e84b0(buf, &DAT_147f42168, 0)`. `147f42168` is `147f42158 + 0x10`, i.e. **past `"ReplicateClient\0"`** — the input is the *following* string, not the type name. If `FUN_1413e84b0` is `Uuid::CreateName`, the vocabulary is computable from names we already hold; if it is `Uuid::CreateString`, ~3,600 literal UUIDs must be extracted. **The 3-arg/`0`-length shape fits `CreateString`.** The session recorded the optimistic reading as fact mid-analysis and withdrew it before writing. §18.3. |

---

## 4. §15 — register updates

**Close:**

- **OI-H2-3** was already answered by P2 for the *Javelin* direction. **§18 adds
  the world-state half**: the server→client update is
  `ReplicateClient::FragmentUpdateMsg`, a Hub fragment message. Add a note to
  the existing closed row pointing at §18.2 — **do not reopen it.**

**Open — append to the register:**

| ID | Item | Owner | Notes |
|---|---|---|---|
| **OI-P5-1** | **Is the Hub type UUID derived from the type name, or a literal from `AZ_TYPE_INFO`?** `FUN_1407fbe00` caches 16 bytes computed by `FUN_1413e84b0(buf, &DAT_147f42168, 0)`, where `147f42168` is the string *after* the type name. | **P6, step 1.** | **The highest-value open question in the project.** `CreateName` → the entire ~3,600-type wire vocabulary is computable offline from names we already hold. `CreateString` → ~3,600 literals must be extracted. Resolved by reading `DAT_147f42168` and decompiling `FUN_1413e84b0`; the fork source has both functions for comparison. §18.3, test #68. |
| **OI-P5-2** | **Does GridMate replica traffic reach the world stream at all?** GridMate replica machinery is present and stock, but the only bound chunk types found are `TransformReplicaChunk` and `TriggerAreaReplicaChunk` — both stock engine components. | **Unowned.** | P5's prediction 0 was never cleanly answered: the chunk found a third layer instead of resolving the two-way question it posed. OI-H2-2 (`REPConnection::OnRecv` body would not resolve statically) remains the obstacle. **Low priority** — even if GridMate replicas do carry traffic, they carry engine transforms, not game state. §18.0. |
| **OI-P5-3** | **Does New World opt into quantizing marshalers for transforms?** GridMate's defaults are raw IEEE floats; compression is opt-in per DataSet. | **P3.** | Determines what a controlled-walk capture should search for. Corrects the CHUNKS P3 note (§13). §18.4. |
| **OI-P5-4** | **Is the 8-slot vftable layout uniform across Hub types?** Everything in §18.3 comes from one worked example, `ReplicateClient`. | **P6.** | Cheap: repeat the trace on `REPClient` (name string `147f47b10`) and compare slot count and targets. **A cap on every §18.3 claim until done.** CHARTER §4. |

---

## 5. Freshness header — update all five

| Field | New value |
|---|---|
| Date | 2026-09-04 |
| Written against commit | **FILL ON COMMIT** |
| Section count (`## `) | **21** ← was 20; §18 is a new `## ` section |
| Highest test number | **68** |
| Correction row count | **31** ← was 29; two rows added |
| Chunks complete | append **P5** |

---

## 6. `P5_PROMPT.md` — DONE banner

```markdown
> # ✅ DONE — 2026-09-04. Findings in STATE §18.
>
> **VERDICT: COMPLETE, with a redirect bigger than the chunk itself.**
>
> The GridMate replica wire format is documented (§18.4) and is **not where the
> game's state lives**. Game state rides **`Amazon::Hub`** — a third layer,
> above GridMate, that this prompt did not know existed.
>
> **Prediction 0 asked the wrong question.** It offered two answers — the world
> stream carries `ReplicaChunk` traffic, or it does not — and the truth was
> neither. GridMate replicas are present and stock but carry *engine*
> components; every `MB::*ReplicatedState` / `Javelin::*ReplicatedState` is a
> Hub fragment. **A premise-targeting prediction must include "neither — it is
> something not yet named."**
>
> **Prediction 1 CONFIRMED** (chunk id is `AZ::Crc32`).
> **Prediction 2 CONFIRMED** (DataSets dirty-bit gated, VLQ mask).
> **Prediction 3 FALSIFIED** — transforms are **raw IEEE floats** by default,
> 12 B per Vector3, 48 B per Transform; quantization is opt-in per DataSet.
> This corrects the CHUNKS P3 note (§13) and changes what P3 should look for.
> **Prediction 4** — the chunk header is small and fixed: broadly confirmed, but
> note every length in the envelope is a **bit** count, not a byte count.
>
> **Also corrected: P2's own §17.9.** `InitializeReplicatedFields` is a Hub
> symbol, not a GridMate one, so the 94 references never supported the GridMate
> retarget. §13.
>
> **Successor: P6 — the Hub message layer.** Step 1 is OI-P5-1, which decides
> whether the ~3,600-type wire vocabulary is computable offline.
>
> Struck-through claims below are preserved per CHARTER §5, not deleted.
```

**Then strike through, in the body** (never delete):

- Prediction 0's two-way framing, with "→ neither; see §18.0" beside it
- Prediction 3 in full, with "→ FALSIFIED, raw floats" beside it
- In "Why this is answerable from source", force-multiplier 2's claim that the
  replica stack's presence in retail implies it carries the world stream
- The scope-bound line "the world stream's actual encoding" in the P5 stub
- Step 5's assumption that the retail cross-check would be a consistency check
  rather than a discovery

---

## 7. `CHUNKS.md` — edits

**P5 row → tick, with verdict and pointer:**

```
| `[x]` | **P5** Replica/chunk model | ~~T1, H4~~ **T1** | **DONE 2026-09-04 —
COMPLETE with a major redirect. STATE §18.** GridMate replica wire format
documented from the pin (envelope, bit-granular `PackedSize`, GridMate VLQ,
`AZ::Crc32` chunk ids, dirty-bit DataSets) — **but it is not where game state
lives.** Found a **third layer, `Amazon::Hub`**: 3,629 symbols, **zero
functions**, fully inlined; game state is Hub fragments; the world handshake is
enumerated (`REPClient::RegistrationRequestMsg`/`V2`/`V3`, `RegistrationResponse`,
`Ping`, `TimeSynch`) and the inbound state update is
`ReplicateClient::FragmentUpdateMsg`. **Prediction 0 asked the wrong question;
prediction 3 falsified — transforms are raw floats, not quantized** (corrects the
P3 note below, §13). **Also corrects P2's §17.9** on
`InitializeReplicatedFields`. Residuals OI-P5-1…4. Tests #66–#68.
→ **P6.** Prompt: `P5_PROMPT.md` |
```

**Add a P6 row** (place it as the new Track P front, above P3/P4):

```
| `[ ]` | **P6** Hub message layer — type vocabulary and fragment wire format |
T1, H2, P2, P5 | **THE TRACK P FRONT, opened 2026-09-04 by P5 (§18).** Amazon's
own replication framework, above GridMate. Step 1 resolves **OI-P5-1** — whether
the ~3,600-type wire vocabulary is computable offline (`Uuid::CreateName`) or
must be extracted literal by literal (`Uuid::CreateString`). Static, source +
Ghidra, no capture, no deadline, **immune to the 2027-01-31 sunset.** Prompt:
`P6_PROMPT.md` |
```

**Strike the P3 quantization note** in the P5 stub and beside it:
**"CORRECTED 2026-09-04 — GridMate's default transform marshalers write raw
IEEE floats; quantization is opt-in per DataSet. §13, §18.4."**

**Add `P6_PROMPT.md` to the standalone-prompt inventory** — *at creation time,
before P6 runs.* That list has now been missed three times; this is the fourth
opportunity to not miss it.

**Order section:** strike "Next is P5"; the front is now **P6**, with **OI-P2-2**
(diff the 10 Javelin type names against `p0_cold`'s routes) still the cheapest
item on the board.

---

## 8. Closing sequence — router before ledger

1. **`CHUNKS.md` first** — tick P5 *and rewrite its note in the same edit*; add
   the P6 row; add `P6_PROMPT.md` to the inventory; strike the P3 note.
2. **`P5_PROMPT.md`** — DONE banner + strikethroughs (§6 above).
3. **`STATE.md`** — §18, then the two §13 rows, then §14 tests 66–68, then the
   §15 updates, then the freshness header (all five fields).
4. **`python3 check_docs.py`** — expect it to flag the commit placeholder and,
   if you paste out of order, a section-count mismatch. **A FAIL means stop.**
5. **`git push`**, then fill the commit hash and push again.
