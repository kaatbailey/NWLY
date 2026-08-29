## T4 — Build the reference `Carrier` from the fork

**Paste order for this session:** `CHARTER.md`, then `STATE.md`, then this prompt.

> You have been given `CHARTER.md` and `STATE.md`. Work **only** this chunk. If you
> find something that belongs to another chunk, record it in FINDINGS under
> "Noticed, out of scope" and do not act on it.
>
> Do not rewrite `CHARTER.md`. Do not delete anything from `STATE.md`.
>
> Charter §3 rules out anti-cheat work absolutely. If a line of inquiry only pays
> off against an integrity/attestation system, stop and record it as off-charter.
>
> The owner runs every command. Give exact commands with real paths. Record the
> exact fork commit under test in FINDINGS.

**Deliverable:** two GridMate `Carrier`s connecting locally in a process we
control, captured both plaintext and DTLS-secured. This is the reference
instrument the whole project leans on (CHARTER §2).

### What is already known from the tree (do not re-derive — see STATE §7)

- **Dependency surface is clean.** GridMate includes only `<AzCore/...>` and the
  standard library — nothing from other frameworks. The carve-out is: compile
  **AzCore** + **GridMate**, ignore the rest of the tree.
- **C++ standard is C++14** (`-std=c++1y` in `compile_settings_clang.py`).
- **No hard clang version gate** (`AZ_COMPILER_CLANG = __clang_major__`). Try the
  system clang 22 first with `-std=c++14 -Wno-error`. Provision `/opt/llvm14`
  ONLY on real compile errors from removed C++14-era features, not on warnings.
  Do not disturb the system clang PZMapMaker uses.
- **Crypto is OpenSSL DTLS, confirmed in source.** `SecureSocketDriver.cpp`
  includes `<openssl/ssl.h>` etc. and uses `DTLS1_VERSION`, `DTLS1_RT_HEADER_LENGTH`
  (13), `DTLS1_HM_HEADER_LENGTH` (12), `SSL3_MT_CLIENT_HELLO`. Link `libssl` +
  `libcrypto`. The `RecordHeader` / `HandshakeHeader` structs in that file are the
  DTLS wire framing and become T5's reference layout — read them, do not reverse
  them.
- **Platform-header include paths** (the thing bypassing Waf usually breaks) are
  known. Waf prepends the `Platform/<OS>/` dir to the include search path. For
  Linux, add these `-I` dirs:
  - `dev/Code/Framework/AzCore/Platform/Linux`
  - `dev/Code/Framework/GridMate/Tests/Platform/Linux` (only if using the harness)
- **OpenSSL 3.x is NOT a blocker — this was checked and the worry was wrong.**
  `SecureSocketDriver.cpp` targets the 1.1.0+ API era (it uses
  `X509_get0_notBefore` and `BIO_s_mem`, and carries no version guards). It
  compiles against OpenSSL 3.x with **0 errors and 3 deprecation warnings**
  (`DTLSv1_2_method`, `ERR_load_BIO_strings`, `ERR_load_SSL_strings`). Add
  `-Wno-deprecated-declarations` at step 5. Do **not** provision an
  `openssl-1.1` compat package, and do not spend time writing a shim. The
  pinned cipher `ECDHE-RSA-AES256-GCM-SHA384` and the RSA-4096 / SHA-384 test
  cert both clear modern security-level policy. See STATE §7 and test-log #1–3.
  Confirm with `clang++ -std=c++14 -c t4_openssl_probe.cpp -o /dev/null`
  before step 5; that is the entire check.
- **STEPS 1-4 ARE DONE.** Archives build (`build_gridmate.sh`), the two-Carrier
  plaintext session passes (`nwly_carrier_probe.cpp`), traffic is captured
  (`capture_carrier.sh`) and the header layout is confirmed against it
  (`decode_carrier.py`). See STATE §7, §8 and test-log #10-#16. **Only step 5
  remains.** Add `-DDTLS1_RT_HEARTBEAT=24` to every GridMate compile — one
  OpenSSL 3 removal, no source edit. Two runtime traps are already solved in the
  probe: create `OSAllocator` before `SystemAllocator`, and scope EBus handlers
  so they die before `GridMateDestroy`. Do not re-derive any of this.
