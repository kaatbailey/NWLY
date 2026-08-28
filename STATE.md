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

Nothing is built yet. This is the initial state. The immediate work is T1 (engine
fingerprint), which decides whether every downstream assumption applies.

**Tooling on hand (per owner):** Ghidra, the retail New World client, the
Lumberyard fork. **Still to set up:** a reference GridMate build from the fork
(T4), Frida or an equivalent for hooking (H1), Wireshark for T3.

---

## 3. What is next, in order

1. **T1 — Engine fingerprint.** Static Ghidra pass. GridMate vs O3DE
   `AzNetworking` vs rewrite. Everything depends on this answer.
2. **T2 — Crypto-library fingerprint.** Find the plaintext boundary (`SSL_read`/
   `SSL_write` or equivalent). This is the hook target; charter §4 says hook here,
   not at the socket.
3. **T3 — Transport recon.** Wireshark, no hooks. Transport, ports, size/timing,
   entropy transition.
4. **T4 — Reference `Carrier` build.** Stand up the known-good instrument.
5. **T5 — Reference vs retail handshake diff.** The milestone that answers the
   charter's one-sentence question.

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
| Lumberyard fork (reference) | `<path; Carrier/ under dev/Code/Framework/GridMate/>` |
| Ghidra project              | `<path>`                              |
| Capture output              | `<path>`                              |

<!-- Fill gotchas here as they cost time. Prior projects found these paid for themselves repeatedly. Likely candidates for this project: fish-shell quoting, ugrep/grep aliasing, Proton vs native for the dynamic tools, whether RTTI survived in the client build. -->

---

## 6. What already exists — do not rebuild

Nothing yet. This section fills as chunks complete. Each completed chunk's
FINDINGS block folds into the relevant section here.

---

## 7+. Reserved for confirmed findings

Sections from 7 onward are added as work produces confirmed results — engine
behaviour proven in the decompiler, header layouts confirmed against the reference
build, message formats decoded from captures. Follow the append-only rule: a new
finding gets a new section; a finding that overturns an old one adds a Corrections
row (§13) and promotes/demotes the claim rather than editing history away.

---

## 13. Corrections — beliefs that turned out wrong

Acting on any of these wastes real time. Empty at project start; every session
that overturns a prior claim adds a row here rather than deleting the claim.

| Old claim | Status |
| --------- | ------ |
| *(none yet)* | |

---

## 14. Test / capture log

A numbered, append-only log of every experiment run, its prediction, and its
result — so no test is silently retried and no result is remembered wrong. Empty
at project start.

| #   | Test / capture | Prediction | Result |
| --- | -------------- | ---------- | ------ |
| *(none yet)* | | | |
