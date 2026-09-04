# P2 FINDINGS — paste into `STATE.md`

Filed as **§17.9**, not a new §18: the schema content is one message, one nested
struct and one enum. It does not make §17 unwieldy, and keeping it a `###`
subsection leaves the freshness header's `## ` count at **20**, unchanged.

---

### 17.9 FINDINGS — P2 (protobuf descriptor extraction, static) — 2026-09-04

**Status:** DONE. Static scan of `NewWorld.exe` b22469132 (179,204,176 bytes,
image base `0x140000000`) from the pin at
`~/Documents/nwly-pin/22469132/Bin64/`. No execution, no hooking, no pcap.

**Verdict: protobuf is present and irrelevant to the world protocol.** The
binary's entire non-stock protobuf surface is a single telemetry event schema.
There is no Javelin descriptor, no `service` block, and no protobuf-encoded
game message of any kind. **FIND-2 closes.** §17.5's "protobuf choke point"
claim is corrected below.

This is a negative result and it is worth more than the schema P2 went looking
for: it removes a wrong belief from §17.5 and redirects Track P off a dead end
before any capture budget was spent on it.

#### All registered `.proto` blobs — complete, 3 of 3

| # | `.proto` path | package | VA | size | msgs | svcs | signature (first 16B) |
|---|---|---|---|---|---|---|---|
| 0 | `campfire_event_default.proto` | *(none)* | `0x1486f5b60` | 1407 | 4 | 0 | `0a1c63616d70666972655f6576656e74` |
| 1 | `google/protobuf/empty.proto` | `google.protobuf` | `0x1495ab7c0` | 190 | 1 | 0 | `0a1b676f6f676c652f70726f746f6275` |
| 2 | `google/protobuf/descriptor.proto` | `google.protobuf` | `0x1495b3330` | 6028 | 27 | 0 | `0a20676f6f676c652f70726f746f6275` |

All three recovered at `exact` confidence (byte-identical protobuf round-trip).
Signatures are the encoded `name` field — the `.proto` path string constant,
patch-stable across a rebase (CHARTER §4, signatures not offsets).

Blobs 1 and 2 are stock protobuf well-known types. `descriptor.proto` is present
because `google::protobuf::Reflection` requires it — this is exactly what T1
predicted in FIND-2, and it turns out to be the *whole* explanation.

**Blob 0 is the only non-stock content.** Its 4 messages are
`CampfireEventDefault`, its nested `ContextData`, and two synthetic map-entry
types. Real content: **one message, one nested struct, one enum.**

#### `campfire_event_default.proto` — full schema

Campfire is Amazon's analytics/telemetry pipeline. The envelope
(`version`/`id`/`type`/`sourceTimeMillis`/`sessionId`/`applicationVersion`/
`metrics`/`attributes`/`eventPriority`) is a generic event-reporting shape, and
fields 20–21 of `ContextData` are `test_new` and `test_new_2` — leftover
developer scaffolding, which no shipped wire protocol carries.

```proto
syntax = "proto3";

message CampfireEventDefault {
  message ContextData {
    string world_id = 1;
    string hub_id = 2;
    string player = 3;
    string guild_id = 4;
    string character_id = 5;
    string persona_id = 6;
    string prefabName = 7;
    sint32 territory_id = 8;
    sint32 poi_id = 9;
    float xpos = 10;
    float ypos = 11;
    float zpos = 12;
    string host_world_id = 13;
    sint32 level = 14;
    optional bool IsGM = 15;
    double owned_expansion = 16;
    optional CampfireEventDefault.FactionType faction_type = 17;
    optional bool pvp_flag_state = 18;
    string objective_id = 19;
    string test_new = 20;
    string test_new_2 = 21;
  }
  enum FactionType { None = 0; Faction1 = 1; Faction2 = 2; Faction3 = 3; }

  uint32 version = 1;
  string id = 2;
  string type = 3;
  int64 sourceTimeMillis = 4;
  optional string utcOffset = 5;
  optional string userId = 6;
  optional string sessionId = 7;
  optional string applicationName = 8;
  optional string applicationVersion = 9;
  optional string platformName = 10;
  optional string platformVersion = 11;
  optional string locale = 12;
  optional string graphName = 13;
  map<string, ?> metrics = 14;        // rendered as repeated MetricsEntry
  map<string, ?> attributes = 15;     // rendered as repeated AttributesEntry
  optional CampfireEventDefault.ContextData context = 16;
  optional int32 eventPriority = 17;
}
```