- **STEP 1 IS DONE. Use this recipe, do not re-derive it.** From
  `dev/Code/Framework`:
  `clang++ -std=c++17 -include utility -fdelayed-template-parsing -w -c <file>.cpp -I AzCore -I AzCore/Platform/Linux`
  Verified 0 errors / 0 warnings on clang 22 for `Math/Vector3.cpp` and
  `Math/Sfmt.cpp`. **The source is C++17, not C++14** — `Math/Crc.inl:114` uses
  an `auto` template parameter. `-include utility` and
  `-fdelayed-template-parsing` fix a dropped libstdc++ transitive include and a
  clang strictness change respectively; both are toolchain drift, neither needs
  a source edit. **Do not provision `/opt/llvm14`** — that decision is closed.
  Keep `Platform/Common/` in the checkout. See STATE §7 and test-log #5–#9.
- **Test certs exist:** `dev/Code/Framework/GridMate/Tests/Certificates.cpp` defines
  `g_untrustedCertPEM` / `g_untrustedPrivateKeyPEM`. Compile that file to resolve the
  `extern`s DTLS needs.
- **The secure test path was likely never run on Linux.** No
  `AZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER` definition exists under the
  Linux platform dir, so it defaults off. You must define it yourself
  (`-DAZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER=1`) and should EXPECT to
  shake out Linux-specific bugs on the DTLS path. The plaintext path is the safe
  first milestone.

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

1. **Toolchain probe.** Try to compile one AzCore `.cpp` (e.g. a Math or Memory
   unit) with `clang++ -std=c++14 -Wno-error -I<AzCore root> -I<AzCore Linux platform>`.
   Predict: it compiles with warnings. If it errors on removed C++ features, that is
   the signal to provision `/opt/llvm14` — record which errors, they are data.
2. **AzCore static lib.** Compile the AzCore subset GridMate names (STATE §7 lists
   the include surface) into `libazcore.a`. Link pthreads. Expect `AzSocket` (UDP)
   and `std/parallel/*` (threads) to be the load-bearing pieces.
3. **GridMate static lib.** Compile GridMate against the AzCore headers into
   `libgridmate.a`.
4. **Plaintext Carrier test (the milestone).** Path B `main()`, plain
   `SocketDriver`, two Carriers on localhost, one connects to the other, exchange a
   message. Capture on the wire with Wireshark. This is a clean cleartext reference
   handshake — the thing T5 diffs the retail client against.
5. **DTLS Carrier test.** Define the secure trait, swap in `SecureSocketDriver` with
   `Certificates.cpp`, link OpenSSL (`-lssl -lcrypto`) and add
   `-Wno-deprecated-declarations`. Confirm the handshake completes and the wire
   traffic is now encrypted. The OpenSSL *version* question is settled (see
   above) — so any failure here is a GridMate-on-Linux bug, not a crypto-library
   mismatch. Do not go looking for the latter. Expect Linux-path bugs (see above).

### Definition of done

A reproducible local GridMate session; a captured plaintext handshake; the
`Carrier` packet header layout (connection id, sequence, ACK bitfield, channel,
reliability flags) read out of `Carrier.cpp`/`Carrier.h` and confirmed against the
plaintext capture; and the DTLS path either working or its Linux failure
characterised exactly.

### Falsification

The header you read from `Carrier.h` must match the bytes on the wire in the
plaintext capture. Predict the first few header bytes before capturing. If they
don't match, either the build config differs from what you read or the fork
diverged — resolve that before T5 relies on this layout.

### Non-goals

Not the retail client. Do not tune anything to match retail — this is the
*known-good*, established on its own terms. No hooking yet (that's H1, which builds
on this).

### FINDINGS to record

Fork commit under test; whether clang 22 sufficed or `/opt/llvm14` was needed (with
the errors if so); the exact `-I` and `-l` flags that produced a working build (this
is the reusable recipe); the Carrier header layout; and the state of the DTLS-on-Linux
path. Fold all into STATE §5 (environment) and §7 (transport facts).
