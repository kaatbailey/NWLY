# nwproto — Chunk index and prompts

Companion to `CHARTER.md` and `STATE.md`. This file holds the work breakdown and
the ready-to-paste prompt for each chunk.

> **Repair note — 2026-08-30. The exact failure this file's own closing section
> warns about, repeated.** T3 and T5 both completed on 2026-08-29 and both index
> rows were still sitting at `[ ]`, with T3 marked `← NEXT` and the Order section
> still reading "Next: T3 → T5" — while `STATE.md` carried both as complete (§12A,
> §12B). A session pasted this file alongside `STATE.md` would have received two
> contradictory accounts of where the project is, and the cheapest wrong move
> available was re-running a chunk that was already done. Changes: **T3 and T5
> ticked `[x]`** with pointers into STATE; **DONE banners added to both prompt
> bodies**, bodies kept verbatim; claims inside those prompts that their own chunk
> or T5 falsified marked **SUPERSEDED** inline; `T5_PROMPT.md` added to the
> standalone-prompt list; the T5-depends-on-T3 repair note marked resolved; the
> Track H note about H2 running "mostly blind" superseded (T5 landed, so H2's
> falsification check is armed); H1's signature-scan suggestion **promoted to a
> requirement**; P1's scope narrowed to what T5 did not already document; the
> Order section replaced (stale planning prose, no findings in it — same treatment
> and same rationale as `STATE.md` §1–§3 on 2026-08-29). One **proposal** added
> under Track S, explicitly marked as awaiting an owner decision and not acted on
> *(that proposal was subsequently **adopted** later the same day — see below)*.
>
> **Second amendment, same day — GATE-1 resolved by owner decision.** H3 removed
> from the critical path and ordered last; three chunks created (**P0** auth-phase
> decode, **S0** redirection feasibility, **S1a** DTLS server); S1 split into
> S1a/S1b; P1's dependency changed from H3 to "S1a or H3"; H3's index row and prompt
> re-banned­ered as LAST RESORT with a terminal-result bound; Order section rewritten
> around the no-EAC-first sequence. Reasoning is STATE §3; the work order is
> STATE §15. **No chunk was marked complete and no finding was altered — this is a
> sequencing change.**
>
> **No prose was deleted.** The only text overwritten in place is the six index-table
> status rows and the T3 prompt's `← NEXT` header — which is precisely what "tick the
> row, add a DONE banner" means, and none of it carried a finding. Everything else
> that changed is struck through with its replacement beside it, including the four
> paragraphs of the old Order section, quoted back verbatim.

> **Repair note — 2026-08-29.** This file was corrected alongside `STATE.md`.
> Changes: **T5's dependency list fixed** (it needs T3's retail capture, which was
> missing); the Standing environment notes filled in with real values; completed
> chunks marked DONE with pointers into STATE; three claims inside the T4 prompt
> marked SUPERSEDED per STATE §13; T3's scope narrowed to match the instrument
> that now exists; the suggested order rewritten. Completed prompts are kept
> verbatim as historical record — a DONE banner is added, the body is not deleted.

---

## How to run a chunk

1. Open a new session.
2. Paste, in this order: **`CHARTER.md`**, then **`STATE.md`**, then **the one
   chunk prompt** you are working on, then **the `FINDINGS` block from the chunk
   you just finished** if it is listed as an input.
3. Work the chunk. Do not start the next one.
4. At the end, the session writes a `FINDINGS` block in the format at the bottom
   of this file.
5. You fold the findings into `STATE.md` — adding, never deleting — and tick the
   chunk here.

**Never paste more than one chunk prompt.** A session that can see three chunks
will half-do all three and hand you back something none of them defined as done.

**Why prompts are short and the charter is long:** the charter is the part that
must survive; the prompt is disposable. If a future session only reads one
document, it should be the charter.

**Standalone prompt files.** Some chunks have a fuller ready-to-run prompt kept as
its own file (`T3_PROMPT.md`, `T4_PROMPT.md`, `T5_PROMPT.md`, `D2_PROMPT.md`).
Where one exists,
**that file is authoritative** and the section here is a summary. Paste the file,
not the summary.

---

## Chunk index

Status: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

### Track T — Transport. Identify how the client secures and frames network data.

|       | Chunk                                             | Depends on   | Deliverable                                                              |
| ----- | ------------------------------------------------- | ------------ | ------------------------------------------------------------------------ |
| `[x]` | **T1** Engine fingerprint (static)                | —            | **DONE 2026-08-29.** GridMate confirmed. STATE §10                        |
| `[x]` | **T2** Crypto-library fingerprint                 | —            | **DONE 2026-08-29.** OpenSSL 1.1.1k, static, `SSL_read`/`SSL_write`. STATE §10 |
| `[x]` | **T3** Transport recon (retail capture, no hooks) | —            | **DONE 2026-08-29.** UDP/DTLS 1.2 via `SecureSocketDriver`; P1–P4 confirmed; epoch-0 pcap saved. STATE §12A. Prompt: `T3_PROMPT.md` |
| `[x]` | **T4** Build the reference `Carrier` from the fork | —           | **DONE 2026-08-29.** Plaintext + DTLS both pass and captured. STATE §7–§9 |
| `[x]` | **T5** Reference vs retail handshake diff         | T1, **T3**, T4 | **DONE 2026-08-29. THE MILESTONE — the charter's core question is answered.** Stock GridMate `SecureSocketDriver`, zero catalogued exceptions; reference validated as an instrument. STATE §12B. Prompt: `T5_PROMPT.md` |

> **Track T is complete.** T1, T2, T3, T4, T5 all landed. What remains in the
> transport layer is Track H, which supplies the epoch-≥1 plaintext that T5's
> verdict licenses P-track to interpret.

> ~~**T5's dependency on T3 was missing from this table until 2026-08-29.** T5 diffs
> the reference epoch-0 handshake (T4, STATE §9) against the *retail* epoch-0
> handshake, and the only source of the latter is T3's capture. T5 cannot start
> before T3 lands.~~ **RESOLVED 2026-08-29** — the dependency was correct and was
> honoured: T3 ran first and produced `t3_handshake_epoch0.pcap`, which was T5's
> retail input. Kept as the record of a real near-miss in the work breakdown.

### Track H — Hooking. Get to plaintext, framed messages. Proven on the reference build first.

|       | Chunk                                          | Depends on | Deliverable                                                          |
| ----- | ---------------------------------------------- | ---------- | ------------------------------------------------------------------- |
| `[ ]` | **H1** Frida crypto hook on the reference build | T2, T4     | `SSL_read`/`SSL_write` plaintext logged from a target we control. **Now also: prove the signature scan here** — see the prompt |
| `[ ]` | **H2** Locate the dispatch point in retail (static) | T1, ~~(T5)~~ **T5 done** | Ghidra: the message-type switch or handler table. **Falsification check is now armed, not deferred** |
| `[~]` | **H3** Crypto/dispatch hook on retail           | H1, H2, T2 | **LAST RESORT — deliberately deprioritised 2026-08-30, not blocked.** Only if P0/S0/S1a/H2/H4 are exhausted. One attempt; EAC prevention is terminal. STATE §3, §15 |
| `[ ]` | **H4** The reflection reader (`SerializeContext`) | T1       | **Decision gate + prototype.** Only if the ABI proves traversable    |