Field numbers, types and wire types for every field are in
`p2_out/fields.tsv`. The two `map<>` value types are unresolved in the render —
tool defect, see "Instrument caps" below; read `fields.tsv` for the truth.

**Secondary value — identifier vocabulary, not wire format.** The schema
independently corroborates Amazon's own identifier model:
`world_id` / `host_world_id`, `character_id` / `persona_id`, `guild_id`,
`territory_id`, `poi_id`, `faction_type`, `pvp_flag_state`. The
`character_id` / `persona_id` split matches §17.3's
`javelin.impersonate-character-id` / `impersonate-persona-id` feature flags. The
`world_id` vs `host_world_id` distinction is worth remembering for S0's
`RepAddress` rewrite. **Naming crib only — nothing here is a wire format and
nothing should be built on it.**

#### Diagnostics — serialization shape

| string | count | reading |
|---|---|---|
| `application/json` | **236** | Javelin is JSON |
| `application/x-protobuf` | **0** | no protobuf transport anywhere |
| `application/octet-stream` | 0 | |
| `JavelinGatewayService` | 20 | matches §17.5's RTTI enumeration |
| `InitializeReplicatedFields` | **94** | matches T1/§10's independently-derived ~94 |
| `ReplicaChunk` | 23 | GridMate replica marshalling present |
| `google::protobuf::Reflection` | 1 | a single `GOOGLE_CHECK` assert string |
| `AmazonSerializableWebServiceRequest` | 1 | |
| `Aws::Utils::Json::JsonValue` | 1 | |

**Caveat, and it binds — half this table is unreliable.** Every search string
containing `::` was matched as a literal, but MSVC stores RTTI **mangled**
(`JsonView` appears as `?…@JsonView@Json@Utils@Aws@@`). So `JsonView` = 0,
`DataSetBase` = 0, `Marshaler` = 0, `MessageLite` = 0 and `DescriptorPool` = 0
are **artefacts of the search, not evidence of absence.** §16.15 read the
`JsonView` GetString helper directly in Ghidra, and that outranks this table.

**Trustworthy rows only:** bare identifiers (`JavelinGatewayService`,
`ReplicaChunk`, `InitializeReplicatedFields`) and content-type literals
(`application/json`, `application/x-protobuf`). Those alone carry the verdict.

`google::protobuf::Reflection` = 1 is a `GOOGLE_CHECK` assertion string, not
RTTI. **That single assert string was the entire evidentiary basis of FIND-2.**

#### Predictions — all recorded before the scan (CHARTER §4)

`P2_PROMPT.md`'s three predictions: **all falsified.**

| Source | Prediction | Outcome |
|---|---|---|
| P2_PROMPT 1 | `InternalAddGeneratedFile` has 20–100 callers, one per compiled `.proto`; total blob count exceeds the 10 RTTI types | **FALSIFIED.** 3 blobs total, 2 of them stock. At most 3 registration sites. |
| P2_PROMPT 2 | Response/result types present in the blobs though absent from RTTI | **FALSIFIED.** No Javelin descriptor exists in any form. |
| P2_PROMPT 3 | A `service JavelinGatewayService` block exists — "the single most valuable find P2 can make" | **FALSIFIED.** Zero service blocks in all 3 descriptors. |
| P2-A (runbook) | ≥1 blob recovered, FIND-2 holds | **Confirmed, but hollow** — holds literally, yields nothing on the world protocol. |
| P2-B | No Javelin service block | **CONFIRMED.** |
| P2-C | Packages are infrastructure, not javelin/world/character | **CONFIRMED.** |
| P2-D | JSON, not protobuf | **CONFIRMED.** `application/json` 236 vs `application/x-protobuf` 0. |
| P2-E | `InternalAddGeneratedFile` absent, `AddDescriptors`/`descriptor_table` present instead | **NOT RESOLVED** — see OI-P2-1. All three matched 0, but a non-virtual free function's name need not appear in the binary at all. The string test cannot answer this. |

