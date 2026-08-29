# nwproto — AI session handoff

Paste this whole file at the start of a new session. It is the single source of
truth for what this project is, what already exists, what has been proven, and
what comes next. Nothing described here as existing needs to be rebuilt.

> **Governance (from CHARTER §5).** This file is append-only in practice. Add
> findings; promote UNVERIFIED → CONFIRMED with evidence. Do **not** delete,
> reorder, or "clean up." A wrong belief moves to the Corrections table (§13); it
> does not disappear.

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
   **In progress.** T1, T2, T4 complete; T3 next, then T5.
2. **Protocol layer** — what the messages mean (handshake, dispatch table,
   replica model, wire encoding of the messages a session needs). **Not started**
   — blocked on H3, which is blocked on H1+H2.
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

**As of 2026-08-29.**

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

**Open, in dependency order:** T3 (retail transport recon) → T5 (the milestone
diff) → H1, H2 → H3 → P-track → S-track. D1 can start any time.

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

**T3 — Transport recon (retail).** Prompt written: `T3_PROMPT.md`. Wireshark on a
real login-to-in-world session, no hooks. This is the last input T5 needs, and it
also settles §7's UNVERIFIED-for-retail question of which secure driver carries
the world connection (`SecureSocketDriver` / UDP-DTLS vs.
`StreamSecureSocketDriver` / TCP-TLS).

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

**Then T5 — reference vs retail handshake diff.** The chunk that answers the
charter's core question. Both inputs will be in hand: the reference epoch-0
handshake from T4 (§9) and the retail epoch-0 handshake from T3.

**Then Track H opens.** H2 (locate the dispatch point in retail, static Ghidra)
can in fact start now — it needs no login and no running client. It is the
fallback if T3 stalls for lack of a usable account or live servers.

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
| Ghidra project              | Not yet created. RTTI survived (§10), so run the PE RTTI analyzer on first import — it recovers the `ReplicaChunk` class tree cheaply and is H2's starting point. |

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

**`T3_PROMPT.md`** — the ready-to-run chunk prompt for T3.

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
  prediction — see §3.
- There are **two** secure drivers: `SecureSocketDriver` (datagram/DTLS) and
  `StreamSecureSocketDriver` (stream/TLS). Which one the retail MMO uses for its
  main connection is a specific T3/T5 question — persistent-world traffic could
  lean either way. **UNVERIFIED for retail.**

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
spend time chasing it.

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

---

## 10. FINDINGS — T1 (engine fingerprint) + T2 (crypto), static

**Client build under test:** `NewWorld.exe`, 171 MB, Steam install, unpacked,
buildid 22469132. OpenSSL version string `OpenSSL 1.1.1k  25 Mar 2021`. (Exact
game version string from the launcher still not recorded — worth pulling before
T5.)

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

## 13. Corrections — beliefs that turned out wrong

Acting on any of these wastes real time. Every session that overturns a prior
claim adds a row here rather than deleting the claim.

| Old claim | Status |
| --------- | ------ |
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
