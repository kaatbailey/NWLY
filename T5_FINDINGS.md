# FINDINGS — T5 — 2026-08-29

Fold into `STATE.md` as **§12B** (append after §12A). Corrections go to §13, test
rows to §14. Nothing in this block deletes or edits an existing finding.

**Build under test:** New World: Aeternum, appid 1063730, **buildid 22469132**,
`LastUpdated 1787844457`.
**Retail input:** `~/Documents/nwly-captures/t3_handshake_epoch0.pcap` (extracted
in T3 from `t3_retail_b22469132_20260829-203901.pcap`).
**Reference input:** `~/Documents/NWLY/build/carrier_dtls.pcap`, built and captured
from fork commit **`7d4f1ee6`**, OpenSSL 3.6.4, clang 22. Not regenerated — the
existing capture contained epoch 0 (16 type-22 records) and was used as-is.
**Method:** offline only. Two pcaps and `SecureSocketDriver.cpp`. No client launch,
no hooks, no injection, no decryption of epoch ≥ 1. CHARTER §3 satisfied.

---

## 12B. The verdict — retail transport is stock GridMate `SecureSocketDriver`

> Retail transport is **structurally stock GridMate `SecureSocketDriver`**, with
> **zero catalogued exceptions**. Every handshake difference between retail
> (buildid 22469132) and the reference (`7d4f1ee6`) is attributable to **OpenSSL
> 1.1.1k vs 3.6.4** defaults in fields `SecureSocketDriver.cpp` does not set.
> **Mutual auth is stock GridMate, not Amazon-added.** **The reference build is a
> valid instrument for retail's transport**, within the caveats at the end of this
> section.

This is the sentence the rest of the project was waiting on. H-track may develop
hooks against the reference trusting they transfer. P-track may decode retail's
epoch-≥1 plaintext using the §8 Carrier format the reference proved.

### The GridMate-controlled field list (established from source before diffing)

Read from `~/Documents/lumberyard/dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp`.
Anything **not** on this list is an OpenSSL default and is P2 noise by construction,
decided before the bytes were looked at (CHARTER §4).