#### OI-H2-3 — ANSWERED, and it is mundane

**The server→client schema is absent from RTTI because AWS SDK for C++ `XResult`
classes are non-polymorphic value types — no vtable, therefore no RTTI.**
`XRequest` derives from the polymorphic `AmazonSerializableWebServiceRequest`
and so does emit RTTI. "10 request types, no result types" is the expected shape
of the SDK, not evidence that responses are deserialized by some exotic path.

Corroborated by `application/json` = 236 against `application/x-protobuf` = 0,
and by §16.15 having already read Javelin-family fields coming out of the stock
`JsonView` GetString helper.

**Consequence:** OI-H2-3 does not transfer to another chunk as written. The
inbound Javelin schema is JSON and is recoverable two ways, both cheap and
neither requiring a running client:

1. **From P0's existing captures** — the auth-phase traffic is already decrypted
   plaintext JSON (§16.2–16.4, §16.9). The response schema can be read off it.
2. **From `.rdata` string constants** — AWS SDK JSON field names are `GetString`
   / `WithString` arguments, exactly as §16.15 recovered the `Token` fields.

#### What P2 unblocks, and what it redirects

**Track P retargets off protobuf entirely.** The world stream is **GridMate
`ReplicaChunk` marshalling** (`ReplicaChunk` 23, `InitializeReplicatedFields`
94, plus §10's `VTransformReplicaChunk` / `VTriggerAreaReplicaChunk` /
`ScriptComponentReplicaChunk`). **We have the source for that** — it is in the
Lumberyard fork at `7d4f1ee6` that already builds (§5, §7). This is CHARTER §2's
thesis paying off: the reference build is not merely the check on this layer, it
is the primary source for it, and it is readable with no capture and no client.

**This route is immune to the 31 Jan 2027 sunset** (§16.0). It should be
prioritised over anything capture-dependent.

**For S1a:** no protobuf send-side schema to emit. The Javelin surface is JSON
REST and is very likely the same auth-phase API P0 already decoded on TCP/443 —
the ten §17.5 type names are literal REST routes
(`PostGameWorldsWorldIdCharactersRequest` = `POST /game/worlds/{worldId}/characters`,
`DeleteGameCharactersCharacterIdRequest` = `DELETE /game/characters/{characterId}`,
plus `PatchCharacterRequest`, `GetLoginInfoRequest`, `ListWorldsRequest`).
**Not yet confirmed against P0's captured routes — see OI-P2-2.**

#### Instrument — `p2_scan.py`, validated before use (CHARTER §2/§4)

Scans `.rdata`/`.data` for the `FileDescriptorProto` artefact rather than for a
registration *function*, because `InternalAddGeneratedFile` is the proto2/early
API and protobuf ≥3.10 emits `internal::AddDescriptors(const DescriptorTable*)`
instead — the artefact is version-independent, the function is not. Recovers
each blob's exact size by walking its top-level fields, so it never needs the
caller's size constant.

| Control | Result |
|---|---|
| Synthetic Javelin-shaped descriptor (nested, `oneof`, enum, service block), butted against adjacent `.rdata` | 2/2, exact sizes without any size constant |
| 171 MB haystack, 6 real Google descriptors at known offsets | 6/6, exact VAs and sizes, 2 s |
| 40 MB adversarial noise with decoy `.proto` anchors | **0 false positives** |

Two defects were caught by these controls before the tool touched retail:
O(n²) extent recovery that hung on adversarial input, and 35,081 false positives
from bare `.proto` paths in strings tables (a path preceded by a byte that
happens to be its length is a valid name-only descriptor). Both fixed;
35,081 → 0 with no loss of recall.

