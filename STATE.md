# nwproto — AI session handoff

Paste this whole file at the start of a new session. It is the single source of
truth for what this project is, what already exists, what has been proven, and
what comes next. Nothing described here as existing needs to be rebuilt.

> **Governance (from CHARTER §5).** This file is append-only in practice. Add
> findings; promote UNVERIFIED → CONFIRMED with evidence. Do **not** delete,
> reorder, or "clean up." A wrong belief moves to the Corrections table (§13); it
> does not disappear.

---

## 1. What this project is

**The goal is a working private server the unmodified New World client connects
to**, reached by understanding the client's network layer. Built in three layers,
in this order:

1. **Transport layer** — how the client secures and frames network messages
   (socket path, crypto boundary, packet headers, reliability, reassembly).
   **Not started.**
2. **Protocol layer** — what the messages mean (handshake, dispatch table,
   replica model, wire encoding of the messages a session needs). **Not started.**
3. **Server layer** — a server that completes a handshake, stands a character in
   the world, and serves enough state to render and move. **Not started.**

**Prior belief going in (UNVERIFIED until T1):** the client is GridMate-based or a
fork of it. New World's development began ~2016 on Amazon Lumberyard, which is the
GridMate era; but Amazon had ~5 years and a dedicated engine team before the 2021
launch, and O3DE deprecated GridMate for `AzNetworking` around 2021. So the client
could be stock GridMate, an internal fork, or a full replacement. **T1 settles
this and nothing should be built on the assumption before it does.**

### The reference build is the primary instrument, not a side project

We have the Lumberyard fork the client was built from. A GridMate `Carrier` test
built from that fork — two processes, our control, full source, symbols, no
runtime protections — is the independent source against which every claim about
the retail client is checked (CHARTER §2, §4). When the reference build and the
retail client conflict, the retail client is the truth; the reference is how we
understand it.

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

Nothing is built yet, but the reference fork has been **read from source** (see §7)
and that answered several questions T4 would otherwise have hit blind: the crypto is
confirmed OpenSSL DTLS, the dependency surface is AzCore-only, the C++ standard is
C++14, the Linux platform-header include paths are known, and the test harness +
certs are located. The `T4_PROMPT.md` file is written and ready to run.

The retail-client work (T1/T2 fingerprint) is still fully open and remains the thing
that confirms whether the §7 reference facts survived into the shipped client.

**Tooling on hand (per owner):** Ghidra, the retail New World client, the Lumberyard
fork (cloned to `~/Documents/lumberyard`). **Still to set up:** the reference
GridMate build from the fork (T4 — prompt ready), static-analysis extras
(pev/radare2 for T1/T2), Wireshark (T3), Frida (H1).

---

## 3. What is next, in order

Two things can proceed in parallel now, because §7 unblocked T4's inputs:

**T4 — Reference `Carrier` build** (prompt ready in `T4_PROMPT.md`). Stand up the
known-good instrument. Every input is resolved: carve-out scope, `-std=c++14`,
clang-22-first, OpenSSL/DTLS, include paths, certs, harness pattern. Deliverable is
two Carriers connecting locally, captured. This produces the reference handshake T5
needs.

**T1 — Engine fingerprint (retail).** Static Ghidra pass on the retail client.
GridMate vs O3DE `AzNetworking` vs rewrite. Confirms whether §7's reference facts
survived into the shipped client. Independent of T4 — can run alongside.

Then:
- **T2 — Crypto-library fingerprint (retail).** Confirm the plaintext boundary is
  OpenSSL `SSL_read`/`SSL_write` as §7 predicts, or find what replaced it.
- **T3 — Transport recon.** Wireshark, no hooks. Transport, ports, size/timing,
  entropy transition.
- **T5 — Reference vs retail handshake diff.** The milestone: does the retail
  ClientHello match the DTLS `RecordHeader`/`HandshakeHeader` shape from §7?

D2 (`.datasheet` extraction) runs in parallel from the start — low effort, and the
server needs the data to serve anything.

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

---

## 5. Environment and machine layout

Owner's environment (from user setup): **Garuda Linux, fish shell**, IntelliJ /
CLion available; the retail client is Windows, so Ghidra runs against the Windows
binary and dynamic work (Frida, Wireshark) targets the client under Windows or
Proton — record which once T3/H1 establish the working setup.

| What                        | Path / value                          |
| --------------------------- | ------------------------------------- |
| Client build under test     | `<record exact version + kept installer>` |
| Retail client binary        | `<path>`                              |
| Lumberyard fork (reference) | `~/Documents/lumberyard` (github.com/kaatbailey/lumberyard, stock fork of aws/lumberyard, `master`). GridMate at `dev/Code/Framework/GridMate/`, AzCore at `dev/Code/Framework/AzCore/`. |
| Lumberyard fork commit      | `413ecaf24d7a534801cac64f50272fe3191d278f` (the tree all §7 facts were read from) |
| Lumberyard fork commit      | `413ecaf24d7a534801cac64f50272fe3191d278f` (the tree all §7 facts were read from) |
| NWLY repo                   | `github.com/kaatbailey/NWLY`, branch `Master` (capital M) |
| Toolchains                  | System **clang 22** (used by PZMapMaker — do not disturb). If an old clang is needed for the fork, drop LLVM 14 into `/opt/llvm14` (isolated, no PATH change) and point CMake at it; keep the two projects separate via CLion toolchains. |
| Local OpenSSL               | **3.6.4 (25 Aug 2026)**, Garuda system package. Probe result below. |
| Ghidra project              | `<path>`                              |
| Capture output              | `<path>`                              |

