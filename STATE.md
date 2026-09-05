# nwproto — AI session handoff

## FRESHNESS HEADER — verify this before reading further (CHARTER §6.2)

| Field | Value |
| ----- | ----- |
| Last updated | **2026-09-05** |
| Written against commit | **FILL ON COMMIT** (parent: f8a536b) |
| Section count (every `## ` header, this one included) | **22** (§16.15 and §17.9 are `###` subsections; **§19 is a new `## ` added by P6**) |
| Highest test number (§14) | **78** |
| Correction row count (§13) | **36** |
| Chunks complete | T1, T2, T3, T4, T5, D2, P0, P0b, S0a, H2, P2, P5, **P6** |
| P6 scope note | **P6 is ticked with steps 1–3 and 5 done and STEP 4 NOT STARTED** — the fragment message is unframed. Carried to **P7** as OI-P6-3. Precedent: P0 was ticked on a PARTIAL verdict. §19, §15. |
| Open gates | **0** — **OPEN-3 RESOLVED 2026-08-31** (NO, confirmed by direct trace of the deserializer; client does not verify the queue token; S0a, §16.15). **OPEN-3R closed same session.** GATE-1 resolved 2026-08-30 (§3, §15). |

**A session's first action is to check these against the working tree.** Not to
read on, not to propose anything:

```fish
cd ~/Documents/NWLY; and git pull
grep -c '^## ' STATE.md                                                    # expect 22
awk '/^## 14\./,/^## 15\./' STATE.md | grep -oP '^\| \K[0-9]+' | tail -1   # expect 78
awk '/^## 13\./,/^## 14\./' STATE.md | grep '^| ' \
  | grep -vc '^| Old claim\|^| ---'                                        # expect 36
git log -1 --format='%h %ad %s' origin/Master
```

> **Header repaired 2026-08-30 (pre-P0).** Three of the four checks were wrong and
> a session obeying §6.2 would have halted at step zero on a false alarm — or, worse,
> learned to wave mismatches through, which is the one thing this mechanism cannot
> survive. Corrected, with the original claim recorded per §5:
> - `# expect 17` contradicted the header's own `18`; the true count is **18**.
> - `grep -oP '^\| \d+ '` matched any table row opening with a bare number, so it
>   returned **8** (a §13/§15 row), not 49. Now anchored to §14.
> - `Highest correction row (§13) | 8` was false — §13 holds **19** rows, and they
>   carry no IDs, so the field was unverifiable as written. It is now a **count**.
>   Numbering the existing rows would be a reorder, which §5 forbids.
> - `Written against commit` was **blank**, i.e. one of the four numbers §6.2
>   requires did not exist. Fill it before this file is pushed.
>
> **Consequence for citations:** §13's rows are unnumbered and append-only, so every
> insertion shifts positional references. `P0_PROMPT.md` cited "§13 row 7" for the
> `SSLKEYLOGFILE` overcall; that is **row 15**, and row 7 is the unrelated
> `AllocatorInstance` correction. **Cite §13 rows by their opening claim text, never
> by index.**

**A mismatch means stop and resolve it. It does not mean proceed carefully.** On
2026-08-29 a session ran to completion against a three-day-old copy of this file
and folded its findings into a §11 that already existed. This header exists so that
staleness announces itself instead of having to be suspected. If these numbers and
the tree disagree, say so before doing anything else.

**Do not trust a rendered GitHub blob page to answer this** — it caches, and it has
already served a 272-line pre-T4 version of this file while the 1432-line current
one sat on `Master`. Use `raw.githubusercontent.com`, the API, or `git`. CHARTER
§6.3.

---

Paste this whole file at the start of a new session. It is the single source of
truth for what this project is, what already exists, what has been proven, and
what comes next. Nothing described here as existing needs to be rebuilt.

> **Governance (from CHARTER §5).** This file is append-only in practice. Add
> findings; promote UNVERIFIED → CONFIRMED with evidence. Do **not** delete,
> reorder, or "clean up." A wrong belief moves to the Corrections table (§13); it
> does not disappear.

> **Repair note — 2026-08-30. Additive only; nothing was deleted, reordered or
> rewritten.** Added: the freshness header above (CHARTER §6.2); the GATE-1 note in
> §3, recording that H3's viability has never been decided; two gotchas in §5 (the
> stale GitHub blob page, and `triage.sh` already carrying
> `-fdelayed-template-parsing`); a corrected prompt-file inventory in §6 flagging
> that `T4_PROMPT.md`, `T5_PROMPT.md` and `D2_PROMPT.md` may not be committed; and
> **§15, the open-items register** required by the new CHARTER §6.6. No finding,
> correction, or test row was touched. **§7–§14 are byte-identical to the 2026-08-29
> version.**

> **Owner decision — 2026-08-30. GATE-1 resolved; H3 removed from the critical
> path.** Everything achievable without contacting EAC is done first; H3 is a last
> resort attempted once, with prevention as a terminal result. Reasoning and the
> bound are in **§3**; the replacement work order is in **§15**. Three new chunks
> follow from it — **P0** (auth-phase decode), **S0** (redirection feasibility) and
> **S1a** (the DTLS server) — indexed in `CHUNKS.md`. This changes sequencing only:
> no finding, correction or test row was altered, and no chunk was marked complete.

> **Repair note — 2026-08-29.** This file was rewritten once to fix accumulated
> damage. **No finding, correction, or test-log row was deleted.** What changed:
> broken markdown tables in §13 and §14 repaired; a duplicate `Capture output`
> row in §5 merged; the misnumbered "§8+" stub renumbered to §12; the mangled
> paste fragment in §2 removed; and the **status prose in §1, §2 and §3 replaced**,
> because it described the pre-T4 position and contained no findings — only stale
> planning. Superseded *findings* are marked inline and left in place. One new
> correction was added to §13 (the `TypeInfo.h` patch) and one new row to §14.

---

## 1. What this project is

**The goal is a working private server the unmodified New World client connects
to**, reached by understanding the client's network layer. Built in three layers,
in this order:

1. **Transport layer** — how the client secures and frames network messages
   (socket path, crypto boundary, packet headers, reliability, reassembly).
   **T-track complete.** T1, T2, T3, T4, T5 all done. **T5 (§12B) answered
   CHARTER §2's core question: retail transport is stock GridMate
   `SecureSocketDriver`, and the reference build is a valid instrument for it.**
   What remains in this layer is H-track (H1/H2 → H3), which supplies the
   epoch-≥1 plaintext.
2. **Protocol layer** — what the messages mean (handshake, dispatch table,
   replica model, wire encoding of the messages a session needs). **Partially
   started** — H2 (§17) mapped the world-message dispatch and enumerated all 10
   Javelin Gateway message types. Deep per-message decode (P-track) and protobuf
   schema extraction (P2/FIND-2) are still open, blocked on H1 plaintext.
3. **Server layer** — a server that completes a handshake, stands a character in
   the world, and serves enough state to render and move. **Not started.** Its
   content source is ready (D2, §11).

**Engine question: SETTLED (T1, §10).** The client is **GridMate**, not O3DE
`AzNetworking` and not a rewrite. The decisive evidence is
`TransportLayerGridMate` — New World's own wrapper class, so GridMate is the live
network layer rather than a leftover string. The pre-T1 uncertainty (2016
Lumberyard origin vs. a possible O3DE-era replacement) is resolved in favour of
GridMate, and the reference-build strategy holds.

### The reference build is the primary instrument, not a side project

We have the Lumberyard fork the client was built from. A GridMate `Carrier` test
built from that fork — two processes, our control, full source, symbols, no
runtime protections — is the independent source against which every claim about
the retail client is checked (CHARTER §2, §4). When the reference build and the
retail client conflict, the retail client is the truth; the reference is how we
understand it. **This instrument now exists and works** (T4, §7–§9).

### Two hard boundaries (CHARTER §3)

- **No anti-cheat work, ever.** The transport research targets the crypto and
  framing layer, not any integrity/attestation system. Findings that only matter
  for defeating an integrity check are off-charter and do not get recorded or
  built on.
- **No client modification as the delivery mechanism.** Injection and hooking are
  research tools for reading plaintext (on a build we control first, then the
  retail client for understanding). The product is a server the unmodified client
  talks to.

---

## 2. Where things stand

**As of 2026-08-30.**

> **THE GAME IS BEING RETIRED — this is a project deadline, added 2026-08-30 (§16.0).**
> Amazon's own sunset notice, served to the client and read in the P0 captures:
> **servers go offline 31 January 2027**; the title was delisted 15 January 2026. The
> development team is gone. **Everything capture-dependent (P0, S0, any observation of
> live retail traffic) stops being possible on that date; everything file-dependent
> (H2, FIND-2, D2, the reference build) is unaffected.** Captures are a perishable
> input — take more than seem necessary and keep them. This *raises* the priority of
> the S-track: after the retirement date, a working private server is the only way the
> client runs at all.

**Complete:**