**Instrument caps (CHARTER §4 — a tool's cap is part of the measurement):**
- **`::`-containing diagnostic strings are literal matches and miss mangled
  MSVC RTTI.** Do not read zeros in those rows as absence.
- **`map<>` fields render with unresolved value types.** Synthetic map-entry
  messages are suppressed but referring fields are not converted to `map<>`
  syntax. `fields.tsv` carries the correct types.
- Finds descriptors **as data**; does not prove any is *registered*. That is
  OI-P2-1.
- A compressed or obfuscated descriptor would be invisible. Nothing in §10
  suggests that, but absence of a hit is not proof of absence.

`p2_out/blobs/*.bin` are literal byte excerpts of Amazon's binary and are
**not committed** (CHARTER §3), same call as the `Bin64/` pin. The derived
`proto/`, `index.tsv`, `fields.tsv` and `report.md` are findings and are.

---

## §13 — correction row to append

| Old claim | Where | Correction |
|---|---|---|
| "**Protobuf choke point (FIND-2 / P2):** All 10 types go through AWS SDK model serialization… P2 should target the AWS SDK `SerializePayload` / `GetBody` path on these model types to locate the protobuf schema boundary." | §17.5 (H2, 2026-09-04) | **Wrong — there is no protobuf schema boundary on that path.** P2 scanned the whole binary and found 3 `FileDescriptorProto` blobs: two stock protobuf well-known types and one telemetry schema (`campfire_event_default.proto`). No Javelin descriptor, no `service` block, `application/x-protobuf` = 0 against `application/json` = 236. The AWS SDK path is **JSON**, consistent with §16.15 having read those fields out of the stock `JsonView` GetString helper. Protobuf in `NewWorld.exe` serves Campfire telemetry only. §17.9. |

---

## §15 — open items register updates

**Close:**

- **FIND-2** → **CLOSED 2026-09-04 by P2, negative.** The `FileDescriptorProto`
  blobs are real but carry no game protocol — one telemetry schema plus two
  stock well-known types. Protobuf hands over nothing about the world messages.
  §17.9.
- **OI-H2-3** → **ANSWERED 2026-09-04 by P2, and dissolved rather than
  transferred.** Response types are absent from RTTI because AWS SDK `XResult`
  classes are non-polymorphic (no vtable → no RTTI), not because responses are
  deserialized exotically. The inbound Javelin schema is JSON and is recoverable
  from P0's existing plaintext captures or from `.rdata` field-name constants.
  §17.9.

**Open:**

| ID | Item | Owner | Notes |
|---|---|---|---|
| **OI-P2-1** | **Registration mechanism unconfirmed.** The 3 blobs were found as data; nothing yet proves they are registered, or by what. `InternalAddGeneratedFile`, `AddDescriptors` and `descriptor_table` all matched 0 as strings, but a non-virtual free function's name need not appear in the binary — the string test cannot answer P2-E. | **Unowned, low priority.** | Resolved by XREF on the three blob VAs (`0x1486f5b60`, `0x1495ab7c0`, `0x1495b3330`) in the warm `nwly.gpr`. Whatever function references those pointers *is* the registration function, named or not; its size constants should read 1407 / 190 / 6028 as an independent check on the scanner. **Low priority because it cannot change P2's verdict** — no Javelin descriptor exists to register. Worth doing only to close P2-E honestly. |
| **OI-P2-2** | **Are the 10 §17.5 Javelin types the same REST calls P0 already decoded on TCP/443?** The names are literal REST routes and `application/json` = 236, so probably yes — but not checked. | **Unowned.** | If yes, §17.5's "world message layer" framing needs a §13 correction too, and Track P's inbound problem is already solved by P0's captures. Cheap: diff the 10 type names against the routes in `p0_cold`. §17.9. |

---

## Before closing (CHARTER §6.4) — router before ledger

1. Tick P2's row in `CHUNKS.md`, pointing at **§17.9**.
2. DONE banner on `P2_PROMPT.md`: *protobuf present, irrelevant to the world
   protocol; all three of this prompt's predictions falsified.*
3. **Strike through, do not delete** (CHARTER §5), in `P2_PROMPT.md`:
   - Predictions 1, 2 and 3 in the Predictions section
   - Step 1's premise that `InternalAddGeneratedFile` is the route
   - "these schemas are what Track P decodes and what S1a must speak"
   - Step 6's expectation that response types are in the blobs
4. Fold §17.9, the §13 correction row and the §15 updates into `STATE.md`.
5. Update the freshness header: date 2026-09-04, new commit, `## ` count
   **stays 20**, test number, correction count **28 → 29**.