Gotchas found so far:
- **`fd` is not installed** on this machine; use `find`. `rg` (ripgrep) IS present.
  Watch stray `-h` in a piped command — it can be parsed as ripgrep's `--help` and
  dump the man page instead of matching.
- **Disk:** single 1.9T nvme root (`/dev/nvme0n1p2`), ~591G free as of setup. Room
  for `/opt/llvm14` (~1.5G) and captures.
- **Installed static-analysis tools:** Ghidra (owner-installed). Still to add per
  chunk: pev/radare2 (T1/T2), Wireshark (T3), Frida (H1), zstandard (D2).
- **Proton vs native for dynamic tools is still undecided** — the retail client is
  Windows; where it runs decides the Frida/Wireshark setup. Record once T3/H1 land.

<!-- Keep filling as things cost time: fish quoting, alias surprises, RTTI survival in the client build. -->

---

## 6. What already exists — do not rebuild

**`t4_openssl_probe.cpp`** (repo root) — a single translation unit reproducing
every OpenSSL call site in `SecureSocketDriver.cpp` at fork commit `413ecaf`.
Compile it to answer "does the local OpenSSL match the API era this source
assumes" in one step. Build line is in its header comment. Re-run it after any
OpenSSL major upgrade; that is the whole point of keeping it.

Otherwise nothing yet. This section fills as chunks complete. Each completed chunk's
FINDINGS block folds into the relevant section here.

---

## 7. Transport facts — CONFIRMED from the reference fork source (pre-T4)

Established by reading `~/Documents/lumberyard` directly, before any build. These
describe **GridMate as it ships in the fork**. They are the reference layout; the
*retail* client (built years later) must still be fingerprinted (T1/T2) to confirm
each survived — Amazon may have swapped OpenSSL for BoringSSL, moved DTLS versions,
or switched to the stream driver. UNVERIFIED-for-retail is noted where it matters.

### The secure transport is OpenSSL DTLS

`dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp` includes
`<openssl/ssl.h>`, `<openssl/bio.h>`, `<openssl/err.h>`, `<openssl/x509.h>`,
`<openssl/hmac.h>`, `<openssl/rand.h>` — **OpenSSL called directly, not abstracted.**
It is unmistakably DTLS: uses `DTLS1_VERSION`, `DTLS1_RT_HEADER_LENGTH` (13-byte
record header), `DTLS1_HM_HEADER_LENGTH` (12-byte handshake header),
`SSL3_MT_CLIENT_HELLO`, and a hello-verify-request cookie exchange.

**Consequences:**
- The plaintext hook boundary (H-track) is OpenSSL `SSL_read` / `SSL_write` — the
  charter §4 "hook above the crypto" target, now confirmed from the reference side.
- The `RecordHeader` (13 bytes) and `HandshakeHeader` (12 bytes) structs in that
  file **are the DTLS wire framing**. They are T5's reference layout — read them,
  don't reverse them.
- There are **two** secure drivers: `SecureSocketDriver` (datagram/DTLS) and
  `StreamSecureSocketDriver` (stream/TLS). Which one the retail MMO uses for its
  main connection is a specific T5 question — persistent-world traffic could lean
  either way. **UNVERIFIED for retail.**

### GridMate's dependency surface is clean

Every non-GridMate include is `<AzCore/...>` or standard library — nothing from
other frameworks (no AzFramework, no gems). The T4 carve-out is therefore
**AzCore + GridMate only**. The AzCore surface used is foundational and broad but
shallow: `Memory` (allocators), `std/` (their STL reimpl — containers, smart
pointers, `parallel/*` threading), `Math`, `EBus`, `RTTI/TypeInfo`,
`Socket/AzSocket` (UDP), `State/HSM`. Links pthreads.

### Build facts

- **C++ standard: C++14.** `dev/Tools/build/waf-1.7.13/platforms/compile_settings_clang.py`
  sets `-std=c++1y`. Pass `-std=c++14` to a standalone build.
- **No hard clang version gate.** `AZ_COMPILER_CLANG` is defined as `__clang_major__`
  in `PlatformDef.h` — it accepts whatever clang major is present. So try system
  clang 22 with `-std=c++14 -Wno-error` first; provision `/opt/llvm14` only on real
  compile errors from removed C++14-era features. UNVERIFIED whether clang 22
  actually compiles it clean — that is T4 step 1.
- **Platform-header include paths** (what Waf resolves and a standalone build must
  supply): Waf prepends the `Platform/<OS>/` dir to the include search path. For
  Linux:
  - `dev/Code/Framework/AzCore/Platform/Linux`
  - `dev/Code/Framework/GridMate/Tests/Platform/Linux` (harness only)