| Field | Source | Retail | Reference | Match |
| ----- | ------ | ------ | --------- | ----- |
| Cipher suite | `:1494` `SSL_CTX_set_cipher_list("ECDHE-RSA-AES256-GCM-SHA384")` | `0xC030`, one real suite | `0xC030`, one real suite | **YES** |
| Protocol version | `:1472` `SSL_CTX_new(DTLSv1_2_method())` — pinned, not `DTLS_method()` | `0xfefd` | `0xfefd` | **YES** |
| MTU option | `:1479` `SSL_OP_NO_QUERY_MTU` (the only option set) | n/a on wire | n/a on wire | — |
| Peer verification | `:1522`–`:1553` | CertReq (13) from server | CertReq (13) from server | **YES** |
| Cookie mechanism | `:1699` `GenerateCookie` / `:1737` `VerifyCookie` — GridMate's own | 20 bytes, echoed verbatim | 20 bytes, echoed verbatim | **YES** |
| Hand-packed record version | `:308`, `:312`, `:343` `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) | `fe ff` on HVR + HelloRequest | `fe ff` on HVR + HelloRequest | **YES** |
| HelloRequest handoff | `:337`–`:349`, `:792`, `:1200`, `:1876` | present, 25 bytes | present, 25 bytes | **BYTE-IDENTICAL** |

**Fields the source never touches** — confirmed absent from `SecureSocketDriver.cpp`
by targeted grep: `set1_groups`, `set1_curves`, sigalgs, SNI, ALPN, and any
`SSL_CTX_set1_*`. `SSL_CTX_set_ecdh_auto` at `:1500` is a no-op macro on OpenSSL
1.1.0+ (§7) and sets nothing. Therefore `supported_groups`, `signature_algorithms`,
`ec_point_formats`, session ticket, EMS, and extension ordering are **all** library
defaults.

### P1 — CONFIRMED

Every GridMate-controlled field matches. Extension **type list is
character-identical** on both sides: `11,10,35,22,23,13`.

### P2 — CONFIRMED. Four divergences, all library noise, none in a field the source sets

| # | Difference | Retail (1.1.1k) | Reference (3.6.4) | Bucket |
| - | ---------- | --------------- | ----------------- | ------ |
| 1 | RFC 5746 renegotiation signalling | `0x00FF` SCSV in cipher list; **no** ext 65281 | ext 65281 `ff 01 00 01 00`; **no** SCSV | Noise. RFC 5746 §3.4 permits either encoding and forbids both. Perfectly anticorrelated across the two captures. `SSL_CTX_set_cipher_list` cannot add `0x00FF` — OpenSSL appends it. |
| 2 | `signature_algorithms` | 23 entries, incl. SHA-1 (`0x0201`, `0x0202`, `0x0203`) | 20 entries, SHA-1 absent | Noise. 3.x dropped SHA-1 sigalgs from defaults. Same order otherwise. |
| 3 | `supported_groups` | `…,0x0019,0x0018` | `…,0x0018,0x0019` | Noise. Same five curves, last two transposed (secp521r1/secp384r1). |
| 4 | `ec_point_formats` | `03 00 01 02` — three formats | `01 00` — uncompressed only | Noise. Known 1.1.1k-vs-3.x default change. |

These four fully account for the ClientHello length difference (retail 146, reference
141). No residual.

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
intent** (the comment above it says the default authenticates only the server):

| `m_desc.m_authenticateClient` | mode | Server behaviour |
| --- | --- | --- |
| false (default) | `0x01` | **Sends CertificateRequest**, does not require a cert back |
| true | `0x02` | Sends nothing — verification off |

Note there is **one shared `SSL_CTX`** built for both roles; there is no separate
client/server context setup. Role separation is in the HSM, not the context.

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
**no** certificate. There is no embedded client cert in `NewWorld.exe`, so
"where does the client get its cert" is not an open question — it doesn't have one,
and there is no `Certificates.cpp`-equivalent to locate. A private server must send
a CertificateRequest and **accept an empty response**. No client PKI, no client-cert
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
sequence. The §12A type-20 (ChangeCipherSpec) gap did not appear here because the
extracted epoch-0 file stops before CCS; it remains an open cosmetic gap in the
decoder, unchanged by T5.

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
That follows directly from the measured cert sizes (958 vs 1380) hitting the PMTU
at different points. Content difference, not protocol difference.

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

---

## The HelloRequest handoff — mechanism, and a hard S-track requirement

**This corrects §12A's "early renegotiation" reading — see §13.** The third
ClientHello is **not** renegotiation. It is stock GridMate's cookie handoff, and
the reference performs it identically without Amazon touching anything.

`message_seq` is what proves it: the cookie-echo ClientHello is **seq 1**, then
HelloRequest arrives, then the next ClientHello **resets to seq 0** carrying **no
cookie**. A renegotiation restarts the flight *after* a completed handshake; this
restarts it *before* one ever began.

The mechanism, from source:

- GridMate runs the cookie exchange **in its own raw-recv state machine**
  (`:1838` generate, `:1869` verify) with a hand-built HelloVerifyRequest. **OpenSSL
  never sees those datagrams.**
- Once the cookie verifies, the server creates a Connection initialized directly
  into `CS_SEND_HELLO_REQUEST` (`:1876`).
- That state packs and sends the HelloRequest (`:792`), resending on exponential
  backoff capped at 1000 ms (`:821`–`:837`).
- The HelloRequest makes the client's OpenSSL start a **fresh** handshake at
  `message_seq 0`, which the server's `SSL*` then consumes.
- GridMate also **detects** HelloRequest on the wire itself (`IsHelloRequestHandshake`,
  `:396`–`:401`; used at `:1218`, `:1230`) rather than passing it through.
- Line `:494` states the intent in a comment: send back HelloRequest to restart the
  hello sequence.

So the hello that satisfies GridMate's cookie check and the hello OpenSSL actually
handshakes on are **two different messages**, and the real handshake carries **no
cookie at all**.

**Hard S-track requirement.** A private server must:

1. Run the cookie exchange **itself, at the datagram layer** — GridMate's own
   `GenerateCookie`/`VerifyCookie`, 20-byte output (HMAC-SHA1; this is why
   `<openssl/hmac.h>` is included in a file with otherwise no use for it). Enabling
   OpenSSL's cookie callbacks is **not** equivalent and will not interoperate.
2. Send a **HelloRequest** after the cookie verifies, with resend/backoff.

Skip step 2 and the client sits at `message_seq 1` waiting for a ServerHello that
never arrives. **Neither behaviour is derivable from RFC 6347** — this is GridMate's
own sequencing, now confirmed identical in retail.

---

## Caveats on "the reference is a valid instrument"

- **Epoch 0 only.** The match is proven for the cleartext handshake. Epoch ≥ 1
  Carrier framing inside DTLS remains proven on the reference and **inferred** for
  retail. H3 plaintext is what promotes it.
- **Content differs, structure does not.** Certificates (958 vs 1380 bytes), cookie
  values, and randoms are per-deployment and per-connection. Do not treat any
  observed cookie or cert as constant.
- **Fragmentation is PMTU-dependent**, not protocol-dependent. Different message
  fragments on the two sides; do not read that as divergence.
- **One shared `SSL_CTX`.** Client/server role differences come from the HSM, not
  from separate context setup — relevant when modelling the server side against the
  reference.
- **`m_authenticateClient` is untested in both directions.** Both captures exercise
  the `false` path. If a future finding requires the `true` path, note it hits the
  inverted branch documented above and will *disable* verification.

---

## Noticed, out of scope — H-track recon (recorded, NOT built on — CHARTER §3)

- **`SSL_CTX_set_ex_data(m_sslContext, kSSLContextDriverPtrArg, this)`** (`:1555`-ish,
  immediately after the verify setup) stashes the driver pointer on the context —
  an `SSL*` → driver back-reference. Potentially useful to H-track for recovering
  driver state from a hooked `SSL_read`/`SSL_write` frame. Recorded only.
- **No `SSL_CTX_set_keylog_callback` anywhere in `SecureSocketDriver.cpp`.** This
  **upgrades** §12A's interpretation: it is not that Amazon removed or failed to
  wire the callback into the DTLS context — **stock GridMate never had it**. Nothing
  was stripped. §12A's conclusion stands unchanged (H3's signature-scan hook is
  still required for the world stream); only the explanation improves.
- The retail `SSL_CTX` shows **no** GridMate-controlled divergence, which
  strengthens the §12A finding that the DTLS context simply never had a keylog
  callback added, rather than having one disabled.

---

## §13 — Corrections to add

| Old claim | Status |
| --------- | ------ |
| "`SSL_CTX_set_cookie_generate_cb` not disabled." — §12A, P3 row (T3, 2026-08-29). Assumes OpenSSL owns the DTLS cookie exchange. | **WRONG — GridMate never used OpenSSL's cookie callbacks at all.** `rg 'set_cookie_generate_cb\|set_cookie_verify_cb'` over the whole of `dev/Code/Framework/GridMate/` returns **0** hits. The cookie is generated and verified by GridMate's own `SecureSocketDriver::GenerateCookie` (`:1699`) / `VerifyCookie` (`:1737`), driven from its raw-recv state machine (`:1838`, `:1869`) with a hand-built HelloVerifyRequest, **before OpenSSL sees the datagram**. Cause of the error: read a wire behaviour that looked like OpenSSL's stateless-cookie feature and attributed it to the library without checking the source. **Consequence:** cookie length and mechanics move into the GridMate-**controlled** bucket (where they match retail exactly, 20 bytes both sides), and a private server must reimplement the derivation rather than enable a library callback. §12B. |
| "**Early renegotiation.** The server sends a HelloRequest, which triggers a *fourth* handshake message — a third ClientHello at frame 245. So the extra ClientHello is renegotiation, not a retransmit." — §12A, additional handshake observations (T3). | **WRONG about the mechanism; the observation itself was correct.** It is not renegotiation — it is stock GridMate's **cookie handoff**, and the reference build (`7d4f1ee6`) does exactly the same thing with no Amazon involvement. Proof: `message_seq` **resets to 0** on the third ClientHello (after the cookie-echo hello at seq 1), and that hello carries **no cookie**; a renegotiation would follow a completed handshake, not precede one. Mechanism is `CS_SEND_HELLO_REQUEST` (`:681`, `:792`, `:1200`, `:1876`), a dedicated server state entered after cookie verification, with exponential-backoff resend (`:821`–`:837`). Cause of the error: a server-initiated HelloRequest is renegotiation in ordinary TLS, so the standard reading was applied to a transport that uses it for something else. **Consequence:** a hard S-track requirement — the server must send a HelloRequest after verifying the cookie or the client stalls at `message_seq 1`. §12B. |
| "Retail will show three cleartext ClientHellos and the reference two, the third being the HelloRequest-triggered renegotiation; do not mix it into the diff." — raised in session (T5, 2026-08-29), as a caution when constructing the Step 3 filter. | **WRONG — the reference shows three as well, and emits its own HelloRequest.** Both captures show the identical `0, 20, 0` cookie-length pattern across three ClientHellos and a type-0 HelloRequest at the same position. The caution was harmless (pinning `frame.number` was still the right call) but the reasoning behind it was the §12A renegotiation error inherited uncritically. Cause of the error: predicted a retail-only behaviour from a retail-only observation without asking whether the reference did it too — which is the exact question the reference build exists to answer (CHARTER §2). |
| "The HelloVerifyRequest is DTLS 1.0 (`fe ff`) … RFC 6347 §4.2.1: the server is stateless at that point and has not negotiated a version." — §9. | **NOT WRONG, BUT INCOMPLETE — and the real mechanism is more useful.** The RFC permits it, but the actual cause is that GridMate **hardcodes** `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) in its hand-packed records (`:308`, `:312`, `:343`). This moves the `fe ff` version from "OpenSSL/RFC default" into the **GridMate-controlled** bucket, where it matches retail exactly. **Diagnostic value:** every `fe ff` record in a capture is a GridMate hand-pack — exactly two per handshake (HelloVerifyRequest, HelloRequest). §9's advice not to chase it stands. §12B. |