- **T4 — reference `Carrier` build.** Builds and runs on the target machine.
  Recipe is `clang++ -std=c++17 -include utility -fdelayed-template-parsing -w`
  plus `-DDTLS1_RT_HEARTBEAT=24` for GridMate. 168/202 AzCore TUs, 41/41 GridMate
  TUs. Plaintext **and** DTLS sessions both pass, both captured, both decoded.
  Reproducible from a wiped `build/` (test #20). See §7, §8, §9.
- **T1 — engine fingerprint (retail).** GridMate confirmed; O3DE absent. §10.
- **T2 — crypto fingerprint (retail).** OpenSSL 1.1.1k, **statically linked**,
  boundary at `SSL_read`/`SSL_write`. Static linkage means the H-track must use an
  inline hook located by signature — no DLL proxying. §10.
- **D2 — client game-data extraction.** 2250 datasheets → JSON with localization.
  Track S has its content source. §11.
- **T3 — retail transport recon.** World connection is **UDP/DTLS 1.2** via
  `SecureSocketDriver` (settles §7's UNVERIFIED-for-retail). P1–P4 all confirmed;
  epoch-0 handshake captured for T5. §12A.
- **T5 — reference vs retail handshake diff. THE MILESTONE.** Retail transport is
  **structurally stock GridMate `SecureSocketDriver` with zero catalogued
  exceptions**; every difference from the reference is OpenSSL 1.1.1k-vs-3.6.4
  noise in fields the source does not set. **Mutual auth is stock, not
  Amazon-added.** **The reference build is a valid instrument for retail's
  transport.** P1–P4 all confirmed. Offline: two pcaps + source, no client launch,
  no hooks, no decryption. §12B.

- **P2 — protobuf descriptor extraction (retail, static).** Scanned the whole
  binary: **3 `FileDescriptorProto` blobs, none of them game protocol** — one
  Campfire telemetry schema plus two stock protobuf well-known types. No Javelin
  descriptor, no `service` block, `application/x-protobuf` = 0 against
  `application/json` = 236. **FIND-2 closes negative**, §17.5's "protobuf choke
  point" is corrected (§13), and **OI-H2-3 is answered mundanely** (AWS SDK
  `XResult` types are non-polymorphic → no RTTI). Track P retargets onto GridMate
  `ReplicaChunk` marshalling, for which we hold the source. §17.9.

- **P5 — replica/chunk model (source-first + static retail).** Documented
  GridMate's replica wire format from the pinned fork — **and found it is not
  where the game's state lives.** There is a **third layer: `Amazon::Hub`**,
  Amazon's own actor/fragment replication framework above GridMate, with ~3,600
  registered types, **3,629 symbols and zero functions** (fully inlined). Game
  state is Hub fragments; the inbound world-state update is
  `ReplicateClient::FragmentUpdateMsg`; the world handshake is enumerated by name
  (`REPClient::RegistrationRequestMsg`/`V2`/`V3`, `RegistrationResponse`, `Ping`,
  `TimeSynch`). **P5's prediction 0 asked the wrong question** and prediction 3
  was falsified (transforms are **raw IEEE floats**, not quantized). **Also
  corrected P2's own §17.9** on `InitializeReplicatedFields` (§13). Opens
  OI-P5-1…4 and **P6**. §18.

**Open, in dependency order:** H1 → H3 → P-track → S-track. D1 can start any
time. **T3 complete 2026-08-29 (§12A). T5 complete 2026-08-29 (§12B) — the
T-track is finished. H2 complete 2026-09-04 (§17) — world-message dispatch map
done, Track P prioritisation and S1a handoff written. H-track active front is
now H1. P2 complete 2026-09-04 (§17.9) — protobuf ruled out as a route to the
world protocol; Track P retargeted onto GridMate replica marshalling, which is
readable from the reference fork source and is therefore immune to the 2027-01-31
sunset. **P5 complete 2026-09-04 (§18) — and that retarget was right by accident:
game state is not GridMate replicas either, but `Amazon::Hub`, a third layer
above them. Track P's front is now P6.** The Hub route is also static and
sunset-immune.**

**Build is pinned.** buildid 22469132, depot manifests recorded, `Bin64/` byte-copied
with a 22-file sha256 baseline. See §5. This closes the only item in the project
that had a clock on it.

**Fork pin corrected 2026-08-29:** the Lumberyard fork tree is **patched** —
`RTTI/TypeInfo.h`, `false_v<T>` → `false_v<>`, committed as **`7d4f1ee6`**, the
single commit on top of `413ecaf`. This contradicts §7's and test #6's original
claim of "no edits to Amazon's tree." **The build point is `7d4f1ee6`, not
`413ecaf`.** See §5 and §13.

---

## 3. What is next, in order

**T3 — Transport recon (retail). ✅ COMPLETE 2026-08-29 — findings in §12A.**
Ran Wireshark/tcpdump on a real login-to-in-world session, no hooks. It was the
last input T5 needs, and it settled §7's UNVERIFIED-for-retail question: the world
connection is **`SecureSocketDriver` / UDP-DTLS**, not `StreamSecureSocketDriver` /
TCP-TLS. P1–P4 all confirmed. The prediction and procedure below are retained as
written; the result is §12A.

Two procedural details decide whether it succeeds:

- **Start the capture before the client connects.** Test #21 only caught the
  cookie exchange because of this. A mid-session capture is all epoch ≥ 1
  ciphertext and useless for T5.
- **Disable voice chat in the client first.** `vivoxsdk.dll` (§10) opens its own
  UDP flow that resembles a game stream and parses as neither DTLS nor Carrier.

The falsifiable prediction to record before capturing: **the retail ClientHello
advertises exactly one cipher suite, `0xC030`** (`ECDHE-RSA-AES256-GCM-SHA384`),
because GridMate hardcodes it at `SecureSocketDriver.cpp:1494`. A single-suite
match is close to conclusive for a stock-ish GridMate transport. A normal
multi-suite list means Amazon replaced the `SSL_CTX` setup, and T5's verdict needs
qualifying even though T1 said GridMate.

**T5 — reference vs retail handshake diff. ✅ COMPLETE 2026-08-29 — findings in
§12B.** The chunk that answers the charter's core question, and it answered it:
stock GridMate, zero exceptions, reference validated as an instrument. Both inputs
were in hand (reference §9, retail §12A) and the reference capture did not need
regenerating (test #42). The framing below is retained as written; the result is
§12B.

**Track H is now the active front.** H2 (locate the dispatch point in retail,
static Ghidra) needs no login and no running client. H1/H3 target a **Proton/Wine**
process and must reach `SSL_read`/`SSL_write` by **signature scan** (static
OpenSSL, §10, §12A) — T5 changed none of that; it only established that tooling
proven against the reference can be trusted to transfer.

**Sequencing rule — decided by the owner 2026-08-30, GATE-1 resolved. This is
standing policy, not a suggestion.**

**Do everything achievable without touching EAC first. H3 is a last resort, run only
if every other route is exhausted.** The reasoning is not that H3 is off-charter — it
is not. Hooking `SSL_read` to read plaintext your own client already decrypted is
reading your own data on your own machine, and §3 forbids *circumventing* an
integrity system, not being observed by one. Two other things decide it:

1. **Account risk.** Injecting into an EAC-protected process is a well-known ban
   trigger regardless of intent — EAC detects injection, not motive. The account is
   load-bearing for everything else: auth captures, world captures, and any future
   handshake testing against a real server. Spending it early to obtain one of
   several available plaintext sources is a bad trade. *(Enforcement specifics for
   New World are not established here — verify before anyone runs H3.)*
2. **Operating directly in front of a detection system that is watching for exactly
   this is poor practice** even where it is permitted.

**The bound that keeps this on-charter:** if H3 is ever attempted, it is attempted
once, plainly. **If EAC prevents the hook, that is a terminal result** — record it
and stop. Any step whose purpose is to make the hook survive detection is
circumvention, is off-charter under §3, and does not get pursued, recorded, or built
on. There is no second attempt with a different technique.

**The consequence that matters: the critical path no longer runs through the retail
client's process.** Between static extraction, the auth phase, and a server the
client connects to, most of P-track is reachable without H3. The order is §15.

**T5 also handed S-track three concrete facts** (§12B): the server must run
GridMate's own 20-byte cookie exchange at the datagram layer, must send a
HelloRequest once the cookie verifies, and must accept an **empty** client
Certificate. There is no client-cert PKI to reverse.

**D1 (signature-scan harness)** has a free head start: the `Bin64.sha256` baseline
in §5 already answers "which binaries did this patch touch."

---

## 4. How to work on this project

**A belief validated only against your own tooling is not validated** (CHARTER
§4). The governing rules:

- **Prove it on the reference build before believing it on retail.** A claim about
  the retail transport not checked against a build we control is a guess with good
  production values.
- **Prefer the source to the sample.** GridMate's `Carrier.cpp` describes the
  protocol family; one capture describes one session.
- **Predict the bytes before you dump them.** A capture that "looks structured"
  proves nothing; one that matches or cleanly breaks a prediction is a test.
- **Hook above the crypto, never at the socket.** The wire datagram is DTLS
  ciphertext. `SSL_read`/`SSL_write` hand you framed plaintext.
- **Ask what would falsify a result.** An entropy test that can't tell "encrypted"
  from "compressed" is not a test.
- **Change one thing per experiment.** Stand still → heartbeat; walk straight →
  position message.
- **A tool's cap is part of the measurement.** A hook that drops oversize packets
  looks exactly like "the client didn't send it."
- **Version-lock from day one.** Record the build, keep the installer,
  signature-scan instead of hardcoding offsets.

Working style: propose an approach, name the check that would prove it wrong, run
it on the reference build, then work the retail client.

**Session-loop discipline (added 2026-08-29).** The pattern that works is: predict
→ run **one** command → read the exact error → fix → re-probe. That is what took
T4 from "provision an isolated toolchain" to "two flags and a five-line patch" in
about twenty minutes. The failure mode is reasoning from memory across several
turns without asking for a command to be run. Keep the loop tight.

---

## 5. Environment and machine layout

Owner's environment: **Garuda Linux, fish shell**, IntelliJ / CLion available.
The retail client is a Windows PE; Ghidra runs against the Windows binary, and
dynamic work runs against the client **under Proton** (confirmed below).

| What                        | Path / value                          |
| --------------------------- | ------------------------------------- |
| Client build under test     | **New World: Aeternum**, appid 1063730, **buildid 22469132**, installdir `New World`, SizeOnDisk 76,416,676,920 (~71.2 GiB). `LastUpdated` 1787844457 (2026-08-27). |
| Retail install path         | `/home/kaatlev/.local/share/Steam/steamapps/common/New World`. **`~/.steam/steam/steamapps/...` is a symlink to this same directory** — the two paths seen in earlier sections are the same place, never a conflict. |
| Retail client binary        | `<install>/Bin64/NewWorld.exe` (171 MB, unpacked). Steam build, OpenSSL 1.1.1k statically linked. |
| **Build pinned**            | Depot 1063731 → manifest `5202358862838894766`; depot 1063732 → `5672526915328587099`; depot 1063730 → `4762214502346222814` (not in `InstalledDepots`, same 27 Aug 10:44 timestamp, kept anyway). appmanifest + 3 manifests + full `Bin64/` at `~/Documents/nwly-pin/22469132/` (272M). Outside the repo, not committed (CHARTER §3). |
| Pin caveat                  | Manifest ids are **documentation, not insurance** — `steam console` → `download_depot` only works while Valve's CDN retains those chunks, and old manifests get pruned. The `Bin64/` byte copy is the actual insurance. The 71G of paks are already reduced to `~/Documents/nwly-datasheets`. |
| Patch-detection baseline    | `cd <install>; and sha256sum -c ~/Documents/nwly-pin/22469132/Bin64.sha256` lists exactly which binaries a patch touched. 22 entries; `Bin64/logs/` excluded (mutable, would false-positive on first launch). Seed for D1. Committed to the repo at `pins/22469132/Bin64.sha256` — hashes only, no Amazon content. |
| Client runtime              | **Proton.** `steamapps/compatdata/1063730` exists, so the retail client is a PE process under Wine on this host. Neutral for T3 (traffic exits `enp2s0` normally); a real complication for H1/H3, since Frida attaching inside Wine is a different problem from attaching natively. |
| Capture interface           | **`enp2s0`**, host `192.168.1.33`, gateway `192.168.1.1`. Not `-i any` — that yields Linux-cooked (SLL) framing; `enp2s0` keeps retail captures on `DLT_EN10MB`, matching the T4 loopback captures so `decode_carrier.py` sees the same link layer. |
| Capture output              | Retail: `~/Documents/nwly-captures/` (outside the repo). Reference: `build/*.pcap` (gitignored except `!build/*.pcap`). |
| Retail launch (confirmed T3) | Launches under **GE-Proton** (2026-08-29). `NewWorld.exe` runs as a PE under `wineserver` (seen in T3 `ss -tunp`), confirming the "Client runtime: Proton" row above by actual launch, not just a `compatdata` prefix. **"Steam Linux Runtime 1.0" is not Proton** — forcing it exits the game to the library instantly. An earlier Proton-Experimental attempt bounced the same way; cause not cleanly isolated (possibly the runtime misconfig), so recorded only as "GE-Proton is the known-good config," not "Experimental fails." **Implication for H1/H3:** Frida attaches to a Wine process — plan Frida-under-Wine, not native attach. |
| Retail captures (T3)        | `~/Documents/nwly-captures/t3_retail_b22469132_20260829-203901.pcap` (good — handshake inside), `t3_handshake_epoch0.pcap` (**T5's retail input**), `t3_sizes.tsv` (still/walk profile). Game flow `192.168.1.33:27001 ↔ 52.223.16.88:54888` (AWS). §12A. |
| EasyAntiCheat location      | `<install>/EasyAntiCheat/` — `EasyAntiCheat_EOS_Setup.exe`, `EOSSDK-Win32-Shipping.dll`, `EOSSDK-Win64-Shipping.dll`. **A sibling of `Bin64/`, not inside it.** §10's mention could be read as implying `Bin64/`; a scan of `Bin64/` alone would wrongly conclude EAC is absent. Location recorded only. CHARTER §3 — not touched, not analysed. |
| Lumberyard fork (reference) | `~/Documents/lumberyard` (github.com/kaatbailey/lumberyard, fork of aws/lumberyard, branch `master`). GridMate at `dev/Code/Framework/GridMate/`, AzCore at `dev/Code/Framework/AzCore/`. |
| Fork commit — **read** from   | `413ecaf24d7a534801cac64f50272fe3191d278f`. Every §7 source-reading fact was established against this tree. **This is not the tree that builds.** |
| Fork commit — **built** from  | **`7d4f1ee6`** — *"AzCore: fix false_v<T> static_assert for modern clang (template-template param can't be a template arg)"*. The **only** commit on top of `413ecaf` (test #31), and it is pushed (`HEAD -> master, origin/master, origin/HEAD`). **Pin every build result to `7d4f1ee6`.** For a full 40-char hash: `git rev-parse HEAD`. |
| What the patch changes       | `dev/Code/Framework/AzCore/AzCore/RTTI/TypeInfo.h`: `static_assert(false_v<T>, ...)` → `static_assert(false_v<>, ...)` at lines 161/169/177/185/193. Amazon's original is `false_v<T>`, which modern clang rejects as a template-template parameter used without arguments. See §13 — §7 and test #6 originally claimed no source edits were made. |
| NWLY repo                   | `github.com/kaatbailey/NWLY`, branch `Master` (capital M). Local: `~/Documents/NWLY`. |
| Toolchains                  | System **clang 22** (also used by PZMapMaker — do not disturb). `/opt/llvm14` was considered and **rejected** — see §7. |
| Local OpenSSL               | **3.6.4 (25 Aug 2026)**, Garuda system package. Reference build only; retail ships its own static 1.1.1k. |
| AzCore build recipe         | **`clang++ -std=c++17 -include utility -fdelayed-template-parsing -w -c <file>.cpp -I AzCore -I AzCore/Platform/Linux`**, run from `dev/Code/Framework`. Verified on clang 18 and clang 22. See §7 for why each flag is there. **All four flags are required** — `-fdelayed-template-parsing` in particular is load-bearing and was briefly and wrongly believed redundant (§13, tests #32–#34). |
| GridMate build recipe       | The AzCore recipe plus `-I GridMate -I GridMate/Platform/Linux` and **`-DDTLS1_RT_HEARTBEAT=24`**. See §7. |
| Ghidra project              | `/home/kaatlev/Documents/Ghidra-projects/nwly.gpr` — auto-analysis and PE RTTI analyzer already run on `NewWorld.exe` b22469132 (sha256 `8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e`). **Do not re-import.** Landmarks confirmed present: `FUN_14644a070` (GameConnection state machine), `PTR_s_Disconnected_1484f9ff0` (state-name array base `1484f9f0`), REP driver object at conn+0x1000, `Amazon::Hub::TransportLayerGridMate` RTTI, `Amazon::ContainerClientSDK::REPConnection` RTTI (OnConnect/OnRecv), `Aws::JavelinGatewayService` model RTTI (10 types). §17. |

**Gotchas found so far:**

- **`fd` is not installed** on this machine; use `find`. `rg` (ripgrep) IS present.
  Watch a stray `-h` in a piped command — ripgrep parses it as `--help` and dumps
  the man page instead of matching.
- **`grep -c` exits 1 on a zero count**, so a shell reports an error on a
  successful "absent" check. The count is the result, not the exit code (test #22).
- **fish aborts a failed glob before evaluating the `or`.** Use `find` for
  existence checks, not a shell glob (§10).
- **`AzCore/std/containers/queue.h:202` has a typo in Amazon's source**
  (`rhs.m_continer`, should be `m_container`). It is invisible under
  `-fdelayed-template-parsing` and costs 108 compile failures without it. Do not
  remove that flag. §7, §13.
- **`triage.sh` and `build_gridmate.sh` enumerate different file sets** — 191/36
  vs 202/41 — because `triage.sh` does a bare `find` while `build_gridmate.sh`
  excludes `WinAPI|Windows|Android|Apple|AppleTV|Mac|iOS|Salem|Provo|Jasper` and
  `Tests?/` (line 87). **`build_gridmate.sh`'s 202/41 are authoritative** — they
  built the archives. Don't compare the two tools' raw counts. Test #35.
- **`triage.sh` already carries `-fdelayed-template-parsing`** — test #34 added it
  permanently. Test #35's closing line, "left as-is. No code change," refers only
  to the *file-selection expression*, not the flag. Do not re-add it.
- **A rendered GitHub blob page can serve a stale file.** On 2026-08-30 a fetch of
  `github.com/kaatbailey/NWLY/blob/Master/STATE.md` returned the 272-line pre-T4
  version while the current 1432-line file was on `Master` — and the session
  concluded from that single result that the work was unpushed and existed on one
  nvme with no remote. Wrong, and alarming. **Verify repository state with
  `raw.githubusercontent.com`, the API, or `git log origin/Master` — never the
  rendered page.** This is now CHARTER §6.3.
- **Disk:** single 1.9T nvme root (`/dev/nvme0n1p2`), ~591G free as of setup.
- **Installed tooling:** Ghidra, `tcpdump`, Go, clang 22. **Still to add per
  chunk:** `wireshark-cli` (T3), Frida (H1), pev/radare2 (optional for H2).

---

## 6. What already exists — do not rebuild

**`t4_openssl_probe.cpp`** (repo root) — a single translation unit reproducing
every OpenSSL call site in `SecureSocketDriver.cpp` at fork commit `413ecaf`.
Compile it to answer "does the local OpenSSL match the API era this source
assumes" in one step. Build line is in its header comment. Re-run it after any
OpenSSL major upgrade; that is the whole point of keeping it.

**Know its blind spot before trusting a clean run.** It enumerates *function
calls*, so a removed *macro constant* is structurally invisible to it — which is
exactly how `DTLS1_RT_HEARTBEAT` got past it and surfaced only when GridMate
itself was compiled (§7, §13). A clean probe run means "the API era matches",
not "OpenSSL is fine". The real test is compiling `SecureSocketDriver.cpp`.

**`build_gridmate.sh`** — builds `libazcore.a` and `libgridmate.a` from the fork
using the §5 recipe. Writes nothing inside the Lumberyard tree; all output goes to
`./build`. Incremental, parallel, and tolerant of the expected 3rdParty failures.
`--ly` points at the fork, `--show-failures` lists what broke.

**`triage.sh`** — bulk compile triage. Compiles every AzCore (or GridMate) TU
independently with the proven recipe and reports which fail and why, grouped by
error kind. `bash triage.sh [azcore|gridmate]`. The `sed` normalisation that
collapses quoted identifiers to `X` before `sort | uniq -c` is what turned test
#10's 34 failures into "27 rapidjson, 6 Lua, 1 rapidxml" instead of 34 separate
investigations. Wanted again the first time the fork or the toolchain moves.

**`CMakeLists.txt`** — a CMake path to the same reference build (`azcore`,
`gridmate`, `carrier_probe` targets). Redundant with `build_gridmate.sh` for
building, but it sets `CMAKE_EXPORT_COMPILE_COMMANDS ON` and gives CLion a
loadable project — much better than a shell script when stepping through the
reference Carrier with a debugger during H1. Note its header comment is what
caught the `TypeInfo.h` patch discrepancy (§13). Two stale comments inside it:
it does not carry `-fdelayed-template-parsing`, and its "expect Linux-specific
DTLS bugs" note was falsified by test #17.

**`nwly_carrier_probe.cpp`** — the T4 step-4 harness. Two Carriers on loopback,
handshake, payload both ways, exit 0 on success. Path B: no gtest, no AzTest.
Build line is in its header comment.

**`capture_carrier.sh`** — runs the probe under tcpdump. No args writes
`build/carrier_plaintext.pcap`; `--secure` writes `build/carrier_dtls.pcap`.
One command; handles the sudo and the start/stop sequencing.

**`decode_carrier.py`** — decodes a capture against the Carrier layout read from
`Carrier.cpp`, and recognises DTLS records as well. This is the step-4 completion
check: the artefact that proves source and wire agree, and the starting point for
diffing our traffic against retail. **T3 points this at retail for the first
time.**

**`t1_fingerprint.sh`** / **`t1_evidence.sh`** — the T1 scanners. First gives
family counts and the verdict; second dumps the verbatim matched strings.

**Chunk prompt files** — `T3_PROMPT.md`, `T4_PROMPT.md`, `T5_PROMPT.md`,
`D2_PROMPT.md`. Where one of these exists it **is** the prompt; the summary in
`CHUNKS.md` is an index entry, not a substitute (CHARTER §6.7).

> **VERIFY THIS — flagged 2026-08-30.** As of 2026-08-29 the repository's `Master`
> branch contained only `.gitattributes`, `CHARTER.md`, `CHUNKS.md` and `STATE.md`.
> **`T4_PROMPT.md` and `D2_PROMPT.md` were not committed**, despite being cited as
> ready-to-run; `T5_PROMPT.md` was produced at the end of the T3 session and there
> is no evidence it was ever committed either. Meanwhile `CHUNKS.md` instructs a
> session to paste these files. A prompt that lives on one machine cannot be handed
> to anything, and cannot be recovered if that machine dies. Check and fix:
>
> ```fish
> cd ~/Documents/NWLY; and git ls-files '*_PROMPT.md'
> ```
>
> If any are missing, commit them and delete this notice. CHARTER §6.7.

Each completed chunk's FINDINGS block folds into the relevant section here.

---

## 7. Transport facts — CONFIRMED from the reference fork source

Established by reading `~/Documents/lumberyard` directly, then confirmed by
building and running it (T4). These describe **GridMate as it ships in the fork**.
They are the reference layout; where a fact still needs confirming against the
*retail* client, it is marked UNVERIFIED-for-retail.

### The secure transport is OpenSSL DTLS

`dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp` includes
`<openssl/ssl.h>`, `<openssl/bio.h>`, `<openssl/err.h>`, `<openssl/x509.h>`,
`<openssl/hmac.h>`, `<openssl/rand.h>` — **OpenSSL called directly, not abstracted.**
It is unmistakably DTLS: uses `DTLS1_VERSION`, `DTLS1_RT_HEADER_LENGTH` (13-byte
record header), `DTLS1_HM_HEADER_LENGTH` (12-byte handshake header),
`SSL3_MT_CLIENT_HELLO`, and a hello-verify-request cookie exchange.

**Consequences:**

- The plaintext hook boundary (H-track) is OpenSSL `SSL_read` / `SSL_write` — the
  charter §4 "hook above the crypto" target. **Confirmed on both sides now:** from
  the reference source here, and from the retail binary in §10.
- The `RecordHeader` (13 bytes) and `HandshakeHeader` (12 bytes) structs in that
  file **are the DTLS wire framing**. They are T5's reference layout — read them,
  don't reverse them. Confirmed on the wire in §9.
- **A single cipher suite is hardcoded** at `SecureSocketDriver.cpp:1494`:
  `ECDHE-RSA-AES256-GCM-SHA384` (`0xC030`). This is T3/T5's sharpest falsifiable
  prediction — see §3. **CONFIRMED on both wires (T3 §12A, T5 §12B).**
- **The full list of fields this file explicitly sets is enumerated in §12B**
  (T5, from source). Anything absent from that list is an OpenSSL default. That
  list is what makes a retail-vs-reference diff falsifiable rather than
  impressionistic — build on it rather than re-deriving it.
- There are **two** secure drivers: `SecureSocketDriver` (datagram/DTLS) and
  `StreamSecureSocketDriver` (stream/TLS). Which one the retail MMO uses for its
  main connection is a specific T3/T5 question — persistent-world traffic could
  lean either way. ~~**UNVERIFIED for retail.**~~ **CONFIRMED for retail
  2026-08-29 (T3, §12A): `SecureSocketDriver` (UDP/DTLS).** The world connection
  is UDP carrying DTLS 1.2 records (`0xfefd`); the stream/TLS driver is not used
  for it. This fixes the shape of every P-track chunk. Evidence in §12A.

### GridMate's dependency surface is clean

Every non-GridMate include is `<AzCore/...>` or standard library — nothing from
other frameworks (no AzFramework, no gems). The T4 carve-out is therefore
**AzCore + GridMate only**. The AzCore surface used is foundational and broad but
shallow: `Memory` (allocators), `std/` (their STL reimpl — containers, smart
pointers, `parallel/*` threading), `Math`, `EBus`, `RTTI/TypeInfo`,
`Socket/AzSocket` (UDP), `State/HSM`. Links pthreads. **Confirmed by build:**
test #10 found every AzCore failure was a missing 3rdParty header, none on
GridMate's dependency surface.

### Build facts — pre-T4 reading, two entries SUPERSEDED

- **~~C++ standard: C++14.~~** `dev/Tools/build/waf-1.7.13/platforms/compile_settings_clang.py`
  sets `-std=c++1y`. **SUPERSEDED — see §13.** The source requires **C++17**;
  `Math/Crc.inl:114` uses an `auto` template parameter and `-std=c++14` is a hard
  error with no flag that rescues it. The Waf setting is what the 2019 clang was
  told, not what the code needs.
- **No hard clang version gate.** `AZ_COMPILER_CLANG` is defined as `__clang_major__`
  in `PlatformDef.h` — it accepts whatever clang major is present. **Now CONFIRMED:**
  clang 22 compiles the tree clean under the §5 recipe, and the recipe also holds on
  clang 18, so it is not an artifact of one compiler build.
- **Platform-header include paths** (what Waf resolves and a standalone build must
  supply): Waf prepends the `Platform/<OS>/` dir to the include search path. For
  Linux:
  - `dev/Code/Framework/AzCore/Platform/Linux`
  - `dev/Code/Framework/GridMate/Tests/Platform/Linux` (harness only)
- **Test certificates:** `dev/Code/Framework/GridMate/Tests/Certificates.cpp` defines
  `g_untrustedCertPEM` / `g_untrustedPrivateKeyPEM` (declared `extern` in the tests).
  Compile that file to satisfy the DTLS handshake's cert/key need.

### The test harness — a gift, with a caveat that did not materialise

`dev/Code/Framework/GridMate/Tests/Carrier.cpp` is Amazon's own two-process Carrier
test, with `SocketDriverProvider` (plaintext) and `SecureDriverProvider`
(DTLS) already abstracted — i.e. the charter §2 plaintext-then-secure toggle is
built in. But `Tests.h` drags in AzCore UnitTest, Driller, Streamer, and the
Session layer, more than §2 needs. T4 used a minimal `main()` (Path B), taking
`Carrier.cpp` as the construction pattern rather than the full harness (Path A).

**~~Caveat — DTLS-on-Linux is likely untested by Amazon.~~** No
`AZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER` definition exists under the Linux
platform dir, so it defaults off, and T4 was told to expect Linux-specific DTLS
bugs. **SUPERSEDED — see §13 and test #17.** DTLS passed on the first run, on both
clang majors. The trait gates the *test harness*, not the driver, and the driver
sits on `SocketDriverCommon`, which the plaintext path exercises constantly.
*Untested* is not *broken*.

---

### The source targets the OpenSSL 1.1.0+ API era, not 1.0.2

Established by probe (test-log #1/#2). `SecureSocketDriver.cpp` contains **no**
`OPENSSL_VERSION_NUMBER` guards anywhere — it targets exactly one API era, and
that era is 1.1.0 or later. Two tells in the source: it calls
`X509_get0_notBefore` / `X509_get0_notAfter` (accessors that only exist from
1.1.0), and it builds its BIOs with `BIO_s_mem` rather than statically
initialising a `BIO_METHOD` struct — so the single largest 1.1.0 breaking
change is simply not present in this file.

**Consequence for T4 step 5:** modern OpenSSL needs no shim and no
`openssl-1.1` compat package. Add `-Wno-deprecated-declarations` and the build
is silent. Three call sites warn and nothing else:

| Call | Line | Status |
| ---- | ---- | ------ |
| `DTLSv1_2_method()` | 1472 | deprecated since 1.1.0, still functional |
| `ERR_load_BIO_strings()` | 1468 | deprecated since 3.0, no-op |
| `ERR_load_SSL_strings()` | 1469 | deprecated since 3.0, no-op |

`SSL_library_init`, `SSL_load_error_strings`, `ERR_load_crypto_strings` and
`SSL_CTX_set_ecdh_auto` warn not at all — they are no-op macros in 3.x.

**The pinned cipher and the test certs both clear modern policy.**
`ECDHE-RSA-AES256-GCM-SHA384` (hardcoded at line 1494) is still enabled at the
default security level on OpenSSL 3.6.4, and survives an explicit
`@SECLEVEL=2`. The `Certificates.cpp` cert is RSA-4096 signed
`sha384WithRSAEncryption`, valid 2016-05-12 to 2036-05-07 — nowhere near any
security-level floor, and not expiring inside this project's life.

**Verified on the target machine.** CONFIRMED on **clang 22 + OpenSSL 3.6.4**:
0 errors, exactly the 3 warnings tabled above (test-log #4). Also CONFIRMED on
OpenSSL 3.0.13 for the compile/link/handshake, so the result holds across six
minor versions rather than resting on one. Re-run `t4_openssl_probe.cpp` after any
OpenSSL major upgrade; that is what it is for.

---

### Verified AzCore toolchain recipe — clang 22, C++17, three flags (T4 step 1)

CONFIRMED by compiling AzCore TUs on the target machine. Run from
`dev/Code/Framework`:

```
clang++ -std=c++17 -include utility -fdelayed-template-parsing -w -c \
  AzCore/AzCore/Math/Vector3.cpp -o /dev/null \
  -I AzCore -I AzCore/Platform/Linux
```

0 errors, 0 warnings on `Math/Vector3.cpp` (leaf: Math only) and on
`Math/Sfmt.cpp` (pulls `std/parallel/lock.h` + `Module/Environment.h`, so the
AZStd threading reimplementation and the allocator/environment bootstrap are
both covered). Test-log #5–#9.

**Why each flag, so none of them get dropped as cargo cult:**

| Flag | Without it | Cause |
| ---- | ---------- | ----- |
| `-std=c++17` | `Math/Crc.inl:114: 'auto' not allowed in template parameter until C++17` | The source is *not* C++14. See correction §13. |
| `-include utility` | `std/utils.h:45: no member named 'exchange' in namespace 'std'` | `using std::exchange;` relied on a transitive `<utility>` that modern libstdc++ no longer pulls in. |
| `-fdelayed-template-parsing` | Two unrelated failure sets: (a) `RTTI/TypeInfo.h:161,169,177,185,193` ×5, and (b) **108 failures** from a one-character typo at `std/containers/queue.h:202` (`m_continer`) | Both are uninstantiated template bodies that modern clang parses eagerly where the 2019 clang did not. (a) is separately fixed at source by commit `7d4f1ee6`; **(b) is not fixed anywhere, so the flag stays.** See below. |
| `-w` | ~31 warnings under C++14 | Cosmetic only, and 0 under C++17 anyway. Drop it if you want to read them. |

**`-fdelayed-template-parsing` is load-bearing, and here is exactly why.**
`AzCore/std/containers/queue.h:202` contains a typo in Amazon's source:

```cpp
void swap(this_type& rhs)  {  AZStd::swap(m_container, rhs.m_continer); ... }
//                                                         ^^^^^^^^^^ missing 'a'
```

The member is `m_container` — every other line in the file spells it correctly.
The typo sits in `priority_queue::swap()`, an uninstantiated template body, so
under `-fdelayed-template-parsing` clang never parses it and the bug is invisible.
That is how it survived Amazon's own builds. Without the flag, eager two-phase
lookup finds it, and because `queue.h` is included nearly everywhere, **one
character produces 108 compile failures across the tree.**

Measured (test #34): flag off → 60/191 with 108 `no member named` errors. Flag on
→ **151/191**, all 108 gone, remaining 40 are `file not found` only. The
`7d4f1ee6` patch fixes five `static_assert` sites; the flag covers something far
broader and neither substitutes for the other.

**Do not remove this flag.** If a future toolchain drops
`-fdelayed-template-parsing`, the fix is a one-character source patch to
`queue.h:202` — the same shape as `7d4f1ee6`, and it would need the same
read-from / built-from treatment in §5.

**Decision: do NOT provision `/opt/llvm14`.** An earlier plan was to fall back to
LLVM 14 on real compile errors. Real errors did occur — but none were removed
language features. Three flags beat carrying a second 2022 toolchain for the life
of the project. ~~Both are toolchain drift with a flag-level fix and **no edits to
Amazon's tree**, which keeps the charter's version-locking rule satisfied.~~
**That last clause is SUPERSEDED — the tree IS patched. See §13.** The
`/opt/llvm14` decision itself stands.

**Third include path, undocumented in the original list.**
`Platform/Linux/AzCore/Math/Internal/MathTypes_Linux.h` includes
`Platform/Common/SIMD/AzCore/Math/Internal/MathTypes_SIMD.h` by a path relative
to `dev/Code/Framework/AzCore`. It is satisfied by `-I AzCore` alone, so no
fourth `-I` is needed — **but `Platform/Common/` must exist in the checkout.**
A sparse checkout that omits it fails with a confusing "file not found" that
points at the *Linux* header rather than the missing one.

---

### One real OpenSSL 3 removal: `DTLS1_RT_HEARTBEAT` (T4 step 3)

`SecureSocketDriver.cpp:416` uses `DTLS1_RT_HEARTBEAT`, which **does not exist
in OpenSSL 3** — heartbeat support was removed after Heartbleed and the constant
went with it. Fix is a define, no source edit:

```
-DDTLS1_RT_HEARTBEAT=24
```

24 (0x18) is the DTLS record type from the pre-1.1.0 headers. The only use is a
`switch` label in a debug string helper that returns `"HeartBeat"`, so the value
only has to match what a peer would put on the wire. See correction §13 — the
earlier "OpenSSL 3.x is a non-issue" claim was too strong.

---

### Standalone bootstrap: two traps that only appear at runtime (T4 step 4)

Neither is a compile error. Both segfault a binary that links fine. AzTest's
environment does this work in the test builds, so `Tests/Tests.h` does **not**
show either step — reading the fixture alone is not enough.

**1. `OSAllocator` must be created before `SystemAllocator`.**
`SystemAllocator`'s heap is supplied by an `azmalloc(..., AZ::OSAllocator)`, so
`OSAllocator` has to exist first or that first call dereferences a null allocator
inside `IAllocator::GetAllocationSource()`. Correct order:

```cpp
AZ::AllocatorInstance<AZ::OSAllocator>::Create();
// ... build SystemAllocator::Descriptor, azmalloc the block ...
AZ::AllocatorInstance<AZ::SystemAllocator>::Create(sysAllocDesc);
IGridMate* gm = GridMateCreate(desc);
AZ::AllocatorInstance<GridMateAllocatorMP>::Create(mpDesc);  // Carrier needs it
```

`GridMateAllocatorMP` is normally created by `StartMultiplayerService`. A probe
that does not start a session service must create it by hand or Carrier has no
allocator.

**2. EBus handlers must be destroyed before `GridMateDestroy`.**
A `CarrierEventBus::Handler` destructor calls `BusDisconnect()`, which touches
the EBus context. Handlers left as plain locals of `main()` are destroyed *after*
the allocator teardown, which is a use-after-free — found by ASan, invisible to a
plain backtrace. Put everything that touches the bus in an explicit scope that
closes before teardown.

**Link line that works** (archives from `build_gridmate.sh`):
`<probe>.cpp libgridmate.a libazcore.a -lssl -lcrypto -lpthread -ldl`
Archive order matters. No undefined symbols — the gmock/zstd objects in
`libazcore.a` are never pulled in, so no `-lgmock`/`-lzstd` is needed.

---

## 8. Wire format — CONFIRMED, GridMate Carrier (plaintext)

Read from `GridMate/Carrier/Carrier.cpp` and confirmed against a live loopback
capture (test-log #15/#16). Layout came from the source first; the capture only
confirmed it.

**Byte order: big-endian throughout.** `kCarrierEndian = EndianType::BigEndian`,
`Carrier.cpp:58`.

```
datagram := [seq u16] message+

message  := [flags u8]
            [dataSize u16]
            [channel u8]      iff MF_DATA_CHANNEL
            [numChunks u16]   iff MF_CHUNKS
            [msgSeq u16]      iff NOT MF_SQUENTIAL_ID
            [relSeq u16]      iff NOT MF_SQUENTIAL_REL_ID
            [payload dataSize bytes]
```

Datagram header: `WriteDataGramHeader`, `Carrier.cpp:2869-2873` — a single
sequence number, nothing else. Message header: `WriteMessageHeader`,
`Carrier.cpp:3494-3541`. Flag bits, `Carrier.cpp:86-93`:

| Bit | Value | Name |
| --- | ----- | ---- |
| 0 | 0x01 | `MF_RELIABLE` |
| 1 | 0x02 | unused — must be 0 |
| 2 | 0x04 | `MF_CHUNKS` |
| 3 | 0x08 | `MF_SQUENTIAL_ID` |
| 4 | 0x10 | `MF_SQUENTIAL_REL_ID` |
| 5 | 0x20 | `MF_DATA_CHANNEL` |
| 6 | 0x40 | unused — must be 0 |
| 7 | 0x80 | `MF_CONNECTING` |

**TRAP: the `MF_SQUENTIAL_*` flags are inverted.** Set means the value is implied
by the previous message and is **absent from the wire**. Read them the intuitive
way — set means present — and the parse desynchronises on the first multi-message
datagram. Bits 1 and 6 being reserved gives a cheap desync check;
`ReadMessageHeader` uses exactly that (`MF_UNUSED_FLAGS`) and so does
`decode_carrier.py`.

Multiple messages pack into one datagram. Confirmed example, 33 bytes:

```
00 02 a0 00 05 03 00 00 ff ff 00 00 00 01 01 88 00 06 ff ff
00 00 00 01 01 01 88 00 02 ff ff 20 06

seq=2
  msg0 flags=0xa0 DATA_CHANNEL|CONNECTING size=5 channel=3 msgSeq=0 relSeq=65535
  msg1 flags=0x88 SEQUENTIAL_ID|CONNECTING size=6 relSeq=65535   <- no msgSeq
  msg2 flags=0x88 SEQUENTIAL_ID|CONNECTING size=2 relSeq=65535   <- no msgSeq
```

**Not Carrier protocol: the `'G'` wakeup byte.** A 1-byte datagram `0x47`
addressed to the socket's *own* port is `AZ_SOCKET_WAKEUP_MSG_VALUE`
(`SocketDriver.cpp:55`), sent by `StopWaitForData()` (lines 1449-1470) to break
the receive thread out of its blocking wait; the receive side drops it as an
internal wakeup (line 1423). **Filter it out before diffing against retail** or
it looks like a phantom message type. Roughly a third of loopback frames are
these.

---

## 9. Wire format — CONFIRMED, DTLS (SecureSocketDriver)

With `SecureSocketDriver` installed on both `CarrierDesc`s, every datagram is a
DTLS 1.2 record and the §8 Carrier framing moves inside the ciphertext. Record
header is the 13-byte layout `SecureSocketDriver.cpp` parses by hand (the
`RecordHeader` recorded pre-T4 in §7), now confirmed on the wire:

```
[type u8][version u16][epoch u16][sequence u48][length u16]  = 13 bytes
   version 0xfeff = DTLS 1.0, 0xfefd = DTLS 1.2
   type 20 ChangeCipherSpec | 21 Alert | 22 Handshake | 23 ApplicationData
```

**Epoch is the thing to read first.** Epoch 0 is the cleartext handshake and its
handshake-type byte at offset 13 is readable. Epoch >= 1 is ciphertext: there is
nothing further to parse without session keys, and no amount of staring at it
will yield Carrier framing.

Measured on a captured `--secure` session, against the plaintext baseline:

| Check | plaintext | `--secure` |
| ----- | --------- | ---------- |
| parse as Carrier datagrams (§8) | 40/40 | **0** |
| parse as DTLS 1.2 records | — | **30/30**, all epoch 1 |
| contain the cleartext payload string | yes | **0** |
| `'G'` wakeup bytes | ~1/3 of frames | 0 |

The payload-string check is the one that matters: "PASS" only proves a session
was established, not that anything was encrypted. Searching the capture for the
known cleartext is what proves it. Keep that check in any future secure test.

`decode_carrier.py` recognises both formats, so one tool identifies which mode a
capture came from.

### The cookie exchange, confirmed on the wire

A capture started before the session opens catches the full DTLS handshake, and
it confirms the `HandshakeHeader` / cookie machinery §7 recorded from
`SecureSocketDriver.cpp` pre-T4:

```
client -> server   ClientHello          DTLS1.2  epoch=0   (no cookie)
server -> client   HelloVerifyRequest   DTLS1.0  epoch=0   (issues cookie)
client -> server   ClientHello          DTLS1.2  epoch=0   (cookie echoed)
```

**The HelloVerifyRequest is DTLS 1.0 (`fe ff`) while both ClientHellos are 1.2
(`fe fd`), and that is correct.** RFC 6347 §4.2.1: the server is stateless at
that point and has not negotiated a version, so HVR goes out at 1.0. **This is
not a bug and not a downgrade.** Expect to see it in retail captures too; do not
spend time chasing it. *(Confirmed in retail, T3 §12A.)*

> **REFINED by T5 (§12B, §13) — not wrong, but incomplete, and the real mechanism
> is more useful.** The RFC permits it, but the actual cause is that GridMate
> **hardcodes** `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) in its
> hand-packed records (`SecureSocketDriver.cpp:308`, `:312`, `:343`). That moves
> the `fe ff` from "library/RFC default" into the **GridMate-controlled** bucket,
> where it matches retail exactly. **Diagnostic value: every `fe ff` record in a
> capture is a GridMate hand-pack — exactly two per handshake
> (HelloVerifyRequest, HelloRequest).** The advice not to chase it stands.

The cookie is plainly visible and echoed verbatim. Observed:

```
14 a2 f9 d4 cb ae ce 22 76 38 4e bd 18 12 b8 f0 89 10 80 02 70
^^ length byte (0x14 = 20), then 20 cookie bytes
```

It appears in the HelloVerifyRequest and again in the second ClientHello. Cookie
values are per-connection — the bytes above are one observed sample, not a
constant.

Everything from `ChangeCipherSpec` onward is epoch >= 1 and therefore ciphertext.
The handshake above is the only part of a secure session that is readable
without session keys, which makes it the only part usable for diffing against
retail.

**This capture is T5's reference input.** The retail counterpart comes from T3.
**Used unmodified in T5 — it already contained epoch 0 (16 type-22 records), so it
was not regenerated (test #42).** Verify content, not just file existence, before
trusting any future reference capture: test #18's `--secure` capture was 30/30
epoch-1 with no handshake in it at all.

---

## 10. FINDINGS — T1 (engine fingerprint) + T2 (crypto), static

**Client build under test:** `NewWorld.exe`, 171 MB, Steam install, unpacked,
buildid 22469132. OpenSSL version string `OpenSSL 1.1.1k  25 Mar 2021`. (Exact
game version string from the launcher still not recorded. **T3 (2026-08-29)
attempted this and it was not surfaced in-client** — no version shown on the
launcher/title/menu this session. `buildid 22469132` / `LastUpdated 1787844457`
remain the only build identifiers; treat this as attempted-not-available, not a
standing task. §12A.)

**Status:** T1 complete. T2 complete except its anti-cheat non-goal — crypto
library, boundary function and linkage are all answered below.

**Method:** `strings -a -n 6` over every binary >1 MB, families counted then
dumped verbatim (`t1_fingerprint.sh`, `t1_evidence.sh`). No Ghidra needed to
reach the verdict; no dynamic analysis; the game was never launched.

**Confirmed — engine is GridMate, not O3DE:**

- Decisive: `TransportLayerGridMate` and `TransportLayerGridMateTickThread` —
  New World's own class wrapping GridMate transport, so GridMate is the live
  network layer, not a leftover string.
- Replica stack present: `GridMateLANSessionReplica`, `GridMatePeerReplica`,
  `GridMateReplicaStatus`, `GridMateReplicaSessionInfo`, plus
  `GridMateAllocatorMP` / `GridMateAllocator` (the same allocators the T4 probe
  had to bootstrap by hand).
- Gameplay replica chunks ride it: `VTransformReplicaChunk`,
  `VTriggerAreaReplicaChunk`, `ScriptComponentReplicaChunk`, and ~94
  `InitializeReplicatedFields` references — the `ReplicaManager` shape the T4
  reference assumed. **T5's diff strategy holds.**
- 43 GridMate-family hits total in `NewWorld.exe`.

**Confirmed — O3DE AzNetworking absent:** the only O3DE-family hit was
`TransformLinkConnectionData`, a gameplay struct ending in `ConnectionData` —
the exact generic-name trap CHUNKS T1 warned about. Zero real `AzNetworking`
symbols. The falsification condition (no GridMate strings AND O3DE set present)
is not met.

**Confirmed — transport is UDP datagram, GridMate shape:** `WSASend`,
`WSARecvFrom`, `WSARecv`, `closesocket`, `WS2_32.dll`. Datagram calls present,
consistent with `SocketDriver`. (String-level evidence; Ghidra should confirm
these are real imports, not incidental ASCII.)

**Confirmed — crypto (this is most of T2):**

- Library: **OpenSSL 1.1.1k (25 Mar 2021)**. Same DTLS-over-OpenSSL design as
  the T4 reference build.
- Plaintext boundary: **`SSL_read` / `SSL_write`** (`dtls1_`, `DTLSv1` also
  present — DTLS confirmed).
- Linkage: **static.** Consequence for the H-track: **no DLL proxying is
  possible** — a hook above the plaintext boundary must be an inline hook located
  by signature, patched in memory. This is the harder of T2's two outcomes and it
  sets H1's method.

**Confirmed — RTTI survived (corrects an in-session claim):** MSVC mangled-name
fragments are present, e.g. `UEAAXPEAVReplicaChunkBase` (`PEAV` = pointer-to-
class) and `AEAAXAEBVGuildsComponentReplicatedState` (`AEBV` = const-ref-to-
class). The binary is not stripped. Ghidra's PE RTTI analyzer will recover the
class hierarchy — this is H2's cheapest starting point.

### `Bin64/` module inventory — 22 files, build 22469132

Positive inventory, replacing the earlier absence-based linkage argument:

`NewWorld.exe` · `NewWorld.exe.eac` · `GameCrashUploader.exe` · `steam_api64.dll` ·
`vivoxsdk.dll` · `bink2w64.dll` · `dbghelp.dll` · `libcds-amd64-vcv141.dll` ·
`dstorage.dll` · `dstoragecore.dll` · `dxcompiler.dll` · `dxil.dll` ·
`WinPixEventRuntime.dll` · `nvngx_dlss.dll` · `nvngx_dlssg.dll` ·
`sl.dlss.dll` · `sl.dlss_g.dll` · `sl.common.dll` · `sl.interposer.dll` ·
`sl.nis.dll` · `sl.pcl.dll` · `sl.reflex.dll`

- **T2's static-linkage claim now rests on a list, not an empty `find`.** No
  `*ssl*`, `*crypto*`, or `*eay*` module exists. Inline hook by signature
  confirmed as the only H-track option.
- **No `steamnetworkingsockets` / GameNetworkingSockets** — only `steam_api64.dll`,
  the interface layer. Weak evidence against Steam Datagram Relay tunnelling the
  game stream. **Absence argument only** — T3 settles it.
- **`vivoxsdk.dll` is a second network stack in the same process.** Vivox opens
  its own UDP media flow plus TCP signalling. It will appear in a T3 capture as a
  sustained bidirectional UDP conversation that resembles a game stream and parses
  as neither DTLS nor Carrier. **Disable voice chat before capturing.**
- **`libcds-amd64-vcv141.dll` unidentified** (MSVC 2017 toolset, name suggests
  Amazon-internal). Noted so H2 knows it exists before following xrefs.

**Unverified (believed, not yet tested):**

- That the `WSA*` strings are real imports rather than incidental ASCII. Test:
  Ghidra import table, or `objdump -p`-equivalent on the PE.
- That retail's DTLS handshake matches the reference cookie exchange (§9). Test:
  T3/T5 — capture a retail session and diff the epoch-0 handshake.

**Flagged, out of scope (CHUNKS T1 says flag loudly):** `google::protobuf::
Reflection::` appears **in `NewWorld.exe` itself** — not in the EAC or Vivox
DLLs (both scanned, both 0). Game code uses protobuf. Embedded
`FileDescriptorProto` blobs may carry the message schema and make **P2 far
cheaper** — potentially schema handed over rather than reverse-engineered. NOT
extracted here per T1 non-goals; recorded as a flag only.

**Noticed, out of scope:** EAC present. Its files live in `<install>/EasyAntiCheat/`,
**not** in `Bin64/` — see §5 for the exact paths. Charter §3: location recorded,
not touched, not analysed.

**Commands worth keeping:**

- `./t1_fingerprint.sh --out t1_scan.txt` — family counts + verdict.
- `./t1_evidence.sh --out t1_evidence.txt` — the verbatim matched strings.
- `find <Bin64> -iname '*ssl*' -o -iname '*crypto*' -o -iname '*eay*'` — the
  static-vs-dynamic linkage check (empty = static). Use `find`, not a shell
  glob; fish aborts a failed glob before the `or`. **Prefer the full inventory
  above** — an empty `find` is a weaker argument than a complete list.

---

## 11. Client game data (`.datasheet`) — CONFIRMED from D2

Folded from FINDINGS — D2 — 2026-08-29. Pure offline file work: no client
launch, no injection, read-only against the install (CHARTER §3 satisfied).

**Build under test:** New World: Aeternum, Steam appid 1063730, **buildid
22469132**, at `/home/kaatlev/.local/share/Steam/steamapps/common/New World`.

### The pak container is standard ZIP

- `50 4b 03 04` at offset 0; the first local header parses cleanly — 41 bytes
  stored, filename length 0x24 = `libs/flownodes/flownodeblacklist.xml`.
- **130 `.pak`** under `assets/`, ~72G on disk, naming `<Name>[-partN].pak`.
  All 130 open as zip; **0 failures**.
- **Compression method 15 = Oodle.** Not a standard ZIP method id (0 store,
  8 deflate, 9 deflate64, 12 bzip2, 14 LZMA, 93 zstd). Python `zipfile` can
  enumerate method-15 entries but cannot `read()` them — it is a census tool
  here, not an extraction tool.
- **No Zip64 anywhere.** EOCD 16-bit entry counts are genuine, not saturated:
  a direct `PK\x01\x02` central-directory walk gave `walked == eocd` on
  every pak, including the four sitting exactly on 65535. The packer rolls to
  a new `-partN` at the 65535 ceiling — that is what the part numbering is
  for. See §13 and §14 for the falsified saturation hypothesis.

### Where the datasheets are

**2250 total**, confined entirely to `SharedDataStrm*`. `GameData.pak` holds
none, despite the name (§13).

| Pak | Datasheets |
| --- | ---------- |
| `SharedDataStrm-part6.pak` | 645 |
| `SharedDataStrm-part4.pak` | 628 |
| `SharedDataStrm-part5.pak` | 569 |
| `SharedDataStrm-part7.pak` | 152 |
| `SharedDataStrm-part9.pak` | 60 |
| `SharedDataStrm-part8.pak` | 45 |
| `SharedDataStrm-part11.pak` | 45 |
| `SharedDataStrm-part10.pak` | 37 |
| `SharedDataStrm-part3.pak` | 29 |
| `SharedDataStrm-part1.pak` | 21 |
| `SharedDataStrm.pak` | 12 |
| `SharedDataStrm-part2.pak` | 7 |

- `-part12` and `-part13` are **22-byte empty-archive stubs** (EOCD record
  only, 0 entries). `-part14` has 3928 entries and 0 datasheets.
- **198 of 2250 are stored (method 0); 2052 are Oodle.**

### Verification

- **Two independent code paths agree on 2250** — the hand-rolled
  central-directory census and `pak-extracter`. Neither is silently dropping
  entries.
- **Verified column-by-column**, not by file count.
  `MasterItemDefinitions_Faction`: **127 columns × 4121 rows**, legible
  headers (`ItemID`, `ItemType`, `TradingCategory`, `GearScoreOverride`,
  `PerkSlot1`). Not plausible-looking garbage, which is the D2 prompt's named
  failure mode.
- **Localization is a separate 184-file tree** under `localization/en-us`.
  Datasheet string fields are `@Key` lookups (e.g. `@DyeB179_Name`) resolved
  by the converter's `-localization` flag.

### Tooling (re-derivable per CHARTER §4)

- **github.com/new-world-tools/new-world-tools**, MIT, pure Go, v0.13.10,
  commit **`e51c79a9af4fba51daecd97c5e190c0b5ee953a5`**
  (Wed Nov 5 04:04:28 2025 +0300), cloned to `~/Documents/new-world-tools`.
- Builds natively on Garuda with `go build -o ./bin/ ./cmd/...` — produces
  `pak-extracter`, `datasheet-converter`, `object-stream-converter`,
  `asset-catalog-parser`. No wine, no cgo.
- **The tool downloads binary libraries from the network on first run** —
  Oodle v2.9.13 and `libtexconv.so`, `dlopen`ed via `ebitengine/purego`.
  Not found under the repo, `~/.cache`, `~/.local/share` or `~/.config` at
  depth 5; **location unresolved**. Matters for any air-gapped or
  reproducible re-run.
- The tool README documents `assets/server/server.pak` as the datasheet
  source. **That path does not exist in this build** (§13).

**The recipe:**

```fish
set -g NW /home/kaatlev/.local/share/Steam/steamapps/common/"New World"
cd ~/Documents/new-world-tools && go build -o ./bin/ ./cmd/...

./bin/pak-extracter -input $NW/assets -output ~/Documents/nwly-extract \
  -include '\.datasheet$' -threads 6
./bin/pak-extracter -input $NW/assets -output ~/Documents/nwly-extract \
  -include '^localization/en-us' -threads 6
./bin/datasheet-converter -input ~/Documents/nwly-extract \
  -output ~/Documents/nwly-datasheets -format json -threads 6 \
  -localization ~/Documents/nwly-extract/localization/en-us -keep-structure
```

Runtimes: extract **540ms** (peak 7.5Mb) · convert **15.4s** (peak
**2297Mb** — the converter is the memory hog, worth knowing on a smaller box).

Outputs, gitignored and outside the repo (CHARTER §3 — not redistributed):
`~/Documents/nwly-extract` (211M raw), `~/Documents/nwly-datasheets`
(499M JSON, 2250 files).

### UNVERIFIED — the loose ends

- ~~**No installer/depot pinned.**~~ **RESOLVED 2026-08-29** — depot manifests
  and a `Bin64/` byte copy are pinned. See §5.
- That the `-partN` split is *driven by* the 65535 ceiling. Consistent with
  every count observed, but correlation. Tested by whether a future build
  exceeds it.
- Whether datasheet *schemas* are stable across builds. Governs how much
  Track S work a patch invalidates.

### Noticed, out of scope

- `object-stream-converter` (slices, timelines, `.*db`, AZCS) and
  `asset-catalog-parser` ship in the same toolkit and would likely say a lot
  about the replicated-object model — **that is P5, not D2.** Recorded, not
  acted on, per the CHUNKS shared preamble.
- Nothing anti-cheat-adjacent was encountered or pursued.

### What this unblocks

Track S has its content source. The item/vitals/ability tables are
server-authoritative content (gear score bounds, perk slots, base vitals) —
what S2/S3 need. **Nothing here bears on T1–T5**; the transport track is
unaffected.

---

## 12. Reserved for later confirmed findings

New sections are added here as work produces confirmed results — retail transport
recon (T3), the handshake diff verdict (T5), dispatch table (H2), message formats
decoded from captures (P-track). Append-only: a new finding gets a new section; a
finding that overturns an old one adds a Corrections row (§13) and
promotes/demotes the claim rather than editing history away.

*(This section was numbered "8+" and misplaced after §11 until the 2026-08-29
repair. Renumbered, not rewritten.)*

---

## 12A. Retail transport — CONFIRMED (T3, capture-only, no hooks)

Folded from FINDINGS — T3 — 2026-08-29. Wireshark/tcpdump on a real
login-to-in-world session; no hooks, no injection, no decryption of epoch ≥ 1
(CHARTER §3 satisfied). **Build under test:** New World: Aeternum, appid 1063730,
**buildid 22469132**, `LastUpdated 1787844457` (2026-08-27). Voice (Vivox)
disabled at source before capturing, per §10.

### Transport, named

The persistent-world connection is **UDP carrying DTLS 1.2**, so retail uses
GridMate **`SecureSocketDriver`**, not `StreamSecureSocketDriver`. This promotes
§7's UNVERIFIED-for-retail note to CONFIRMED and fixes the shape of every P-track
chunk.

- Game stream: local `192.168.1.33:27001` ↔ server **`52.223.16.88:54888`** (AWS).
  Sustained bidirectional, ~8,600 UDP frames across the in-world window. It is the
  UDP conversation with two-way traffic across the whole session — **not** the
  largest by bytes. Same IP:port on both of the day's captures.
- Auth / server-list is a **separate TCP/443 HTTPS phase** to AWS
  (`44.220.67.249` ×3, `13.217.79.62`, `18.238.35.71`), TLS 1.2, cipher `0xC02F`.
  Cloudflare 443 (`104.18.124.108`, `162.159.*`) is CDN/API, not the game server.
- **Attribution rule for next time:** find the game flow by the sustained two-way
  UDP shape to an AWS host, cross-checked against `ss -tunp` showing it under
  `NewWorld.exe`/`wineserver` — never by byte volume (a Steam/CDN transfer can be
  larger). Local port is ephemeral and will change per session; do not hardcode
  `27001`.

### Predictions P1–P4 — all confirmed

| # | Prediction | Result |
| - | ---------- | ------ |
| **P1** | World is UDP; auth/server-list a separate TCP/443 HTTPS phase | **CONFIRMED.** UDP game stream + distinct TCP/443 HTTPS cluster to AWS, per the `conv,udp`/`conv,tcp` tables above. |
| **P2** | UDP payloads parse as DTLS 1.2; `decode_carrier.py` recognises them unmodified | **CONFIRMED.** All game-flow records parse as DTLS 1.2 (`0xfefd`) once the dissector is forced with `-d udp.port==…,dtls`. `decode_carrier.py` decoded retail **unmodified**: 8618/8637 datagrams as DTLS, 0 Carrier. The predicted loopback/offset bug did not occur (both loopback and `enp2s0` are `DLT_EN10MB`). |
| **P3** | ClientHello (`fe fd`) → HelloVerifyRequest (`fe ff`) → ClientHello with cookie echoed | **CONFIRMED.** Frames 241 (ClientHello, `0xfefd`, no cookie) → 242 (HelloVerifyRequest, `0xfeff`) → 243 (ClientHello, `0xfefd`, cookie echoed). Cookie **`eb14bc1b7aaadacffb30cd3334bc814690591056`** appears on 242 and is echoed verbatim on 243. ~~`SSL_CTX_set_cookie_generate_cb` not disabled.~~ **WRONG — corrected by T5: GridMate never used OpenSSL's cookie callbacks at all (0 hits tree-wide); the cookie is its own `GenerateCookie`/`VerifyCookie`, run before OpenSSL sees the datagram. See §12B and §13.** HVR at DTLS 1.0 is correct (RFC 6347 §4.2.1), as §9 predicted. |
| **P4** *(load-bearing)* | ClientHello advertises exactly one suite, `0xC030` | **CONFIRMED.** Cipher list is `0xC030,0x00FF` — **one real suite** (ECDHE-RSA-AES256-GCM-SHA384) plus `0x00FF`, the TLS renegotiation-info **SCSV** (a signalling pseudo-suite, not a cipher). Matches the reference hardcode at `SecureSocketDriver.cpp:1494`. **T5's structural-match verdict stands unqualified — retail is stock-ish GridMate transport.** |

### Additional handshake observations (P-track relevant, not acted on in T3)

- **~~Early renegotiation.~~** The server sends a **HelloRequest**
  (`decode_carrier.py` datagram #5), which triggers a *fourth* handshake message —
  a third ClientHello at frame 245. So the extra ClientHello is renegotiation, not
  a retransmit. Note for T5/P-track epoch reasoning.
  **SUPERSEDED by T5 (§12B, §13). The observation is right; "renegotiation" is
  wrong.** It is stock GridMate's **cookie handoff** — the reference build does
  exactly the same thing with no Amazon involvement. `message_seq` **resets to 0**
  on that third ClientHello and it carries **no cookie**; renegotiation would
  follow a completed handshake, not precede one. Mechanism is the
  `CS_SEND_HELLO_REQUEST` server state. **This is a hard S-track requirement** —
  see §12B.
- **Mutual auth.** The server sends a **CertificateRequest** (handshake type 13) —
  it asks the client for a certificate. Relevant to the eventual **server layer**:
  a private server will have to satisfy whatever client-cert behaviour this
  implies. Recorded, not pursued.
  **RESOLVED by T5 (§12B): stock GridMate, not Amazon-added**, and **the client
  answers with an empty Certificate (length 0)** on both retail and reference. So
  the server-layer obligation is small: send the request, accept nothing back.
  There is no client-cert PKI and no embedded cert to find in `NewWorld.exe`.
- **ChangeCipherSpec accounting.** CCS is content type **20** (frames 254, 257).
  `decode_carrier.py` has **no type-20 branch**, so those two records plus a few
  Brave/QUIC strays on `:50229` are the "19 undecodable" datagrams (of 8637).
  Harmless; add a CCS branch for completeness so the next session doesn't
  re-investigate.
- Full handshake flight is present in the capture (ServerHello, Certificate,
  ServerKeyExchange, ServerHelloDone, ClientKeyExchange, NewSessionTicket), i.e.
  the epoch-0 exchange T5 needs is complete, not just the opening bytes.

### Capture procedure that worked (so it isn't rediscovered)

- **Start `tcpdump` while the game is fully quit, then launch.** The world socket
  opens *earlier than "enter world"* — during character creation / cut-scenes.
  The first retail capture started tcpdump after the socket was already open
  (`conv,udp` `Start 0.000000`) and caught only epoch-1 ciphertext (test #36). The
  good capture started tcpdump first; the game flow appears at `t≈18.6s`, so the
  handshake is inside the file (test #37).
- **A full quit + relaunch forces a fresh full handshake** (no session to resume).
  A brand-new character guarantees the first-time world-load path. `set -g PCAP
  (command ls -t …)` — `command ls` bypasses Garuda's `ls`→`eza` alias, which
  otherwise eats `-t` as `--time`.

### Version string

**Not surfaced in-client this session.** No human-readable version on the
launcher/title/menu. `buildid 22469132` / `LastUpdated 1787844457` remain the only
build identifiers. Closes §10's "pull before T5" as attempted-not-available.

### Noticed, out of scope — H-track recon (recorded, NOT built on — CHARTER §3)

**`SSLKEYLOGFILE` is honoured for the TLS/HTTPS stack, NOT for the DTLS world
stream.** This is the cheap-plaintext question the H-track cares about, and it
splits cleanly:

- Launched via Steam option `SSLKEYLOGFILE=/home/kaatlev/nwly-keylog.txt
  %command%`. File **written**, 178 lines — 158 `CLIENT_RANDOM` (TLS/DTLS 1.2) and
  the TLS 1.3 `*_TRAFFIC_SECRET_0` / `*_HANDSHAKE_TRAFFIC_SECRET` / `EXPORTER_SECRET`
  sets. So the keylog **callback is compiled into the shipped OpenSSL** — the thing
  §10 left open.
- **Auth phase DECRYPTS.** On the TCP/443 flows, Wireshark's `tls.debug` shows
  `ssl_add_record_info stored decrypted record` / `dissect_ssl_payload decrypted`.
- **World stream does NOT decrypt.** The world ClientHello's client random
  (`0674c28f00c23264ba91029310653b3d6a1d0e2d591b31319d1a5f54df5aa976`) is **absent**
  from the keylog file, and `tls.debug` reports `no decoder available` for every
  UDP/27001 record. (An incrementing byte run in the payload looked like decrypted
  framing but was the **AES-GCM explicit-nonce counter** — visible by design in
  ciphertext. The `tls.debug` decrypt log is the falsifiable check; it returned
  zero decrypts for the world flow.)
- **Interpretation:** the keylog callback is wired into the general TLS/HTTPS
  `SSL_CTX` but **not** into the GridMate `SecureSocketDriver` DTLS `SSL_CTX`
  (separate context setup — the two paths are built by different code).
- **Consequence: H3's signature-scan inline hook on `SSL_read`/`SSL_write` is
  STILL REQUIRED for the world stream — keylog does not replace it.** It does give
  the auth/API phase in plaintext for free if the H-track ever needs
  login/session-token traffic. Whether the DTLS context *could* be made to log
  (forcing the callback) is an interception/mod question, H-track, not T3.
- Static OpenSSL (§10): `SSL_read`/`SSL_write` have no export; H3 reaches them by
  signature scan; plaintext is on the stack the instant they return. Unchanged.
- **Session-resumption note:** the server issues a `NewSessionTicket` and
  renegotiates early, so a reconnect may resume rather than do a full epoch-0
  exchange — the reason the good capture used a full quit + fresh character.

**EAC/EOS in the capture:** endpoints were identified only so they could be
excluded from the game-stream analysis. Not characterised, not recorded beyond
"not the game stream" (CHARTER §3).

### What this unblocks

- **T5 now has both inputs:** the reference epoch-0 handshake (§9) and the retail
  epoch-0 handshake (`t3_handshake_epoch0.pcap`). P4's single-suite match means
  the structural-match verdict is **not** pre-qualified.
- The secure-driver question (§7) is settled: `SecureSocketDriver` / UDP-DTLS.
- H1/H3 setup targets a **Proton/Wine** process (GE-Proton confirmed, §5).

---

## 12B. Retail transport verdict — CONFIRMED (T5, offline diff, no hooks)

Folded from FINDINGS — T5 — 2026-08-29. **This is the section that licenses the
rest of the project.** Two pcaps and one source file; no client launch, no hooks,
no injection, no decryption of epoch ≥ 1 (CHARTER §3 satisfied).

**Build under test:** New World: Aeternum, appid 1063730, **buildid 22469132**,
`LastUpdated 1787844457`.
**Retail input:** `~/Documents/nwly-captures/t3_handshake_epoch0.pcap` (extracted
in T3 from `t3_retail_b22469132_20260829-203901.pcap`).
**Reference input:** `~/Documents/NWLY/build/carrier_dtls.pcap`, from fork commit
**`7d4f1ee6`**, OpenSSL 3.6.4, clang 22. **Not regenerated** — it already contained
epoch 0 (test #42).

### The verdict

> Retail transport is **structurally stock GridMate `SecureSocketDriver`**, with
> **zero catalogued exceptions**. Every handshake difference between retail
> (buildid 22469132) and the reference (`7d4f1ee6`) is attributable to **OpenSSL
> 1.1.1k vs 3.6.4** defaults in fields `SecureSocketDriver.cpp` does not set.
> **Mutual auth is stock GridMate, not Amazon-added.** **The reference build is a
> valid instrument for retail's transport**, within the caveats below.

CHARTER §2's core question — fork or rewrite — is answered. The reference build has
done the job it was built for.

### The GridMate-controlled field list (established from source *before* diffing)

Read from `SecureSocketDriver.cpp`. Anything **not** on this list is an OpenSSL
default and is noise by construction — the bucket was assigned before the bytes
were looked at (CHARTER §4).

| Field | Source | Retail | Reference | Match |
| ----- | ------ | ------ | --------- | ----- |
| Cipher suite | `:1494` `SSL_CTX_set_cipher_list("ECDHE-RSA-AES256-GCM-SHA384")` | `0xC030`, one real suite | `0xC030`, one real suite | **YES** |
| Protocol version | `:1472` `SSL_CTX_new(DTLSv1_2_method())` — pinned, not `DTLS_method()` | `0xfefd` | `0xfefd` | **YES** |
| MTU option | `:1479` `SSL_OP_NO_QUERY_MTU` (the only option set) | n/a on wire | n/a on wire | — |
| Peer verification | `:1522`–`:1553` | CertReq (13) from server | CertReq (13) from server | **YES** |
| Cookie mechanism | `:1699` `GenerateCookie` / `:1737` `VerifyCookie` — GridMate's own | 20 bytes, echoed verbatim | 20 bytes, echoed verbatim | **YES** |
| Hand-packed record version | `:308`, `:312`, `:343` `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) | `fe ff` on HVR + HelloRequest | `fe ff` on HVR + HelloRequest | **YES** |
| HelloRequest handoff | `:337`–`:349`, `:792`, `:1200`, `:1876` | present, 25 bytes | present, 25 bytes | **BYTE-IDENTICAL** |

**Fields the source never touches**, confirmed by targeted grep: `set1_groups`,
`set1_curves`, sigalgs, SNI, ALPN, any `SSL_CTX_set1_*`. `SSL_CTX_set_ecdh_auto`
at `:1500` is a no-op macro on OpenSSL 1.1.0+ (§7) and sets nothing. Therefore
`supported_groups`, `signature_algorithms`, `ec_point_formats`, session ticket,
EMS and extension ordering are **all** library defaults.

### P1 — CONFIRMED

Every GridMate-controlled field matches. Extension **type list is
character-identical** on both sides: `11,10,35,22,23,13`.

### P2 — CONFIRMED. Four divergences, all library noise, none in a field the source sets

| # | Difference | Retail (1.1.1k) | Reference (3.6.4) | Bucket |
| - | ---------- | --------------- | ----------------- | ------ |
| 1 | RFC 5746 renegotiation signalling | `0x00FF` SCSV in cipher list; **no** ext 65281 | ext 65281 `ff 01 00 01 00`; **no** SCSV | Noise. RFC 5746 §3.4 permits either encoding and forbids both. Perfectly anticorrelated across the two captures. `SSL_CTX_set_cipher_list` cannot add `0x00FF` — OpenSSL appends it. Confirmed at byte level: `00 04 c0 30 00 ff` vs `00 02 c0 30`. |
| 2 | `signature_algorithms` | 23 entries, incl. SHA-1 (`0x0201`, `0x0202`, `0x0203`) | 20 entries, SHA-1 absent | Noise. 3.x dropped SHA-1 sigalgs from defaults. Same order otherwise. |
| 3 | `supported_groups` | `…,0x0019,0x0018` | `…,0x0018,0x0019` | Noise. Same five curves, last two transposed (secp521r1/secp384r1). |
| 4 | `ec_point_formats` | `03 00 01 02` — three formats | `01 00` — uncompressed only | Noise. Known 1.1.1k-vs-3.x default change. |

These four fully account for the ClientHello length difference (retail 146,
reference 141). No residual.

### P3 — CONFIRMED. Mutual auth is stock GridMate — and rests on a bug in Amazon's source

**This was the load-bearing question T3 could not answer, and the reason the
reference build exists (CHARTER §2).**

Source, `:1522`–`:1525`:

```cpp
int verificationMode = SSL_VERIFY_PEER;                    // 0x01
if (m_desc.m_authenticateClient)
{
    verificationMode = SSL_VERIFY_FAIL_IF_NO_PEER_CERT;    // 0x02 — assignment, not |=
}
```

OpenSSL gates CertificateRequest on `verify_mode & SSL_VERIFY_PEER`.
`SSL_VERIFY_FAIL_IF_NO_PEER_CERT` (`0x02`) is documented as meaningful only in
combination with `SSL_VERIFY_PEER` (`0x01`); alone, `0x02 & 0x01 == 0`, so it
behaves as `SSL_VERIFY_NONE`. **The branch is inverted against its own stated
intent** — the comment above it says the default authenticates only the server:

| `m_desc.m_authenticateClient` | mode | Server behaviour |
| --- | --- | --- |
| false (default) | `0x01` | **Sends CertificateRequest**, does not require a cert back |
| true | `0x02` | Sends nothing — verification off |

There is **one shared `SSL_CTX`** built for both roles; role separation is in the
HSM, not the context.

Confirmed on the wire, both sides:

| | Reference (`carrier_dtls.pcap`) | Retail (`t3_handshake_epoch0.pcap`) |
| --- | --- | --- |
| CertificateRequest (13) | frame 12, from **4428** (server) | frame 10, from **52.223.16.88** (server) |
| Server Certificate (11) | frames 9–10, **1380** bytes | frame 7, **958** bytes |
| Client Certificate (11) | frame 14, from 4427, **length 0** | frame 12, from 192.168.1.33, **length 0** |

**Retail's type 13 needs no Amazon modification to explain it.** Server asks,
client answers with an empty certificate list, handshake continues — exactly
`SSL_VERIFY_PEER` without `FAIL_IF_NO_PEER_CERT`.

**S-track consequence — a requirement removed, not added.** The client presents
**no** certificate. There is no embedded client cert in `NewWorld.exe`, so "where
does the client get its cert" is not an open question, and there is no
`Certificates.cpp`-equivalent to locate. A private server sends a
CertificateRequest and **accepts an empty response**. No client PKI, no client-cert
validation. T5_PROMPT Step 5 held this open as an H/S-track lead; it is closed.

### P4 — CONFIRMED

`decode_carrier.py` parsed both epoch-0 flights through the same code path, no
per-capture special-casing:

| | Retail | Reference |
| --- | --- | --- |
| datagrams with payload | 16 | 64 |
| DTLS | 16 | 57 |
| Carrier | 0 | 0 |
| `'G'` wakeup | 0 | 7 |
| **undecodable** | **0** | **0** |

Same 13-byte `RecordHeader`, same 12-byte `HandshakeHeader`, same handshake-type
sequence. The §12A type-20 (ChangeCipherSpec) decoder gap did not arise here — the
extracted epoch-0 file stops before CCS — and **remains open**.

### The handshake flights are identical, including `message_seq`

```
CH(seq0, no cookie) → HVR(seq0) → CH(seq1, cookie=20)
  → HelloRequest(seq0) → CH(seq0, no cookie)
  → SH(0) Cert(1) SKE(2) CertReq(3) SHD(4)
  → Cert(1, empty) CKE(2) → [CCS] → NewSessionTicket(5)
```

Same types, same order, same `message_seq` on both sides. The **only** structural
difference is which oversized message got DTLS-fragmented: retail splits
ServerKeyExchange (frames 8–9), the reference splits Certificate (frames 9–10).
That follows from the measured cert sizes (958 vs 1380) hitting the PMTU at
different points. Content difference, not protocol difference — **do not read the
frame-count asymmetry as a divergence.**

### The strongest single piece of evidence: a byte-identical HelloRequest

Retail datagram #3 and reference datagram #5 are identical across all 25 bytes:

```
16 fe ff 00 00 00 00 00 00 00 00 00 0c 00 00 00 00 00 00 00 00 00 00 00 00
```

This message is **hand-built by GridMate**, not emitted by OpenSSL —
`ConnectionSecurity::HelloRequest` is a headers-only struct (`:337`–`:349`) packed
by `OnStateSendHelloRequest` (`:792`). The `fe ff` is GridMate's hardcoded
`DTLS1_VERSION` (`:308`, `:312`, `:343`), **not** DTLS 1.2. An identical hand-built
message on both sides cannot be produced by an OpenSSL version difference.

**Corollary:** every `fe ff` record in either capture is a GridMate hand-pack. Both
captures contain exactly two — HelloVerifyRequest and HelloRequest.

### The HelloRequest handoff — mechanism, and a hard S-track requirement

**This corrects §12A's "early renegotiation" reading — see §13.** The third
ClientHello is **not** renegotiation. It is stock GridMate's cookie handoff, and
the reference performs it identically without Amazon touching anything.

`message_seq` is what proves it: the cookie-echo ClientHello is **seq 1**, then
HelloRequest arrives, then the next ClientHello **resets to seq 0** carrying **no
cookie**. A renegotiation restarts the flight *after* a completed handshake; this
restarts it *before* one ever began.

Mechanism, from source:

- GridMate runs the cookie exchange **in its own raw-recv state machine** (`:1838`
  generate, `:1869` verify) with a hand-built HelloVerifyRequest. **OpenSSL never
  sees those datagrams.**
- Once the cookie verifies, the server creates a Connection initialized directly
  into `CS_SEND_HELLO_REQUEST` (`:1876`).
- That state packs and sends the HelloRequest (`:792`), resending on exponential
  backoff capped at 1000 ms (`:821`–`:837`).
- The HelloRequest makes the client's OpenSSL start a **fresh** handshake at
  `message_seq 0`, which the server's `SSL*` then consumes.
- GridMate also **detects** HelloRequest on the wire itself
  (`IsHelloRequestHandshake`, `:396`–`:401`; used at `:1218`, `:1230`) rather than
  passing it through.
- Line `:494` states the intent in a comment: send back HelloRequest to restart the
  hello sequence.

So the hello that satisfies GridMate's cookie check and the hello OpenSSL actually
handshakes on are **two different messages**, and the real handshake carries **no
cookie at all**.

**Hard S-track requirement.** A private server must:

1. Run the cookie exchange **itself, at the datagram layer** — GridMate's own
   `GenerateCookie`/`VerifyCookie`, 20-byte output (HMAC-SHA1; this is why
   `<openssl/hmac.h>` is included in a file with otherwise no use for it).
   Enabling OpenSSL's cookie callbacks is **not** equivalent and will not
   interoperate.
2. Send a **HelloRequest** once the cookie verifies, with resend/backoff.

Skip step 2 and the client sits at `message_seq 1` waiting for a ServerHello that
never arrives. **Neither behaviour is derivable from RFC 6347** — this is
GridMate's own sequencing, now confirmed identical in retail.

### Caveats on "the reference is a valid instrument"

- **Epoch 0 only.** The match is proven for the cleartext handshake. Epoch ≥ 1
  Carrier framing inside DTLS remains proven on the reference and **inferred** for
  retail. H3 plaintext is what promotes it.
- **Content differs, structure does not.** Certificates (958 vs 1380 bytes), cookie
  values and randoms are per-deployment and per-connection. No observed cookie or
  cert is a constant.
- **Fragmentation is PMTU-dependent**, not protocol-dependent.
- **One shared `SSL_CTX`.** Client/server differences come from the HSM, not from
  separate context setup — relevant when modelling the server side against the
  reference.
- **`m_authenticateClient` is untested in both directions.** Both captures exercise
  the `false` path. If future work needs the `true` path, note it hits the inverted
  branch above and will *disable* verification.

### Noticed, out of scope — H-track recon (recorded, NOT built on — CHARTER §3)

- **`SSL_CTX_set_ex_data(m_sslContext, kSSLContextDriverPtrArg, this)`**, set
  immediately after the verify setup, stashes the driver pointer on the context —
  an `SSL*` → driver back-reference. Potentially useful for recovering driver state
  from a hooked `SSL_read`/`SSL_write` frame. Recorded only.
- **No `SSL_CTX_set_keylog_callback` anywhere in `SecureSocketDriver.cpp`.** This
  **upgrades** §12A's interpretation: it is not that Amazon removed or failed to
  wire the callback into the DTLS context — **stock GridMate never had it.**
  Nothing was stripped. §12A's conclusion is unchanged (H3's signature-scan hook is
  still required for the world stream); only the explanation improves.

### What this unblocks

- **H-track opens.** The reference is a validated model for retail's transport, so
  H1/H2 tooling developed against it can be trusted to transfer. Unchanged from
  §12A: retail OpenSSL is static, so H3 reaches `SSL_read`/`SSL_write` by
  **signature scan**, against a **Proton/Wine** process (GE-Proton, §5).
- **P-track's shape is fixed.** Retail's epoch-≥1 plaintext is expected to be §8
  Carrier framing, on the strength of a validated reference. Confirming it is H3's
  output, not an assumption to build on beforehand.
- **S-track gains two requirements and loses one.** Gained: GridMate's own 20-byte
  cookie exchange plus the HelloRequest handoff; and send CertificateRequest,
  accept an empty client Certificate. Lost: no client-certificate PKI, nothing to
  locate inside `NewWorld.exe`.

---

## 13. Corrections — beliefs that turned out wrong

Acting on any of these wastes real time. Every session that overturns a prior
claim adds a row here rather than deleting the claim.

| Old claim | Status |
| --------- | ------ |
| "**Committed to the repo at `pins/22469132/Bin64.sha256` — hashes only, no Amazon content.**" — §5, patch-detection baseline. | **Was WRONG at S0a runtime, now fixed.** `git ls-files` on `origin/Master` (HEAD 6eea228, 2026-08-31) shows **no `pins/` path at all**; the baseline exists only locally at `~/Documents/nwly-pin/22469132/Bin64.sha256`. Verified via `git ls-files`, not the blob page (CHARTER §6.3). Consequence: the S0a Step-0 SHA check cannot run against the repo path from a fresh clone — it must use the local pin. **Action:** the file is charter-safe to commit (hashes only, no Amazon content), so commit it and the claim becomes true; until then it is a false claim about our own repo. Caught during S0a while walking the tree for the pin. **Resolved 2026-08-31: the file was committed this session, so §5's claim is now true; the S0a run itself used the local pin.** |
| "The three field names (`RepAddress`, `Signature`, `HostHash`) sit as **literal JSON keys the deserialiser clusters on**." — `S0A_PROMPT.md` Step 1, "Why this is answerable statically." | **FALSIFIED (S0a, §16.15).** They are not literal keys: `LoginQueueResponse` — zero matches; `RepAddress` — only in the case-9 log format string; `HostHash `/`TicketId ` — only as trailing-space .rdata label text; `Signature` — only in an AWS SigV4/error neighbourhood. The queue `Token` is deserialised through a **generic/reflective** AWS-SDK path (`Aws::JavelinGatewayService::Model::PostGameLoginQueueV2TicketIdRequest`), not a bespoke per-field parser. The string-xref anchor the prompt assumed did not exist; the trace used the `GameConnectionWrapper` log string and the +0x1100 object offset instead. This is why OPEN-3 closed inferred-not-traced (the field read-sites are not string-addressable). |
| "**No edits to Amazon's tree**, which keeps the charter's version-locking rule satisfied." — §7's `/opt/llvm14` decision. Also test #6: "No source edits required." | **WRONG, and it affects the build pin.** `dev/Code/Framework/AzCore/AzCore/RTTI/TypeInfo.h` reads `false_v<>` at lines 161/169/177/185/193; Amazon's original is `false_v<T>`. `git status --short` in `~/Documents/lumberyard` is **clean**, so the patch is committed to the fork, not a working-tree edit. Evidence: `rg -n 'false_v' dev/Code/Framework/AzCore/AzCore/RTTI/TypeInfo.h`. **Consequence:** §5's fork pin `413ecaf24d7a...` does **not** describe the tree that built. Charter §4 version-locking is satisfied by pinning the patched commit, not by the absence of edits. Caught because the recovered `CMakeLists.txt` documented the patch in a header comment — a file that was nearly discarded unread. **Both follow-up actions are now closed (tests #31, #32):** the patch is commit **`7d4f1ee6`**, the only one on top of `413ecaf`, and it is pushed. §5 now carries a read-from / built-from pair. Test #20's reproducibility result holds for `7d4f1ee6`. `-fdelayed-template-parsing` was briefly believed redundant on the strength of this patch — **that was wrong, see the next row.** |
| "`-fdelayed-template-parsing` is redundant now that `7d4f1ee6` patches `TypeInfo.h`." — inferred from `Vector3.cpp` compiling exit 0 without the flag (test #32). | **WRONG, and the probe was the problem.** The flag guards a *second, unrelated* defect: `std/containers/queue.h:202` reads `rhs.m_continer` where the member is `m_container` — a one-character typo in Amazon's source, inside `priority_queue::swap()`, an uninstantiated template body. `queue.h` is included nearly everywhere, so removing the flag costs **108 compile failures** (60/191 without, 151/191 with — tests #33, #34). `7d4f1ee6` fixes five `static_assert` sites and nothing else. **Cause of the error: `Vector3.cpp` is Math-only and never includes `queue.h`, so it could not have detected this.** Picking the TU that surfaced the *original* symptom felt like the right probe and was in fact the narrowest possible one. Lesson: a single-TU result generalises to the build only when the TU's include surface covers what is being tested. |
| "**C++ standard: C++14.** Waf sets `-std=c++1y`; pass `-std=c++14` to a standalone build." — §7 Build facts, stated as CONFIRMED from the Waf config. | **WRONG for any modern clang.** `AzCore/Math/Crc.inl:114` uses `auto` as a template parameter, a C++17 feature, and under `-std=c++14` that is a hard error with no flag that rescues it. `-std=c++17` compiles clean. Cause of the error: read the build *config* and treated it as the language level the *source* requires. `-std=c++1y` was what the 2019 clang was told; it is not what the code needs today. |
| "RTTI is stripped from `NewWorld.exe` — no mangled names found." Said in session after the first scan's RTTI regex returned nothing. | **WRONG.** The regex only matched fully-formed `.?AV...@ns@@` symbols; the binary carries mangled-name *fragments* (`UEAAXPEAVReplicaChunkBase`, `AEBV...ReplicatedState`) that a stricter pattern missed. RTTI survived. Cause: judged absence from one narrow regex rather than a broad mangled-fragment search. Ghidra's RTTI analyzer will confirm and recover the class tree. |
| "Expect Linux-path bugs at T4 step 5" — §7 and T4_PROMPT, reasoned from `AZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER` being undefined on Linux, i.e. Amazon compiled the secure tests out on this platform and so presumably never ran them. | **DID NOT MATERIALISE.** DTLS passed on the first run, on both clang 18 and clang 22, in the same 201 updates as plaintext. Zero Linux-path bugs. The inference was reasonable and the conclusion was still wrong: *untested* is not *broken*. The trait gates the **test harness**, not the driver, and the driver sits on `SocketDriverCommon`, which the plaintext path exercises constantly. Worth remembering before budgeting time against a similar warning. |
| "OpenSSL 3.x is a non-issue for `SecureSocketDriver.cpp`; modern OpenSSL needs no shim." — stated after the probe compiled clean, and written into §7. | **TOO STRONG.** `SecureSocketDriver.cpp:416` uses `DTLS1_RT_HEARTBEAT`, removed from OpenSSL after Heartbleed. It compiles only with `-DDTLS1_RT_HEARTBEAT=24`. Cause of the error: `t4_openssl_probe.cpp` enumerates *function calls*, so a removed *macro constant* was invisible to it. The probe's conclusion was right about the API era and wrong about completeness. Lesson: a probe proves what it tests, not what it was designed to reassure about. |
| "Step 2 is understated — expect an explicit `AllocatorInstance` bootstrap in `main()` just to get AzCore compiling." Raised in session. | **WRONG about the phase, right about the trap.** Compiling AzCore needs no bootstrap at all: 168/202 TUs build with the plain step-1 recipe and every failure is a missing 3rdParty header. The bootstrap is a *runtime* requirement and it surfaced exactly at step 4, as a segfault in a binary that linked cleanly. See §7. |
| "OpenSSL 3.x will break `SecureSocketDriver.cpp` at T4 step 5 — expect removed 1.0.2-era APIs (custom `BIO_METHOD`, `HMAC_CTX_init`, opaque-struct breaks)." Raised in session, never promoted past UNVERIFIED. | **WRONG.** The file is already 1.1.0-era API. Compiles with 0 errors / 3 deprecation warnings on OpenSSL 3.0.13; DTLS 1.2 handshake completes with the shipped certs. Cause of the error: predicted from Lumberyard's release date instead of reading the file. Two tells were visible in the source the whole time (`X509_get0_notBefore`, `BIO_s_mem`). Lesson is charter §4 verbatim — *prefer the source to the sample*. |
| "D2 datasheets will be in `assets/GameData.pak`" — inferred from the name before looking. | **WRONG.** `GameData.pak` holds zero. All 2250 are in `SharedDataStrm-part{1..11}.pak` + base. Cause of the error: inferred location from a filename instead of reading the central directory. A census across all 130 paks settles it in one pass and should have been step one. |
| "new-world-tools' documented path `assets/server/server.pak` is the datasheet source." — taken from the tool README. | **STALE for build 22469132.** No `assets/server/` directory exists in this install. The README predates the Aeternum relaunch. A session following it verbatim stalls here; go by the census, not the README. |
| "EOCD entry counts of exactly 65535 are 16-bit saturation, so the 2250 datasheet count is a floor." — raised in session on seeing four paks report 65535. | **WRONG.** A direct `PK\x01\x02` central-directory walk gave `walked == eocd` on every pak including all four. No Zip64 anywhere. 2250 is exact. The `-partN` split exists precisely to stay under the 65535 ceiling. Reasonable suspicion, wrong conclusion — and the check was cheap. |
| "Oodle (ZIP method 15) needs the MSVC redistributable, so Linux extraction is Proton-or-nothing." — inferred from the tool README listing MSVC as a dependency. | **WRONG.** `go-oodle-lz` + `ebitengine/purego` `dlopen` a **native** Oodle v2.9.13 fetched at first run. No wine, no PE DLL, no cgo. Built and extracted clean on Garuda. Cause of the error: read a dependency note written for the Windows release binaries and assumed it described the source. |
| "645 datasheets extracted in 173ms is suspiciously fast — likely a silent failure." — raised in session. | **WRONG.** Output verified column-by-column: `MasterItemDefinitions_Faction`, 127 columns × 4121 rows, legible headers. Oodle is simply that fast. Worth the check regardless — it is the D2 prompt's named failure mode — but speed alone was not evidence of anything. |
| "EAC ships as `EOSSDK-Win64/Win32-Shipping.dll`" — §10, written in a way that reads as implying `Bin64/`. | **IMPRECISE, and misleading in one specific way.** The EAC files live in `<install>/EasyAntiCheat/`, a **sibling** of `Bin64/`. A session scanning `Bin64/` alone would wrongly conclude EAC is absent. Corrected location is in §5. Charter §3 unchanged — location only. |
| "`SSLKEYLOGFILE` is honoured, so the client's decrypted stream is readable from a file with no hook — H1/H3 may be unnecessary." — raised in session (T3, 2026-08-29) on finding the keylog file populated (178 lines) and an incrementing byte pattern in the payload. | **WRONG for the world stream; true only for auth.** The keylog decrypts the TLS 1.2 HTTPS auth phase but **not** the DTLS world stream: the world ClientHello's client random (`0674c28f…5aa976`) is absent from the file and Wireshark reports `no decoder available` for every UDP/27001 record, while the TCP/443 flows show `dissect_ssl_payload decrypted`. The callback is wired into the general TLS `SSL_CTX`, not the GridMate `SecureSocketDriver` DTLS context. **H3's signature-scan hook on `SSL_read`/`SSL_write` is still required.** Cause of the error: a populated keylog file plus an incrementing payload run (actually the AES-GCM explicit-nonce counter, visible by design in ciphertext) were read as success *before* running the falsifiable check — the `tls.debug` decrypt log, which returned zero decrypts for the world flow. §12A. |
| "`SSL_CTX_set_cookie_generate_cb` not disabled." — §12A, P3 row (T3, 2026-08-29). Assumes OpenSSL owns the DTLS cookie exchange. | **WRONG — GridMate never used OpenSSL's cookie callbacks at all.** `rg 'set_cookie_generate_cb\|set_cookie_verify_cb'` over the whole of `dev/Code/Framework/GridMate/` returns **0** hits. The cookie is generated and verified by GridMate's own `SecureSocketDriver::GenerateCookie` (`:1699`) / `VerifyCookie` (`:1737`), driven from its raw-recv state machine (`:1838`, `:1869`) with a hand-built HelloVerifyRequest, **before OpenSSL sees the datagram**. Cause of the error: saw a wire behaviour that looked like OpenSSL's stateless-cookie feature and attributed it to the library without checking the source. **Consequence:** cookie length and mechanics move into the GridMate-**controlled** bucket (where they match retail exactly, 20 bytes both sides), and a private server must reimplement the derivation rather than enable a library callback. §12B, test #44. |
| "**Early renegotiation.** The server sends a HelloRequest, which triggers a *fourth* handshake message — a third ClientHello at frame 245. So the extra ClientHello is renegotiation, not a retransmit." — §12A, additional handshake observations (T3). | **WRONG about the mechanism; the observation itself was correct.** It is not renegotiation — it is stock GridMate's **cookie handoff**, and the reference build (`7d4f1ee6`) does exactly the same thing with no Amazon involvement. Proof: `message_seq` **resets to 0** on the third ClientHello (after the cookie-echo hello at seq 1), and that hello carries **no cookie**; a renegotiation would follow a completed handshake, not precede one. Mechanism is `CS_SEND_HELLO_REQUEST` (`:681`, `:792`, `:1200`, `:1876`), a dedicated server state entered after cookie verification, with exponential-backoff resend (`:821`–`:837`). Cause of the error: a server-initiated HelloRequest *is* renegotiation in ordinary TLS, so the standard reading was applied to a transport that uses the message for something else. **Consequence: a hard S-track requirement** — the server must send a HelloRequest after verifying the cookie or the client stalls at `message_seq 1`. §12B, test #47. |
| "Retail will show three cleartext ClientHellos and the reference two, the third being the HelloRequest-triggered renegotiation; do not mix it into the diff." — raised in session (T5, 2026-08-29) as a caution when building the Step 3 filter. | **WRONG — the reference shows three as well, and emits its own HelloRequest.** Both captures show the identical `0, 20, 0` cookie-length pattern across three ClientHellos plus a type-0 HelloRequest at the same position. The caution was harmless (pinning `frame.number` was still right) but its reasoning was the §12A renegotiation error inherited uncritically. Cause of the error: predicted a retail-only behaviour from a retail-only observation without asking whether the reference did it too — which is the exact question the reference build exists to answer (CHARTER §2). Test #47. |
| "The HelloVerifyRequest is DTLS 1.0 (`fe ff`) … RFC 6347 §4.2.1: the server is stateless at that point and has not negotiated a version." — §9. | **NOT WRONG, BUT INCOMPLETE — and the real mechanism is more useful.** The RFC permits it, but the actual cause is that GridMate **hardcodes** `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) in its hand-packed records (`:308`, `:312`, `:343`). This moves the `fe ff` version from "OpenSSL/RFC default" into the **GridMate-controlled** bucket, where it matches retail exactly. **Diagnostic value:** every `fe ff` record in a capture is a GridMate hand-pack — exactly two per handshake (HelloVerifyRequest, HelloRequest). §9's advice not to chase it stands. §12B. |
| "**Auth / server-list is a separate TCP/443 HTTPS phase to AWS** (`44.220.67.249` ×3, `13.217.79.62`, `18.238.35.71`)." — §12A, Transport named (T3, 2026-08-29). | **WRONG on all three hosts, and the error is the same one three times: AWS ownership inferred from IP, never checked against SNI.** By SNI: `44.220.67.249` is **kinesis telemetry**, `18.238.35.71` is **`d1hkbwzm1bktgo.cloudfront.net` (CDN)**, and `13.217.79.62` **appears nowhere in the T3 capture at all** — not in any ClientHello, not in `conv,tcp`. The `13.217.79.*` range *is* real and *is* auth-adjacent: it resolves to **`sts.us-east-1.amazonaws.com`** (P0, frame 485, host `13.217.79.90`). Cause of the error: "AWS-owned TCP/443 near login" was read as "the auth phase" without ever reading a server name. Same class as the `GameData.pak` and `assets/server/` rows. **Consequence:** the real auth host set is in §16.2, and `P0_PROMPT.md`'s Scope section inherits the wrong list and must be struck. §16. |
| "**Start `tcpdump` while the game is fully quit, then launch.**" — §12A, capture procedure (T3), presented as the procedure that makes a capture good. | **NOT WRONG, BUT ITS SCOPE IS OVERSTATED — and that cost a session.** What the procedure guarantees is that the **world socket** opens inside the capture window, which is all T3 and T5 needed. It does **not** guarantee the **login phase** is inside the window: the T3 captures were started at world-load, so all three contain the DTLS handshake and **none** contains an auth exchange. A P0 session reading §12A would reasonably believe those captures were suitable; they were not. Evidence: across all three T3 pcaps, the only TLS ClientHellos preceding the world handshake are telemetry and config, and six streams totalling 54.9 MB pre-date the capture entirely. **Corrected procedure for auth-phase work:** sign out *inside the client*, quit the client **and Steam**, close other network applications, truncate the keylog, start `tcpdump` on `enp2s0`, then launch. §16.1. |
| "Application data is probably **HTTP/2** and probably compressed; tell tshark so, rather than concluding the bodies are binary." — `P0_PROMPT.md`, Scope, written 2026-08-30 as a warning against a predicted failure mode. | **WRONG, and the warning caused the failure it was meant to prevent.** Every game auth flow is **HTTP/1.1** (`aws-sdk-cpp/1.7.193`). The `http2.*` filters built on this advice returned empty on 148 successful decrypts, which read as "no traffic" rather than "wrong dissector." Cause of the error: predicted the protocol from "modern AWS API" instead of reading ALPN or checking `_ws.col.Protocol`. **Lesson, and it generalises past this row: an empty tshark result is not a finding until `tls.debug_file` has been read.** §16.8. |
| "The address will most likely be **split across fields rather than as `ip:port` in one string** — so grep both halves independently, and don't conclude from a failed search on the joined form." — raised in session (P0b, 2026-08-30) as a caution before reading the queue response. | **WRONG, and backwards.** `Token.RepAddress` is exactly the joined form: `"35.71.190.194:44727"` — one string, one field, colon-separated. Cause of the error: generalised from the `getlogininfo` world list's field-per-attribute style (§16.3) to a response that had never been read. The caution was harmless in practice — the searches run were independent anyway — but it is the same class as the `http2` row above: predicting a format from an adjacent format instead of reading it. §16.10, test #56. |
| "**`GUID2` in `{WorldId}_{GUID2}` is unidentified.** Candidates: instance, shard, or channel." — §16.7 / OPEN-2 (P0, 2026-08-30). | **ALL THREE CANDIDATES WRONG.** `GUID2` is the **queue ticket id**: `Token.TicketId == GUID2`, and the outer `TicketId` is literally `"{WorldId}_{GUID2}"`. It is **minted by the server** in the enqueue response (frame 1586 of `p0b`) and echoed back by the client on redemption, so it is not a client-supplied parameter at all. A `CharacterId` hypothesis raised at the start of the P0b session was also falsified (`Token.CharacterId != GUID2`). Cause of the error: the candidate list was drawn from what a *world-selection* parameter could plausibly mean, without considering that the endpoint is a **queue** and the segment might identify the queue entry. §16.12, test #57. |
| "Same world **host** across captures a day apart but a **different port each session** (`44727` → `24083`)." — §16.5, prediction 4 (P0, 2026-08-30). | **THE PORT CLAIM IS WRONG AS STATED.** P0b observed `35.71.190.194:`**`44727`** again — the same port as `p0_login`, a day later, across a full Steam re-login and a cold launch. Three datapoints now read `44727` → `24083` → `44727`, which is not per-session assignment; it looks like a small set of listeners the client is dealt from. Cause of the error: two datapoints that happened to differ were read as a per-session *rule* rather than as two draws from an unknown distribution. **Consequence: none for S0** — the address is delivered explicitly in `Token.RepAddress` either way, so its stability was never load-bearing. Recorded because §12A was corrected on the strength of this claim. §16.10. |
| "Separately **falsified in the strong form**: the address is *not* in any readable auth body — exhaustive search across all exported HTTP objects and decrypted records … returned nothing but two false hits inside `.dds` textures." — §16.5, prediction 1 (P0, 2026-08-30). | **TRUE AS SCOPED, SUPERSEDED AS PHRASED.** The search was exhaustive over the bodies readable *at that time*, and the one body that carries the address was precisely the one that did not decrypt. P0b decrypted it; the address is there, in plaintext ASCII, as `Token.RepAddress`. This row is not an error — the scope qualifier was doing real work — but the phrase "not in any readable auth body" invites the wrong generalisation on re-reading, and **prediction 1 is now CONFIRMED** (§16.10, §16.14). Lesson, and it is §16.8 from the other direction: an exhaustive search is bounded by what the instrument could open, and that bound belongs **inside the sentence**, not in a caveat elsewhere. |

| "**Protobuf choke point (FIND-2 / P2):** All 10 types go through AWS SDK model serialization. The move-constructor family (`FUN_146406a90` and siblings) embed named Javelin model vftables directly. P2 should target the AWS SDK `SerializePayload` / `GetBody` path on these model types to locate the protobuf schema boundary." — §17.5 (H2, 2026-09-04). | **FALSE — there is no protobuf schema boundary on that path, and no protobuf anywhere near the Javelin models.** P2 scanned the entire binary the same day and recovered **3** `FileDescriptorProto` blobs: `campfire_event_default.proto` (Campfire telemetry), `google/protobuf/empty.proto`, `google/protobuf/descriptor.proto`. No Javelin descriptor, no `service` block, **`application/x-protobuf` = 0** against **`application/json` = 236**. The AWS SDK path is **JSON**, which §16.15 had already demonstrated from the other direction by reading queue-`Token` fields out of the stock `JsonView` GetString helper — the evidence was in this file before H2 wrote the claim. Protobuf in `NewWorld.exe` serves Campfire telemetry and nothing else. **Lesson: "X and Y are both present in the binary" is not evidence that X serialises Y.** §17.9. |
| "`InitializeReplicatedFields` **94** — matches T1/§10's independently-derived ~94, an instrument cross-check that passed" and, in the Track P retarget, "The world stream is **GridMate `ReplicaChunk` marshalling** (`ReplicaChunk` 23, `InitializeReplicatedFields` 94, plus §10's `VTransformReplicaChunk` …)" — §17.9 (P2, 2026-09-04). | **WRONG — `InitializeReplicatedFields` is not a GridMate symbol.** It is a virtual on `Javelin::*ComponentServerFacet` classes, i.e. **`Amazon::Hub`**, and is absent from the whole of `dev/Code/Framework` (AzCore + AzFramework + GridMate) at the pinned commit `7d4f1ee6`. The count matching T1's ~94 was a genuine cross-check of the **number**; the **attribution** was inherited from §10 and never verified. Those 94 references are evidence for **Hub**, not for GridMate replicas. The retarget conclusion was therefore right by accident and for the wrong reason: Track P did need to leave protobuf, but its destination is Hub (§18), not GridMate replica marshalling. **Lesson: an instrument cross-check that confirms a number does not confirm what the number is about.** §18.0, §18.1. |
| "Note P3 depends on this: GridMate's transform marshalers **quantize**, so a raw float triple is the wrong thing to look for." — `CHUNKS.md`, P5 stub (2026-09-04). | **FALSE for the defaults.** `Marshaler<AZ::Vector3>` writes three **raw IEEE floats** (12 bytes) and `Marshaler<AZ::Transform>` four of those (**48 bytes, uncompressed**) — `Serialize/MathMarshal.h:59,186` at `7d4f1ee6`. Quantizing marshalers exist (`Float16Marshaler`, `Vec3CompRangeMarshaler`, `TransformCompressor`, `IntegerQuantizationMarshaler`) but are **opt-in per DataSet declaration**, not the default. **P3 should search for a smoothly varying raw float triple after all.** Whether New World opts in per-DataSet is unresolved — OI-P5-3. §18.4. |
| "`CreateName` is MD5 over the name" — `P6_PROMPT.md` Step 1.2 (2026-09-04). | **FALSE — it is SHA-1.** `Uuid.cpp:285` forwards `CreateName` to `CreateData` (`:293–322`), which builds a `Sha1`, calls `ProcessBytes`/`GetDigest` into five `u32`s and writes them big-endian; `AzCore/Math/Sha1.h` included at `:15`, no MD5 include anywhere. The version nibble written is 5 (`data[6] &= 0x5F; |= 0x50`, `:315–317`, comment `VER_NAME_SHA1`). `VER_NAME_MD5 = 3` (`Uuid.h:40`) is a decode-only case in the version getter (`:386`) and is never written. **A session trusting the prompt would have implemented MD5, failed to reproduce the cached bytes, and had a live path to a false negative on OI-P5-1 that looks like a clean result.** §19.2. |
| "Scan for the brace-delimited pattern `{XXXXXXXX-XXXX-...}`" — `P6_PROMPT.md` Steps 1.1 and 2b (2026-09-04). | **FALSE as a universal.** Both forms are present and both are parsed by `CreateStringSkipWarnings` (length window `[32,38]`, explicit brace handling). `ReplicateClient` and `REPClient` are unbraced; `PingMsg` and 5,930 others are braced. Brace style is a per-translation-unit authoring habit and discriminates nothing. A brace-anchored `.rdata` scan recovers a fraction of the set. §19.2. |
| "`FUN_1407fbe00` … caches 16 bytes computed by `FUN_1413e84b0`" — §18.3 (P5, 2026-09-04). | **True at runtime, misleading statically.** The slot is a lazily-initialised MSVC function-local static and `_DAT_14a2e7750` reads as **all zeros in the on-disk image**. A static reader who goes to the address concludes the claim is false. This also rules out harvesting the vocabulary from `.data`: on disk the identities exist only as `.rdata` string literals. §19.1, §19.7. |
| "The vftable layout is uniform across Hub types (8 slots, name / identity compare / visitor dispatch in slots 0–2)" — §18.3 and `P6_PROMPT.md` prediction 3 (2026-09-04). | **FALSIFIED — OI-P5-4 answered.** `FragmentUpdateMsg`'s handler table at `147f44828` has **4** entries against `ReplicateClient`'s **8** at `147f42110`. §18.3 is restated as a **single-instance observation**. Honest caveat: these may be different *kinds* of object (a message handler vs a type), so the claim is that layout is not uniform across Hub types, not that §18.3 was wrong about `ReplicateClient`. §19.7. |
| "The Hub type vocabulary is recoverable by walking `CreateString` call sites" — `P6_PROMPT.md` Step 2b premise (2026-09-04). | **PARTLY FALSE, and the correction is the chunk's main finding.** That walk recovers 5,907 accessors at 99.4% resolution — but it is the **engine's `AZ_TYPE_INFO` vocabulary**, and **none of the ten session-layer message types are in it**. Hub message types register through `FUN_1407de270` with the UUID parse **inlined**, so there is no call site to find. **Lesson: a mechanism present in the binary and used by most types is not therefore the mechanism the layer you care about uses.** §19.3, §19.4. |
---

## 14. Test / capture log

A numbered, append-only log of every experiment run, its prediction, and its
result — so no test is silently retried and no result is remembered wrong.

| #   | Test / capture | Prediction | Result |
| --- | -------------- | ---------- | ------ |
| 1 | Compile + link a probe TU reproducing every OpenSSL call site in `SecureSocketDriver.cpp` @ `413ecaf`, `-std=c++14`, against OpenSSL 3.0.13 headers/libs. | Hard errors from APIs removed after 1.0.2. | **Prediction falsified.** 0 errors, 3 deprecation warnings, links and runs clean. Artefact kept as `t4_openssl_probe.cpp`. |
| 2 | Live DTLS 1.2 handshake (`openssl s_server`/`s_client`) using the `Certificates.cpp` cert+key and the hardcoded `ECDHE-RSA-AES256-GCM-SHA384`, OpenSSL 3.0.13. | Rejected on security level or cipher policy. | **Prediction falsified.** `Protocol: DTLSv1.2`, `Cipher: ECDHE-RSA-AES256-GCM-SHA384`, `Verify return code: 0 (ok)`. |
| 3 | `openssl ciphers -s -v 'ECDHE-RSA-AES256-GCM-SHA384'` on the actual target machine (Garuda, OpenSSL 3.6.4). | Cipher still listed at default seclevel. | **Confirmed.** Listed, `TLSv1.2 Kx=ECDH Au=RSA Enc=AESGCM(256) Mac=AEAD`. |
| 4 | Compile `t4_openssl_probe.cpp` on the target machine: **clang 22, OpenSSL 3.6.4**, `-std=c++14`. | 0 errors, the same 3 deprecation warnings. | **Confirmed exactly.** 0 errors; 3 warnings (`ERR_load_BIO_strings`, `ERR_load_SSL_strings`, `DTLSv1_2_method`). Crypto-library question for T4 step 5 is closed. Side result: clang 22 accepts `-std=c++14` on this TU without complaint — a first, narrow data point for step 1. |
| 5 | `clang++ -std=c++14 -Wno-error -c AzCore/Math/Vector3.cpp -I AzCore -I AzCore/Platform/Linux` on clang 18. | Clean, or errors from removed C++14-era features (which would trigger `/opt/llvm14`). | **Falsified, and in an unexpected direction.** First a missing include dir surfaced (`Platform/Common/SIMD`), then 7 errors — but of a *different kind* than predicted: a dropped libstdc++ transitive include and a clang strictness change, not removed language features. `/opt/llvm14` not needed. |
| 6 | Same TU, add `-include utility`, then `-fdelayed-template-parsing`. | Both are flag-fixable; no edits to Amazon's tree needed. | **Confirmed at the time, and the second half was later falsified.** 7 → 5 → 0 errors. The "no source edits required" conclusion was wrong: the fork's `TypeInfo.h` was subsequently patched and committed. See §13. |
| 7 | Same TU, `-std=c++14` plus both fix flags. | Clean. | **Falsified.** 1 error: `Crc.inl:114`, `auto` template parameter requires C++17. This is what killed the C++14 claim — see §13. |
| 8 | `clang++ -std=c++17 -include utility -fdelayed-template-parsing -w` on `AzCore/Math/Vector3.cpp`, target machine, clang **22**. | Clean, matching clang 18. | **Confirmed.** exit 0, no diagnostics. Recipe holds across four clang majors, so it is not an artifact of one compiler build. |
| 9 | Same recipe on `AzCore/Math/Sfmt.cpp` (pulls `std/parallel/lock.h` + `Module/Environment.h`), clang 22. | Clean — though `Module/Environment.h` was flagged as the likelier to break, being the most platform-conditional. | **Confirmed, prediction held.** exit 0. AZStd threading and the allocator/environment bootstrap both compile under the recipe. |
| 10 | Compile every AzCore TU (202, excluding Windows/Apple/Android/Tests) with the step-1 recipe. | Some genuine failures on the AZStd or EBus surface. | **Confirmed clean.** 168 built, 34 failed, and **every** failure is `file not found` for rapidjson (27), Lua (6), rapidxml (1). All are Lumberyard 3rdParty absent from the repo; none are on GridMate's dependency surface. `libazcore.a`, 31M, 168 objects. Triage by error-kind grouping via `triage.sh`. |
| 11 | Compile all 41 Linux GridMate TUs with the same recipe plus `-DDTLS1_RT_HEARTBEAT=24`. | A few failures on the platform layer. | **41/41, zero failures.** `libgridmate.a`, 4.9M. Step 3 done. |
| 12 | Link `nwly_carrier_probe.cpp` against both archives with `-lssl -lcrypto -lpthread -ldl`. | Undefined symbols, probably from the gmock/zstd objects in the archive. | **Confirmed, linked first try.** No undefined symbols; archive semantics mean unreferenced objects are never pulled. |
| 13 | Run the linked probe. | Runs. | **Falsified — segfault.** `IAllocator::GetAllocationSource()` on a null allocator: `OSAllocator` did not exist when `azmalloc` supplied `SystemAllocator`'s heap. Found with ASan. See §7 trap 1. |
| 14 | Re-run with `OSAllocator` created first. | Runs. | **Falsified — use-after-free.** `Callbacks` destructors ran after allocator teardown, calling `BusDisconnect()` on a freed EBus context. Harness bug, not GridMate. See §7 trap 2. |
| 15 | Re-run with EBus handlers in an explicit scope. | Session completes. | **PASS — T4 milestone.** Handshake, payload round-tripped both directions, clean teardown, exit 0, 201 of 2000 updates. Reproduced identically on clang 18 and on the target clang 22. |
| 16 | Decode a live capture against the Carrier layout read from `Carrier.cpp`. | Layout matches, if it was read correctly. | **Confirmed.** All datagrams decode, consuming every byte with no trailing remainder. Multi-message datagrams confirm the inverted `MF_SQUENTIAL_*` semantics. 1-byte `0x47` frames identified from source as the SocketDriver wakeup, not protocol. §8. |
| 17 | Build the probe with `Certificates.cpp` and `SecureSocketDriver` on both `CarrierDesc`s; run it. | Failure somewhere in Amazon's untested Linux DTLS path. | **Falsified — passed first run.** Handshake completed, payload round-tripped both ways, 201 of 2000 updates, identical to plaintext. Reproduced on clang 18 and on the target clang 22. See §13. |
| 18 | Capture the `--secure` session and re-run the §8 Carrier decoder over it. | Carrier framing no longer visible. | **Confirmed.** 0/30 parse as Carrier; 30/30 parse as DTLS 1.2 ApplicationData at epoch 1. |
| 19 | Search the `--secure` capture for the literal payload string. | Absent if encryption is real. | **Confirmed absent — 0 datagrams.** This, not the PASS line, is what establishes the traffic is actually encrypted. |
| 20 | Rebuild archives from scratch after `build/` was deleted, re-run plaintext capture. | Byte-identical traffic. | **Confirmed.** Datagram 2 reproduced exactly (`00 02 a0 00 05 03 ...`). The build is reproducible; `build/` is safe to delete. **Scope caveat added later:** reproducible from the *patched* fork tree, not from bare `413ecaf` — see §13. |
| 21 | Decode a `--secure` capture taken from before the session opens. | ApplicationData only, as in the earlier mid-session capture. | **Richer than expected.** Caught the full cookie exchange at epoch 0: ClientHello (DTLS1.2) / HelloVerifyRequest (DTLS**1.0**) / ClientHello with the 20-byte cookie echoed. Confirms §7's pre-T4 reading of the `HandshakeHeader`. See §9. |
| 22 | Search the `--secure` capture for the literal payload string, on the target machine. | Absent. | **Confirmed, 0 matches.** Note `grep -c` exits 1 on a zero count, so the shell reports an error on success — the count is the result, not the exit code. |
| 23 | T1: `strings` fingerprint of `NewWorld.exe` for engine family. Predicted GridMate (2016 LY origin). | GridMate present, O3DE absent. | **Confirmed.** 43 GridMate hits incl. `TransportLayerGridMate`; the sole O3DE hit was the gameplay struct `TransformLinkConnectionData`. Crypto fell out: OpenSSL 1.1.1k, static, `SSL_read`/`SSL_write`. Protobuf in the game binary. §10. |
| 24 | D2: identify the pak container from header bytes of `assets/GameData.pak`. | Standard ZIP, magic `50 4b 03 04` at offset 0. | **Confirmed.** `50 4b 03 04`; first local header parses (41 bytes stored, name len 0x24 = `libs/flownodes/flownodeblacklist.xml`). All 130 paks open as zip, 0 failures. |
| 25 | D2: locate the `.datasheet` files across all 130 paks. | In `GameData.pak`, by name inference. | **Falsified.** Zero in `GameData.pak`. All 2250 in the `SharedDataStrm*` family; part6=645, part4=628, part5=569 carry 82% of them. See §13. |
| 26 | D2: test whether EOCD counts of 65535 are 16-bit saturation, by walking `PK\x01\x02` records directly. | Saturated; 2250 is a floor and the true count is higher. | **Falsified.** `walked == eocd` on every pak. No Zip64. 2250 exact. `-part12`/`-part13` are 22-byte empty-archive stubs; `-part14` has 3928 entries and 0 datasheets. |
| 27 | D2: build new-world-tools `@e51c79a9` natively on Garuda and extract method-15 (Oodle) entries. | Fails — MSVC/PE-DLL dependency forces Proton. | **Falsified.** `go build` clean; runtime `dlopen` of a native Oodle v2.9.13 (+ `libtexconv.so`), both auto-downloaded on first run. Extraction succeeded. Note: the tool fetches binaries from the network — relevant to any air-gapped re-run. |
| 28 | D2: bulk-extract every `.datasheet` and compare against the independent census. | 2250, matching the central-directory count. | **Confirmed.** `pak-extracter` produced exactly 2250 → 2250 JSON. Two independent code paths agree, so neither is silently dropping entries. 198 of 2250 stored (method 0), 2052 Oodle. |
| 29 | Enumerate every module in `Bin64/` and check against §10's static-linkage claim, which rested on a `find` returning empty. | No `*ssl*`/`*crypto*` module; inventory otherwise unremarkable. | **Confirmed, and richer than predicted.** 22 files, no crypto module — linkage claim now positive rather than absence-based. Three unanticipated findings: `vivoxsdk.dll` (second network stack, contaminates T3), no `steamnetworkingsockets` (weak evidence against SDR), `libcds-amd64-vcv141.dll` unidentified. |
| 30 | Check whether the Lumberyard fork tree is modified, after a recovered `CMakeLists.txt` comment referenced a "TypeInfo.h patch" that §7 and test #6 said did not exist. `git status --short` + `rg -n 'false_v' .../RTTI/TypeInfo.h`. | Tree clean and unmodified; the CMake comment is stale. | **Falsified — the tree is patched.** `false_v<>` at lines 161/169/177/185/193 (Amazon's original is `false_v<T>`), with a **clean** `git status`, so the patch is committed. §5's pin `413ecaf` does not describe the tree that built. See §13. |
| 31 | `git log --oneline 413ecaf..HEAD` in the fork — how much has accumulated on top of the pinned commit? | One commit, the `TypeInfo.h` patch. Possibly more, since nobody had looked. | **Confirmed, prediction held exactly.** Exactly one commit: **`7d4f1ee6`** *"AzCore: fix false_v<T> static_assert for modern clang (template-template param can't be a template arg)"*. `HEAD -> master, origin/master, origin/HEAD` — pushed, not local-only. §5 now records read-from (`413ecaf`) and built-from (`7d4f1ee6`) separately. Closes the §13 open action. |
| 32 | Drop `-fdelayed-template-parsing` and compile `AzCore/Math/Vector3.cpp` — the TU that originally produced the five `TypeInfo.h` diagnostics (test #6). Is the flag still needed now the source is patched? | Exit 0 — the `7d4f1ee6` patch fixes the same diagnostics at source, making the flag redundant. | **Confirmed for this TU, and the conclusion drawn from it was wrong.** exit 0, no diagnostics. But `Vector3.cpp` is Math-only and never includes `std/containers/queue.h`, which is where the flag actually earns its keep — see #33/#34. A single-TU probe whose include surface does not cover the thing being tested. §13. |
| 33 | Run `triage.sh` (which carries no `-fdelayed-template-parsing`) over AzCore, as a full-build version of #32. | 168/202, matching test #10 — i.e. the flag is redundant. | **Falsified, badly.** 60/191, with **108** `no member named X in X` failures. Two variables differed from #10 at once (flag absent *and* a different file set — 191 vs 202, `triage.sh` includes Android TUs that `build_gridmate.sh` excludes), so this run alone proved nothing. Reading the actual error text is what settled it. |
| 34 | Add `-fdelayed-template-parsing` to `triage.sh` and re-run AzCore — change exactly one thing from #33. | The 108 `no member named` failures vanish; ~40 `file not found` remain. | **Confirmed exactly.** **151/191**, all 108 gone, remaining 40 are `file not found` only (jni.h, rapidjson, Lua, rapidxml). Root cause identified from the error text: `std/containers/queue.h:202` spells `rhs.m_continer` instead of `m_container` — one typo in an uninstantiated template body, invisible under delayed parsing, fatal without it. The flag is load-bearing. §7, §13. |
| 35 | `triage.sh` enumerates 191 AzCore and 36 GridMate TUs; `build_gridmate.sh` enumerated 202 and 41 (tests #10, #11), and `triage.sh` picks up Android TUs (`APKFileHandler.cpp`, needs `jni.h`) that the recorded run excluded. Diff the two file-selection expressions. | The scripts' `find` predicates differ in platform exclusions; `build_gridmate.sh` is the one whose counts the archives were built from. | **Confirmed, prediction held.** `build_gridmate.sh:87` filters `EXCLUDE='/(WinAPI\|Windows\|Android\|Apple\|AppleTV\|Mac\|iOS\|Salem\|Provo\|Jasper)/\|/Tests?/'` through `grep -Ev`; `triage.sh:26,29` does a bare `find` on `AzCore` + `Platform/Linux` with no exclusion, so it walks `Android/` and inflates the failure count with `jni.h` misses. **`build_gridmate.sh`'s 202/41 are authoritative** — they are what produced `libazcore.a`/`libgridmate.a`. `triage.sh` is a triage tool; its wider net doesn't change error-kind grouping, so it is left as-is. No code change. |
| 36 | **T3** first retail capture: start `tcpdump`, reach in-world, then search the game flow for epoch-0 handshake (type-22) records. | Handshake present. | **Falsified — timing.** Game UDP flow `27001↔52.223.16.88:54888` had `conv,udp` `Start 0.000000` — the world socket was already open when tcpdump began. 0 type-22 records; all epoch-1 ApplicationData. The socket opens earlier than "enter world" (during creation/cut-scenes). Capture discarded, not analysed. |
| 37 | **T3** second retail capture: fresh character, `tcpdump` started **before** launch; search for DTLS handshake records. | Handshake now inside the file. | **Confirmed.** Game flow `Start 18.575s` (socket opened after capture began). Type-22 sequence present: ClientHello(1)/HelloVerifyRequest(3)/ClientHello(1) at frames 241/242/243, full flight through Finished. `t3_retail_b22469132_20260829-203901.pcap`; epoch-0 extracted to `t3_handshake_epoch0.pcap`. §12A. |
| 38 | **T3 · P4** count cipher suites on the retail ClientHello. | Exactly one, `0xC030`. | **Confirmed.** `0xC030,0x00FF` — one real suite (ECDHE-RSA-AES256-GCM-SHA384) plus `0x00FF`, the renegotiation-info **SCSV** (not a cipher). Matches reference hardcode `SecureSocketDriver.cpp:1494`. T5 structural-match stands unqualified. |
| 39 | **T3 · P3** is the DTLS cookie echoed verbatim? | ClientHello → HVR(`0xfeff`) → ClientHello with the same cookie. | **Confirmed.** Cookie `eb14bc1b7aaadacffb30cd3334bc814690591056` on the HelloVerifyRequest (frame 242, `0xfeff`) and echoed on the retry ClientHello (frame 243, `0xfefd`); first ClientHello (241) carries none. |
| 40 | **T3 · P2** run `decode_carrier.py` against the retail capture; predict a loopback/offset break. | Ethernet-vs-loopback offset or a `127.0.0.1` filter breaks it. | **Falsified (no break).** Decoder ran unmodified: 8618/8637 datagrams as DTLS 1.2, 0 Carrier. Both loopback and `enp2s0` are `DLT_EN10MB`, so no offset issue. 19 undecodable = ChangeCipherSpec (content type 20, no decoder branch) + Brave/QUIC strays on `:50229`. Also surfaced: server HelloRequest (early renegotiation) and CertificateRequest (type 13, mutual auth). §12A. |
| 41 | **T3 · H-track** launch once with `SSLKEYLOGFILE` set; does the client honour it? | Negative — the keylog callback is usually stripped from a shipped OpenSSL. | **Split result.** File **written**, 178 lines. **Auth/HTTPS DECRYPTS** (TCP/443; `tls.debug` `dissect_ssl_payload decrypted`). **World DTLS does NOT**: world ClientHello random `0674c28f…5aa976` absent from keylog; `tls.debug` `no decoder available` for every UDP/27001 record. Callback wired into the general TLS context, not the GridMate DTLS `SSL_CTX`. **H3 signature-scan hook still required** for the world stream; keylog gets the auth phase free. §12A, §13. |
| 42 | **T5 · Step 0** verify `build/carrier_dtls.pcap` contains epoch 0, not merely that the file exists (`conv,udp` + count `dtls.record.content_type==22`). | Handshake present, or regenerate. Test #18's `--secure` capture was 30/30 epoch-1 with no handshake, so existence alone proves nothing. | **Confirmed, no regeneration needed.** 16 type-22 records. Flow `127.0.0.1:4427 ↔ 4428`; the two self-addressed rows are `'G'` wakeups (215 bytes / 5 frames = 43 = 14+20+8+1, confirming §8). Server is **4428** — the heavier direction (4,840 B), which sends the cert flight. |
| 43 | **T5 · Step 2** read `SecureSocketDriver.cpp` for every explicitly-set `SSL_CTX` field, to fix the GridMate-controlled list **before** diffing bytes (CHARTER §4). | A short list: cipher, version, maybe verify. Everything else library default. | **Confirmed, and richer than predicted.** Only `SSL_OP_NO_QUERY_MTU` is set via `set_options`; **no** `set1_groups`/`set1_curves`/sigalgs/SNI/ALPN anywhere; `SSL_CTX_set_ecdh_auto` is a 3.x no-op. Unanticipated: the cookie is GridMate's own (see #44) and `RecordHeader::m_version` is hardcoded `DTLS1_VERSION`. Also surfaced `SSL_CTX_set_ex_data` driver back-reference (H-track, recorded only). |
| 44 | **T5 · Step 2** `rg 'set_cookie_generate_cb\|set_cookie_verify_cb'` across all of `dev/Code/Framework/GridMate/`. | Present — §12A assumed OpenSSL owned the cookie exchange. | **Falsified — 0 hits tree-wide.** The cookie is GridMate's own `GenerateCookie`/`VerifyCookie`, hand-built HVR, before OpenSSL sees the datagram. Moves cookie mechanics into the GridMate-controlled bucket. §12B, §13. |
| 45 | **T5 · P3** cross the `:1522`–`:1553` verify-mode source read against CertificateRequest (13) and client Certificate (11) on both wires. | Uncertain going in — `SSL_VERIFY_PEER` appears in the file, but the `:1525` branch **assigns** `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` rather than OR-ing it, which alone is `SSL_VERIFY_NONE`. Predicted type 13 on both sides if the default (`false`) path is taken. | **Confirmed, prediction held.** CertReq from the server on both (ref frame 12 / port 4428; retail frame 10 / 52.223.16.88). **Client Certificate present but length 0 on both** (ref frame 14; retail frame 12 from 192.168.1.33). Mutual auth is stock; the client presents nothing. **S-track requirement removed:** no client PKI, no embedded cert to find in `NewWorld.exe`. |
| 46 | **T5 · P1/P2** field-by-field ClientHello diff, frames pinned, first hello each side. | GridMate-controlled fields identical; extension block differs on 1.1.1k-vs-3.x defaults. | **Confirmed, both halves.** Version `0xfefd` and one real suite `0xC030` identical; extension **type list character-identical** (`11,10,35,22,23,13`). Four noise divergences, all in unset fields: RFC 5746 SCSV-vs-ext-65281 (perfectly anticorrelated; byte level `00 04 c0 30 00 ff` vs `00 02 c0 30` + `ff 01 00 01 00`), sigalgs 23-vs-20 (SHA-1 dropped in 3.x), `supported_groups` last-two transposed, `ec_point_formats` `03 00 01 02` vs `01 00`. Fully accounts for the 146-vs-141 length difference. |
| 47 | **T5** dump the full ordered handshake sequence with `message_seq`, both sides, to classify the third ClientHello. | Retail three hellos and a HelloRequest; reference two and none — i.e. §12A's renegotiation is retail-specific. | **Falsified — both sides identical: three hellos and a HelloRequest each.** Same types, same order, same `message_seq`. The third hello **resets to seq 0 with no cookie**, so it is the GridMate cookie handoff, not renegotiation. §12A corrected (§13). The HelloRequest is **byte-identical across retail and reference**, all 25 bytes — a GridMate hand-pack, and the single strongest structural-identity result in T5. Only structural difference: which oversized message fragments (retail SKE frames 8–9, ref Certificate frames 9–10), from the 958-vs-1380 cert sizes hitting PMTU. |
| 48 | **T5 · P4** run `decode_carrier.py` over both epoch-0 flights. | Both parse through the same code path, no special-casing. | **Confirmed.** Retail 16/16 DTLS, 0 Carrier, **0 undecodable**. Reference 57 DTLS + 7 wakeup, 0 Carrier, **0 undecodable**. Same 13-byte `RecordHeader` / 12-byte `HandshakeHeader`, same type sequence. The §12A type-20 CCS gap did not arise (the extracted file stops before CCS) and **remains open**. |
| 49 | **T5** `openssl s_client -dtls1_2 -connect 127.0.0.1:1` to confirm local 3.6.4 emits ext 65281 rather than SCSV. | Local hello shows 65281 and no SCSV, pinning the RFC 5746 difference on the library. | **Inconclusive, and unnecessary.** Port 1 refused (`write:errno=111`) before any ClientHello was emitted; nothing to inspect. Not retried: the reference capture **is** the 3.6.4 datapoint, and test #43 established GridMate never sets that field, so the bucket holds by construction. Recorded so it is not re-attempted. |
| 50 | **P0 · Step 0** pair the keylog against the T3 pcaps: pull every `tls.handshake.type==1` random on TCP/443 and grep `nwly-keylog.txt` for each. | All randoms present — the T3 captures are valid P0 inputs. | **Confirmed for pairing, and the input was still wrong.** 14/15 randoms paired; the miss was `api.github.com` (a browser/git process, correctly absent from the client's keylog). But **no auth exchange exists in any T3 capture** — only two TLS ClientHellos precede the world handshake and both are telemetry/config. The captures were started at world-load. See §13. **`ls -la` is not a pairing test; the random-vs-keylog grep is.** |
| 51 | **P0** exhaustive search of `p0_login` for the world address `35.71.190.194` / port `44727`: all exported HTTP objects and all decrypted records, as ASCII **and** as packed hex (`2347bec2`, `c2be4723`, `aeb7`, `b7ae`). Plus DNS for any query resolving to it. | Present somewhere if prediction 1 holds. | **Absent.** Zero hits except two `aeb7` byte-coincidences inside `.dds` textures. Zero DNS queries for the host or any game-related name. **Caveat that limits the result:** six TLS streams totalling 54.9 MB were unreadable because their handshakes pre-dated the capture. This is what motivated the cold re-capture (#52). |
| 52 | **P0** cold re-capture: sign out in-client, quit client and Steam, close all other network applications, truncate keylog, `tcpdump -i enp2s0` **before** launch, then launch → character select → world. Capture `ss -tunp` at character select and in-world. | A login exchange finally inside the window, and every TLS stream with a captured handshake. | **Confirmed, and richer than predicted.** 8,943 frames, 0 dropped. 40 ClientHellos, full auth chain present (§16.2). Keylog 14,571 B. **Unplanned bonus:** the operator selected US West (refused) then US East (connected), producing a two-variant differential on the selection call (§16.4) that could not have been constructed deliberately without knowing the endpoint first. `ss -tunp` gave direct process attribution and settled in one command what three rounds of IP-prefix inference had not. |
| 53 | **P0** locate the world-address handoff by ordering: find every request preceding the world DTLS ClientHello and identify which names the world. | A server-list response carrying an address, per prediction 1. | **Position confirmed, payload not read.** `POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni` at **frame 2644**, response at **2648** (2,970 B), world ClientHello at **2716**. The world list at frame 1183 (`getlogininfo`) is **GUID-only with no address field of any kind** — so the address is not in the list, and 2648 is the only candidate left. |
| 54 | **P0** decrypt frame 2648 (the queue response). | Decrypts — every other record on that host did. | **Falsified. `tls.debug`: `Cannot find master secret`.** TLS stream 33 carries **two sessions** on one TCP connection: random `896d329d…` **is** in the keylog (so the *requests* at 2514/2644 decrypt), random `f0c4bcf4…` has **0 hits**. Handshake at 2125–2135 is full, incl. NewSessionTicket (type 4). Hypothesis: **resumption — the keylog callback fires on full handshakes only.** Recorded as **OPEN-1** and **DEF-2**; owned by P0b. |
| 55 | **P0b · Step 1** cold launch (Steam logged out and back in, tcpdump on `enp2s0` before launch), then check the queue TLS stream for a Certificate (handshake type 11) and pair its client random against the keylog. | Full handshake, key logged — clearing the resumption that produced OPEN-1. | **Confirmed.** `p0b_b22469132_20260830-181911.pcap`, 5,187 frames. TLS stream 10 (`d2oeuvxi3kfsrw.cloudfront.net`): ClientHello 480, ServerHello 485, **Certificate 487**, SKE/SHD 489, CKE/CCS 491, NewSessionTicket 505. One ClientHello, one random, **1 keylog hit** (keylog 6,110 B). `tls.debug`: **295 decrypted records**, 2 `Cannot find master secret`, neither on stream 10. §16.9. |
| 56 | **P0b · Step 2** search every object from `--export-objects http` for the world host `35.71.190.194`, then locate the carrying body by frame with `http.file_data contains`. | The address appears in the queue response, at a frame earlier than the first world DTLS ClientHello. | **Confirmed, and exclusively.** `grep -rl` returns **exactly one** of 20+ exported objects: the 2,571-byte ticket-redeem reply, **frame 1660**, HTTP 200. First DTLS ClientHello to `35.71.190.194:44727` at **frame 1723** — 63 frames of margin. The 16,645-byte `getlogininfo` world list does **not** contain it, corroborating §16.3. Field is **`LoginQueueResponse.Token.RepAddress`**, a literal `"ip:port"` string. **Prediction 1 confirmed.** §16.10. |
| 57 | **P0b** compare `GUID2` against `Token.TicketId`, `Token.CharacterId`, `Token.WorldId`, and the outer `TicketId` against `"{WorldId}_{GUID2}"`. | Session hypothesis: `GUID2` is the `CharacterId`, moved from body to path the way `WorldId` was (§16.4). | **Falsified, and OPEN-2 closed by the same run.** `Token.CharacterId == GUID2` → False. `Token.TicketId == GUID2` → **True**; outer `TicketId == "{WorldId}_{GUID2}"` → **True**; `Token.WorldId == WorldId` → True. `GUID2` is the **queue ticket id**. §16.12. |
| 58 | **P0b** `HostHash` preimage sweep: SHA-256/SHA-1/MD5/SHA-512 over every scalar `Token` field plus bare IP and bare port, then SHA-256 over all ordered pairs of those with separators `""`, `":"`, `"_"`, `"|"`. | `HostHash` is a SHA-256 of `RepAddress` or one of its components. | **Falsified. Zero hits.** 44 base64 chars → exactly **32 bytes**, so the length is right for SHA-256, but no tested preimage matches. Salted, HMAC'd with a server key, computed over a field not present in this response, or not a digest of the address at all. **Left unresolved deliberately** — its weight depends entirely on OPEN-3. Recorded as **FIND-4** so it is not re-swept blind. §16.12. |
| 59 | **P0b** read the 214-byte reply to the *generic* queue POST (frame 1586), which `--export-objects` did not write out (no exported object is under 1 KB); read it by frame instead via `http.file_data`. | It hands back the ticket id that the second call addresses. | **Confirmed, and it revealed the poll loop.** Body carries `TicketId`, `AllowQueueTransfer`, `EstimatedTime: 3`, `Position: 0`, `RefreshInterval: 2`, `QueueName: "DEFAULT000"` — and **no `Token` and no address**. So the two-call sequence is **enqueue-then-redeem**, not P0's reading of refused-then-accepted (§16.4), and a *queued* world would have the client poll the ticket path every `RefreshInterval` seconds until a `Token` appears. Changes what S0 must answer. §16.11. |
| 60 | **S0a** import-table survey of `NewWorld.exe` (b22469132) for an asymmetric-signature-verify API, via Ghidra Symbol Tree → Imports. | If the client verifies the queue `Token`, a verify API (CNG `BCryptVerifySignature`, CAPI `CryptVerifySignature`, or a static-OpenSSL EVP) is reachable. | **No Windows verify API imported.** BCRYPT has symmetric/hash/RNG + `BCryptImportKey/ExportKey` but **no `BCryptImportKeyPair`/`BCryptVerifySignature`**; CAPI has `CryptSignHashW` (signing) but no verify/`CryptImportKey`; CRYPT32 is base64+DPAPI only. Any client verify could only be static OpenSSL. Point toward NO, not proof. §16.15. |
| 61 | **S0a** traced the five functions on the `RepAddress` consume path (dial `FUN_14644a070` case 9, connect `FUN_146425f20`, launcher `FUN_146465060`, guard `FUN_146435e40`, disconnect-report `FUN_14643c570`) for any read of `Signature`/`HostHash` or any verify/EVP call. | Prediction 1 (load-bearing): `RepAddress` flows to a socket connect; `Signature`/`HostHash` are stored-and-forwarded; no crypto on the path. | **Consistent with prediction 1. None of the five reads a `Signature`/`HostHash` field or calls a verify;** `RepAddress` (obj +0x1100) goes straight to the driver connect. **But the `Signature` read-site and the deserializer write-site were never located** (register-relative std::string assigns defeat scalar/string search), so this is the consume side only — inferred NO, residual OPEN-3R. §16.15. |
| 62 | **S0a (OPEN-3R)** located and read the queue-response deserializer, found via xref of the response-unique keys `AllowQueueTransfer`/`JwtClaims`: `FUN_1474e4f20` (top-level) → `FUN_1474e5990` (`Token`). | Prediction 1, direct form: `Signature`/`HostHash` are `GetString`-and-store, no verify at parse time. | **CONFIRMED. Both are pulled by the stock AWS-SDK `JsonView` GetString helper (`FUN_1474654e0`), stored into Token members (Signature +0x64, HostHash +0x24, RepAddress +0x5a), and never read/hashed/verified/compared again.** No inline verification — structurally impossible in SDK codegen. Upgrades OPEN-3 from provisional to traced NO; closes OPEN-3R. §16.15. |
| 63 | **P2** instrument validation of `p2_scan.py` **before** it was pointed at retail (CHARTER §2/§4): (a) synthetic Javelin-shaped descriptor with nested messages, `oneof`, enum, repeated, defaults and a `service` block, butted directly against adjacent `.rdata`; (b) 171 MB haystack with six **real** Google descriptors planted at known offsets; (c) 40 MB adversarial noise seeded with decoy `.proto` paths and hand-crafted anchors. | A scanner that finds descriptors in noise is worthless; one that misses them at scale is worse. Expect full recall on (a)/(b) and zero hits on (c). | **PASSED — after two defects the controls caught.** (a) 2/2, exact offsets/VAs/sizes recovered **without any size constant**, service block round-tripped. (b) **6/6**, all sizes exact, 2 s runtime. (c) **0 false positives**. Defects found and fixed: **O(n²) extent recovery that hung** on adversarial input (now single-pass), and **35,081 false positives** — a bare `.proto` path in a strings table preceded by a byte that happens to be its length is a valid *name-only* `FileDescriptorProto`; fixed with a substance gate (must declare ≥1 message/enum/service/extension), 35,081 → 0 with no loss of recall. §17.9. |
| 64 | **P2** whole-binary `FileDescriptorProto` scan of `NewWorld.exe` b22469132 (179,204,176 bytes, image base `0x140000000`) from the pin, `.rdata`/`.data`. | P2_PROMPT predicted 20–100 registration call sites, response types present in the blobs, and a `service JavelinGatewayService` block ("the single most valuable find P2 can make"). Runbook predicted the opposite: infrastructure namespaces only, no service block. | **All three P2_PROMPT predictions FALSIFIED; runbook P2-B/C confirmed.** **3 blobs, exact confidence:** `campfire_event_default.proto` (VA `0x1486f5b60`, 1407 B, 4 msgs), `google/protobuf/empty.proto` (`0x1495ab7c0`, 190 B), `google/protobuf/descriptor.proto` (`0x1495b3330`, 6028 B). **0 service blocks. 0 messages named `*Result`/`*Response`/`*Notification`/`*Event`.** Campfire's 4 messages are really 1 message + 1 nested struct + 2 synthetic map entries. §17.9. |
| 65 | **P2** serialization-shape string survey of the same binary (`--diagnostics`). | If Javelin were protobuf, a protobuf content type and descriptor-registration symbols should be present in proportion to 20 `JavelinGatewayService` hits. | **Javelin is JSON.** `application/json` **236**, `application/x-protobuf` **0**, `application/octet-stream` 0. `JavelinGatewayService` 20. `InitializeReplicatedFields` **94** — matches T1/§10's independently-derived ~94, an instrument cross-check that passed. `ReplicaChunk` 23. **Instrument cap, and it binds: every search string containing `::` was matched literally and therefore misses mangled MSVC RTTI** (`JsonView` is stored as `?…@JsonView@Json@Utils@Aws@@`), so `JsonView`/`DataSetBase`/`Marshaler`/`MessageLite`/`DescriptorPool` = 0 are **artefacts of the search, not absence**. Only bare identifiers and content-type literals from this test are citable. §17.9. |
| 66 | **P5** whole-symbol-table sweep of `NewWorld.exe` b22469132 for `InstallRegistrationHook`, `REPClient`, `ReplicateClient` and `Amazon::Hub`, via `hub_probe.py` under PyGhidra. | P5 planned to decompile a registration hook and read how Hub types identify themselves. The plan assumed the hooks exist as functions. | **They do not exist as functions at all, and the sweep is what revealed the Hub layer.** `Amazon::Hub`: **3,629 symbols, 100% `Label`**. `InstallRegistrationHook`: **3,482 symbols, 100% `Label`**. **Functions with `Hub::` in the name: 0.** Every hook is inlined into a static initializer; only the type-erased lambda's RTTI descriptor survives (`…InstallRegistrationHook<T>(void)'::__l2::<lambda_1>::RTTI_Type_Descriptor`). Descriptors are **contiguous in link order** from `14a1340c0`; name strings are **scattered per translation unit** (`s_ReplicateClient` `147f42158`, `s_REPClient` `147f47b10`, `s_Amazon::Hub::ActorRef` `14803e230`). §18.1. |
| 67 | **P5** XREF trace from the `"ReplicateClient"` name string (`147f42158`) and the `FragmentUpdateMsg` RTTI descriptor (`14a134340`) through to executable code. | If Hub is fully inlined, XREFs on data are the only route in; expect them to converge on a shared registration routine. | **They reach the type's vftable, not a registry.** vftable `0x147f42110`, **8 slots**, ending `147f42148`; targets reached via MSVC **adjustor thunks** (`MOVSXD RAX,[RCX-4]; SUB RCX,RAX; JMP`), i.e. multiple inheritance. Slot 0 (`147f42120`) → `1407f9b60` = `return "ReplicateClient";`. Slot 1 (`147f42128`) → `FUN_1407f9f30` = **16-byte identity compare**. Slot 2 (`147f42130`) → `FUN_1407f98d0` = visitor dispatch. Both call **`FUN_1407fbe00`**, a TLS-guarded magic static caching **16 bytes** at `_DAT_14a2e7750`. Also recovered **`FUN_1407f3720`**, an **inlined hook body**, building `"ReplicateClient"` as a 15-char inline `AZStd::string`. §18.3. |
| 68 | **P5** identify the source of the 16-byte Hub type identity: decompile `FUN_1407fbe00` and locate its hash input. | Decides whether the ~3,600-type wire vocabulary is computable offline or must be extracted literal by literal. | **UNRESOLVED — OI-P5-1, and the withdrawal is the finding.** `FUN_1407fbe00` calls `FUN_1413e84b0(buf, &DAT_147f42168, 0)`, and `147f42168` is `147f42158 + 0x10` — **past `"ReplicateClient\0"`**. The input is therefore the string **following** the type name, not the name. If `FUN_1413e84b0` is `AZ::Uuid::CreateName`, the vocabulary computes offline from names already held; if `AZ::Uuid::CreateString`, ~3,600 literal UUIDs must be extracted. **The 3-argument call with a `0` length fits `CreateString`.** The session recorded the optimistic `CreateName` reading as fact mid-analysis and **withdrew it before writing** — logged because the withdrawal, not the guess, is the result. §18.3. |
| 69 | **P6** read `DAT_147f42168` in the Listing and decompile `FUN_1413e84b0`. | OI-P5-1: decides whether the vocabulary is computed offline or extracted literal by literal. | **`CreateStringSkipWarnings`. OI-P5-1 ANSWERED; extraction, not computation.** `147f42168` holds `6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d` (36 chars, unbraced). Decompilation matches `Uuid.cpp:61–133` at `7d4f1ee6` point for point — `[32,38]` length window, brace/dash handling, `GetValue` folded to `pcVar3[-0x73a8]`, `<<4 |`, 16 iterations. Arg count corroborates: `CreateString` is 3 with sret, `CreateName` is 2. P5 prediction 1 confirmed. §19.1. | |
| 70 | **P6** goto `_DAT_14a2e7750` to read the cached 16 bytes for `ReplicateClient`. | Proposed as an end-to-end check of literal → parser → cache. | **Zeros — and the test was invalid by construction.** The slot is a lazily-initialised function-local static; it is populated at runtime and P6 is static-only. The correct static check is the xref pairing inside `FUN_1407fbe00`: literal read at `1407fbe4b`, cache written at `1407fbe5f`. §13 row added against §18.3's wording. §19.1. | |
| 71 | **P6** enumerate `FUN_1413e84b0`'s callers via the Ghidra flat API. | Sizes the vocabulary: caller count is an upper bound on the type count. | **4,092 returned against 15,919 in the XRefs window — the flat API `getReferencesTo()` caps at 4,096 and truncates silently.** The run sampled only the low `.text` block and its 287 literals were unrepresentative. `ReferenceManager.getReferencesTo()` returns 15,914 call/jump refs. Recorded as a tooling trap. §19.3. | |
| 72 | **P6** resolve the `rdx` operand at all 15,914 call sites and pair each literal with a preceding name string. | Produce the name↔UUID map the chunk was chartered to deliver. | **5,907 accessors, 99.4% site resolution, gap 0–7 to the adjacent name.** Verified against three witnesses including `REPClient` at `147f47b10`, the address §18.3 recorded independently. **But none of the ten session-layer message types are in it** — this is the engine's `AZ_TYPE_INFO` vocabulary, not Hub's. §19.3. | |
| 73 | **P6** decompile `FUN_1407eeca0`, the function referencing both the `FragmentUpdateMsg` name and its UUID literal. | Explain why the session-layer types are absent from a map with 99.4% resolution. | **Second mechanism found.** The `InstallRegistrationHook<T>` body builds the name as an `AZStd::string`, **parses the UUID inline** (`CreateString` unrolled — no call to find), calls `FUN_1407de270(&out, uuid, &name)`, and installs a handler vftable at `out+0x48`. §19.4. | |
| 74 | **P6** enumerate `FUN_1407de270`'s references. | Test whether it is the Hub registrar and size the true vocabulary. | **3,512 refs / 3,511 call sites, against 3,482 `InstallRegistrationHook` instantiations** — two independently derived counts 30 apart. Walking them yields **3,509 distinct UUIDs from 3,510 rows**, one identity per registered Hub type. §19.4, §19.5. | |
| 75 | **P6** recover type names from the registrar call sites (four passes: `.rdata` adjacency, RTTI descriptors, immediate reconstruction, length-checked immediates). | Complete the name half of the vocabulary. | **311 named / 3,199 anonymous, and the anonymity is by design — 8.9% is the answer, not a shortfall.** `FUN_1408947a0` constructs an **explicitly empty** string (`local_18 = 0`, `local_28 = 0`) and passes it to the registrar, structurally identical to `FUN_1407f0fb0` (`PingTrait`, `local_18 = 9`) in every other respect. The names do not exist in the binary. Four unrelated extraction strategies converging on the same figure was the data constraining the result. §19.5. | |
| 76 | **P6** bucket named vs anonymous hooks by address region. | Test whether the named subset is scattered (tooling artifact) or structural. | **Structural.** Named hooks occur only in `1407xxxxx` (92) and `146axxxxx` (219); every other region is entirely anonymous. Those two regions are exactly the ones holding `ReplicateClient`, `REPClient`, the registration messages and `FragmentUpdateMsg`. **Hub attaches runtime names only to the wire-facing session and message layer.** The anonymous set also uses uppercase UUID literals against the named set's lowercase. §19.5. | |
| 77 | **P6** compare `FragmentUpdateMsg`'s handler vftable at `147f44828` against `ReplicateClient`'s 8 slots at `147f42110`. | OI-P5-4: is §18.3's layout uniform or single-instance? | **4 entries vs 8 — NOT uniform. OI-P5-4 ANSWERED, §18.3 restated as single-instance.** Prediction 3 falsified. Caveat: these may be different kinds of object, so the claim is non-uniformity across Hub types, not that §18.3 was wrong about `ReplicateClient`. §19.7. | |
| 78 | **P6** follow `InstallRegistrationHook<T>` RTTI descriptors to their hooks (`14a134340`, `14a134b30`). | A pooling-immune route to qualified type names. | **Dead, on two samples.** The descriptors describe the `<lambda_1>` inside the hook — `std::function` type-erasure — and each has one code xref landing nowhere near its hook (`1407c9370`, `1407c3a70`); neither is in the registrar map. Also dead: hook → vftable → COL, since every xref to `FUN_1407fbe00` is a `CALL` and the accessors are not virtual. §19.8. | |

---

## 15. Open items register (CHARTER §6.6)

Every open item has an owning chunk, or is explicitly marked unowned. Added
2026-08-30. Three kinds: **defects** in our own instruments, **findings** proven and
not yet used, and **gates** — undecided questions that block a chunk.

An item leaves this table by being resolved with evidence, or by being handed to a
chunk. It does not leave by being forgotten.

> **FIND-1 closed 2026-08-30 — handed to P0, worked, findings in §16.** It said the
> auth phase decrypts and that nobody had read the contents. It has now been read.
> What it promised — "login → server-list → session token → the address and
> credentials the world connect uses" — was delivered for the first three and
> **not** for the address: the world list is GUID-only and the response that would
> carry an address does not decrypt (**OPEN-1**). FIND-1 does not return to this
> table; its unfinished remainder is OPEN-1 and OPEN-2.

### Gates

| ID | Gate | Blocks | Status |
| -- | ---- | ------ | ------ |
| **GATE-1** | **Can H3 run at all?** H3 attaches to the running retail client, which has EAC loaded in-process. | Formerly H3 → P1–P5 → S1–S3, i.e. everything. | **RESOLVED 2026-08-30 by owner decision. The gate is dissolved, not answered** — H3 was removed from the critical path rather than cleared to run. See §3 for the sequencing rule and the table below for the order that replaces it. H3 survives as a **last resort**, attempted once if every other route is exhausted, with EAC prevention as a terminal result. |

### Work order — reachable without touching EAC (established 2026-08-30)

Everything here operates on files we own, on our own reference build, or on a socket
we answer. None of it contacts a running retail client. In rough dependency order:

| # | Work | Owner chunk | Why it needs no EAC contact |
| - | ---- | ----------- | --------------------------- |
| 1 | **Static extraction from `NewWorld.exe`** — dispatch point, handler table, type enum. **DONE (H2, §17, 2026-09-04).** Dispatch mapped, 10 Javelin Gateway message types enumerated, stock/game boundary confirmed, S1a and Track P handoffs written. | ~~**H2**~~ **COMPLETE** | The binary sits on disk. Nothing is running; EAC is not loaded. |
| 2 | ~~**Protobuf descriptor extraction.** FIND-2: if the embedded `FileDescriptorProto` blobs are real, message schemas come out of the binary with no captured packet at all. Flagged by T1, never extracted.~~ **DONE (P2, §17.9, 2026-09-04) — and the blobs are real but carry no game protocol.** 3 descriptors total: `campfire_event_default.proto` (telemetry) + `google/protobuf/empty.proto` + `google/protobuf/descriptor.proto`. No Javelin schema exists to extract. | ~~**P2**~~ **COMPLETE** | Same: static file inspection. |
| 3 | **Auth-phase decode.** FIND-1: the TCP/443 flow already decrypts via `SSLKEYLOGFILE`. Contains login, server list, session token, and the world-address handoff. Proven decryptable, **never read**. | **P0** (new) | The client writes the keylog itself. We read a file it produced. Nothing is injected or modified. |
| 4 | **Redirection feasibility.** Can the client be pointed at a world server we run? The address comes from auth, so this depends on 3. Cheap to test and everything below rests on it. | **S0** (new) | A hosts/DNS change on our own machine. |
| 5 | **The inversion — build the DTLS server.** T5 specified this layer completely (§12B). When the retail client completes a handshake against our server, **we hold the session keys**, and every message it sends arrives as plaintext on our socket. This is the route that replaces H3 for the client→server half. | **S1a** (new) | We are answering on a port. There is no hook, no injection, and nothing EAC is built to observe. |
| 6 | **Reference-build hook + signature scan.** Our binary, our symbols, and the last place a signature scan has a free oracle to check against (CHARTER §6.4). | **H1** | The reference build is ours. No retail client involved. |
| 7 | **Reflection reader decision gate.** T1 and T4 made both sides of the ABI comparison inspectable, so it can be decided on evidence. Independent of everything above. | **H4** | Static. |
| 8 | **H3 — last resort only.** Gets the server→client half directly. Everything else must be exhausted first, and §3's bound applies: one attempt, prevention is terminal. | **H3** | *(This one does contact EAC. That is why it is last.)* |

**What this order does not give you** is the server→client direction in captured
form — items 1–7 yield the client's outbound messages plus whatever structure comes
out of the binary. That half is what S-track has to construct regardless, and H2 +
FIND-2 are the substitute for observing it.

### Defects in our own instruments

| ID | Defect | Owner | Notes |
| -- | ------ | ----- | ----- |
| **DEF-2** | **The `SSLKEYLOGFILE` keylog is NOT complete for every session on the client's general TLS context.** | ~~**P0b.**~~ **Unowned — workaround in hand.** | §12A established the callback is wired in; P0 established it nonetheless misses sessions. TLS stream 33 of `p0_cold` carries two sessions on one TCP connection; only one random appears in the keylog. Working hypothesis: the callback fires on **full handshakes only**, so resumed sessions are never logged. **CHARTER §4 in one line — a tool's cap is part of the measurement.** Any future chunk finding an empty result on a TLS flow must check `tls.debug_file` for `Cannot find master secret` before concluding anything about the client. Test #54, §16.7. **REFINED 2026-08-30 by P0b: operationally solved, mechanism still a hypothesis.** A cold launch produces a full handshake on the queue stream and a logged key — the workaround works, and it is now the standing procedure for any auth-phase capture (§16.9). But P0b's capture contains **no resumed game session**, so "the callback fires on full handshakes only" has one consistent observation and no direct test. The two remaining `Cannot find master secret` records are attributed to EOS and IntelliJ streams **by session-id correlation, not by direct evidence**. §16.8's rule stands unchanged. Tests #55, #59. |
| **DEF-1** | `decode_carrier.py` has **no ChangeCipherSpec (content type 20) branch**. | **Unowned.** | Surfaced test #40 (part of the 19 undecodables), did not arise in test #48 because the extracted flight stops before CCS. Harmless today. CHARTER §4: a tool's cap is part of the measurement — an unhandled type will eventually be read as a finding about the client rather than a gap in the decoder. Small fix; worth doing before H3 output goes through it. |

### Gates and blockers opened by P0

| ID | Item | Blocks | Status |
| -- | ---- | ------ | ------ |
| ~~**OPEN-1**~~ **CLOSED** | ~~**The queue response (frame 2648 of `p0_cold`) does not decrypt.**~~ It is the reply to the call that names the world, it precedes the world DTLS ClientHello by 68 frames, and it is the only remaining place the world address can be delivered. `tls.debug`: `Cannot find master secret`. | **S0 — its design, not merely its confidence.** | **CLOSED 2026-08-30 by P0b.** A cold launch (Steam logged out and back in) forced a **full** handshake on the queue stream; the key was logged and the body decrypted. The world address is **`LoginQueueResponse.Token.RepAddress`**, a literal `"ip:port"` string, at frame 1660 — 63 frames before the client's first DTLS ClientHello to that host:port, and present in **exactly one** of 20+ exported objects. **S0 is unblocked.** §16.9, §16.10; tests #55, #56. |
| ~~**OPEN-2**~~ **CLOSED** | ~~**`GUID2` in the selection path `{WorldId}_{GUID2}` is unidentified.** Candidates: instance, shard, channel.~~ | S0 — a redirect must produce or echo it. | **CLOSED 2026-08-30 by P0b. All three candidates were wrong.** `GUID2` is the **queue ticket id** (`Token.TicketId == GUID2`; outer `TicketId == "{WorldId}_{GUID2}"`). It is **server-minted** in the enqueue response and echoed back by the client on redemption — so a redirect does not have to *produce* it, only echo what it issued. §16.12, test #57, §13. |
| ~~**OPEN-3**~~ **RESOLVED (NO — confirmed by trace)** | ~~**Does the client validate `Token.Signature` (RSA-2048, 256 bytes) or `Token.HostHash` (32 bytes) before dialling `Token.RepAddress`?**~~ | S0's design shape. | **RESOLVED 2026-08-31 by S0a → NO, confirmed by direct trace. §16.15.** No asymmetric-verify API imported; five consume-side functions crypto-free; **and the deserializer itself was read** (`FUN_1474e4f20` → `FUN_1474e5990`): `Signature`/`HostHash`/`RepAddress` are pulled by the stock AWS-SDK `JsonView` GetString helper, stored, and never inspected. Client treats `RepAddress` as opaque cargo → **S0 is the small field-rewrite branch.** Upgraded from the provisional NO recorded earlier the same day; **OPEN-3R closed.** |
| ~~**OPEN-3R**~~ **CLOSED** | ~~Residual of OPEN-3: is there a verify at *deserialize* time?~~ | ~~S0~~ | **CLOSED 2026-08-31, same session. Route (a) taken.** The deserializer was located by xref of the response-unique keys `AllowQueueTransfer`/`JwtClaims` (the field names are `GetString` args, not typed-model members — hence unreachable by the earlier scalar/string search) and read directly: `FUN_1474e4f20` (top-level) → `FUN_1474e5990` (`Token`). `Signature` and `HostHash` are stored via the same GetString helper as every other field and **never read again** — no verify at deserialize time. The static-OpenSSL scenario is excluded by reading, not by import absence. `login-token-signature-check` did not need its xref: it names the auth JWT, and the queue `Token` deserializer provably contains no verify. **No empirical (perishable) test was needed.** §16.15. |
| **OI-H2-1** | **LibUV role — confirm whether `Amazon::Hub::TransportConnectionLibUV` wraps the DTLS/world path or only a parallel HTTP/service channel.** `StartRecv`/`StopRecv` confirmed in imports; T5/§12B's "structurally stock" conclusion holds for the Carrier/crypto layer but the socket driver is LibUV-wrapped, which was not predicted. | **H1** sub-task | If LibUV wraps the DTLS path, T5/§12B needs a precision note ("zero catalogued exceptions in the Carrier layer" rather than "in the transport"). §17.1. |
| **OI-H2-2** | **`REPConnection::OnRecv` body not resolved statically.** Ghidra treats the entry as an `UndefinedFunction` thunk at `146b717b0`; the actual callable body was not isolated. | **H1** | H1 runtime hook on the vtable slot at `148591750` will confirm the body and its ReadBuffer dispatch logic. §17.2. |
| ~~**OI-H2-3**~~ **ANSWERED** | ~~**Server→client response schema absent from RTTI.** No `Result`/`Response` types in the Javelin Gateway RTTI — 10 request types only. Server→client messages are deserialized differently, not instantiated as typed RTTI objects.~~ | ~~P2~~ | **ANSWERED 2026-09-04 by P2, and dissolved rather than transferred. The premise "deserialized differently" was wrong.** Response types are absent from RTTI because AWS SDK for C++ `XResult` classes are **non-polymorphic value types — no vtable, therefore no RTTI**; `XRequest` derives from the polymorphic `AmazonSerializableWebServiceRequest` and so does emit it. "10 requests, no results" is the expected shape of the SDK, not evidence of an exotic inbound path. Corroborated by `application/json` = 236 vs `application/x-protobuf` = 0, and by §16.15 having already read Javelin-family fields out of the stock `JsonView` GetString helper. **The inbound Javelin schema is JSON** and is recoverable from P0's existing plaintext captures or from `.rdata` field-name constants — neither needs a running client. §17.9. |
| **OI-H2-4** | **Second state-machine function for states 5–8** (`QueryForRemoteConfigClass` through `WaitingForREPRequirements`) not yet located. `FUN_14644a070` only handles states 1–4 and 7–0xe. | **Unowned** | Low priority — these states are pre-connect and do not affect S1a or Track P. §17.6. |
| ~~**OI-P5-1**~~ **ANSWERED** | ~~**Is the Hub type UUID derived from the type name, or a literal from `AZ_TYPE_INFO`?**~~ | ~~P6, step 1.~~ | **ANSWERED 2026-09-05 by P6: `FUN_1413e84b0` is `AZ::Uuid::CreateStringSkipWarnings`. The UUIDs are literals; the vocabulary is extracted, not computed.** `147f42168` holds `6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d`; the decompilation matches `Uuid.cpp:61–133` at `7d4f1ee6` point for point. P5 prediction 1 confirmed. **But the answer did not deliver the vocabulary the question assumed** — walking `CreateString` call sites yields the engine's `AZ_TYPE_INFO` map (5,907 types), not Hub's; Hub registers through `FUN_1407de270` with the parse inlined. §19.1, §19.3, §19.4, tests #69–#72. |
| **OI-P5-2** | **Does GridMate replica traffic reach the world stream at all?** The replica machinery is present and stock, but the only bound chunk types found are `AzFramework::TransformReplicaChunk` and `LmbrCentral::TriggerAreaReplicaChunk` — **both stock engine components, not game content**. | **Unowned, low priority.** | P5's prediction 0 was never cleanly answered: the chunk found a third layer instead of resolving the two-way question it posed. **OI-H2-2** (`REPConnection::OnRecv` body would not resolve statically) remains the obstacle. Low priority because even if GridMate replicas do carry traffic, they carry engine transforms — game state is Hub. §18.0. |
| **OI-P5-3** | **Does New World opt into quantizing marshalers for transforms?** GridMate's defaults are raw IEEE floats (12 B per Vector3, 48 B per Transform); compression is opt-in per DataSet. | **P3.** | Determines what a controlled-walk capture should search for. Corrects the CHUNKS P3 note (§13, row 31). §18.4. |
| ~~**OI-P5-4**~~ **ANSWERED** | ~~**Is the 8-slot vftable layout uniform across Hub types?**~~ | ~~P6.~~ | **ANSWERED 2026-09-05 by P6: NO.** `FragmentUpdateMsg`'s handler table at `147f44828` has **4** entries against `ReplicateClient`'s **8** at `147f42110`. **§18.3 is restated as a single-instance observation.** P6 prediction 3 falsified. Caveat: these may be different kinds of object (message handler vs type), so the claim is non-uniformity across Hub types, not that §18.3 was wrong about `ReplicateClient`. §19.7, test #77, §13. |
| **OI-P6-1** | **Which `FragmentUpdateMsg` is `ReplicateClient`'s?** Two distinct types share the leaf name: `951ef3ed-c9a0-4e3d-a6fd-7fe0673d28d2` (hook `1407eeca0`, handler `147f44828`) and `62f68299-7bb2-4e0a-90d9-b664bd363dae` (hook `146ac5390`, handler `148578628`). `P6_PROMPT` attributes RTTI descriptor `14a134340` to `ReplicateClient::FragmentUpdateMsg`, but that descriptor's only code xref is `1407c9370`, which is neither hook. | **P7 / Step 4.** | Step 4 cannot name its target until this is settled. Do not assume the lower address is the right one. §19.5, §19.6. |
| **OI-P6-2** | **Which registration revision does b22469132 actually send?** All three are registered — `RegistrationRequestMsg` `8673a3cc-…` (`1407f27f0`), `V2Msg` `da4e5889-…` (`1407f2a20`), `V3Msg` `0b826b33-…` (`1407f2c50`), contiguous at 0x230 spacing. | **S1a, P7 / Step 5.** | **The most S1a-actionable open item.** Registration alone does not imply use; the answer is in whichever construction site is reachable from `GameConnection` state 10 (§17.7, OI-H2-5). Cross-reference §17.3's 15-state table. §19.6. |
| **OI-P6-3** | **Step 4 not started — the fragment message is not framed.** How a Hub message is serialized/deserialized, whether the 16-byte UUID or a negotiated index goes on the wire, how a fragment payload is delimited, and whether Hub rides inside GridMate replica chunks or beside them. | **P7.** | P6 predictions 2 and 4 remain **untested**, and prediction 0's wire question is therefore still open. Entry point: the handler vftables in §19.6, starting with `147f44828`. §19.9. |
| **OI-P6-4** | **The 311 recovered names are not pooling-audited.** 311 named rows yield only ~288 distinct names, and MSVC `/GF` merges name literals across translation units while each type keeps its own UUID. | **P7, low priority.** | The UUID is the key and the name is a label, so this does not threaten the identity map — but a name column treated as authoritative would mis-attribute. §19.5, §19.8. |
| **OI-P6-5** | **`*ReplicatedState` / `ComponentClientFacet_*` / `ComponentServerFacet_*` naming convention — noticed, not pursued.** The 3,482-name dump shows a component model with paired client/server halves and a replicated-state fragment per component (`AbilityComponentReplicatedState`, `AbilityComponentServerFacet_RequestApplyAbilityPoints`, …). `Replicate` and `ReplicateClient` each have a paired `::State` type. | **P3, P4.** | **Inference from naming convention, not verified.** If it holds, `*ReplicatedState` types are what `FragmentUpdateMsg` transports and P3/P4 get their targets by name. Out of P6's scope bound (actors, routing, persistence, AOI are a different chunk). §19.5, §19.6. |
| **OI-P2-1** | **Registration mechanism unconfirmed (residual of P2-E).** P2's 3 blobs were located **as data**; nothing yet proves they are registered, or by what. `InternalAddGeneratedFile`, `AddDescriptors` and `descriptor_table` all matched **0** as literal strings — but a non-virtual free function's name need not appear in the binary at all, so **the string test cannot answer this** and P2-E is not resolved. | **Unowned, low priority.** | Resolved by XREF on the three blob VAs (`0x1486f5b60`, `0x1495ab7c0`, `0x1495b3330`) in the warm `nwly.gpr`. Whatever function references those pointers **is** the registration function, named or not; its size constants should read **1407 / 190 / 6028** as an independent check on the scanner's self-derived sizes (CHARTER §4 — two derivations, not one). **Low priority because it cannot change P2's verdict:** there is no Javelin descriptor to register regardless of what registers the three that exist. Worth doing only to close P2-E honestly. §17.9. |
| **OI-P2-2** | **Are the 10 Javelin types in §17.5 the same REST calls P0 already decoded on TCP/443?** Their names are literal REST routes (`PostGameWorldsWorldIdCharactersRequest` = `POST /game/worlds/{worldId}/characters`, `DeleteGameCharactersCharacterIdRequest` = `DELETE /game/characters/{characterId}`, plus `PatchCharacterRequest`, `GetLoginInfoRequest`, `ListWorldsRequest`), and `application/json` = 236. Probably yes — **not checked.** | **Unowned.** | Cheap: diff the 10 type names against the routes in `p0_cold` (§16.2). If they match, **§17.5's "world message layer" framing needs its own §13 correction** and Track P's inbound problem was already solved by P0 in August. If they do not, the Javelin surface is a second JSON API on the world path and is worth its own chunk. §17.9. |
| **OI-H2-5** | **`vtable+0xa8` on REP driver object — what triggers its non-zero return?** This is the gate between state 10 and 0xb (`WaitingForActorGameConnection`). S1a's primary open question: what must the server emit to advance the client past state 10. | **S1a** | The poll call is at `(**(code **)(*param_1->field4054_0x1000 + 0xa8))()` in `FUN_14644a070` case 10. §17.7. |

### Findings proven and not yet used

| ID | Finding | Owner | Notes |
| -- | ------- | ----- | ----- |
| **FIND-3** | **`Characters[].PublishedData`** — a base64, zlib-compressed (`eNr…`) blob per character in the `getlogininfo` response. Almost certainly server-published character state. | **Unowned.** | Decompresses without keys, from a response we can already read. Cheap, and it is server→client state in a readable form — the direction §15's work-order note says items 1–7 do *not* give us. Worth a small chunk. §16.3. |
| **FIND-4** | **`Token.HostHash`** — 32 bytes, base64, in every login-queue response. **Not** a digest of any field tested: SHA-256/SHA-1/MD5/SHA-512 over every scalar `Token` field plus bare IP and bare port, and SHA-256 over all ordered pairs with four separators, all returned zero (test #58). | **Unowned.** | Low priority **by itself**; it matters only if OPEN-3 resolves toward client-side validation. **Do not chase open-endedly** — the sweep already run is recorded so it is not repeated blind. §16.12. **2026-08-31 (S0a):** OPEN-3 resolved NO by trace. `HostHash` **now characterised**: its read-site is in the `Token` deserializer `FUN_1474e5990` (GetString → member +0x24, present-flag +0x2c) — **store, not compare.** It is filed like any other string and never re-read on the connect path. FIND-4's preimage question is moot for S0 (the client never checks it); it remains only a curiosity. §16.15. |
| ~~**FIND-2**~~ **CLOSED** | ~~**`google::protobuf` is present in `NewWorld.exe`** (T1, §10). Embedded `FileDescriptorProto` blobs may hand over message schemas directly.~~ | ~~P2~~ **CLOSED** | **CLOSED 2026-09-04 by P2 — negative. The blobs are real and carry no game protocol.** A whole-binary scan found exactly 3 `FileDescriptorProto` blobs: `campfire_event_default.proto` (Amazon Campfire telemetry — 1 message, 1 nested context struct, 1 enum), plus the stock `google/protobuf/empty.proto` and `google/protobuf/descriptor.proto`. The latter is present because `google::protobuf::Reflection` requires it — which is the *entire* explanation for T1's flag. No Javelin descriptor, no `service` block, no message named `*Result`/`*Response`. Protobuf hands over nothing about the world messages. §17.9. |

### Unverified, carried forward

- Whether the datasheet `-partN` split is *driven by* the 65535 ceiling (§11).
  Correlation only. Tested by a future build exceeding it.
- Whether datasheet **schemas** are stable across builds (§11). Governs how much
  Track S work a patch invalidates.
- Epoch ≥ 1 Carrier framing on **retail** is inferred, not proven (§12B). H3's
  plaintext is what promotes it.

---

## 16. FINDINGS — P0 (auth-phase decode, TCP/443)

Folded from the P0 session, 2026-08-30. Capture-only, no hooks, no injection, no
client modification. Decryption is entirely from the keylog the client itself wrote
via `SSLKEYLOGFILE` (§12A, test #41). CHARTER §3 satisfied.

**Verdict: partial. The selection call and its position are identified; its response
body is not readable from the captures in hand.** See "Prediction 1" and OPEN-1.

### 16.0 Project clock — the servers are being retired

The news payload served to the client (`/newsstories/STEAM_APP_ID.1063730/metadata.json`,
CloudFront, read in the 2026-08-30 captures) carries Amazon's sunset notice:

- **Servers go offline 31 January 2027.**
- **Title delisted 15 January 2026** (already past).
- Nighthaven season extended until shutdown.

Amazon has wound the game down and the development team is gone. Two consequences
for this project, and they cut in opposite directions:

1. **Everything capture-dependent has a hard deadline.** P0, S0, and any future
   observation of live retail traffic stop being possible on 31 Jan 2027. Captures
   are a *perishable* input. Take more of them than seem necessary, and keep them.
2. **Everything file-dependent does not.** H2 (static extraction), FIND-2 (protobuf
   descriptors), D2's datasheets, and the reference build all operate on files that
   sit on disk indefinitely. These are unaffected by the shutdown.

This raises rather than lowers the priority of the whole S-track: after the retirement
date a working private server is the *only* way the client runs at all. It also means
the §15 work order should be read with capture-dependent items pulled earlier where
that is cheap.

### 16.1 Step 0 — which branch

**Branch 1 for the T3-era pcaps** (all client randoms paired), but those captures
proved to be the **wrong input** — see the correction in §13. Two new captures were
taken this session:

| Pcap | Keylog | Notes |
| ---- | ------ | ----- |
| `p0_login_b22469132_20260830-160722.pcap` | `nwly-keylog.txt` (truncated first, 6,286 B) | Client already running at capture start; six TLS streams pre-dated the window. |
| `p0_cold_b22469132_20260830-170445.pcap` | `nwly-keylog.txt` (truncated first, 14,571 B) | **The good one.** Capture started before launch, everything but the game closed. |

Prior keylogs preserved as `nwly-keylog-t3-20260829.txt` and
`nwly-keylog-p0-20260830-160722.txt`. **A keylog only opens the launches it was
written during; `SSLKEYLOGFILE` appends, so one file may cover several launches
unless truncated.** The pairing test that actually works (not `ls -la`) is to pull
each `tls.handshake.type==1` random from the pcap and grep the keylog for it.

Also recorded: `p0_cold_sockets.txt`, two `ss -tunp` snapshots taken at character
select and in-world. **Process attribution via `ss` should be step one of every
future capture analysis** — it settled in one command what three rounds of IP-prefix
guessing did not.

### 16.2 The ordered auth sequence (from `p0_cold`, frames in order)

All over TCP/443, HTTP/1.1 (**not** HTTP/2 — see the correction in §13),
`aws-sdk-cpp/1.7.193`. EAC/EOS endpoints identified only to exclude them.

| Frame | Host | Method / path | Role |
| ----- | ---- | ------------- | ---- |
| 164–241 | `dynamodb.{ap-southeast-2,sa-east-1,us-west-2,us-east-1,eu-central-1}` | `GET /ping` (**plaintext :80**) | Region latency probe. Responds `healthy: <host>`, 47 B. |
| 255 | `api.epicgames.dev` | `POST /auth/v1/oauth/token` | EOS auth. **Excluded, CHARTER §3.** |
| 283 | `tokenservice.amazongames.com` | `POST /games/new-world/tokens` | Issues the `x-nw-auth` JWT. |
| 307/335 | `prod.identity-service.amazongames.com` | `POST /auth/platform/user/code` | Platform identity. |
| 327 | `d2oeuvxi3kfsrw.cloudfront.net` | `GET /prod/credentials/omni` | Credential bootstrap. |
| 380–469 | `ags-javelin-remote-config.s3` | `GET /applications/{public,publicGameplay}/configuration-sets/{ProductId,RegionId,CognitoId}/…` | Config fan-out. |
| 397 | `prod.identity-service` | `POST /federated/identities/user` | Federated identity; repeats throughout. |
| 485/531 | `sts.us-east-1.amazonaws.com` | `POST /` | **AWS STS.** Issues the `x-amz-security-token`. |
| 529–589 | `client.entitlementservice.amazongames.com` | `GET/POST …/entitlements`, `…/entitlements/sync` | Ownership check. |
| **1183** | `d2oeuvxi3kfsrw.cloudfront.net` | `GET /prod/game/getlogininfo/jwt/omni?channelId=…&includeNames=true` | **The world list.** 16,604 B. See 16.3. |
| 1202 | `d1hkbwzm1bktgo.cloudfront.net` | `GET /motd/worlds_STEAM_APP_ID.1063730.json` | MOTD overlay, GUID-keyed. **Not** a server list. |
| **2514** | `d2oeuvxi3kfsrw.cloudfront.net` | `POST /prod/game/login/queue/v2/jwt/omni?channelId=…&tokenVersion=10` | **Selection call, control variant.** See 16.4. |
| **2644** | `d2oeuvxi3kfsrw.cloudfront.net` | `POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni?tokenVersion=10` | **Selection call, world variant.** |
| **2648** | ← `3.160.30.142` | 2,970-byte TLS ApplicationData response | **The handoff response. NOT READ — see OPEN-1.** |
| **2716/2719/2722** | `35.71.190.194:24083` | DTLS ClientHello ×3 (GridMate cookie handoff, §12B) | World connection opens. |

Continues after connect: catalog, privacy-settings, kinesis telemetry. None of it
pre-dates the world handshake, so none of it is the handoff.

### 16.3 The world list — GUID-only, no addresses

`GET /prod/game/getlogininfo/jwt/omni` → `{"LoginInfoList":{"Worlds":[…],
"RecommendedWorlds":[…],"Characters":[…],"NameReservations":[…]}}`.

Per-world fields: `WorldId` (GUID), `WorldName`, `PublicName`, `WorldSet`,
`WorldStatus`, `WorldType`, `WorldVersion`, `TransferToRegion`, `MaxAccountCharacters`,
`ConnectionCount`, `MaxConnectionCount`, `IsFull`, `IsRecommended`, `IsSelectable`,
and `WorldMetrics{QueueSize, QueueWaitTimeSec, WorldAgeDays, WorldPopulationStatus}`.

**There is no address field of any kind.** No host, no port, no endpoint, no region
URL. This is the finding that shapes S0.

Structural notes worth keeping:

- **One playable world remains: `PublicName` "Valhalla", `WorldName` `live-2-02-1`,
  `WorldType: OpenWorld`, `WorldSet: CrossPlay`, `IsRecommended: true`.** Every other
  `OpenWorld` entry has `WorldSet: transfer` and a name of the form
  `retail-transfer-iad-prod-to-<region>-prod` — these are transfer stubs, not
  playable. Also present: `WorldType: Tools` (`live-2-tools-1`) and `WorldType: Pool`
  (`live-2-pool-1`).
- **`WorldVersion` on Valhalla is a server build string** of the form
  `JAVELIN_RC_<digits>_nw-rc-retail-ptch-<digits>_SERVER_LOOSE`. Relevant to S1a: it
  names the server build the client expects to meet. Recorded as a *format*; the
  live value is in the capture.
- **This explains the failed US West selection** (see 16.4): the only `pdx-prod`
  entry is a transfer stub, so there is nothing there to connect to.

`Characters[]` and `NameReservations[]` carry per-character `CharacterId`,
`WorldId`, timestamps, `LocationGroupId`/`LocationId`, and a base64 `PublishedData`
blob (zlib-compressed, `eNr…` — an S-track lead: it is character state the server
publishes). **Values redacted: character names, persona ID, character GUIDs.**

### 16.4 The selection call — and a natural experiment

The client made **two** queue POSTs on the same TLS connection, because the operator
selected US West (refused), then US East (succeeded). This is the differential the
chunk needed and it was unplanned.

| | Frame 2514 — US West, refused | Frame 2644 — US East, connected |
| - | ---- | ---- |
| Path | `/prod/game/login/queue/v2/jwt/omni?channelId=STEAM_APP_ID.1063730&tokenVersion=10` | `/prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni?tokenVersion=10` |
| Body | 680 B | 25 B |
| Body shape | `{"LoginQueueRequest":{"CharacterId":<guid>,"ClientCapabilities":[],"IsTrialOwner":false,"SteamAppId":1063730,"SteamAuthTicket":<hex>,"WorldId":""}}` | `{"ClientCapabilities":[]}` |
| World named | **`WorldId` empty**, absent from path | **In the path**, as `{WorldId}_{GUID2}` |
| Region config fetched just before | `RegionId/pdx-prod`, Cognito id A | `RegionId/iad-prod`, Cognito id B |

So: the world identifier moves **from the body to the URL path** between the generic
and the specific call, and the second GUID in `{WorldId}_{GUID2}` is unidentified —
candidate meanings are instance, shard, or channel. **Identifying `GUID2` is an S0
prerequisite.**

Request headers on both (structure only, values redacted):

- `authorization: AWS4-HMAC-SHA256 Credential=<ASIA…>/<yyyymmdd>/us-east-1/execute-api/aws4_request, SignedHeaders=…, Signature=<hex>` — **SigV4 signed**, service `execute-api`.
- `x-amz-security-token: <STS session token>` — from the STS call at frame 531.
- `x-nw-auth: <RS256 JWT>` — from `tokenservice`. Claims include `iss` (tokenservice
  issuer URL), `aud` (`amzn1.organizationId.prod.new-world`, `EOS.prod.new-world`),
  `sub`/`az_persona_id` (persona id), `az_platform: steam`, `az_platform_id` (Steam
  ID), `az_ags_identity`, `az_region`, `sid` (session id), `az_identities[]`, and
  `exp`/`iat`/`nbf` — **4-hour lifetime observed**. `jku` points at a public JWKS
  endpoint under `tokenservice.amazongames.com`.
- `x-amz-content-sha256`, `x-amz-date`, `x-amz-api-version: 2017-09-26`.

**Login is Steam-inherited, not entered (confirmed 2026-08-30).** New World has no
in-game sign-in prompt and no account switch because identity comes from the Steam
session: the client presents a per-session **Steam auth ticket** (the `SteamAuthTicket`
hex in the frame-2514 body) and exchanges it — EOS `oauth/token` → `tokenservice`
JWT → STS — for the game's own credentials. Switching accounts means switching Steam
sessions. **Consequence for P0b:** every re-capture carries a *fresh* ticket, JWT, and
STS token, so the whole chain replays inside the window on a cold launch — which is the
same cold launch that forces the full TLS handshake OPEN-1 needs. The two requirements
coincide; do not attempt P0b from a resumed session.

**S1a-relevant:** the world connection carries no visible token in the DTLS handshake
(§12B), so whatever authorises the client to the world server is either issued in the
frame-2648 response or carried in the first epoch-1 Carrier message. Unresolved.

### 16.5 Predictions 1–4

| # | Prediction | Result |
| - | ---------- | ------ |
| **1** *(load-bearing)* | The world address arrives in a decrypted auth response, at an earlier frame than the first UDP datagram to that host. | **UNRESOLVED, and the position test passes.** The response at **frame 2648** precedes the world ClientHello at **2716** by 68 frames and is the reply to the call that names the world. Its 2,970-byte body **does not decrypt** (OPEN-1). Separately **falsified in the strong form**: the address is *not* in any readable auth body — exhaustive search across all exported HTTP objects and decrypted records for `35.71.190.194` / `44727` / `24083` as ASCII **and** as packed hex (`2347bec2`, `aeb7`) returned nothing but two false hits inside `.dds` textures. |
| **2** | JSON over HTTP/2, server list with an address or hostname per entry. | **Half right, half wrong.** JSON: yes. HTTP/2: **no — HTTP/1.1 throughout**, see §13. Server list with addresses: **no — GUID-only**, 16.3. |
| **3** | A session token issued at login is carried into the world connection. | **Partly confirmed.** Tokens exist and are characterised (16.4). Their path into the world connection is **not** established; §12B shows no place for one in the DTLS handshake. Still open, now owned by S1a. |
| **4** | Auth host set stable; world address not. | **Confirmed, and §12A corrected.** Same world **host** across captures a day apart (`35.71.190.194`) but a **different port each session** (`44727` → `24083`). T3's `52.223.16.88:54888` is a third, older value. §12A's "same IP:port on both captures" was true within one evening and does not generalise; its ephemeral-port warning referred to the **local** port. |

### 16.6 What S0 must do — derived, not assumed

1. **Do not plan a DNS or hosts-file redirect.** No DNS query resolves the world
   host in any of five captures. The client is handed an address (or derives one)
   without a name lookup, so `/etc/hosts` has nothing to catch.
2. **The interception point is the queue response**, frame 2648's equivalent —
   `POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni`. Redirection means
   answering that call, not intercepting a name.
3. **Answering it requires reading it first.** OPEN-1 blocks S0's design, not merely
   its confidence.
4. **A local TLS-terminating proxy for `d2oeuvxi3kfsrw.cloudfront.net` is the likely
   S0 mechanism**, since the endpoint *is* DNS-resolvable even though the world host
   is not. Certificate trust in a Wine prefix is the obvious obstacle and should be
   scoped before committing.
5. **SigV4 + STS + JWT all sign the request.** A replayed or hand-built queue POST
   must satisfy whatever the server checks. If S0 proxies rather than forges, this
   is moot — another argument for the proxy shape.

### 16.7 New open items (mirrored into §15)

- **OPEN-1 — frame 2648 does not decrypt.** `tls.debug` reports **`Cannot find
  master secret`**. TLS stream 33 carries **two sessions** on one TCP connection:
  random `896d329d…` has a keylog entry (which is why the *requests* at 2514/2644
  decrypt), random `f0c4bcf4…` has **zero**. The handshake at frames 2125–2135 is a
  full one including NewSessionTicket (type 4). Working hypothesis: **session
  resumption — OpenSSL's keylog callback fires on full handshakes, so a resumed
  session's secret is never written.** Testable, and the exchange repeats every
  login. Owner: **P0b**, a narrow re-capture.
- **DEF-2 — the keylog is not complete for every session on the general TLS
  context.** §12A established that the callback *is* wired in; this session
  establishes that it nonetheless misses sessions. A future chunk that finds an
  empty result on a TLS flow must check `tls.debug` for `Cannot find master secret`
  before concluding anything about the client.
- **`GUID2` in `{WorldId}_{GUID2}` is unidentified.** Blocks S0.
- **`PublishedData` (base64 zlib, `eNr…`) in `Characters[]` is unexamined.** Likely
  server-published character state — an S-track lead.

### 16.8 Instrument lessons (CHARTER §4 — a tool's cap is part of the measurement)

Four filter mistakes cost real time this session and each produced an *empty result
that looked like a finding*:

1. `http2.*` filters on a connection that is **HTTP/1.1** — returned nothing, which
   read as "no traffic."
2. `tls.app_data` is the **encrypted** record payload; grepping it for plaintext
   tests nothing.
3. `tcp.stream` and `tls.stream` are **different indexes**; `follow,tls` takes the
   latter. Feeding it a TCP index returns an empty follow.
4. `follow,tls` silently omits records it cannot decrypt, so an incomplete follow
   can mean *missing keys* rather than *end of conversation*.

**Rule for future chunks: on any empty tshark result, check `tls.debug_file` before
believing it.** That is the same check test #41 used correctly and that these four
mistakes each skipped.

### 16.9 P0b — the capture, and the gate it had to pass

`p0b_b22469132_20260830-181911.pcap`, **5,187 frames**, `enp2s0`, tcpdump started
before launch. Keylog `nwly-keylog.txt`, **6,110 B**. Cold launch by the third and
heaviest method P0b offered: **Steam logged out and back in**. The two cheaper
escalations (quit-and-wait, quit Steam so `wineserver` exits) were **never tested** —
the sledgehammer worked first try, so nothing is known about whether they suffice.

Short session: character select → Valhalla → a brief run → logout.

**The gate P0b existed to pass, passed.** TLS stream 10
(`d2oeuvxi3kfsrw.cloudfront.net`) shows a **full handshake**:

| Frame | Source | Handshake type |
| ----- | ------ | -------------- |
| 480 | client | 1 — ClientHello |
| 485 | `3.160.30.142` | 2 — ServerHello |
| **487** | `3.160.30.142` | **11 — Certificate** |
| 489 | `3.160.30.142` | 22, 12, 14 |
| 491 | client | 16, 20 |
| 505 | `3.160.30.142` | 4 — NewSessionTicket, 20 |

One ClientHello, one client random, **1 keylog hit**. **Keylog preserved as `nwly-keylog-p0b-20260830.txt`** — the working `nwly-keylog.txt` is truncated on the next cold launch; the preserved copy holds this session’s stream-10 key and is the mate to `p0b_b22469132_20260830-181911.pcap`, pairing re-verified by the randoms grep above. Contrast `p0_cold`, where the
same endpoint carried two sessions on one TCP connection and the second random had
zero hits (test #54). `tls.debug`: **295 decrypted records**, 2 `Cannot find master
secret` — **neither on stream 10**.

**DEF-2 — supported, not proven, and operationally solved.** The cold launch removed
the resumption, which is what the hypothesis predicted. But this capture contains no
resumed *game* session to test the mechanism against, so "the callback fires on full
handshakes only" still rests on one consistent observation and no direct test. What
**is** established is the workaround: a cold launch yields a full handshake on the
queue stream and a logged key, and that is now standing procedure for any auth-phase
capture.

The two remaining failures are almost certainly out of scope. The only ClientHellos
in the capture offering a **non-empty `session_id`** are `api.epicgames.dev` ×3 (EOS
— excluded, CHARTER §3) and `analytics.services.jetbrains.com` (IntelliJ running on
the host, not the game). **That attribution is circumstantial:** a `grep -B4` against
the debug log returned no lines tying a failure to a stream, so it rests on the
session-id correlation, not on direct evidence. Recorded as such rather than as a
result.

Incidental: the capture contains host-wide traffic — IntelliJ telemetry, Discord,
mDNS, SSDP. Harmless here, but a future capture wanting a clean stream list can
narrow with a BPF filter at tcpdump time.

### 16.10 The world-address handoff — READ

**Frame 1660, TLS stream 10, HTTP 200, 2,571 bytes**, content type `text/plain;
charset=utf-8` — mislabelled; the body is JSON. It is the reply to
`POST /prod/game/login/queue/v2/{WorldId}_{TicketId}/jwt/omni?tokenVersion=10`.

Full field shape. Values elided where sensitive (CHARTER §3 — structure, never the
secret):

```
LoginQueueResponse
├─ TicketId            str(73)   "{WorldId}_{TicketId}" — the path segment, echoed back
├─ AllowQueueTransfer  bool      false
└─ Token
   ├─ TokenVersion         int     10
   ├─ HostHash             str(44) base64 → 32 bytes. UNRESOLVED — §16.12, FIND-4
   ├─ AccountAge           int     seconds
   ├─ CharacterId          str(36) GUID                      [REDACTED]
   ├─ GenerateTime         int     unix seconds
   ├─ IssueTime            int     unix seconds (GenerateTime − 1 observed)
   ├─ IsPermanentAppOwner  bool
   ├─ IsTrialOwner         bool
   ├─ JwtClaims            str(1218)                         [REDACTED]
   ├─ PersonaId            str(61)                           [REDACTED]
   ├─ RepAddress           str     "35.71.190.194:44727"     ← THE HANDOFF
   ├─ TicketId             str(36) GUID — the second half of the outer TicketId
   ├─ SteamAppId           int     1063730
   ├─ SteamUserId          str                               [REDACTED]
   ├─ ChannelId            str     "STEAM_APP_ID.1063730"
   ├─ LocationGroupId      str     "DEFAULT"
   ├─ LocationId           str     "000"
   ├─ WorldId              str(36) GUID — matches the path's WorldId
   └─ Signature            str(512) hex → 256 bytes → RSA-2048  [REDACTED]
```

**`RepAddress` is a literal IPv4 address and port joined by a colon in a single
string.** Not split across fields, not a hostname, not packed binary. That one string
is what S0 must rewrite.

**Ordering — the test that makes it load-bearing.** The response is at frame
**1660**; the first world DTLS ClientHello to `35.71.190.194:44727` is at frame
**1723**. **63 frames of margin.** The client is told where to go before it goes.

**Exclusivity.** `grep -rl` for the address string across every object written by
`--export-objects http` returned **exactly one file** — this one, out of 20+. The
16,645-byte `getlogininfo` world list does **not** contain it, which **corroborates
§16.3 rather than contradicting it**: the list names worlds by GUID, and the address
arrives only on ticket redemption.

Port note: `44727` is the same port as `p0_login`, which corrects §16.5's
"different port each session" (§13).

### 16.11 The queue is a poll loop, not a single call

P0 saw two queue POSTs and read them as a refused US-West selection followed by a
successful US-East one (§16.4). P0b's capture has the **same two-call shape with no
refusal involved**, which means the two calls are the *normal* sequence and P0's
reading was an artefact of how that session happened to unfold.

| | **Call 1 — enqueue** | **Call 2 — redeem** |
| - | ---- | ---- |
| Path | `/queue/v2/jwt/omni?channelId=…&tokenVersion=10` | `/queue/v2/{WorldId}_{TicketId}/jwt/omni?tokenVersion=10` |
| Request body | `{"LoginQueueRequest":{CharacterId, ClientCapabilities, IsTrialOwner, SteamAppId, SteamAuthTicket, WorldId}}` | `{"ClientCapabilities":[]}` — 25 bytes |
| Response frame | **1586**, 214 B | **1660**, 2,571 B |
| Response body | `{TicketId, AllowQueueTransfer, EstimatedTime:3, Position:0, RefreshInterval:2, QueueName:"DEFAULT000"}` | `{TicketId, AllowQueueTransfer, Token{…RepAddress…}}` |
| Carries the address | **no** | **yes** |

So: the client **enqueues**, receives a ticket plus a queue position, then **polls the
ticket path** until the response carries a `Token`. Admission was immediate here —
`Position: 0`, `EstimatedTime: 3` — so exactly one poll was needed.

**Consequence for S0, and it is not cosmetic.** On a populated world the client will
re-POST the ticket path every `RefreshInterval` seconds and receive position updates
carrying **no `Token`** until admitted. A proxy that answers the ticket path once,
with a token, works against an empty queue and is fragile against a full one.
**Answer the poll shape, not the single observed exchange.**

`QueueName: "DEFAULT000"` pairs with `Token.LocationGroupId: "DEFAULT"` and
`Token.LocationId: "000"` — the queue is keyed per location group.

### 16.12 OPEN-2 closed; `HostHash` and `Signature` characterised

**`GUID2` is the queue ticket id.** Proven directly (test #57):

```
outer TicketId == "{WorldId}_{GUID2}"  : True
Token.TicketId == GUID2                : True
Token.CharacterId == GUID2             : False
Token.WorldId == GUID2                 : False
Token.WorldId == WorldId               : True
```

The path segment is a composite key naming *this queue ticket for that world*. **All
three of §16.7's candidates — instance, shard, channel — were wrong**, and so was the
`CharacterId` hypothesis raised at the start of this session (§13). The client does
not supply `GUID2`: the server mints it in the enqueue response and the client echoes
it back on redemption. **A redirect therefore does not have to produce it, only echo
what it issued.**

**`HostHash` — UNRESOLVED, deliberately.** 44 base64 chars → exactly 32 bytes, so the
length is right for SHA-256. Not a bare digest of anything in the token: swept
SHA-256/SHA-1/MD5/SHA-512 over every scalar field plus the bare IP and the bare port,
then SHA-256 over all ordered pairs of those with separators `""`, `":"`, `"_"`,
`"|"`. **Zero hits** (test #58). Remaining candidates: salted, HMAC with a server key,
a digest over a field not present in this response, or an internal host identifier
unrelated to `RepAddress`. **Do not chase open-endedly** — its weight depends entirely
on OPEN-3. Recorded as FIND-4 so the sweep is not repeated blind.

**`Signature`** is 512 hex characters → 256 bytes → **RSA-2048**, consistent with the
RS256 chain in §16.4. It presumably covers the `Token` object, `RepAddress` included.
We do not hold the key and will not.

### 16.13 What S0 does now — revised from §16.6

§16.6 items 1, 2, 4 and 5 stand. Items 2 and 4 are now **confirmed rather than
inferred**, and there are three additions:

1. **The interception point is confirmed**: the ticket-redeem response,
   `POST /prod/game/login/queue/v2/{WorldId}_{TicketId}/jwt/omni`.
2. **The rewrite is a single string**: `LoginQueueResponse.Token.RepAddress`, from
   `ip:port` to ours. Nothing else in the response needs to change for the client to
   dial elsewhere — **subject to OPEN-3**.
3. **Handle the poll loop** (§16.11), not just the one exchange observed.
4. **`RepAddress` is not a hostname**, so `/etc/hosts` remains useless for the world
   host — but the *queue endpoint* `d2oeuvxi3kfsrw.cloudfront.net` **is**
   DNS-resolvable, which is what makes the proxy shape possible at all.
5. **Wine-prefix certificate trust is the first thing to scope**, before any proxy is
   written. If the client pins, the whole shape changes.

**The question that decides the shape is OPEN-3:** does the client verify
`Token.Signature` (or `HostHash`) before dialling `RepAddress`? The world server is
the natural verifier, and under S0/S1a the world server is **us** — so the signature
only bites if the *client* checks it. Cheap static question; owned by **S0a**; answer
it before S0 commits to a design.

**S1a-relevant, and it advances P0 prediction 3.** The `Token` object **is** the world
credential. §12B proved the DTLS handshake carries none of it, so it must be presented
in the **first epoch-1 Carrier message**. That is now a concrete requirement rather
than an open question about where a token might live. `JwtClaims`, `Signature`,
`CharacterId`, `WorldId`, `TicketId` and the location fields are the material a world
server would expect to receive and validate.

### 16.14 Predictions — P0b (CHARTER §4)

| # | Prediction, recorded before looking | Result |
| - | ---------- | ------ |
| **1** *(load-bearing)* | The queue response contains the world address, at a frame earlier than the first UDP datagram to that host. | **CONFIRMED.** `Token.RepAddress = "35.71.190.194:44727"` at frame 1660; first DTLS ClientHello to that host:port at 1723. Present in **exactly one** of 20+ exported objects. Test #56. |
| **2** | JSON, address as a literal IP + port rather than a hostname. | **CONFIRMED as to type — and the session's own refinement of it was wrong.** Literal IP+port, but **joined in one string**, not split across fields as predicted mid-session. §13. |
| **3** | Also carries a session token the world connection needs. | **CONFIRMED.** The whole `Token` object (§16.10). *Where* it enters the world stream is still unobserved and belongs to S1a. |
| **4** | `GUID2` echoed or explained by the response. | **CONFIRMED, and it closes OPEN-2.** `GUID2 == Token.TicketId`. All three of §16.7's candidate meanings falsified. §16.12, test #57. |

**Named failure mode that did not occur, recorded because it nearly did.** Before
looking, this session flagged that a login *queue* classically returns a ticket and a
poll URL rather than a destination, which would have falsified prediction 1 in a
specific way. §16.11 shows that **is** the design — the client does enqueue, then
poll — and prediction 1 survived only because admission was immediate at `Position:
0`. On a queued world the first response carries no address. The prediction was right
about the endpoint and lucky about the queue depth, and S0 must not inherit the luck.

### 16.15 FINDINGS — S0a (does the client validate the queue token?) — 2026-08-31

Static Ghidra analysis of `NewWorld.exe`, buildid **22469132**, sha256
`8654f01d324636d9f74f1c793b0cc4a417c3c5fa9847d9913c358ca29e0fdc8e` (matched
`Bin64.sha256`, PE32+ x86-64, 8 sections). No execution, no hooking, no capture —
CHARTER §3 satisfied. **Answers OPEN-3.**

**Verdict: NO — CONFIRMED BY DIRECT TRACE (2026-08-31, upgraded from provisional).**
The client does not verify `Token.Signature` or check `Token.HostHash` before dialling
`Token.RepAddress`. It treats the address as an opaque `std::string` at connection-object
offset **+0x1100**, read straight to a socket connect. **S0 is the small branch:** rewrite
the one `RepAddress` string. **OPEN-3R closed** — the deserializer was opened and read (below).

**This is now traced from the `Signature` read-site itself (OPEN-3R resolved).** The
load-bearing trace the S0a prompt named ("from the `Signature` read site, follow the
value") was completed: the queue-response parser and the nested `Token` deserializer were
located and read. `Signature` and `HostHash` are pulled by the same stock AWS-SDK
`JsonView` GetString helper as every other field, stored into members, and **never read
again** — no hash, no verify, no EVP/RSA/bignum, no comparison, no branch on their value.
The earlier residual (a verify hiding at deserialize time inside static OpenSSL) is
**excluded by direct reading**, not merely by import-table absence. See "The deserializer
trace" below.

**Crypto-provider survey (import table).** No asymmetric-signature-verify API is linked:
- **BCRYPT.DLL** — symmetric + hashing + RNG (`BCryptEncrypt/Decrypt`, `BCryptCreateHash/
  HashData/FinishHash`, `BCryptGenRandom`, `BCryptImportKey`, `BCryptExportKey`). **No
  `BCryptImportKeyPair`, no `BCryptVerifySignature`** — CNG cannot RSA-verify here.
- **ADVAPI32.DLL** (legacy CAPI) — `CryptSignHashW` present (client *signs* its own
  requests), but **no `CryptVerifySignature`, no `CryptImportKey`** for a server pubkey.
- **CRYPT32.DLL** — `CryptStringToBinaryA`/`CryptBinaryToStringA` (base64/hex),
  `CryptProtectData`/`CryptUnprotectData` (DPAPI). No certificate-signature verify.
- **SECUR32** — `EncryptMessage`/`DecryptMessage` (SSPI channel), not token verify.

So any client-side token verify could only be static-OpenSSL EVP. **None is reached on
the address path** across the five functions below. Absence of a Windows verify import
is a point toward NO but not proof on its own — the proof is the deserializer read below, which is why the verdict is confirmed rather than resting on import absence.

**The five address-path functions traced, all crypto-free** (signatures, not bare
offsets — CHARTER §4):

1. **`FUN_14644a070` — GameConnection state machine.** State enum at obj **+0x1530**;
   human-readable state-name table at **`PTR_s_Disconnected_1484f9ff0`** (indexed by the
   state int — a gift for H2). Recovered states: 0 Disconnected, 3 QueueGameLogin,
   4 WaitingForQueuedLogin, 9 StartREPConnection, 10 WaitingForREPConnection,
   0xb WaitingForActorGameConnection, 0xc WaitingForSpawnPoint, 0xd WaitingForPlayerSpawn,
   0xe InGame. **Case 9 is the dial:** reads `RepAddress`(+0x1100) and `worldId`(+0x1120)
   as `std::string`s, logs `"GameConnectionWrapper: start REP connection RepAddress = %s,
   worldId = %s"` (`s_..._1484fe8f0`), calls the connect, advances to state 10. No verify.
2. **`FUN_146425f20` — the REP/DTLS connect.** Builds 6 driver option strings
   (`FUN_146161a20`), copies `RepAddress` from +0x1100, checks two impersonation feature
   flags (`javelin.impersonate-character-id/-persona-id`, dev tooling), installs event
   vtables (`PTR_LAB_1485029e8/1485029b8/148502988`), then calls the driver at obj
   **+0x1000** via **vtbl+8 (init)** and **vtbl+0x18 (connect)**. Connect args:
   `RepAddress`, options, **cred `std::string` @ +0x10c0**, **cred `std::string` @ +0x10e0**,
   personaFlags, bool. No verify; the address goes straight to the socket.
3. **`FUN_146465060` — queue-login launcher.** Allocates a 0xA8-byte handler stamped
   vtable `PTR_FUN_148502958`, wires callbacks off `param_2[7]`, hands off to
   `FUN_146435e40`. Thin async launcher; no parse, no crypto.
4. **`FUN_146435e40` — request guard/dispatch.** Errors with `"NO_GATEWAY" / "Login is
   not available"` when no gateway client (obj+0x118==0); else builds a 0x50-byte handler
   (`PTR_FUN_1485027d8`) and fires it through a `std::function`. Registers the request;
   no parse, no crypto.
5. **`FUN_14643c570` — disconnect telemetry reporter.** *Reads* the object for an
   analytics event; contributes the object layout (below). No crypto.

**Connection-object layout** (decoded from the telemetry key strings in `FUN_14643c570`
— little-endian ASCII inline constants; this is the S0/S1a/H2 map):

| Offset | Field | Offset | Field |
| --- | --- | --- | --- |
| +0x1000 | REP driver object (vtbl +8 init, +0x18 connect, +0xa8 "connected?") | +0x1160 | `persona_id` (std::string) |
| +0x10c0 | credential std::string → connect | +0x1288 | `match_id` (std::string) |
| +0x10e0 | credential std::string → connect | +0x1420 | `is_loading` (byte) |
| +0x1050 | `player` (std::string) | +0x1530 | state enum (int) |
| +0x1100 | **`rep_address`** (std::string) — the dial target | +0x13f8 | `message` (std::string) |
| +0x1120 | `world_id` (std::string) | +0x130 | actor-game-connection subobject |
| +0x1140 | `character_id` (std::string) | | |

**The credential strings at +0x10c0/+0x10e0** handed to the connect are the likely
carriers of the `Token`/JWT into the world stream — advances P0 prediction 3 / §16.13
(the `Token` is the world credential presented in the first epoch-1 Carrier message).
S1a must supply/accept them.

**On the field-name strings (S0a prompt Step 1 falsified — see §13).** The three JSON
keys were expected as literals the deserialiser clusters on. They are **not**:
`LoginQueueResponse` — zero matches; `RepAddress` — only inside the case-9 log format
string; `HostHash `/`TicketId ` — only as trailing-space label text in .rdata; `Signature`
— present but in an AWS SigV4 / error-code neighbourhood (`SignatureV4`, `X-Amz-Signature`,
`SignatureDoesNotMatch…`). Reads as a **generic/reflective deserialize** that stores
fields rather than a bespoke per-field parser that validates them — corroborating NO,
not proving it. The queue stack RTTI is `Aws::JavelinGatewayService::Model::
PostGameLoginQueueV2TicketIdRequest` — AWS-SDK, statically linked (matches §16.2).

**The `LoginToken` signature strings are the auth-JWT path, not the queue `Token`.**
`Javelin.RPC.LoginToken.signature`, `login-token-signature-check`, and
`@mm_authresult_Denied_LoginTokenSignatureInvalid` all name **LoginToken** (the §16.4
RS256 login credential); the last is a *server* denial the client only holds a display
string for. **Not xref'd** — flagged in the S0a prompt as needing an xref and not run, so
"off the queue-Token path" is believed, not proven. Folded into OPEN-3R.

**`HostHash` — not characterised.** The definition-of-done asked for a store-vs-compare
trace; none was done (no read-site located). Weight is low now that OPEN-3 leans NO
(FIND-4 already notes its weight depends on OPEN-3). Left with FIND-4.

**What S0 now is, in the confirmed branch (for scoping without re-opening Ghidra):** a
TLS-terminating proxy for `d2oeuvxi3kfsrw.cloudfront.net` that rewrites the single
`LoginQueueResponse.Token.RepAddress` string on the ticket-redeem response, handling the
poll loop (§16.11). No re-signing: the client never checks the signature, and the world
server that would (us, under S1a) can accept whatever it likes. **OPEN-3R** is the only
caveat — cheap to close by reading the deserializer statically at leisure, or empirically
when S0's proxy is first tested against a live client (perishable, before 31 Jan 2027).

**The deserializer trace (OPEN-3R, resolved 2026-08-31).** The queue response is not a
typed SDK model — RTTI shows only `Request` classes under `Model@JavelinGatewayService`
(no `Result`/`Response`/`Token` type), so the body is parsed as a raw `Aws::JsonView`.
Two functions do it, found by xref of the response-only key literals `AllowQueueTransfer`
and `JwtClaims` (unique to this response):
- **`FUN_1474e4f20`** — top-level queue-response parser. Stock has-then-get: `has(key)`
  (`FUN_147465730`) then a typed getter, per field — `AllowQueueTransfer`(bool),
  `EstimatedTime`/`Position`/`RefreshInterval`(int), `QueueName`/`RecommendedTransferWorldId`/
  `TicketId`(string), and **`Token`** → `GetObject` → recurses into `FUN_1474e5990`. No crypto.
- **`FUN_1474e5990`** — the `Token` deserializer. ~20 fields, all has-then-get-store.
  **`Signature`** (GetString → member +0x64, flag +0x6c), **`HostHash`** (GetString → +0x24,
  flag +0x2c), **`RepAddress`** (GetString → +0x5a, flag +0x62), plus `AccountId`,
  `AccountIsLocked`, `ChannelId`, `CharacterId`, `ClientCapabilities`, `GenerateTime`,
  `IsPermanentAppOwner`, `IsTrialOwner`, `IsUseTime`, `JwtClaims`, `LocationGroupId`,
  `LocationId`, `PersonaId`, `SteamAppId`, `SteamUserId`, `TicketId`, `TokenVersion`,
  `WorldId`. Every field, `Signature` and `HostHash` included, is pulled by the **same**
  `FUN_1474654e0` GetString helper and stored; **none is read again, hashed, verified,
  compared, or branched on.** The function returns the moment the last field is stored.

**This is decisive and structural.** It is stock AWS-SDK `JsonView` codegen, which has no
inline-verification concept: a signature check would have to be a separate explicit call on
the assembled object, and no such call exists on any path traced (the five consume-side
functions, the top-level parser, or the Token deserializer). `Token.Signature` is received
and filed like any other string. **The client cannot reject a rewritten `RepAddress` on
signature grounds because it never inspects the signature.** OPEN-3 is closed NO by direct
trace, not inference.

**Token object field map** (from `FUN_1474e5990`, offsets into the Token struct — S1a will
need these to *emit* a Token the client accepts, and they confirm §16.10's wire fields):
`Signature` +0x64, `HostHash` +0x24, `RepAddress` +0x5a, `WorldId` +0x86, `TicketId` +0x7a,
`CharacterId` +0xc, `PersonaId` +0x50, `ChannelId` +0x32, `JwtClaims` +2, `LocationGroupId`
+0x3c, `LocationId` +0x46, `GenerateTime` +0x20, `TokenVersion` +0x83 — each with a paired
present-flag byte. (Offsets are in the Token sub-object, distinct from the connection-object
offsets above.)


---

## 17. World-message dispatch map (H2)

**Status:** DONE 2026-09-04. Static analysis of `NewWorld.exe` b22469132 from
Ghidra project `~/Documents/Ghidra-projects/nwly.gpr`. No execution, no hooking,
no pcap. Open items OI-H2-1 through OI-H2-5 added to §15.

---

### 17.1 Inbound path — stock/game boundary

The inbound datagram path:

```
WSARecvFrom (WS2_32.DLL import)
  → Amazon::Hub::TransportLayerLibUV (LibUV async I/O event loop)
    → Amazon::Hub::TransportLayerGridMate::Connect / Listen
      → Amazon::ContainerClientSDK::REPConnection::OnConnect
      → Amazon::ContainerClientSDK::REPConnection::OnRecv(Amazon::Pervasives::ReadBuffer)
        → Aws::JavelinGatewayService handler objects (message layer)
```

**Stock/game boundary:** Everything from `WSARecvFrom` through
`TransportLayerGridMate` is stock transport (GridMate + LibUV). The game-specific
message layer begins at `REPConnection::OnConnect` / `OnRecv`.

**LibUV finding (prediction-1 partial strain):** The raw socket is driven by
LibUV's event loop (`Amazon::Hub::TransportConnectionLibUV::StartRecv` /
`StopRecv` confirmed in imports), not a raw GridMate `SocketDriver` poll loop.
T5/§12B's "structurally stock GridMate" conclusion holds for the Carrier/crypto
layer, but the socket driver is LibUV-wrapped. Record as a precision gap in
T5/§12B's "zero catalogued exceptions" wording — not a falsification of the
transport conclusion. OI-H2-1: confirm whether LibUV wraps the DTLS path or only
a parallel HTTP/service channel.

---

### 17.2 REPConnection — Anchor C

**Class:** `Amazon::ContainerClientSDK::REPConnection`

**Constructor:**
```
REPConnection(Amazon::Hub::Log&, Amazon::Pervasives::Endpoint const&,
              std::function, std::function, std::function)
```
Three `std::function` callbacks registered at construction: onConnect,
onDisconnect, onMessage (order inferred from usage).

**Key methods (confirmed in RTTI):**
- `OnConnect(Amazon::Hub::TransportConnection*)` — private, fires on DTLS
  handshake completion. Handler at `146474e80` logs:
  `"GameConnectionWrapper: REP socket connection established, now waiting to
  i[nitialize]"`. This is the transition into GameConnection state 10
  (`WaitingForREPConnection`).
- `OnRecv(Amazon::Pervasives::ReadBuffer)` — private, fires on inbound
  decrypted data. RTTI type descriptor at `14a268a90`. Thunk at `146b717b0`;
  actual callable body not resolved statically (OI-H2-2).

**REPConnection vtable layout (partial, from `148591718`–`148591760`):**

| Address | Target | Notes |
|---|---|---|
| `148591718` | `LAB_146b717c0` | thunk |
| `148591720` | `LAB_146b717c0` | thunk |
| `148591728` | `FUN_14078fa10` | |
| `148591730` | `FUN_14046dc90` | |
| `148591738` | `LAB_146b71300` | copy constructor helper |
| `148591740` | `LAB_146b71300` | |
| `148591748` | `LAB_146b714b0` | |
| `148591750` | `LAB_146b717b0` | **OnRecv thunk** (RTTI confirmed) |
| `148591758` | `FUN_14078fa10` | |
| `148591760` | `FUN_14046dc90` | |

**Three event handler tables** passed to REP driver connect call
(`FUN_146425f20`, vtable slot `+8` on `param_1+0x1000`):
- `PTR_LAB_148502988` — connection lifecycle (OnConnect at `146474e80`)
- `PTR_LAB_1485029b8` — second handler table
- `PTR_LAB_1485029e8` — third handler table (factory thunk at `1464733d0`)

---

### 17.3 Connect call and credential fields

In `FUN_146425f20` (called from GameConnection state machine case 9,
`StartREPConnection`):

```c
// vtable +8: install handler tables
(**(code **)(**(longlong **)(param_1 + 0x1000) + 8))
    (*(longlong **)(param_1 + 0x1000), local_188, &local_2f8, &local_338);

// vtable +0x18: the actual connect call with credentials
(**(code **)(**(longlong **)(param_1 + 0x1000) + 0x18))
    (*(longlong **)(param_1 + 0x1000), &local_238, &local_218,
     param_1 + 0x10c0, param_1 + 0x10e0, &local_2b8, bVar10);
```

**`param_1 + 0x10c0` and `param_1 + 0x10e0`** are the credential fields
(Token/JWT) passed to the world connect — confirmed consistent with §16.15's
connection-object layout. Also confirmed: the `javelin.impersonate-character-id`
and `javelin.impersonate-persona-id` feature flags are checked here (dev tooling,
irrelevant to production).

---

### 17.4 Dispatch mechanism — Javelin Gateway Service handler registry

**Prediction 2: CONFIRMED.** Dispatch is registration-based, not a hand-written
switch.

The world message layer uses `Aws::JavelinGatewayService` — Amazon's own gateway
SDK, statically linked. Each message type is a typed model object with its own
vftable, constructed by a factory function in the `FUN_146473xxx` family. The
handler object vtable is `PTR_FUN_1485034d8`. Factory constructor `FUN_1464733f0`
allocates 0x300 bytes and installs this vtable.

The dispatcher (`FUN_14642b130`) constructs handler objects, acquires an SRW lock
on the connection object (`param_1 + 0x70`/`0x74`/`0x78`), looks up a handler by
message key (`FUN_1416a6030` at offset `+0x68`), and dispatches via vtable slot
`+8` on the registry object (`*(longlong**)(param_1 + 0x28)`).

---

### 17.5 Message type enumeration — complete (client→server, 10 types)

All 10 types confirmed by RTTI. Symbol Table filter `JavelinGateway` (Name Only
unchecked) matched 99 of 422809 symbols. Source: Imported (statically linked AWS
SDK).

| Message Type | vftable Address |
|---|---|
| `JavelinGatewayServiceRequest` (base) | `148703a38` |
| `DeleteGameCharactersCharacterIdRequest` | `148703e8` |
| `GetLoginInfoRequest` | `148703d0` |
| `LinkIdentityRequest` | `148703b8` |
| `ListWorldsRequest` | `148703c0` |
| `PatchCharacterRequest` | `148703a8` |
| `PostGameLoginQueueV2Request` | `148703570` |
| `PostGameLoginQueueV2TicketIdRequest` | `148703658` |
| `PostGameWorldsWorldIdCharactersRequest` | `148703748` |
| `UnlinkIdentityRequest` | `148703828` |
| `ValidateCharacterRequest` | `148703918` |

**No Response/Result types in RTTI.** Server→client responses are not
instantiated as typed RTTI objects — they are deserialized differently (OI-H2-3).
This is the primary gap for Track P: the inbound (server→client) message schema
is not enumerable statically from RTTI alone.

**Protobuf choke point (FIND-2 / P2):** All 10 types go through AWS SDK model
serialization. The move-constructor family (`FUN_146406a90` and siblings) embed
named Javelin model vftables directly. P2 should target the AWS SDK
`SerializePayload` / `GetBody` path on these model types to locate the protobuf
schema boundary. Named model confirmed in `FUN_146406a90`:
`Aws::JavelinGatewayService::Model::PostGameWorldsWorldIdCharactersRequest`.

---

### 17.6 GameConnection state table — complete

State-name array at `PTR_s_Disconnected_1484f9ff0`, base address `1484f9f0`,
indexed by state integer. Full table (H2 extended S0a's partial list):

| Index | Address | State Name |
|---|---|---|
| 0 | `1484f9f0` | `Disconnected` |
| 1 | `1484f9f8` | `QueryGameUpdateCheck` |
| 2 | `1484fa000` | `WaitingForGameUpdateCheck` |
| 3 | `1484fa008` | `QueueGameLogin` |
| 4 | `1484fa010` | `WaitingForQueuedLogin` |
| 5 | `1484fa018` | `QueryForRemoteConfigClass` |
| 6 | `1484fa020` | `WaitingForRemoteConfigClass` |
| 7 | `1484fa028` | `ObtainREPRequirements` |
| 8 | `1484fa030` | `WaitingForREPRequirements` |
| 9 | `1484fa038` | `StartREPConnection` |
| 10 | `1484fa040` | `WaitingForREPConnection` |
| 11 | `1484fa048` | `WaitingForActorGameConnection` |
| 12 | `1484fa050` | `WaitingForSpawnPoint` |
| 13 | `1484fa058` | `WaitingForPlayerSpawn` |
| 14 | `1484fa060` | `InGame` |

State machine function: `FUN_14644a070`. State transition helper: `FUN_14645fd70`.
`InGame` XREF[1]: `FUN_146446800` (only one reader — likely the session health
monitor or a status reporter).

States 5–8 (`QueryForRemoteConfigClass` through `WaitingForREPRequirements`) are
**not handled in `FUN_14644a070`** — a second state-machine function handles them.
Not yet located (OI-H2-4).

---

### 17.7 Handoff notes

**For S1a (first-message expectation):**
The client advances to state 10 (`WaitingForREPConnection`) after `FUN_146425f20`
fires the connect call with credentials at `param_1+0x10c0` / `param_1+0x10e0`.
It then polls `vtable+0xa8` on the REP driver object (`param_1+0x1000`) each tick.
When that poll returns non-zero, it calls `FUN_145a905d0` to set up the actor game
connection and advances to state 0xb (`WaitingForActorGameConnection`). S1a must
therefore complete the DTLS handshake **and** trigger `OnConnect` (which fires
`146474e80`) before the client will advance past state 10. The first epoch-1
message the server must emit is whatever causes `vtable+0xa8` to return non-zero
— that is S1a's primary open question (OI-H2-5).

**For Track P (prioritised message list):**
- All 10 Javelin Gateway request types are client→server. Decode priority:
  `PostGameWorldsWorldIdCharactersRequest` (character placement),
  `PostGameLoginQueueV2Request` (session establishment),
  `GetLoginInfoRequest` (auth info fetch) — these three are on the session
  critical path.
- Server→client response schema is not in RTTI (OI-H2-3); P2 must locate it
  via the AWS SDK `GetBody` / `SerializePayload` path or via H1 runtime capture.
- Protobuf boundary: target `FUN_146406a90` family and the Javelin model
  `SerializePayload` vtable slots.

---

### 17.8 Signatures (scannable, patch-stable)

| Landmark | Signature |
|---|---|
| GameConnection state machine | RTTI string `"GameConnection"` + switch on `param_1[1].field_0x528`; first log call is `"QueryGameUpdateCheck: no game update check needed."` |
| State-name array base | Data pointed to by the array used in all `"Update state %s to new state %s"` log calls in the state machine |
| REPConnection::OnConnect | Log string `"GameConnectionWrapper: REP socket connection established"` |
| REPConnection constructor | Takes `Log&`, `Endpoint const&`, three `std::function` args; installs vtable containing OnRecv thunk at slot `148591750` |
| Javelin dispatch factory | Allocates 0x300 bytes; installs `PTR_FUN_1485034d8` vtable; called from dispatcher that acquires SRW lock at `param_1+0x70` |
| Connect call with credentials | Two LEA instructions loading `param_1+0x10c0` and `param_1+0x10e0` immediately before vtable `+0x18` call on REP driver |
| Javelin model base | RTTI string `Aws::JavelinGatewayService::Model::JavelinGatewayServiceRequest` |

### 17.9 FINDINGS — P2 (protobuf descriptor extraction, static) — 2026-09-04

**Status:** DONE. Whole-binary scan of `NewWorld.exe` b22469132 (179,204,176
bytes, image base `0x140000000`) from the pin at
`~/Documents/nwly-pin/22469132/Bin64/`. No execution, no hooking, no pcap, no
login. Instrument: `p2_scan.py`, validated before use (test #63). Open items
OI-P2-1 and OI-P2-2 added to §15.

Filed as a `###` subsection rather than a new §18: the schema content is one
message, one nested struct and one enum, which does not make §17 unwieldy. The
`## ` count stays 20.

**Verdict: protobuf is present in the client and irrelevant to the world
protocol.** The entire non-stock protobuf surface of a 171 MB binary is a single
telemetry event schema. There is no Javelin descriptor, no `service` block, and
no protobuf-encoded game message of any kind. **FIND-2 closes negative.**
§17.5's "protobuf choke point" claim is corrected in §13.

This is a negative result and it is worth more than the schema P2 went looking
for: it removes a wrong belief from §17.5 and redirects Track P off a dead end
before any perishable capture budget was spent on it.

#### All registered `.proto` blobs — complete, 3 of 3

| # | `.proto` path | package | VA | size | msgs | svcs | signature (first 16B) |
|---|---|---|---|---|---|---|---|
| 0 | `campfire_event_default.proto` | *(none)* | `0x1486f5b60` | 1407 | 4 | 0 | `0a1c63616d70666972655f6576656e74` |
| 1 | `google/protobuf/empty.proto` | `google.protobuf` | `0x1495ab7c0` | 190 | 1 | 0 | `0a1b676f6f676c652f70726f746f6275` |
| 2 | `google/protobuf/descriptor.proto` | `google.protobuf` | `0x1495b3330` | 6028 | 27 | 0 | `0a20676f6f676c652f70726f746f6275` |

All three recovered at `exact` confidence — the extracted slice re-serialises
byte-identically. **Signatures, not offsets** (CHARTER §4): the first 16 bytes
are the encoded `name` field, i.e. the `.proto` path string constant, which
survives a rebase where a VA does not.

Blobs 1 and 2 are stock protobuf well-known types. `descriptor.proto` is present
because `google::protobuf::Reflection` requires it — and that is the **entire**
explanation for T1's FIND-2 flag. Blob 0 is the only non-stock content, and its
"4 messages" are `CampfireEventDefault`, its nested `ContextData`, and two
synthetic map-entry types. Real content: **one message, one nested struct, one
enum.**

Field names, numbers and wire types for every field are in `p2_out/fields.tsv`.
`p2_out/blobs/*.bin` are literal byte excerpts of Amazon's binary and are **not
committed** (CHARTER §3) — same call as the `Bin64/` pin, where only the hashes
went into the repo. The derived `proto/`, `index.tsv`, `fields.tsv` and
`report.md` are findings and are committed.

#### `campfire_event_default.proto` — the only game-adjacent schema, and it is telemetry

Campfire is Amazon's analytics/telemetry pipeline. The envelope
(`version`/`id`/`type`/`sourceTimeMillis`/`sessionId`/`applicationVersion`/
`metrics`/`attributes`/`eventPriority`) is a generic event-reporting shape, and
`ContextData` fields 20–21 are **`test_new` and `test_new_2`** — leftover
developer scaffolding, which no shipped wire protocol carries.

```proto
syntax = "proto3";

message CampfireEventDefault {
  message ContextData {
    string world_id = 1;          string hub_id = 2;
    string player = 3;            string guild_id = 4;
    string character_id = 5;      string persona_id = 6;
    string prefabName = 7;        sint32 territory_id = 8;
    sint32 poi_id = 9;            float xpos = 10;
    float ypos = 11;              float zpos = 12;
    string host_world_id = 13;    sint32 level = 14;
    optional bool IsGM = 15;      double owned_expansion = 16;
    optional CampfireEventDefault.FactionType faction_type = 17;
    optional bool pvp_flag_state = 18;
    string objective_id = 19;
    string test_new = 20;         string test_new_2 = 21;
  }
  enum FactionType { None = 0; Faction1 = 1; Faction2 = 2; Faction3 = 3; }

  uint32 version = 1;                     string id = 2;
  string type = 3;                        int64 sourceTimeMillis = 4;
  optional string utcOffset = 5;          optional string userId = 6;
  optional string sessionId = 7;          optional string applicationName = 8;
  optional string applicationVersion = 9; optional string platformName = 10;
  optional string platformVersion = 11;   optional string locale = 12;
  optional string graphName = 13;
  map<string, ?> metrics = 14;      // emitted as repeated MetricsEntry
  map<string, ?> attributes = 15;   // emitted as repeated AttributesEntry
  optional CampfireEventDefault.ContextData context = 16;
  optional int32 eventPriority = 17;
}
```

**Secondary value — identifier vocabulary, not wire format.** The schema
independently corroborates Amazon's own identifier model: `world_id` /
`host_world_id`, `character_id` / `persona_id`, `guild_id`, `territory_id`,
`poi_id`, `faction_type`, `pvp_flag_state`. The `character_id` / `persona_id`
split matches §17.3's `javelin.impersonate-character-id` /
`impersonate-persona-id` feature flags, and `world_id` vs `host_world_id` is
worth remembering for S0's `RepAddress` rewrite. **Naming crib only — nothing
here is a wire format and nothing should be built on it.**

#### Diagnostics — serialization shape (test #65)

| string | count | reading |
|---|---|---|
| `application/json` | **236** | Javelin is JSON |
| `application/x-protobuf` | **0** | no protobuf transport anywhere |
| `application/octet-stream` | 0 | |
| `JavelinGatewayService` | 20 | matches §17.5's RTTI enumeration |
| `InitializeReplicatedFields` | **94** | matches T1/§10's independent ~94 — cross-check passed |
| `ReplicaChunk` | 23 | GridMate replica marshalling present |
| `google::protobuf::Reflection` | 1 | a single `GOOGLE_CHECK` assert string |
| `AmazonSerializableWebServiceRequest` | 1 | |
| `Aws::Utils::Json::JsonValue` | 1 | |

**Caveat, and it binds: half this table is unreliable.** Every search string
containing `::` was matched **literally**, but MSVC stores RTTI **mangled**
(`JsonView` appears as `?…@JsonView@Json@Utils@Aws@@`). So `JsonView` = 0,
`DataSetBase` = 0, `Marshaler` = 0, `MessageLite` = 0 and `DescriptorPool` = 0
are **artefacts of the search, not evidence of absence** — §16.15 read the
`JsonView` GetString helper directly in Ghidra, and that outranks this table.
**Citable rows are bare identifiers and content-type literals only.** CHARTER §4
— a tool's cap is part of the measurement.

`google::protobuf::Reflection` = 1 is a `GOOGLE_CHECK` assertion string, not
RTTI. **That single assert string was the entire evidentiary basis of FIND-2.**

#### Predictions — recorded before the scan (CHARTER §4)

`P2_PROMPT.md`'s three predictions: **all falsified.**

| Source | Prediction | Outcome |
|---|---|---|
| P2_PROMPT 1 | `InternalAddGeneratedFile` has 20–100 callers; total blob count exceeds the 10 RTTI types | **FALSIFIED.** 3 blobs, 2 of them stock. |
| P2_PROMPT 2 | Response/result types present in the blobs though absent from RTTI | **FALSIFIED.** No Javelin descriptor exists in any form. |
| P2_PROMPT 3 | A `service JavelinGatewayService` block exists — "the single most valuable find P2 can make" | **FALSIFIED.** Zero service blocks across all 3 descriptors. |
| P2-A | ≥1 blob recovered, FIND-2 holds | **Confirmed but hollow** — holds literally, yields nothing on the world protocol. |
| P2-B | No Javelin service block | **CONFIRMED.** |
| P2-C | Packages are infrastructure, not javelin/world/character | **CONFIRMED.** |
| P2-D | JSON, not protobuf | **CONFIRMED.** 236 vs 0. |
| P2-E | `InternalAddGeneratedFile` absent, `AddDescriptors`/`descriptor_table` present instead | **NOT RESOLVED — OI-P2-1.** All three matched 0, but a non-virtual free function's name need not appear in the binary; the string test cannot answer this. |

#### OI-H2-3 — answered, and the answer is mundane

**The server→client schema is absent from RTTI because AWS SDK for C++
`XResult` classes are non-polymorphic value types — no vtable, therefore no
RTTI.** `XRequest` derives from the polymorphic
`AmazonSerializableWebServiceRequest` and so does emit RTTI. "10 request types,
no result types" is the expected shape of SDK codegen, **not** evidence that
responses are deserialized by some exotic path — which was H2's inference and is
now withdrawn.

The inbound Javelin schema is **JSON**, recoverable two ways, neither needing a
running client and neither perishable:

1. **From P0's existing captures** — the auth-phase traffic is already decrypted
   plaintext JSON (§16.2–16.4, §16.9).
2. **From `.rdata` string constants** — AWS SDK JSON field names are `GetString`
   / `WithString` arguments, exactly as §16.15 recovered the `Token` fields.

#### What P2 unblocks, and what it redirects

**Track P retargets off protobuf entirely.** The world stream is **GridMate
`ReplicaChunk` marshalling** (`ReplicaChunk` 23, `InitializeReplicatedFields`
94, plus §10's `VTransformReplicaChunk` / `VTriggerAreaReplicaChunk` /
`ScriptComponentReplicaChunk`). **We hold the source for that** — the Lumberyard
fork at `7d4f1ee6`, which already builds (§5, §7). This is CHARTER §2's thesis
paying off: on this layer the reference build is not merely the check, it is the
primary source, readable with no capture and no client.

**That route is immune to the 2027-01-31 sunset** (§16.0) and should be
prioritised over anything capture-dependent.

**For S1a:** there is no protobuf send-side schema to emit. The Javelin surface
is JSON REST and is very likely the same auth-phase API P0 decoded on TCP/443 —
the ten §17.5 type names are literal REST routes. **Not yet confirmed —
OI-P2-2.**

#### Instrument — `p2_scan.py`

Scans `.rdata`/`.data` for the `FileDescriptorProto` **artefact** rather than for
a registration **function**, because `InternalAddGeneratedFile` is the
proto2/early-proto3 API while protobuf ≥3.10 emits
`internal::AddDescriptors(const DescriptorTable*)` — the artefact is
version-independent, the function is not. Recovers each blob's exact size by
walking its top-level fields, so it never needs the caller's size constant,
which leaves that constant free to serve as an independent check (OI-P2-1).

Validation and the two defects the controls caught are test #63. **Known caps:**
`::`-containing diagnostic strings miss mangled MSVC RTTI (above); `map<>` fields
render with unresolved value types (`fields.tsv` carries the truth); the scanner
finds descriptors **as data** and does not prove any is registered (OI-P2-1); a
compressed or obfuscated descriptor would be invisible, and absence of a hit is
not proof of absence.

## 18. FINDINGS — P5 (replica/chunk model, source-first) — 2026-09-04

**Status:** DONE, with a redirect larger than the chunk itself. Source read from
the pinned Lumberyard fork; retail cross-check performed statically in the warm
`nwly.gpr`. No execution, no hooking, no capture, no login. Opens **OI-P5-1…4**
and a new chunk **P6**. Two §13 corrections, **one of them against P2's own
§17.9**.

Filed as a new `## ` section rather than a `###` under §17: the content spans two
engines plus a newly discovered third layer and does not belong inside H2's
dispatch map. **The `## ` count moves 20 → 21.**

**Source pin:** `github.com/kaatbailey/lumberyard` @ **`7d4f1ee6`**, under
`dev/Code/Framework/GridMate/GridMate/` and `.../AzFramework/AzFramework/Network/`.
Verified 2026-09-04 that `Replica/ReplicaChunk.h`, `Serialize/MathMarshal.h` and
`Serialize/CompressionMarshal.h` are **byte-identical** between `413ecaf` and
`7d4f1ee6` — the `false_v<>` patch touched only `AzCore/RTTI/TypeInfo.h` — so
§7's source-reading facts transfer unchanged.

**Retail instrument:** `NewWorld.exe` b22469132 from the pin, warm `nwly.gpr`.

### 18.0 The headline: there is a THIRD layer, and the game's state is in it

P5 set out to document GridMate's replica wire format on the assumption that the
world stream is GridMate `ReplicaChunk` marshalling. **That assumption was wrong,
and so was the alternative the prompt offered against it.**

| Layer | What it is | Status in retail b22469132 |
|---|---|---|
| **GridMate replicas** | Stock Lumberyard `ReplicaChunk` / `DataSet` marshalling | **Present and stock.** `AzFramework::NetworkContextChunkDescriptor` verbatim from source (`NetworkContext.h:103–119`). Bound chunk types found: `AzFramework::TransformReplicaChunk`, `LmbrCentral::TriggerAreaReplicaChunk` — **both stock engine components, not game content.** |
| **Javelin (AWS SDK)** | JSON REST over HTTP | Auth phase. Settled by P2, §17.9. |
| **`Amazon::Hub`** ← **NEW** | Amazon's own actor/fragment replication framework, built **above** GridMate and using it for transport only | **Where the game's state actually lives.** ~3,600 registered types. Not in the fork — Amazon-proprietary. |

**P5's prediction 0 asked the wrong question.** It was written specifically to
target the chunk's own premise, and it still failed, because it enumerated only
two answers — "the world stream carries `ReplicaChunk` traffic" or "it does not"
— and reality was a third layer neither option named. Every game-state type
(`MB::*ReplicatedState`, `Javelin::*ReplicatedState`) is a **Hub fragment**.

**This is the same error class as P2's, for the third time in two chunks:**
*X is in the binary, therefore the protocol is X* (P2 → protobuf; §17.9 → GridMate;
P5's premise → GridMate again). **Lesson, now recorded twice: a premise-targeting
prediction must leave room for "neither — it is something not yet named."**
Carried into P6's prediction 0.

### 18.1 Amazon::Hub — structure

**Hub is entirely inlined. There is not one named Hub function in the binary.**

| Query | Result |
|---|---|
| Symbols matching `Amazon::Hub` | **3,629 — all `Label`, zero `Function`** |
| Symbols matching `InstallRegistrationHook` | **3,482 — all `Label`, zero `Function`** |
| Functions with `Hub::` in the name | **0** |

Every `InstallRegistrationHook<T>` is inlined into a static initializer. What
survives is the RTTI descriptor of the type-erased lambda each hook constructs:

```
`bool __cdecl Amazon::Hub::InstallRegistrationHook<T>(void)'::__l2::<lambda_1>::RTTI_Type_Descriptor
```

`?1` / `__l2` marks a function-local magic static. **Consequence: hook bodies
cannot be found by name, and XREFs on descriptors and name strings are the only
doors into the layer.** (Test #66.)

**Two address regions, two different orderings:**

- **RTTI descriptors — contiguous, in LINK order**, from `14a1340c0` upward,
  spaced 0x60–0x90 apart. Link order mirrors translation-unit order, which is why
  related services cluster (§18.2).
- **Name strings — scattered, per translation unit.** `s_ReplicateClient`
  `147f42158`; `s_REPClient` `147f47b10` (~0x5A00 away);
  `s_Amazon::Hub::ActorRef` `14803e230` (a third neighbourhood entirely).
  **A single contiguous dump will not enumerate the vocabulary.**

**The registration shape is uniform:** each service registers `X`, then
`X::State`, then each `X::*Msg` — a service, its state fragment, its messages.

### 18.2 The world-session surface — one contiguous ~0xA00-byte neighbourhood

The entire replication and session surface sits together in link order:

| VA | Type |
|---|---|
| `14a134340` | **`ReplicateClient::FragmentUpdateMsg`** |
| `14a1343c0` | `ReplicateClient::State` |
| `14a134430` | `ReplicateClient` |
| `14a134498` | `ReplicateClient::ReplicateClient(void)` — ctor lambda |
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
| `14a134ab0` | **`REPClient::RegistrationRequestV3Msg`** |
| `14a134b30` | **`REPClient::RegistrationRequestV2Msg`** |
| `14a134bb0` | **`REPClient::RegistrationRequestMsg`** |
| `14a134c30` | `REPClient::PingMsg` |
| `14a134ca0` | **`REPClient::RegistrationResponseMsg`** |
| `14a134d20` | `REPClient::TimeSynchMsg` |
| `14a134d90` | `REPClient::State` |
| `14a134e00` | `REPClient` |
| `14a134e60` | `REPClient::REPClient(void)` — ctor lambda |

**`Replicate` / `ReplicateClient` are a server/client service pair**, and
**`ReplicateClient::FragmentUpdateMsg` is the inbound world-state update** — the
server→client direction the project has been chasing since OI-H2-3, now with a
name and an address.

**For S1a this is the most concrete target the project has ever had:** the world
handshake enumerated by name, in **three versioned revisions**
(`RegistrationRequestMsg` / `V2Msg` / `V3Msg`), plus `RegistrationResponseMsg`,
`PingMsg`, `TimeSynchMsg`, and the connection lifecycle
(`REPConnectionListener::ClientConnectionMsg` / `ClientDisconnectionMsg`). This
maps onto §17.3's 15-state GameConnection table. **Which revision b22469132
actually sends is unresolved — P6 step 5.**

Both `REPClient::REPClient(void)` and `ReplicateClient::ReplicateClient(void)`
carry lambda descriptors, so these services register something **at construction
time** as well as via the static hooks.

### 18.3 Hub type identity — a 16-byte `AZ::Uuid`, source UNRESOLVED

Worked example, `ReplicateClient` (test #67).

**vftable at `0x147f42110`, 8 slots**, ending `147f42148` (`DAT_147f42150` begins
the next structure). Slots reach their targets through MSVC **adjustor thunks**
(`MOVSXD RAX,[RCX-4]; SUB RCX,RAX; JMP …`) — multiple inheritance.

| Slot VA | Thunk | Target | What it does |
|---|---|---|---|
| `147f42120` | `LAB_1407c4b28` | `1407f9b60` | `return "ReplicateClient";` — **the type's own name** |
| `147f42128` | `LAB_1407c4b34` | `FUN_1407f9f30` | identity compare — two 8-byte halves, i.e. **16 bytes** |
| `147f42130` | `LAB_1407c4b40` | `FUN_1407f98d0` | visitor / apply, dispatching through a function pointer |
| `147f42138`, `147f42140` | `LAB_1407c4b58` | (shared) | — |
| `147f42148` | — | `FUN_1407c2fd0` | — |

**The vftable and the type's name strings are adjacent** (`0x147f42110` vs
`0x147f42158`), which is why name strings cluster per translation unit rather
than in one table (§18.1).

**`FUN_1407fbe00` produces the identity.** A TLS-guarded magic static
(`_tls_index`, `DAT_14a2e7760`, `_Init_thread_footer`): computes **four
`undefined4` = 16 bytes** exactly once, caches at `_DAT_14a2e7750`, returns its
address. Both slot 1 and slot 2 call it. **16 bytes is `AZ::Uuid`.**

```c
puVar1 = (undefined4 *)FUN_1413e84b0(local_18, &DAT_147f42168, 0);
```

**UNRESOLVED — OI-P5-1, and it is the highest-value open question on the board.**
`147f42168` is `147f42158 + 0x10` — i.e. **past `"ReplicateClient\0"`** (15 chars
plus terminator). The hash input is therefore **the string that follows the type
name, not the type name itself.** Two readings, with opposite consequences:

| If `FUN_1413e84b0` is… | Then `DAT_147f42168` is… | Consequence |
|---|---|---|
| `AZ::Uuid::CreateName` | a name string | **The vocabulary is computable offline.** ~3,600 type names are already in hand from the symbol dump; run them through the same digest and the full name↔UUID map falls out. No extraction needed. |
| `AZ::Uuid::CreateString` | a **literal** `"{XXXXXXXX-XXXX-…}"` emitted by `AZ_TYPE_INFO` | **Not computable.** ~3,600 literal UUIDs must be extracted from `.rdata` and paired with their names across scattered neighbourhoods. |

The 3-argument call with a `0` third parameter fits `CreateString(str, len=0)`.
**The session recorded the optimistic `CreateName` reading as fact mid-analysis
and withdrew it before writing this section** — logged because the withdrawal,
not the guess, is the result. Resolved by reading `DAT_147f42168` and decompiling
`FUN_1413e84b0` against the fork's `AzCore/Math/Uuid.*`. **P6 step 1.**

**Worked example of an inlined hook body: `FUN_1407f3720`.** TLS magic static
(`DAT_14a2e7790`); builds `"ReplicateClient"` inline as an `AZStd::string` —
`0x746163696c706552`, `0x696c4365`, `0x6e65`, `0x74`, `\0`, with length and
capacity both `0xf` — then loops over `(&DAT_147f42168)[i]`, the same following
string. **This is one of the `InstallRegistrationHook` bodies that has no symbol**
(§18.1), recovered only by XREF.

### 18.4 GridMate replica wire format — documented, and it is not the game's

Read from the pin; correct as far as it goes, but see §18.0 — this describes the
layer carrying **engine** components, not game state.

**Replica envelope** (`Replica/Replica.cpp:541`, `Replica::Marshal`):

```
ReplicaId
payloadLen            VLQ, in BITS          <- PackedSize
chunkManifest         VLQ u64 bitmask       <- which chunk slots follow
  per set bit:
    chunkLen          VLQ, in BITS
    chunkPayload:
      [ChunkTypeId : AZ::Crc32]             <- only when IncludeCtorData
      changebits    VLQ u32                 <- dirty DataSet mask
      dirty DataSets, in index order
      RPCs
```

**`PackedSize` is bit-granular, not byte-granular** (`Serialize/PackedSize.h`,
`m_totalBits`), and `Marshaler<PackedSize>` writes **the bit count**, VLQ-encoded.
**A decoder reading these as byte lengths desyncs immediately** — the single most
dangerous gotcha in the format.

**GridMate's VLQ is not protobuf's varint.** Length is signalled by the high bits
of the *first* byte; payload bits pack low-first across the remainder
(`Serialize/CompressionMarshal.h:345`):

| First byte | Total bytes | Value bits |
|---|---|---|
| `< 0x80` | 1 | 7 |
| `0x80–0xBF` | 2 | 14 |
| `0xC0–0xDF` | 3 | 21 |
| `0xE0–0xEF` | 4 | 28 |
| `0xF0+` | 5 | 32 |

**Chunk type id is `AZ::Crc32`** — `typedef AZ::Crc32 ReplicaChunkClassId`
(`Replica/ReplicaDefs.h`). *P5 prediction 1 CONFIRMED.*

**DataSets are dirty-bit gated** — a VLQ-encoded changebits mask, only set
members written (`Replica/ReplicaChunk.cpp:339`, `MarshalDataSets`).
*P5 prediction 2 CONFIRMED.*

**Reserved command IDs** (`ReplicaDefs.h`): `Cmd_Greetings`, `Cmd_NewProxy`,
`Cmd_DestroyProxy`, `Cmd_NewOwner`, `Cmd_Heartbeat`, `RepId_SessionInfo`. Note
the encoding trick recorded in the source: *a CmdId above
`Max_Reserved_Cmd_Or_Id` is implicitly `UpdateReplica`, saving a byte per update.*

**P5 prediction 3 FALSIFIED — transforms are NOT quantized by default.**
`Marshaler<AZ::Vector3>` writes **three raw IEEE floats, 12 bytes**;
`Marshaler<AZ::Transform>` is four Vector3s — **48 bytes, uncompressed**
(`Serialize/MathMarshal.h:59,186`). Quantization exists — `Float16Marshaler`,
`Vec3CompRangeMarshaler`, `QuatCompNormQuantizedMarshaler`, `TransformCompressor`,
`IntegerQuantizationMarshaler` — but is **opt-in per DataSet declaration**.
**This bears directly on P3:** a controlled-walk capture should look for a
smoothly varying **raw float triple**. Whether New World opts in is OI-P5-3.
§13, row 31.

### 18.5 What P5 unblocks and redirects

- **P6 opens** — the Hub message layer, everything in §18.1–18.3. **The Track P
  front.**
- **Track P retargets again**, off GridMate replicas and onto Hub. §17.9's
  retarget was right to leave protobuf and wrong about the destination (§13).
- **For S1a:** the world handshake is enumerated by name (§18.2), and the
  server→client state update has a name — `ReplicateClient::FragmentUpdateMsg`.
- **For P3:** look for raw float triples, not quantized ints (§18.4).
- **OI-H2-3 does not reopen.** P2 answered it for the Javelin direction; §18.2
  supplies the world-state half. The closed row should carry a pointer to §18.2.

### 18.6 Instrument notes and caps

- Ghidra 11.3+ replaced the Jython console with **PyGhidra**; launch via
  `/opt/ghidra/support/pyghidraRun`, not `ghidraRun`. On this machine Ghidra
  lives at `/opt/ghidra`.
- **The PyGhidra console mangles multi-line pastes** — it strips indentation and
  strands the prompt at `...`, after which every subsequent line appends to a
  broken statement. **Run scripts from `~/ghidra_scripts` via Script Manager
  instead.** `hub_probe.py` is the one used here.
- **The Symbol Tree shows namespaces (`{}` icons), not functions.** Symbols
  matching a template name may be `Label` only, with no code attached. **Use the
  Symbol Table and read the Type column.** The session lost time to this twice.
- Whole-symbol-table sweeps take 1–5 minutes on this binary.
- **Cap, and it binds:** every §18.1–18.3 finding comes from **one worked
  example** (`ReplicateClient`) plus symbol-table aggregates. The vftable layout
  is **assumed** uniform across Hub types and **has not been checked against a
  second type** — OI-P5-4. CHARTER §4: one example is one example.

---

## 19. The Hub type vocabulary and the registration mechanism (P6)

**Status:** Step 1 and Step 2 DONE 2026-09-05. Steps 3–5 partially done; Step 4
not started. Static analysis of `NewWorld.exe` b22469132 in `nwly.gpr`, plus the
Lumberyard fork at `7d4f1ee6` for AzCore. No execution, no hooking, no capture.
Scripts run via `analyzeHeadless -readOnly -postScript`.

---

### 19.1 OI-P5-1 ANSWERED — `FUN_1413e84b0` is `AZ::Uuid::CreateStringSkipWarnings`

**The vocabulary is extracted, not computed.** P5's prediction 1 confirmed; the
`CreateName` branch and P6_PROMPT's Step 2a are dead.

Three independent lines of evidence:

1. **The operand is a UUID literal.** `DAT_147f42168` (= `147f42158 + 0x10`,
   past `"ReplicateClient\0"`) is the 36-character string
   `6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d`. Ghidra labels the string from
   `147f42169`; the byte at `147f42168` is `0x36` = `'6'` and the four xrefs
   point at `147f42168`, so the split is a display artifact.

2. **The decompilation matches the fork point for point** against
   `dev/Code/Framework/AzCore/AzCore/Math/Uuid.cpp:61–133` at `7d4f1ee6`:
   the `strlen` branch when the length argument is 0 (`:71–74`); the
   `len < 32 || len > 38` window (`:76`); open-brace handling (`:83–89`);
   `i == 4` dash detection (`:94–100`); the `i == 6 || 8 || 10` dash checks,
   emitted as `((i - 6) & ~6) == 0 && i != 12` (`:104`); `GetValue` folded to a
   single displaced load `pcVar3[-0x73a8]` over the 22-char digit table
   (`:45–51`); `<<= 4` then `|=` (`:119–124`); 16 iterations (`:91`).

3. **Argument count.** `CreateString(const char*, size_t = 0)` is 3 args with the
   x64 sret pointer — matching `FUN_1413e84b0(local_18, &DAT_147f42168, 0)`.
   `CreateName(const char*)` is 2. `CreateData` is 3 but requires
   `dataSize > 0` and returns a null Uuid otherwise (`:295`, `:322`).

**Two minor divergences from the fork, noticed-not-pursued:** retail early-outs
on an empty string as well as null, and validates each hex digit
(`if (0xf < value)` → null Uuid) where `CreateStringSkipWarnings` at this commit
assigns `GetValue`'s result unchecked. Probably an AzCore version delta rather
than a New World change; not established.

**`FUN_1407fbe00` is an MSVC thread-safe function-local static** (`/Zc:threadSafeInit`):
TLS `_Init_thread_epoch` at offset `0x3684` compared against guard
`DAT_14a2e7760`, `FUN_147aa6598` = `_Init_thread_header`, named
`_Init_thread_footer`, 16-byte copy into `_DAT_14a2e7750`. Source is
approximately:

```cpp
static const Uuid& TypeId() {
    static Uuid s_id = Uuid::CreateString("6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d");
    return s_id;
}
```

### 19.2 Two corrections to P6_PROMPT.md, both load-bearing

**`CreateName` is SHA-1, not MD5.** P6_PROMPT Step 1.2 says MD5. At `7d4f1ee6`,
`CreateName` (`Uuid.cpp:285`) forwards to `CreateData` (`:293–322`), which
constructs a `Sha1`, calls `ProcessBytes`/`GetDigest` into five `u32`s and writes
them big-endian; `AzCore/Math/Sha1.h` is included at `:15` and there is no MD5
include. The version nibble written is 5 (`data[6] &= 0x5F; |= 0x50`, `:315–317`,
comment `VER_NAME_SHA1`). `VER_NAME_MD5 = 3` (`Uuid.h:40`) appears only as a
decode case in the version getter (`Uuid.cpp:386`) and is never written.

**Why this mattered:** Step 2a instructs a session to implement `CreateName` from
the fork source. A session trusting the prompt would have implemented MD5, failed
to reproduce the cached bytes, and had a live path to concluding "not
`CreateName` after all" — a false negative on OI-P5-1 that looks like a clean
result.

**The literals are not uniformly brace-delimited.** Step 1.1 and Step 2b assume
`"{XXXXXXXX-...}"`. Both forms are present and both are parsed: `ReplicateClient`
and `REPClient` are unbraced, `PingMsg` and 5,930 others are braced. Brace style
is a per-translation-unit authoring habit and is **not** a discriminator of
anything. A brace-anchored `.rdata` scan would have returned a fraction of the
set.

### 19.3 The `AZ_TYPE_INFO` map — 5,907 types, and what it is NOT

`FUN_1413e84b0` has **15,919 references**, 15,914 of them call/jump. Walking them
and resolving the `rdx` operand recovers **5,907 accessors** with 99.4% site
resolution (101 unresolved, all `MOV`/`XOR`/`CMOV` into `rdx`, i.e. runtime
strings). Each has a single-use literal, a `.rdata` name string within 0–7 bytes,
and the magic-static shape. Output: `hub_vocab3_candidates.csv`.

**This is the engine's `AZ_TYPE_INFO` vocabulary, not Hub's.** AzCore, GridMate,
game components and Hub all share the idiom, so the map spans the whole binary.
**None of the ten session-layer message types appear in it.** A later session
finding a 5,907-row file named `hub_vocab*` must not assume it holds the Hub
vocabulary.

**Tooling trap worth recording:** Ghidra's flat-API `getReferencesTo()` caps its
return array at **4,096** entries and truncates silently. The first run reported
4,092 sites as if complete, sampling only the low `.text` block. Use
`ReferenceManager.getReferencesTo()`, which returns an unbounded iterator.

### 19.4 The registrar — `FUN_1407de270`, the actual Hub mechanism

Hub message types do **not** register through the shared `CreateString`
accessor. `InstallRegistrationHook<T>` bodies are magic statics that:

1. build the type name as an `AZStd::string` (heap or inline);
2. **parse the UUID literal inline** — `CreateString` unrolled, so there is no
   call for a call-site scan to find;
3. call **`FUN_1407de270(&out, uuid_bytes, &name)`** — the registrar;
4. allocate a handler object via `FUN_147aa6610(0x10)`, store a vftable pointer
   in it, and install it at `out + 0x48`, releasing any prior occupant through
   its own virtual;
5. register an `atexit` destructor.

Worked examples read in full: `FUN_1407eeca0` (`FragmentUpdateMsg`),
`FUN_1407f0fb0` (`PingTrait`), `FUN_1408947a0` (anonymous).

**`FUN_1407de270` has 3,512 references, 3,511 call/jump** — against **3,482**
`InstallRegistrationHook` symbol instantiations, two independently derived counts
30 apart. This is the Hub type set.

### 19.5 The vocabulary — 3,509 identities; names exist for 311 by design

Walking the registrar's call sites recovers **3,509 distinct UUIDs from 3,510
rows** — essentially one identity per registered Hub type. Output:
`hub_vocabulary.csv` (uuid, literal VA, name, handler vftable, hook VA, site).

**311 named, 3,199 anonymous, and the anonymity is deliberate.** The named hooks
build a real string (`local_18 = 9`, `local_10 = 0xf`, buffer holding
`"PingTrait"` — `FUN_1407f0fb0`). The anonymous hooks construct an **explicitly
empty** string and pass it anyway (`local_18 = 0`, `local_28 = 0`,
`local_10 = 0xf` — `FUN_1408947a0`), and are otherwise structurally identical.
**The names do not exist in the binary for those 3,199 types**, so no extraction
strategy could recover them. Four unrelated approaches converging on the same
8.9% was the data constraining the result, not the tooling.

**The split is regional, not scattered.** Named hooks occur only in `1407xxxxx`
(92) and `146axxxxx` (219); every other region (`1416`, `1468`, `1434`, `143e`,
`1429`, `1428`, `1448`, and a long tail) is entirely anonymous. The two named
regions are exactly the ones holding `ReplicateClient`, `REPClient`, the
registration messages, `FragmentUpdateMsg` and the connection messages.

**Finding: Hub attaches runtime names only to the wire-facing session and message
layer; everything else is identified by UUID alone.** The anonymous set also uses
uppercase UUID literals against the named set's lowercase — a different source
convention, consistent with generated code.

**Name collisions are real.** 311 named rows yield only ~288 distinct names, and
MSVC `/GF` identical-string-pooling merges name literals across translation units
while each type keeps its own UUID literal. **The UUID is the key; the name is a
label.** Two distinct `FragmentUpdateMsg` types and two distinct `PingMsg` types
exist.

### 19.6 Step 5 — the session-layer types, with identities

The most S1a-actionable output of the chunk. All recovered from the registrar
map with hook and handler addresses.

| Type | UUID | Hook | Handler vftable |
|---|---|---|---|
| `RegistrationRequestMsg` | `8673a3cc-2848-4c87-aa72-cc860589d1b5` | `1407f27f0` | `147f47108` |
| `RegistrationRequestV2Msg` | `da4e5889-a65c-4480-8642-0278160125a7` | `1407f2a20` | `147f471f0` |
| `RegistrationRequestV3Msg` | `0b826b33-89f5-49e0-b8cb-fe4433427778` | `1407f2c50` | `147f47278` |
| `RegistrationResponseMsg` | `104145a7-ff95-44f1-9468-21fb41c8ac2b` | `1407f2e80` | `147f46910` |
| `TimeSynchMsg` | `038cd847-0653-4243-9a26-936e3bd7f312` | `1407f6a30` | `147f46648` |
| `ClientConnectionMsg` | `c4f1e7b5-d502-49f4-ac71-27928c9d25c5` | `1407ec310` | `147f483d8` |
| `ClientDisconnectionMsg` | `cabd72ff-cca0-4c8a-804e-c585b386dcfe` | `1407ec550` | `147f48688` |
| `PingMsg` | `6a379fb8-0bdd-43a1-ab3e-9843d7be8cd3` | `1407f0940` | `147f46d38` |
| `PingMsg` (second type) | `519a3d71-f901-46b8-8969-f47b6fd492bc` | `146aceec0` | `148575db0` |
| `PingRequestMsg` | `ad4c28bd-4208-4b47-9679-9a46dd9e5287` | `1407f0b60` | `147f478c0` |
| `PingResponseMsg` | `259734dd-9277-4e08-b11f-1ab9e71de1be` | `1407f0d80` | `147f47ad8` |
| `PingTrait` | `a535df54-830c-4bef-a8ae-2020c796a806` | `1407f0fb0` | `147f46f28` |
| `PingTrait::State` | `e43d64aa-fa73-403c-a5c4-a184f7352437` | `1407f58b0` | `147f47c08` |
| `REPClient` | `532e765a-3393-4a50-9010-b73c627512b2` | `1407f1870` | `147f45570` |
| `REPClient::State` | `91a9cf78-0214-461b-8471-1b0e96224da9` | `1407f5f50` | `147f46ac0` |
| `Replicate` | `ff1ec011-3d18-4f09-a0ac-3fb27b313984` | `1407f3500` | `147f420d0` |
| `Replicate::State` | `d3d3e94e-2966-4f14-8ffa-dd3b61161d5c` | `1407f65e0` | `147f435d0` |
| `ReplicateClient` | `6bb22ea1-feb6-4f4b-81ab-79372b9f1f3d` | `1407f3720` | `147f43b08` |
| `ReplicateClient::State` | `44e6eeea-541f-4534-a540-a5a08f377907` | `1407f6800` | `147f44978` |
| `FragmentUpdateMsg` | `951ef3ed-c9a0-4e3d-a6fd-7fe0673d28d2` | `1407eeca0` | `147f44828` |
| `FragmentUpdateMsg` (second) | `62f68299-7bb2-4e0a-90d9-b664bd363dae` | `146ac5390` | `148578628` |
| `FragmentUpdatesMsg` (plural) | `560a34b3-9acc-473f-93a4-a62a78de39a2` | `146ac55c0` | `148578ac0` |
| `DebugPingMessage` | `fa98cc6a-2e38-4d8c-9346-6f348c3df1e0` | `146ac3ff0` | `148574b68` |
| `PersistencePingMessage` | `6057eb60-bac3-4fa7-a06d-3d013c09be21` | `146ace390` | `14857efc8` |

**All three registration revisions exist and are registered.** Their hooks are
contiguous — `1407f27f0`, `1407f2a20`, `1407f2c50`, 0x230 apart, one emission
run. **Which revision b22469132 actually sends is NOT answered** (OI-P6-2); this
establishes only that all three are registered.

`Replicate` and `ReplicateClient` each have a paired `::State` type, matching the
`*ReplicatedState` convention in the name dump.

### 19.7 OI-P5-4 ANSWERED — the vftable layout is NOT uniform

`FragmentUpdateMsg`'s handler table at `147f44828` has **4 entries**
(`FUN_1407c7db0`, `FUN_1407c7df0`, `LAB_1407c7b40`, `LAB_1407c7b50`) against
`ReplicateClient`'s **8 slots** at `147f42110` (§18.3).

**§18.3's 8-slot layout is a single-instance observation and is restated as
such.** Caveat recorded honestly: these may be different *kinds* of object — a
message handler versus a type — so the claim is that layout is not uniform
across Hub types, not that §18.3 was wrong about `ReplicateClient`.

Related correction: §18.3 says the accessor "caches 16 bytes." True at runtime.
**The slot is a lazily-initialised function-local static and reads as zero in the
static image** — `_DAT_14a2e7750` is all zeros on disk. A static reader who goes
to the address will otherwise think the claim is false. This also kills any
notion of harvesting the vocabulary from `.data`.

### 19.8 Three dead routes — do not retry

Recorded so a successor does not spend the same passes.

1. **Name↔UUID by `.rdata` adjacency.** Works for unpooled top-level types
   (gap 0–7) and fails otherwise: `/GF` string pooling merges name literals
   across translation units (`FragmentUpdateMsg` at `147f423d0` has one string,
   two xrefs, two owning types), and anonymous types have no name at all.
   `REPClient::State` at `147f48070` is followed by *two* literals.

2. **`InstallRegistrationHook<T>` RTTI descriptors → hook.** The 3,482
   descriptors carry the qualified type name in mangled form, but they describe
   the `<lambda_1>` inside the hook — `std::function` type-erasure machinery —
   and each has exactly one code xref that lands nowhere near its hook. Two
   samples: `14a134340` → `1407c9370`; `14a134b30` → `1407c3a70`. Neither
   appears in the registrar map. **There is no path from descriptor to hook.**

3. **Hook → vftable → COL → type descriptor.** The identity accessors are not
   virtual: every one of `FUN_1407fbe00`'s 20+ xrefs is a `CALL`, none from
   `.rdata`. They do not appear in vftables, so the standard MSVC RTTI chain
   does not apply.

### 19.9 Predictions (CHARTER §4)

- **0 (premise) — FALSIFIED, in the manner the prompt required be left open.**
  Not "UUID on the wire" vs "negotiated index" but a **fourth possibility**: two
  distinct identity mechanisms coexist, and the one P6 first mapped
  (`AZ_TYPE_INFO` via shared `CreateString`) is **not** the one the message layer
  uses. Whether the UUID reaches the wire at all remains untested (OI-P6-5).
- **1 — CONFIRMED.** `CreateString`, not `CreateName`. §19.1.
- **2 (negotiated index) — UNTESTED.** Step 4 not started.
- **3 (uniform 8-slot vftable) — FALSIFIED.** §19.7.
- **4 (Hub rides beside GridMate replicas) — UNTESTED.** Step 4 not started.

### 19.10 Method note — the session's own error rate

Six hypotheses were advanced and falsified before the mechanism was found:
brace style as a discriminator; two populations split on braces; qualified names
being the emitted form; the caller-column join; a second UUID parser; small-string
capacity explaining the missing names. **Every one generalised from a single
example** — the same failure §18.6 flagged as P5's cap and the same one test #68
records.

Contributing factor worth recording: the analyst had no direct interface to
Ghidra, so each hypothesis cost a full round trip to test. The scripts that
worked were mechanical once the anchor was known; the anchoring was not. A
delegated agent could run the enumeration but would not supply the "how many
examples is this resting on" check, and would produce a clean-looking map with an
unaudited name column.