- **Test certificates:** `dev/Code/Framework/GridMate/Tests/Certificates.cpp` defines
  `g_untrustedCertPEM` / `g_untrustedPrivateKeyPEM` (declared `extern` in the tests).
  Compile that file to satisfy the DTLS handshake's cert/key need.

### The test harness — a gift, with a caveat

`dev/Code/Framework/GridMate/Tests/Carrier.cpp` is Amazon's own two-process Carrier
test, with `SocketDriverProvider` (plaintext) and `SecureDriverProvider`
(DTLS) already abstracted — i.e. the charter §2 plaintext-then-secure toggle is
built in. But `Tests.h` drags in AzCore UnitTest, Driller, Streamer, and the
Session layer, more than §2 needs. T4 plan: write a minimal `main()` (Path B),
using `Carrier.cpp` as the construction pattern, not the full harness (Path A).

**Caveat — DTLS-on-Linux is likely untested by Amazon.** No
`AZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER` definition exists under the Linux
platform dir, so it defaults off. T4 must define it explicitly and should expect to
shake out Linux-specific DTLS-path bugs. The **plaintext** Carrier path is the safe
first milestone.

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

**Verified on the target machine.** CONFIRMED on **clang 22 + OpenSSL 3.6.4**,
`-std=c++14`: 0 errors, exactly the 3 warnings tabled above (test-log #4). Also
CONFIRMED on OpenSSL 3.0.13 for the compile/link/handshake, so the result holds
across six minor versions rather than resting on one. Re-run
`t4_openssl_probe.cpp` after any OpenSSL major upgrade; that is what it is for.

---

## 8+. Reserved for later confirmed findings

Sections from 8 onward are added as work produces confirmed results — retail
fingerprint (T1/T2), header layouts confirmed against the reference build (T4/T5),
message formats decoded from captures (P-track). Append-only: a new finding gets a
new section; a finding that overturns an old one adds a Corrections row (§13) and
promotes/demotes the claim rather than editing history away.

---

## 13. Corrections — beliefs that turned out wrong

Acting on any of these wastes real time. Empty at project start; every session
that overturns a prior claim adds a row here rather than deleting the claim.

| Old claim | Status |
| --------- | ------ |
| "OpenSSL 3.x will break `SecureSocketDriver.cpp` at T4 step 5 — expect removed 1.0.2-era APIs (custom `BIO_METHOD`, `HMAC_CTX_init`, opaque-struct breaks)." Raised in session, never promoted past UNVERIFIED. | **WRONG.** The file is already 1.1.0-era API. Compiles with 0 errors / 3 deprecation warnings on OpenSSL 3.0.13; DTLS 1.2 handshake completes with the shipped certs. Cause of the error: predicted from Lumberyard's release date instead of reading the file. Two tells were visible in the source the whole time (`X509_get0_notBefore`, `BIO_s_mem`). Lesson is charter §4 verbatim — *prefer the source to the sample*. |

---

## 14. Test / capture log

A numbered, append-only log of every experiment run, its prediction, and its
result — so no test is silently retried and no result is remembered wrong. Empty
at project start.

| #   | Test / capture | Prediction | Result |
| --- | -------------- | ---------- | ------ |
| 1 | Compile + link a probe TU reproducing every OpenSSL call site in `SecureSocketDriver.cpp` @ `413ecaf`, `-std=c++14`, against OpenSSL 3.0.13 headers/libs. | Hard errors from APIs removed after 1.0.2. | **Prediction falsified.** 0 errors, 3 deprecation warnings, links and runs clean. Artefact kept as `t4_openssl_probe.cpp`. |
| 2 | Live DTLS 1.2 handshake (`openssl s_server`/`s_client`) using the `Certificates.cpp` cert+key and the hardcoded `ECDHE-RSA-AES256-GCM-SHA384`, OpenSSL 3.0.13. | Rejected on security level or cipher policy. | **Prediction falsified.** `Protocol: DTLSv1.2`, `Cipher: ECDHE-RSA-AES256-GCM-SHA384`, `Verify return code: 0 (ok)`. |
| 3 | `openssl ciphers -s -v 'ECDHE-RSA-AES256-GCM-SHA384'` on the actual target machine (Garuda, OpenSSL 3.6.4). | Cipher still listed at default seclevel. | **Confirmed.** Listed, `TLSv1.2 Kx=ECDH Au=RSA Enc=AESGCM(256) Mac=AEAD`. |
| 4 | Compile `t4_openssl_probe.cpp` on the target machine: **clang 22, OpenSSL 3.6.4**, `-std=c++14`. | 0 errors, the same 3 deprecation warnings. | **Confirmed exactly.** 0 errors; 3 warnings (`ERR_load_BIO_strings`, `ERR_load_SSL_strings`, `DTLSv1_2_method`). Crypto-library question for T4 step 5 is closed. Side result: clang 22 accepts `-std=c++14` on this TU without complaint — a first, narrow data point for step 1. |