---

## §14 — Test log rows to add

| #  | Test / capture | Prediction | Result |
| -- | -------------- | ---------- | ------ |
| 42 | **T5 · Step 0** verify `build/carrier_dtls.pcap` contains epoch 0, not just that the file exists (`conv,udp` + count `dtls.record.content_type==22`). | Handshake present, or regenerate. Test #18's `--secure` capture was 30/30 epoch-1 with no handshake, so existence alone proves nothing. | **Confirmed, no regeneration needed.** 16 type-22 records. Flow `127.0.0.1:4427 ↔ 4428`; the two self-addressed rows are `'G'` wakeups (215 bytes / 5 frames = 43 = 14+20+8+1, confirming §8). Server is **4428** (heavier direction, 4840 B, sends the cert flight). |
| 43 | **T5 · Step 2** read `SecureSocketDriver.cpp` for every explicitly-set `SSL_CTX` field, to fix the GridMate-controlled list **before** diffing bytes. | A short list: cipher, version, maybe verify. Everything else library default. | **Confirmed, and richer.** Only `SSL_OP_NO_QUERY_MTU` is set via `set_options`; **no** `set1_groups`/`set1_curves`/sigalgs/SNI/ALPN anywhere; `SSL_CTX_set_ecdh_auto` is a 3.x no-op. Unanticipated: cookie is GridMate's own (see #44), and `RecordHeader::m_version` is hardcoded `DTLS1_VERSION`. Also found `SSL_CTX_set_ex_data` driver back-reference (H-track, recorded only). |
| 44 | **T5 · Step 2** `rg 'set_cookie_generate_cb\|set_cookie_verify_cb'` across all of `GridMate/`. | Present — §12A assumed OpenSSL owned the cookie exchange. | **Falsified — 0 hits tree-wide.** Cookie is GridMate's own `GenerateCookie`/`VerifyCookie`, hand-built HVR, before OpenSSL sees the datagram. Moves cookie mechanics into the GridMate-controlled bucket. §13. |
| 45 | **T5 · P3** cross the `:1522`–`:1553` verify-mode read against CertificateRequest (13) and client Certificate (11) on both wires. | Uncertain going in — `SSL_VERIFY_PEER` appears in the file, but the `:1525` branch **assigns** `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` rather than OR-ing it, which alone is `SSL_VERIFY_NONE`. Predicted type 13 on both sides if the default (`false`) path is taken. | **Confirmed, prediction held.** CertReq from the server on both (ref frame 12/port 4428; retail frame 10/52.223.16.88). **Client Certificate present but length 0 on both** (ref frame 14; retail frame 12 from 192.168.1.33). Mutual auth is stock; the client presents nothing. **S-track requirement removed:** no client PKI, no embedded cert to find in `NewWorld.exe`. |
| 46 | **T5 · P1/P2** field-by-field ClientHello diff, frames pinned, first hello each side. | GridMate-controlled fields identical; extension block differs on 1.1.1k-vs-3.x defaults. | **Confirmed both halves.** Version `0xfefd` and one real suite `0xC030` identical; extension **type list character-identical** (`11,10,35,22,23,13`). Four noise divergences, all in unset fields: RFC 5746 SCSV-vs-ext-65281 (perfectly anticorrelated, confirmed at byte level `00 04 c0 30 00 ff` vs `00 02 c0 30` + `ff 01 00 01 00`), sigalgs 23-vs-20 (SHA-1 dropped in 3.x), `supported_groups` last-two transposed, `ec_point_formats` `03 00 01 02` vs `01 00`. Fully accounts for the 146-vs-141 length difference. |
| 47 | **T5** dump the full ordered handshake sequence with `message_seq`, both sides, to classify the third ClientHello. | Retail three hellos and a HelloRequest; reference two and none — i.e. §12A's renegotiation is retail-specific. | **Falsified — both sides identical, three hellos and a HelloRequest each.** Same types, same order, same `message_seq`. Third hello **resets to seq 0 with no cookie**, so it is the GridMate cookie handoff, not renegotiation. §12A corrected (§13). The HelloRequest is **byte-identical across retail and reference**, all 25 bytes — a GridMate hand-pack, the single strongest structural-identity result in T5. Only structural difference: which oversized message fragments (retail SKE frames 8–9, ref Certificate frames 9–10), from the 958-vs-1380 cert sizes hitting PMTU. |
| 48 | **T5 · P4** run `decode_carrier.py` over both epoch-0 flights. | Both parse through the same code path, no special-casing. | **Confirmed.** Retail 16/16 DTLS, 0 Carrier, **0 undecodable**. Reference 57 DTLS + 7 wakeup, 0 Carrier, **0 undecodable**. Same 13-byte `RecordHeader` / 12-byte `HandshakeHeader`, same type sequence. The §12A type-20 CCS gap did not arise (the extracted file stops before CCS) and remains open. |
| 49 | **T5** `openssl s_client -dtls1_2 -connect 127.0.0.1:1` to confirm local 3.6.4 emits ext 65281 rather than SCSV. | Local hello shows 65281, no SCSV — pinning the RFC 5746 difference on the library. | **Inconclusive, and unnecessary.** Port 1 refused (`write:errno=111`) before any ClientHello was emitted; nothing to inspect. Not retried: the reference capture **is** the 3.6.4 datapoint, and Step 2 established GridMate never sets that field, so the bucket holds by construction. Recorded so it is not re-attempted. |

---

## What this unblocks

- **H-track opens.** The reference is a validated model for retail's transport, so
  H1/H2 tooling developed against it can be trusted to transfer. Unchanged from
  §12A: retail OpenSSL is static, so H3 reaches `SSL_read`/`SSL_write` by
  **signature scan**, and the target is a **Proton/Wine** process (GE-Proton, §5).
- **P-track's shape is fixed.** Retail's epoch-≥1 plaintext is expected to be §8
  Carrier framing, on the strength of a validated reference. Confirming that is
  H3's output, not an assumption to build on before then.
- **S-track gains two requirements and loses one.**
  - **Gained:** implement GridMate's own 20-byte cookie exchange at the datagram
    layer; send a HelloRequest after verification, with backoff.
  - **Gained:** send a CertificateRequest and accept an **empty** client
    Certificate.
  - **Lost:** no client-certificate PKI, no cert to locate inside `NewWorld.exe`.
- **CHARTER §2's core question is answered.** The reference build has done the job
  it was built for.