> ~~**H2 can start now.** Its hard input is T1, which is complete. T5 is only needed
> for H2's *falsification* check at the end (does the xref chain resemble
> `Carrier::Receive` → `ReplicaManager`), so H2 can run mostly blind and be
> confirmed once T5 lands. It needs no login, no running client, and no live
> servers — which makes it the fallback if T3 stalls.~~
>
> **SUPERSEDED 2026-08-30 — T3 and T5 both landed.** H2 no longer runs blind and is
> no longer a fallback for a stalled T3. Both consequences are live:
> **(a)** the falsification check is now a real test with a known answer behind it —
> T5 proved the transport is stock GridMate `SecureSocketDriver` (STATE §12B), so an
> xref chain that does *not* resemble `Carrier::Receive` → `ReplicaManager` means the
> static analysis is wrong, no longer that T1 might be. **(b)** H2 remains the one
> H-track chunk needing no login, no running client, and no Proton — which is now an
> argument for sequencing it *first*, not a contingency. See the note under Order.

### Track P — Protocol. What the messages mean. Built on captures, not guesses.

|       | Chunk                                     | Depends on | Deliverable                                     |
| ----- | ----------------------------------------- | ---------- | ----------------------------------------------- |
| `[ ]` | **P0** Auth-phase decode (TCP/443)        | —          | **NEW 2026-08-30, unblocked, no EAC contact.** The keylog already decrypts this flow (§12A, test #41) and nobody has read it. Login → server list → session token → **the world-address handoff**, which S0 depends on |
| `[ ]` | **P1** Handshake sequence                 | ~~T5~~ **T5 done**, ~~H3~~ **S1a or H3** | The connect exchange, byte-documented. **Scope narrowed — the epoch-0 DTLS half is already byte-documented in STATE §12B; what remains is the GridMate `Carrier` handshake inside epoch ≥ 1.** Reachable from S1a's plaintext for the client→server half without H3 |
| `[ ]` | **P2** Message-type census                | ~~H3~~ **H2, or S1a, or FIND-2** | The dispatch table as a list of known types. **Dependency corrected 2026-08-30** — H2's static table and FIND-2's protobuf descriptors both reach this without H3 |
| `[ ]` | **P3** Position/movement message          | ~~H3~~ **S1a or H3**, P2 | The controlled-walk experiment, decoded. Outbound position messages arrive as plaintext at an S1a server; H3 only adds the inbound half |
| `[ ]` | **P4** Initial world-state sync           | **H3**, P2 | The login state dump. **Genuinely needs H3** — this one is server→client, the direction S1a cannot observe. Expect to construct rather than capture it |
| `[ ]` | **P5** Replica/chunk model                | T1, H4     | How replicated objects map to the wire          |

### Track S — Server. Speak back to the client.

|       | Chunk                                       | Depends on | Deliverable                          |
| ----- | ------------------------------------------- | ---------- | ------------------------------------ |
| `[ ]` | **S0** Redirection feasibility              | P0         | **NEW 2026-08-30, no EAC contact.** Can the client be pointed at a world server we run? Hosts/DNS on our own machine. Cheap, and everything below rests on it |
| `[ ]` | **S1a** DTLS server (epoch 0)               | T5         | **NEW 2026-08-30, unblocked, no EAC contact.** Fully specified by §12B. **The inversion: when the client handshakes with us we hold the session keys, so its messages arrive as plaintext on our socket** — this replaces H3 for the client→server half |
| `[!]` | **S1b** Carrier handshake (epoch ≥ 1)       | S1a, P1    | The GridMate `DefaultHandshake` / connection request-ack inside the encrypted channel |
| `[!]` | **S2** Stand a character in the world       | S1b, P4    | A character loads and renders         |
| `[!]` | **S3** Movement round-trips                 | S2, P3     | The client can move and see it persist |

> ~~**PROPOSAL — 2026-08-30, not acted on. Owner decision required; the index above is
> unchanged pending it.**~~ **ADOPTED 2026-08-30.** The proposal below argued for
> splitting S1 into an unblocked DTLS half and a blocked Carrier half. The GATE-1
> decision settled it: with H3 off the critical path, S1a is no longer a parallel
> nicety — **it is the primary route to client→server plaintext.** Rows created
> above. The counter-case recorded below (that it opens a fourth track and CHARTER
> §1's layering exists to stop server work outrunning protocol understanding) still
> stands and is answered thus: S1a builds only what T5 already *proved*, and it is
> the instrument by which protocol understanding is obtained rather than a guess
> that runs ahead of it. Original text kept:
>
> STATE §12B fully specifies the **DTLS layer** of a server, from source plus two
> captures: `DTLSv1_2_method` (pinned, not `DTLS_method`), single suite `0xC030`,
> `SSL_OP_NO_QUERY_MTU`, GridMate's own 20-byte HMAC-SHA1 cookie generated and
> verified **at the datagram layer before OpenSSL sees it**, a hand-built
> HelloVerifyRequest with `RecordHeader::m_version` hardcoded to `fe ff`, a
> HelloRequest sent once the cookie verifies with exponential backoff capped at
> 1000 ms, and a CertificateRequest that accepts an **empty** client Certificate.
> None of that needs H3. All of it is testable against the reference `Carrier`
> client we already build — which is CHARTER §4's "prove it on the reference build
> first" reaching S-track for the first time.
>
> What genuinely needs P1/H3 is the **GridMate `Carrier` handshake inside epoch 1**.
>
> Splitting **S1a** (DTLS server — unblocked, testable now against the reference
> client) from **S1b** (Carrier handshake — blocked on P1) would put real S-track
> work on the board in parallel with H-track, rather than holding the entire server
> behind a hook that has an unsolved Proton problem in front of it. The counter-case
> is that it opens a fourth active track and CHARTER §1's layering exists precisely
> to stop server work outrunning protocol understanding. Recorded here so the option
> is not lost; **do not create S1a/S1b rows without an explicit decision.**

### Track D — Sustaining.

|       | Chunk                                        | Depends on | Deliverable                             |
| ----- | -------------------------------------------- | ---------- | --------------------------------------- |
| `[ ]` | **D1** Signature-scan harness                | —          | Offsets survive a client patch. **Head start:** `pins/22469132/Bin64.sha256` already answers "which binaries did this patch touch" (STATE §5) |
| `[x]` | **D2** Client game-data extraction (`.datasheet`) | —      | **DONE 2026-08-29.** 2250 datasheets → JSON. STATE §11 |

### Order — where the project actually is

**Rewritten 2026-08-30.** The previous text ("Next: T3 → T5") described the
pre-T3 position and contained no findings, only stale planning — replaced on the
same rationale and with the same precedent as `STATE.md` §1–§3. It read, verbatim:

> ~~**T1, T2, T4 and D2 are complete.** The engine question is settled (GridMate), the
> crypto boundary is located (`SSL_read`/`SSL_write`, statically linked), the
> reference instrument is built and captured, and Track S has its content source.~~
>
> ~~**Next: T3 → T5.** T3 is the last input T5 needs. T5 is the milestone — it answers
> the charter's one-sentence question by diffing the retail epoch-0 handshake
> against the reference one.~~
>
> ~~**Then Track H opens.** H2 can in fact run in parallel with T3 (see the note
> above) and is the fallback if T3 is blocked on account or server availability.~~
>
> ~~D1 can start whenever; it has a free head start from the pin baseline.~~

**Track T is finished. T1, T2, T3, T4, T5 and D2 are all complete.** The engine
question is settled (GridMate, STATE §10), the crypto boundary is located
(`SSL_read`/`SSL_write`, statically linked, STATE §10), the reference instrument is
built and captured (STATE §7–§9), Track S has its content source (STATE §11), and
**the charter's core question is answered**: retail transport is structurally stock
GridMate `SecureSocketDriver` with zero catalogued exceptions, and the reference
build is a valid instrument for it (STATE §12B).

**Track H is no longer the whole front.** GATE-1 resolved 2026-08-30 (STATE §3,
§15): **do everything reachable without contacting EAC first; H3 is a last resort.**
Not because H3 is off-charter — reading plaintext your own client decrypted is
reading your own data — but because injection into an EAC-protected process risks
the account everything else depends on, and working directly in front of a detection
system watching for exactly that is poor practice. If H3 is ever attempted it is
attempted **once**; EAC preventing the hook is a **terminal result**, and any step
aimed at surviving detection is circumvention, off-charter under §3, and does not
get pursued or recorded.

**The order, none of items 1–7 contacting a running retail client:**

1. **H2** — static Ghidra. Scope it **ambitiously**: with H3 off the critical path
   this is a primary source of protocol structure, not just a hook-targeting step.
2. **P2 / FIND-2** — protobuf `FileDescriptorProto` extraction. Possibly schemas
   for free, from the binary, with no capture at all.
3. **P0** — auth-phase decode. Already decrypts; never read. Yields the
   world-address handoff.
4. **S0** — redirection feasibility. Cheap, and S1a rests on it.
5. **S1a** — the DTLS server. **The inversion:** the client handshakes with us, we
   hold the keys, its messages arrive as plaintext on our socket.
6. **H1** — reference-build hook and signature scan. Our binary, and the last free
   oracle for the scan.
7. **H4** — reflection-reader decision gate. Static, independent, a "no" is as
   useful as a "yes".
8. **H3** — last resort only.

**Start with H2 or P0.** H2 needs nothing and no client. P0 needs only the keylog
capture you already have. Neither depends on the other.

**What this order does not yield** is the server→client direction in captured form.
Items 1–7 give the client's outbound messages plus whatever comes out of the binary;
the inbound half is what S-track must construct regardless, with H2 and FIND-2 as
the substitute for observing it.

**D1 can start whenever**; it has a free head start from the `pins/22469132/Bin64.sha256`
baseline (STATE §5), and it earns its keep the moment any offset is hardcoded.

**Open items now live in `STATE.md`'s register, per CHARTER §6.6** — including the
H3 gate, the `decode_carrier.py` ChangeCipherSpec gap, and the unused auth-phase
decryption. Do not track them here; this file routes chunks, it does not hold state.

> **Correction, 2026-08-30.** A paragraph here previously described `SSLKEYLOGFILE`
> as an unexploited opportunity that "no chunk owns." That was wrong and it was
> written by a session reasoning from its own inference rather than from a document
> — the exact failure CHARTER §6.3 now names. The keylog was a scoped T3 recon item;
> it ran on 2026-08-29, produced a split result (auth decrypts, world stream does
> not), received its falsification check, and is recorded in STATE §12A, test #41,
> and a §13 correction row. What is genuinely open is narrower: **nobody has decoded
> the auth flow's contents.** That is now an entry in the STATE register, not a note
> here.

---

## Shared preamble

Every prompt below assumes this, and every prompt written later must include it:

> You have been given `CHARTER.md` and `STATE.md`. Work **only** the chunk below.
> If you find something that belongs to another chunk, record it in FINDINGS under
> "Noticed, out of scope" and do not act on it.
>
> Do not rewrite `CHARTER.md`. Do not delete anything from `STATE.md`.
>
> Charter §3 rules out anti-cheat work absolutely. If a line of inquiry only pays
> off against an integrity or attestation system, stop and record it as
> off-charter in FINDINGS — do not pursue it.
>
> Before doing anything on the retail client: prove the technique on the reference
> build first, state the check that would prove your result wrong, and run it.
>
> **The owner runs every command.** Give exact commands with real paths. Note the
> exact client build under test in every capture — offsets and possibly the
> protocol move between builds.
>
> **Keep the loop tight.** Predict → run **one** command → read the exact error →
> fix → re-probe. Do not reason from memory across several turns without asking
> for something to be run. This is what took T4 from "provision an isolated
> toolchain" to "two flags and a five-line patch" in about twenty minutes.

### Standing environment notes

Filled 2026-08-29. Full detail in STATE §5; this is the working subset.

- **Client build under test:** New World: Aeternum, Steam appid **1063730**,
  **buildid 22469132**, `LastUpdated` 2026-08-27. Installed at
  `/home/kaatlev/.local/share/Steam/steamapps/common/New World`
  (`~/.steam/steam/steamapps/...` is a symlink to the same place).
  **Pinned** at `~/Documents/nwly-pin/22469132/` — depot manifests plus a byte
  copy of `Bin64/` with a 22-file sha256 baseline.
- **Client runs under Proton** (`steamapps/compatdata/1063730`). The retail client
  is a PE process under Wine on this host. Neutral for packet capture; a real
  complication for Frida in H1/H3.
- **Reference-build tree:** `~/Documents/lumberyard`, branch `master`. GridMate at
  `dev/Code/Framework/GridMate/`, AzCore at `dev/Code/Framework/AzCore/`.
  **The tree is patched** — `RTTI/TypeInfo.h` reads `false_v<>` where Amazon's
  original reads `false_v<T>`, committed. The pin `413ecaf24d7a...` therefore does
  **not** describe the tree that builds. See STATE §13.
- **Build recipe:** `clang++ -std=c++17 -include utility -fdelayed-template-parsing -w`
  with `-I AzCore -I AzCore/Platform/Linux`, run from `dev/Code/Framework`. GridMate
  adds `-I GridMate -I GridMate/Platform/Linux -DDTLS1_RT_HEARTBEAT=24`.
  Scripts: `build_gridmate.sh` (build), `triage.sh` (bulk compile triage),
  `CMakeLists.txt` (CLion/clangd path).
- **Capture interface:** `enp2s0`, host `192.168.1.33`, gateway `192.168.1.1`.
  Not `-i any` — that yields Linux-cooked (SLL) framing and breaks link-layer
  parity with the T4 loopback captures.
- **Ghidra project:** not yet created. Run the PE RTTI analyzer on first import —
  RTTI survived in `NewWorld.exe` (STATE §10), so it recovers the `ReplicaChunk`
  class tree cheaply. This is H2's starting point.
- **Frida vs compiled hook:** Frida for all exploration (reload JS without
  restarting). Move to a MinHook/Detours DLL writing to a named pipe only once the
  hook target is known and stable. **Note:** retail runs under Proton, so H1/H3
  must solve attaching to a PE process inside Wine.
- **Never parse in the hook.** Log raw bytes + timestamp + direction + conn-id to a
  binary file; parse offline. You will re-parse the same capture many times.
- **Shell gotchas:** fish. `fd` is not installed — use `find`. `grep -c` exits 1 on
  a zero count, so a successful "absent" check looks like an error. fish aborts a
  failed glob before evaluating the `or`, so use `find` for existence checks.

---

# Track T prompts

## T1 — Engine fingerprint (static) ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §10. Do not re-run.**
> Verdict: **GridMate**, decisively — `TransportLayerGridMate` is New World's own
> wrapper class, so GridMate is the live network layer. 43 GridMate-family hits.
> O3DE `AzNetworking` absent; the single O3DE-looking hit was the gameplay struct
> `TransformLinkConnectionData`, exactly the generic-name trap this prompt warned
> about. Crypto fell out of the same scan (most of T2). Protobuf present in
> `NewWorld.exe` — flagged for P2. RTTI survived.
> Prompt kept below as historical record.

**Deliverable is a document**, not code and not a hook.

**Why this is first.** Everything downstream assumes an engine. GridMate means a
`Carrier`/`ReplicaManager`/DTLS shape; O3DE `AzNetworking` means a different one;
a full rewrite means neither, and the reference-build strategy narrows to "shared
AZ DNA only." The wrong assumption here wastes every later chunk.

**Scope.** Static analysis of the client executable and its DLLs in Ghidra.
String-search for the three fingerprint families and report which is present:

- **GridMate:** `GridMate`, `Carrier`, `CarrierThread`, `SocketDriver`,
  `SecureSocketDriver`, `ReplicaMgr`, `ReplicaChunk`, `ReplicaChunkDescriptor`,
  `DataSet`, `Marshaler`, `DefaultHandshake`, `DefaultTrafficControl`,
  `GridSession`.
- **O3DE-era (GridMate replaced):** `AzNetworking`, `NetworkEntity`,
  `NetBindComponent`, `IConnectionListener`, `MultiplayerComponent`,
  `NetworkInput`, `ConnectionData`.
- **AZ baseline (how much LY DNA survives):** `AZ::`, `AzCore`, `AzFramework`,
  `SerializeContext`, `BehaviorContext`, `ComponentApplication`, `AZ_CRC`, `EBus`.
- **Third-party netcode / serialization:** `enet`, `RakNet`, `yojimbo`,
  `google::protobuf`, `flatbuffers`, `msgpack`.

**Method.**
- Run the Windows PE RTTI analyzer first. If RTTI survived, search mangled names
  `.?AV...@GridMate@@` — a single hit like `.?AVCarrier@GridMate@@` closes this
  chunk on its own.
- Check the import table: `sendto`/`recvfrom`/`WSASendTo` → UDP datagram design
  (GridMate shape); `send`/`recv` only → TCP stream (not GridMate's SocketDriver).
- If `google::protobuf` appears, note it loudly — the embedded `FileDescriptorProto`
  blobs may hand over the entire message schema (P2 becomes far cheaper). Do not
  extract them here; just flag it.

**Definition of done.** A document naming the engine family with the specific
strings/RTTI symbols that prove it, the transport shape from the import table, and
a flag on whether protobuf/flatbuffers descriptors are present.

**Falsification.** Predict GridMate before searching (the 2016 LY origin says so),
and say what a rewrite would look like instead — absence of every GridMate string
*and* presence of the O3DE set. "Some AZ strings present" does not prove GridMate;
those survive a rewrite.

**Non-goals.** No hooking. No dynamic analysis. No touching the crypto layer yet.

---

## T2 — Crypto-library fingerprint ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §10. Do not re-run.**
> Verdict: **OpenSSL 1.1.1k (25 Mar 2021), statically linked.** Plaintext boundary
> is `SSL_read` / `SSL_write`; `dtls1_` and `DTLSv1` confirm DTLS. Static linkage
> is the harder of the two outcomes: **no DLL proxying is possible**, so the
> H-track must use an inline hook located by signature and patched in memory.
> The linkage claim now rests on a positive 22-file `Bin64/` inventory, not on an
> empty `find` (STATE §10, test #29).
> Prompt kept below as historical record.

**Deliverable is a document.** Where is the plaintext boundary, and what function
sits on it?

**Why.** Charter §4: hook above the crypto, never at the socket. This chunk finds
the hook target. GridMate's `SecureSocketDriver` wraps datagrams in OpenSSL DTLS;
a rewrite may use mbedTLS or Windows CNG instead.

**Scope.** In Ghidra, look for:
- **OpenSSL:** strings `"SSL routines"`, `"OpenSSL"`, `EVP_DecryptUpdate`,
  `SSL_read`, `SSL_write`, `DTLSv1`, `dtls1_`.
- **mbedTLS:** `mbedtls_ssl_read`, `mbedtls_ssl_write`, mbedTLS version strings.
- **Windows CNG:** imports of `bcrypt.dll` / `ncrypt.dll` (`BCryptDecrypt`,
  `BCryptEncrypt`) — attractive because these are system DLLs, always dynamically
  linked, hookable even when everything else is static.
- Determine **static vs dynamic linking** for whichever it is. A real `libssl`/
  `libcrypto` DLL in the install → DLL proxying is possible (H-track). Statically
  linked into the main exe → inline hook by signature only.

**Definition of done.** The crypto library named, the specific plaintext-boundary
function identified (`SSL_read`/`SSL_write` or equivalent), and static-vs-dynamic
linkage stated for it.

**Falsification.** If no known crypto library's fingerprint is present, that is a
finding, not a dead end — say so and note whether the T3 entropy profile shows
encryption at all. A low-entropy stream would mean there is no crypto layer to
hook above, which changes the whole H-track.

**Non-goals.** No hooking yet. Do not locate anti-cheat crypto — charter §3.

---

## T3 — Transport recon (retail capture, no hooks) ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §12A. Do not re-run.**
> Verdict: the world connection is **UDP/DTLS 1.2 via `SecureSocketDriver`**, not
> `StreamSecureSocketDriver`/TCP-TLS — settling the STATE §7 question. Flow
> `192.168.1.33:27001 ↔ 52.223.16.88:54888` (AWS). Predictions 1–4 all confirmed;
> **prediction 4 held**, the retail ClientHello offers exactly one real suite
> `0xC030` plus `0x00FF` (SCSV, not a cipher). `decode_carrier.py` handled retail
> **unmodified** (test #40 — the predicted loopback/offset break did not occur).
> Epoch-0 handshake saved as `t3_handshake_epoch0.pcap`, which became T5's retail
> input. **Two claims below are marked SUPERSEDED inline** — both were corrected by
> T5, and both are in STATE §13. Prompt kept as historical record.

> **The full ready-to-run prompt is `T3_PROMPT.md`. Paste that file, not this
> summary.** What follows is the scope in brief, plus the reasons this chunk is
> narrower than it was originally written.

**Deliverable: the retail transport profile, and the retail epoch-0 handshake as
its own artefact.** That artefact is T5's input.

**Scope is smaller than the original T3 text.** The original assumed recon from
zero — entropy profiling, "is there crypto at all." That predates STATE §9 and
`decode_carrier.py`, which already recognises both Carrier framing and DTLS
records. So the primary analysis is **point the existing instrument at retail
traffic**; entropy profiling is the fallback if it does not parse.

**It also settles a STATE §7 question:** GridMate ships two secure drivers —
`SecureSocketDriver` (UDP/DTLS) and `StreamSecureSocketDriver` (TCP/TLS). Which
one carries the persistent world connection decides the shape of every P-track
chunk, and a capture answers it with no hooks.

**Predictions to record before capturing (CHARTER §4):**

1. Game stream is **UDP**; auth and server-list are a separate TCP/443 phase.
2. UDP payloads parse as **DTLS 1.2 records**, `decode_carrier.py` unmodified.
3. ~~Opening exchange is ClientHello (`fe fd`) → HelloVerifyRequest (`fe ff`) →
   ClientHello with cookie echoed. **The 1.0 HVR is correct**, RFC 6347 §4.2.1 —
   not a downgrade, do not chase it.~~
   **CONFIRMED but INCOMPLETE in two ways — SUPERSEDED by T5, STATE §13.**
   (a) The RFC explanation is permitted but is not the actual cause: GridMate
   **hardcodes** `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) in its
   hand-packed records (`SecureSocketDriver.cpp:308`, `:312`, `:343`). That moves
   `fe ff` out of the "library/RFC default" bucket and into the **GridMate-controlled**
   bucket, where it matches retail exactly. Diagnostic value: **every `fe ff` record
   in a capture is a GridMate hand-pack**, and there are exactly two per handshake
   (HelloVerifyRequest, HelloRequest). The advice not to chase it still stands.
   (b) The exchange does not stop there. The real sequence, identical on retail and
   reference, is `CH(seq0, no cookie) → HVR(seq0) → CH(seq1, cookie=20) →
   HelloRequest(seq0) → CH(seq0, no cookie) → ServerHello…`. **Three ClientHellos,
   not two**, and the handshake OpenSSL actually completes carries **no cookie at
   all**.
4. **The retail ClientHello advertises exactly one cipher suite, `0xC030`**
   (`ECDHE-RSA-AES256-GCM-SHA384`), because GridMate hardcodes it at
   `SecureSocketDriver.cpp:1494`.

**Prediction 4 is the load-bearing one.** A single-suite ClientHello matching the
reference is close to conclusive for a stock-ish GridMate transport, and it is
readable at epoch 0 without a hook. A normal multi-suite list means Amazon
replaced the `SSL_CTX` setup, and T5's verdict needs qualifying even though T1
said GridMate.

**Two procedural details that decide whether the chunk succeeds:**

- **Start the capture before the client connects.** Test #21 only caught the
  cookie exchange because of this. A mid-session capture is all epoch ≥ 1
  ciphertext and useless for T5.
- **Disable voice chat in the client first.** `vivoxsdk.dll` (STATE §10) opens its
  own UDP media flow that resembles a game stream and parses as neither DTLS nor
  Carrier. Eliminate it at the source rather than filtering it later.

**Expect three or four UDP conversations, not one:** the game stream, Vivox (if not
disabled), EOSSDK/EAC, and Steam background traffic. Attribute them with
`ss -tunp` during the session rather than guessing from traffic shape.

**Definition of done.** Transport named (UDP vs TCP) with ports and endpoints;
auth phase separated from the game stream; predictions 1–4 each confirmed or
falsified with command output as evidence; the epoch-0 handshake saved as its own
pcap; size/timing profile for a stand-still window and a walking window; and
whether `decode_carrier.py` handled retail unmodified.

**Non-goals.** No hooks, no injection, no Frida. No decryption attempts — epoch ≥ 1
is ciphertext and there is nothing there without session keys (STATE §9). No
message-body decoding (P-track). **EAC/EOSSDK traffic will be in the capture** —
identify its endpoints so they can be excluded, record nothing further about it.
Charter §3. Do not modify traffic.

---

## T4 — Build the reference `Carrier` from the fork ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §7, §8, §9. Do not re-run.**
> Both plaintext and DTLS sessions pass, are captured, and are decoded. 168/202
> AzCore TUs, 41/41 GridMate TUs. Reproducible from a wiped `build/` (test #20).
> **Three claims in the prompt below turned out wrong and are marked SUPERSEDED
> inline — read those before reusing any of this.** Prompt kept as historical
> record and because the Path A/B reasoning is still the right shape for a rebuild.

**Deliverable:** two GridMate `Carrier`s connecting locally in a process we
control, captured both plaintext and DTLS-secured. This is the reference
instrument the whole project leans on (CHARTER §2).

### What is already known from the tree (do not re-derive — see STATE §7)

- **Dependency surface is clean.** GridMate includes only `<AzCore/...>` and the
  standard library — nothing from other frameworks. The carve-out is: compile
  **AzCore** + **GridMate**, ignore the rest of the tree. *(Confirmed by build —
  every AzCore failure was a missing 3rdParty header, none on GridMate's surface.)*
- ~~**C++ standard is C++14** (`-std=c++1y` in `compile_settings_clang.py`).~~
  **SUPERSEDED — STATE §13.** The source needs **C++17**. `Math/Crc.inl:114` uses
  an `auto` template parameter and `-std=c++14` is a hard error with no rescuing
  flag. The Waf setting is what the 2019 clang was told, not what the code needs.
- ~~**No hard clang version gate.** Try system clang 22 with `-std=c++14 -Wno-error`.
  Provision `/opt/llvm14` ONLY on real compile errors from removed C++14-era
  features.~~ **PARTLY SUPERSEDED.** The no-gate observation holds and
  `/opt/llvm14` was correctly rejected — but the working invocation is
  **`-std=c++17 -include utility -fdelayed-template-parsing -w`**, verified on
  clang 18 and clang 22. Do not disturb the system clang PZMapMaker uses.
- **Crypto is OpenSSL DTLS, confirmed in source.** `SecureSocketDriver.cpp`
  includes `<openssl/ssl.h>` etc. and uses `DTLS1_VERSION`, `DTLS1_RT_HEADER_LENGTH`
  (13), `DTLS1_HM_HEADER_LENGTH` (12), `SSL3_MT_CLIENT_HELLO`. Link `libssl` +
  `libcrypto`. The `RecordHeader` / `HandshakeHeader` structs in that file are the
  DTLS wire framing and become T5's reference layout — read them, do not reverse
  them. **Add `-DDTLS1_RT_HEARTBEAT=24`** — the constant was removed from OpenSSL 3
  after Heartbleed and `SecureSocketDriver.cpp:416` still uses it (STATE §7, §13).
- **Platform-header include paths** (the thing bypassing Waf usually breaks) are
  known. Waf prepends the `Platform/<OS>/` dir to the include search path. For
  Linux, add these `-I` dirs (fork at `/home/kaatlev/Documents/lumberyard`):
  - `dev/Code/Framework/AzCore/Platform/Linux`
  - `dev/Code/Framework/GridMate/Tests/Platform/Linux` (only if using the harness)
  - **`Platform/Common/` must exist in the checkout** — a sparse checkout that
    omits it fails with a confusing error pointing at the *Linux* header instead.
- **Test certs exist:** `dev/Code/Framework/GridMate/Tests/Certificates.cpp` defines
  `g_untrustedCertPEM` / `g_untrustedPrivateKeyPEM`. Compile that file to resolve the
  `extern`s DTLS needs.
- ~~**The secure test path was likely never run on Linux.** You must define
  `-DAZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER=1` and should EXPECT to shake
  out Linux-specific bugs on the DTLS path.~~ **SUPERSEDED — STATE §13, test #17.**
  The trait does need defining, but **DTLS passed on the first run**, on both clang
  majors, identical to plaintext. Zero Linux-path bugs. The trait gates the *test
  harness*, not the driver, and the driver sits on `SocketDriverCommon` which the
  plaintext path exercises constantly. *Untested is not broken* — do not budget
  time against this.
- **The fork tree is patched.** `RTTI/TypeInfo.h` reads `false_v<>`, committed.
  A rebuild from bare `413ecaf` is **not** what was tested. STATE §13.

### Approach — two paths, attempt B first

**Path B (primary): minimal `main()`, skip the test harness.** `Tests/Carrier.cpp`
pulls in `Tests.h`, which drags in AzCore UnitTest, Driller, Streamer, and the
Session layer — more than CHARTER §2 needs. Instead, write ~80 lines that include
only `Carrier.h`, `SocketDriver.h`, `SecureSocketDriver.h`, `DefaultHandshake.h`,
compile `Certificates.cpp` alongside, and stand up two `Carrier`s that connect and
exchange one message. Use `Tests/Carrier.cpp` and its `SocketDriverProvider` /
`SecureDriverProvider` classes as the *reference pattern* for how a Carrier is
constructed and driven — copy the setup, drop the framework.

**Path A (fallback): full harness.** Only if you later need Amazon's session-level
tests. Satisfy the whole `Tests.h` chain plus both Linux `-I` dirs above.

### Steps

1. **Toolchain probe.** Compile one AzCore `.cpp` (a Math or Memory unit) with the
   recipe above. *(Result: clean on clang 18 and 22. `/opt/llvm14` not needed.)*
2. **AzCore static lib.** Compile the AzCore subset GridMate names into
   `libazcore.a`. Link pthreads. *(Result: 168/202, `libazcore.a` 31M. Use
   `triage.sh` to group failures by error kind rather than investigating each.)*
3. **GridMate static lib.** Compile GridMate against the AzCore headers into
   `libgridmate.a`. *(Result: 41/41, `libgridmate.a` 4.9M.)*
4. **Plaintext Carrier test (the milestone).** Path B `main()`, plain
   `SocketDriver`, two Carriers on localhost, exchange a message, capture the wire.
   **Two runtime traps live here, neither a compile error, both segfault a binary
   that links fine:** `OSAllocator` must be created before `SystemAllocator`, and
   EBus handlers must be destroyed before `GridMateDestroy`. STATE §7.
5. **DTLS Carrier test.** Define the secure trait, swap in `SecureSocketDriver`
   with `Certificates.cpp`, link OpenSSL. **Then search the capture for the literal
   payload string** — "PASS" only proves a session was established, not that
   anything was encrypted. STATE §9.

### Definition of done

A reproducible local GridMate session; a captured plaintext handshake; the
`Carrier` packet header layout read out of `Carrier.cpp`/`Carrier.h` and confirmed
against the plaintext capture; and the DTLS path either working or its Linux
failure characterised exactly.

### Falsification

The header you read from `Carrier.h` must match the bytes on the wire in the
plaintext capture. Predict the first few header bytes before capturing. If they
don't match, either the build config differs from what you read or the fork
diverged — resolve that before T5 relies on this layout.

### Non-goals

Not the retail client. Do not tune anything to match retail — this is the
*known-good*, established on its own terms. No hooking yet (that's H1).

### FINDINGS to record

Fork commit under test; whether clang 22 sufficed or `/opt/llvm14` was needed; the
exact `-I` and `-l` flags that produced a working build; the Carrier header layout;
and the state of the DTLS-on-Linux path. Fold into STATE §5 and §7.

---

## T5 — Reference vs retail handshake diff ✅ DONE 2026-08-29 — THE MILESTONE

> **COMPLETE. Findings in STATE §12B. Do not re-run.**
> **The full ready-to-run prompt is `T5_PROMPT.md`** — richer than this summary,
> and it is the one that was actually executed.
> **Verdict: retail transport is structurally stock GridMate `SecureSocketDriver`
> with zero catalogued exceptions.** Every handshake difference between retail
> (buildid 22469132) and the reference (`7d4f1ee6`) is OpenSSL 1.1.1k-vs-3.6.4
> noise in fields `SecureSocketDriver.cpp` does not set. **Mutual auth is stock
> GridMate, not Amazon-added**, and rests on an inverted branch at `:1525` that
> *assigns* `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` instead of OR-ing it. **The reference
> build is a valid instrument for retail's transport**, epoch 0 only. P1–P4 all
> confirmed. Offline throughout: two pcaps and one source file, no client launch,
> no hooks, no decryption — CHARTER §3 satisfied.
> **Outcome 1 of the three in "Definition of done" below is the one obtained.**
> Strongest single result: a **byte-identical 25-byte HelloRequest** across retail
> and reference, a GridMate hand-pack that no OpenSSL version difference could
> produce. Four beliefs were overturned and are in STATE §13. Prompt kept as
> historical record.

**This is the chunk that answers the charter's core question.** Depends on T1
(done), ~~**T3** (the retail capture — not yet run)~~ **T3 (done 2026-08-29 —
`t3_handshake_epoch0.pcap` was the retail input)**, and T4 (done).

**Both inputs are specific artefacts, not vibes:**

- **Reference:** the epoch-0 handshake from T4's `--secure` capture, documented in
  STATE §9 — ClientHello (`fe fd`) / HelloVerifyRequest (`fe ff`) / ClientHello
  with a 20-byte cookie echoed.
- **Retail:** the epoch-0 pcap T3 saves as its own artefact.

**Scope.** Diff structurally: does the retail client's pre-encryption handshake
line up with GridMate's `DefaultHandshake` + `Carrier` header — same fields in the
same order, even if magic values or field widths differ?

**Filter the `'G'` wakeup byte first.** A 1-byte `0x47` datagram addressed to the
socket's own port is `AZ_SOCKET_WAKEUP_MSG_VALUE`, not protocol, and roughly a
third of reference loopback frames are these (STATE §8). Diffing without filtering
them invents a phantom message type.

**T3's cipher-suite result largely pre-answers this.** If T3 found a single-suite
ClientHello offering `0xC030`, the structural match is close to established before
the diff starts, and T5 becomes confirmation plus field-level documentation.

**Definition of done.** One of:
- **Structural match** → the client is GridMate or a close fork; the `Carrier`
  header layout is now the retail protocol's header layout, documented for free.
  **← THIS IS THE OUTCOME OBTAINED, 2026-08-29. STATE §12B.**
- **No match, O3DE strings present** → an `AzNetworking` rewrite. *Note: T1 already
  ruled this out, so this outcome would mean T1 was wrong — investigate the
  contradiction rather than accepting it.* **Did not occur.**
- **No match, neither** → a bespoke protocol; the reference build degrades to "AZ
  reflection may still help" and P-track is fully empirical. **Did not occur.**

**Caveat on the match, carried forward (STATE §12B).** It is proven for **epoch 0**,
the cleartext handshake. Epoch ≥ 1 Carrier framing inside DTLS is proven on the
reference and **inferred** for retail; H3's plaintext is what promotes it. Content
(certificate sizes 958 vs 1380, cookie values, randoms) is per-deployment and
per-connection — do not treat any observed value as constant. Fragmentation
differences between the two captures are PMTU-dependent, not protocol-dependent.

**Falsification.** T1 said GridMate, which predicts a structural match. **If the
handshakes don't line up at all, one of T1 or T5 is wrong — find out which before
building on either.** Do not quietly prefer the newer result.

**Non-goals.** No decoding of message *bodies* yet — that's P-track. Handshake
framing only.

---

# Track H prompts

## H1 — Frida crypto hook on the reference build

Depends on T2 (target function, done) and T4 (a build we control, done). **Prove
the hook on the reference build before H3 points it at retail.**

**Scope.** `Interceptor.attach` on `SSL_read`/`SSL_write` in the reference
`Carrier` process. Log the plaintext buffer, direction, timestamp, and connection
id to a binary file. Confirm the logged plaintext matches the
`SecureSocketDriver`-disabled capture from T4.

**Two environment facts that shape this chunk:**

- The reference build is a **native Linux binary** with full symbols — Frida
  attaches trivially. Retail (H3) is a **PE process under Proton/Wine**, which is
  a different and harder problem. Solve it in H3, not here, but know it is coming.
- Retail's OpenSSL is **statically linked** (STATE §10), so H3 will need a
  signature scan rather than a symbol lookup. ~~Consider proving the
  signature-scanning approach here too, where a known-good answer exists to check
  it against.~~ **AMENDED 2026-08-30 — this is now a requirement, not a
  suggestion.** Two things changed it. First, T5 established that the reference is
  a valid instrument for retail's transport (STATE §12B), so a technique proven
  here can be trusted to transfer — which is the whole reason to prove it here.
  Second, and more practically: **H1 is the last chunk in which a free oracle
  exists.** The reference binary has full symbols, so `Module.findExportByName`
  gives the known-good address that the signature scan must independently
  reproduce. In H3 there is no symbol to check the scan against, so a scan that is
  subtly wrong there is indistinguishable from "the client didn't send it" —
  CHARTER §4's instrument-cap rule, in the specific. Build the scanner here, or
  build it blind later.

**Definition of done.** A Frida script that captures the full bidirectional
plaintext stream from the reference build, verified against the known plaintext.
This script is the template H3 adapts for retail. **Plus (added 2026-08-30): a
signature scan that locates `SSL_read`/`SSL_write` in the reference binary and is
verified to land on the same addresses the symbol table gives.**

**Falsification.** The plaintext you log with `SecureSocketDriver` enabled must
match the cleartext capture with it disabled. If it doesn't, the hook is on the
wrong function or after the wrong transform.

**Non-goals.** Do not parse in the hook (charter §4). Do not touch retail.

---

## H2 — Locate the dispatch point in retail (static)

Depends on T1 (done). ~~T5 is needed only for the falsification check at the end —
**this chunk can start now**, and is the fallback if T3 is blocked.~~
**AMENDED 2026-08-30 — T5 is done (STATE §12B), so the falsification check below is
armed rather than deferred, and this chunk is no longer a fallback for anything.**
It is static, needs no login, no running client and no Proton, which now makes it
the natural first H-track chunk rather than a contingency. **Static only** — no
execution, no login, no running client.

**Scope.** In Ghidra, work forward from `recvfrom`/`WSARecvFrom`: xref the call
site (the `SocketDriver::Receive` equivalent), follow the output buffer through
decrypt → header parse → reliability/reassembly → **dispatch**. The dispatch
function is the target: either a large `switch` on a message-type id or an indexed
jump through a function-pointer table. That table is the message-handler map.

**Start with the RTTI analyzer.** RTTI survived in `NewWorld.exe` (STATE §10) —
mangled-name fragments like `UEAAXPEAVReplicaChunkBase` are present. Ghidra's PE
RTTI analyzer recovers the `ReplicaChunk` class tree, which is a far cheaper entry
point than following xrefs blind.

**Two modules to know about before following xrefs** (STATE §10): `vivoxsdk.dll`
has its own network stack, and `libcds-amd64-vcv141.dll` is unidentified. Neither
is the game transport.

**Definition of done.** The dispatch function's address (as a signature, not a raw
offset — charter §4), and, if it's a table, the table extracted as a list of
(type-id → handler-address) pairs. Each entry is a message type that exists.

**Falsification.** ~~If GridMate (T1 says so, T5 will confirm), the path should pass
through `Carrier::Receive` and a `ReplicaManager` receive entry. If the xref chain
doesn't resemble that, revisit whether T1's verdict was right — do not just accept
the mismatch.~~
**AMENDED 2026-08-30 — T5 confirmed it.** The path should pass through
`Carrier::Receive` and a `ReplicaManager` receive entry. **The "maybe T1 was wrong"
branch is closed:** T1 said GridMate from strings and RTTI, and T5 then proved the
transport is stock GridMate `SecureSocketDriver` on the wire, byte-for-byte against
a build we control (STATE §12B). Two independent methods agree. So an xref chain
that does not resemble that shape means **the static analysis is wrong** — wrong
`recvfrom` call site, wrong module, or the chain lost in a thunk — not that the
engine verdict is in doubt. Do not accept the mismatch, and do not reopen T1 to
explain it.

**Non-goals.** No hooking. No decoding handler bodies — P2 does that with captures.
Nothing touching EAC, which lives in `<install>/EasyAntiCheat/` (charter §3).

---

## H3 — Crypto/dispatch hook on retail ⏸ LAST RESORT

> **DEPRIORITISED 2026-08-30 by owner decision (GATE-1, STATE §3 §15). Not blocked
> — deliberately ordered last.** Do not run this until H2, P2/FIND-2, P0, S0, S1a,
> H1 and H4 are exhausted. Two reasons, neither being that H3 is off-charter:
> **(a)** injection into an EAC-protected process is a well-known ban trigger
> regardless of intent, and the account is load-bearing for auth captures, world
> captures and any handshake testing; **(b)** operating directly in front of a
> detection system watching for exactly this is poor practice even where permitted.
>
> **The bound, if it is ever attempted:** one attempt, plainly made. **EAC
> preventing the hook is a TERMINAL RESULT** — record it and stop. Any step whose
> purpose is to make the hook survive detection is circumvention, off-charter under
> CHARTER §3, and does not get pursued, recorded, or built on. No second attempt
> with a different technique.
>
> **What replaces it:** S1a inverts the problem — the client handshakes with a
> server we run, we hold the session keys, and its messages arrive as plaintext on
> our socket with no hook at all. That covers the client→server half; H2 and FIND-2
> cover structure. H3's unique remaining value is the **server→client** direction
> observed live, which is the only reason it survives at all.

**Blocked on H1 and H2.** Do not start until both land.

When unblocked: adapt the H1 Frida script to the retail client, attaching at the
T2 crypto boundary and/or the H2 dispatch function. **Signature-scan for the
target; never hardcode the address** — retail's OpenSSL is statically linked, so
there is no symbol to look up (STATE §10). Mirror captures to a loopback UDP socket
so they can be piped into Wireshark with a growing Lua dissector.

**The Proton problem is this chunk's first real obstacle.** The retail client runs
as a PE process under Wine (STATE §5). Attaching Frida to that is materially
different from attaching to the native reference build, and it should be treated
as the opening question of the chunk rather than a detail.

**What T5 changed here, and what it did not (added 2026-08-30).** T5 changed one
thing: the reference build is now a *validated* model for retail's transport (STATE
§12B), so an H1 hook proven against it can be trusted to transfer, and the epoch-≥1
plaintext this chunk produces is expected to be §8 `Carrier` framing. T5 changed
**nothing** about the mechanics — retail's OpenSSL is still static, the target is
still a PE under Wine, and the hook must still be located by signature. Note also
that T5 removed one possible shortcut permanently: the keylog callback is absent
from the DTLS context because **stock GridMate never had one** (STATE §12B, §13),
not because Amazon stripped it. There is nothing to re-enable. This hook is the only
route to the world stream's plaintext.

**Before starting this chunk, settle the §3 question explicitly rather than in
passing.** H1 and H2 are clean — one targets a native binary we compile, the other
is static analysis of a file on disk. H3 is the first chunk that attaches to the
running retail client, and `<install>/EasyAntiCheat/` is loaded in that process.
CHARTER §3 rules out anti-cheat work absolutely and permanently, which means this
chunk cannot be allowed to drift into "and then work around what fights the hook."
Decide up front what H3 is permitted to be — and if the answer is that it cannot run
without engaging an integrity system, that is a finding to record, not an obstacle
to route around.

Expect the retail client to carry runtime protections the reference build does not
— note what fights the hook, but per charter §3 do not engage anything that is an
integrity/attestation system.

---

## H4 — The reflection reader (`SerializeContext`) — DECISION GATE

Depends on T1 (done). **Deliverable is a written decision, then a prototype only
if the decision is go.**

**Why this could collapse P-track.** The client holds a global
`ComponentApplication` with a `SerializeContext` (class names, field names, member
offsets for every reflected type) and GridMate holds a `ReplicaChunkDescriptorTable`
mapping wire CRCs → chunk descriptors. Compiled in-process against matching `AzCore`
headers from our fork, we may be able to walk that metadata and read structured,
named, typed objects instead of guessing byte offsets.

**The gate.** The blocker is header/ABI drift between our fork and the shipped
build — struct layouts must match closely enough to traverse. Decide, with
evidence, whether the ABI is close enough to attempt this. If not, say so and
P-track stays fully empirical.

**Evidence now available that this prompt predates:** T1 confirmed the retail
client carries `GridMateAllocatorMP` / `GridMateAllocator` and ~94
`InitializeReplicatedFields` references, and that RTTI survived (STATE §10). The
fork builds and runs (STATE §7). Both sides of the ABI comparison are therefore
inspectable — this decision can be made on evidence rather than guesswork.

**Definition of done.** A decision with the ABI evidence attached. If go, a
prototype that locates the global `ComponentApplication` on the reference build and
enumerates one reflected type by name.

**Falsification.** Prove it on the reference build first. If the walker can't
traverse `SerializeContext` on the build we compiled against, it will not traverse
the retail client's, and that kills the approach cleanly.

**Non-goals.** Not a client mod. Reading metadata to interpret captures, not
altering the client.

---

# Track P / Track S / Track D — stubs

Write the full prompt when the chunk comes up, using the shape above.

- **P1 Handshake sequence.** Byte-document the connect exchange from H3 captures,
  cross-referenced against T5's header layout. **Scope narrowed 2026-08-30: the
  epoch-0 DTLS half is already done.** STATE §12B documents that flight completely
  and identically on both sides — `CH(seq0, no cookie) → HVR(seq0) → CH(seq1,
  cookie=20) → HelloRequest(seq0) → CH(seq0, no cookie) → SH(0) Cert(1) SKE(2)
  CertReq(3) SHD(4) → Cert(1, empty) CKE(2) → [CCS] → NewSessionTicket(5)` — with a
  13-byte `RecordHeader` and 12-byte `HandshakeHeader`. What P1 still owes is the
  **GridMate `Carrier` handshake inside epoch 1** (`DefaultHandshake`, connection
  request/ack, and the `Carrier` header on real traffic), and that is what needs H3.
- **P2 Message-type census.** Turn H3's dispatch-table hits into a list of known
  message types with frequencies. **T1 found `google::protobuf::Reflection::` in
  `NewWorld.exe` itself** (not in EAC or Vivox — both scanned, both zero), so
  embedded `FileDescriptorProto` blobs may hand over the schema rather than
  requiring reverse engineering. This is where they get extracted. STATE §10.
- **P3 Position/movement message.** The controlled-walk experiment (walk a straight
  line at constant speed; the smoothly-varying float triple or quantized int is the
  position). GridMate's transform marshalers quantize — see `CompressionMarshal.h`
  / `MathMarshal.h` in the fork for the exact scheme. **T3 collects a stand-still
  and a walking window**, so the timing/size delta is a free head start.
- **P4 Initial world-state sync.** The login state dump is the biggest, most
  informative single message — capture it with a log-out/log-in cycle.
- **P5 Replica/chunk model.** Map `ReplicaChunk` types (identified on the wire by
  `AZ::Crc32` of the chunk name) to the descriptor table dumped via H4. **Noticed
  during D2:** `object-stream-converter` and `asset-catalog-parser` in the
  new-world-tools kit would likely say a lot about the replicated-object model.
  Recorded, not acted on. STATE §11.
- **S1–S3.** Server work, all blocked on the corresponding P-track chunks. Prompts
  when P1/P3/P4 resolve. Content source is ready (D2). **T5 handed S-track three
  hard requirements and removed one (STATE §12B):** the server must run GridMate's
  own 20-byte cookie exchange at the datagram layer — enabling OpenSSL's cookie
  callbacks is **not** equivalent and will not interoperate; it must send a
  HelloRequest once the cookie verifies, with backoff, or the client stalls at
  `message_seq 1` waiting for a ServerHello that never comes; and it must send a
  CertificateRequest and accept an **empty** client Certificate. **Removed:** there
  is no client-certificate PKI and no embedded cert to find in `NewWorld.exe` — the
  client presents nothing. Neither of the first two behaviours is derivable from
  RFC 6347; they are GridMate's own sequencing. **See the marked PROPOSAL under
  Track S** on splitting S1 into an unblocked DTLS half and a blocked Carrier half.
- **D1 Signature-scan harness.** So offsets survive a client patch. **Head start:**
  `pins/22469132/Bin64.sha256` plus `sha256sum -c` already gives a per-file list of
  which binaries a patch touched (STATE §5). Worth finishing the moment H3 has more
  than one hardcoded offset.
- **D2 Client game-data extraction.** **DONE 2026-08-29** — prompt in
  `D2_PROMPT.md`, findings in STATE §11. Paks are standard ZIP; compression method
  15 is Oodle. **2250 datasheets**, all in `SharedDataStrm-part{1..11}.pak` + base
  — *not* `GameData.pak`, and there is no `assets/server/server.pak` in build
  22469132 despite the tool README. Extracted and converted to JSON with
  localization applied via new-world-tools @ `e51c79a9`, built natively on Linux.
  Track S has its content source.

---

## FINDINGS block format

Every chunk ends by producing this. Paste it into the next session if it is listed
as an input, and fold it into `STATE.md` before starting anything else.

```
## FINDINGS — <chunk id> — <date>

**Client build under test:** <exact version>

**Status:** complete / partial / blocked

**What was done:**
- …

**Confirmed** (verified against the reference build, the decompiler, or a capture):
- …

**Unverified** (believed, not tested — say what would test it):
- …

**Corrections** (something in STATE.md is wrong):
- Old claim → what is actually true → evidence

**Files / addresses worth keeping** (signatures, not bare offsets):
- …

**Commands worth keeping:**
- …

**Noticed, out of scope** (incl. anything that turned out to be anti-cheat-only — charter §3):
- …

**What the next chunk needs to know:**
- …
```

The **Corrections** and **Unverified** sections earn their keep. A session that
records what it merely *believes*, separately from what it *checked*, is handing
the next session the list of things worth checking.

**Also update this file when a chunk lands:** tick the index row, add a DONE banner
to the prompt, and mark any claim inside the prompt that the chunk falsified. A
stale prompt is how a future session rebuilds something that already exists — the
T1/T2/T4 rows sat at `[ ]` for a full session after they were complete.

**This has now happened twice. 2026-08-30.** T3 and T5 both landed on 2026-08-29,
both were folded into `STATE.md` as §12A and §12B, and both index rows here were
still `[ ]` — with T3 additionally flagged `← NEXT` and the Order section still
routing the reader to it. The warning above was written *about the first
occurrence* and did not prevent the second, which says the problem is not that the
rule is unknown but that folding into `STATE.md` feels like completion and this
file gets left behind.

Two observations, for whatever they are worth. **First: the update is a different
motion from the fold, and it is the one with no natural trigger.** Writing FINDINGS
and folding them into `STATE.md` is where the session's attention already is; this
file is a separate document that nothing in that motion forces you to open.
**Second: the two files fail differently.** `STATE.md` is append-only, so its worst
case is clutter — a stale claim sits next to its correction and a reader can see
both. This file is a *router*: it tells a session what to do next. A stale row here
does not clutter, it **misdirects**, and it misdirects a session that has been
deliberately given only one chunk and no way to notice the contradiction. That
asymmetry is the argument for updating this file *before* folding findings, not
after — the fold is the part you will not forget.

**As of 2026-08-30 this is CHARTER §6.4, and it is binding rather than advisory.**
§6 exists specifically because the two paragraphs above were true, were written
down, and still did not prevent the second occurrence. The rules that bear on this
file: **§6.4** — tick the row, banner the prompt, and strike through whatever the
chunk falsified, *before* folding findings into `STATE.md`; a chunk is not complete
until all three are done. **§6.5** — never tick a row on the strength of remembered
work; a false `[x]` misdirects exactly as badly as a false `[ ]`. **§6.6** — open
items belong in STATE's register, not in this file. **§6.7** — where a standalone
`*_PROMPT.md` exists it *is* the prompt, and it belongs in the repository, not on
one machine.
