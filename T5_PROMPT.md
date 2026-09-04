# T5 — Reference vs retail handshake diff (the milestone verdict)

> You have been given `CHARTER.md` and `STATE.md`. Work **only** this chunk. If you
> find something that belongs to another chunk, record it in FINDINGS under
> "Noticed, out of scope" and do not act on it.
>
> Do not rewrite `CHARTER.md`. Do not delete anything from `STATE.md` — append,
> and move any overturned belief to the §13 Corrections table.
>
> Charter §3 rules out anti-cheat work absolutely. If a line of inquiry only pays
> off against an integrity or attestation system, stop and record it as off-charter
> in FINDINGS — do not pursue it.
>
> **The owner runs every command.** Give exact commands with real paths. Stamp the
> build under test (buildid 22469132) and the capture filename in every claim.
>
> This chunk is **offline analysis only** — two pcaps and one source file. No
> client launch, no hooks, no decryption. Everything you need already exists.

---

## Environment (resolved — do not re-derive)

| What | Value |
| ---- | ----- |
| The charter's core question | "Is retail transport a **GridMate fork** or a **rewrite**?" This chunk answers it (CHARTER §2). |
| Retail epoch-0 handshake | `~/Documents/nwly-captures/t3_handshake_epoch0.pcap` — extracted in T3. **T5's retail input.** |
| Retail full capture (context) | `~/Documents/nwly-captures/t3_retail_b22469132_20260829-203901.pcap`. Game flow `192.168.1.33:27001 ↔ 52.223.16.88:54888` (AWS). |
| Reference DTLS handshake | `~/Documents/NWLY/build/carrier_dtls.pcap` — from `capture_carrier.sh --secure`. **`build/` is disposable (STATE test #20); if the pcap is absent, regenerate it — see Step 0.** This is **T5's reference input** (STATE §9). |
| The instrument | `~/Documents/NWLY/decode_carrier.py` — parses both Carrier framing (§8) and DTLS records (§9). Handled retail unmodified in T3. |
| Reference source of truth | `~/Documents/lumberyard/dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp`. Single cipher hardcoded at **`:1494`** (`ECDHE-RSA-AES256-GCM-SHA384`, `0xC030`). Read from fork commit `413ecaf`; built from `7d4f1ee6` (STATE §5). |
| **The confounder** | Retail OpenSSL **1.1.1k** (static); reference/local OpenSSL **3.6.4** (STATE §5, §10). **Handshake differences caused by the library version are NOT evidence of a rewrite.** Separating them is the whole method — see below. |
| Retail facts already banked (T3, §12A) | Single real suite `0xC030` + `0x00FF` (reneg SCSV, not a cipher). Cookie echoed verbatim (`eb14bc1b7aaadacffb30cd3334bc814690591056`). Server sends **HelloRequest** (early renegotiation) and **CertificateRequest** (type 13 → mutual auth). World transport is `SecureSocketDriver` / UDP-DTLS. |
| Shell | fish |
| tshark | present |

---

## Why this chunk

T5 is the chunk the reference build was built *for* (CHARTER §2). T3 already
confirmed the transport is UDP/DTLS `SecureSocketDriver` and that its ClientHello
is single-suite `0xC030` — that is most of the structural-identity signal. **T5
does not re-run T3.** It does three things T3 did not:

1. Turns the P1–P4 signals into a **documented verdict** by diffing the retail
   epoch-0 handshake against the reference epoch-0 handshake field-by-field, and
   proving each divergence is either GridMate-controlled (real) or OpenSSL-default
   (noise).
2. Resolves the **CertificateRequest / mutual-auth** question — the genuinely new
   work — by comparing retail's server flight against the reference server's. This
   feeds the server layer: a private server must satisfy whatever client-cert
   behaviour is stock vs Amazon-added.
3. Writes the verdict that **licenses the rest of the project**: if the reference
   is a valid model for retail's transport, H-track develops hooks against it
   trusting they transfer, and P-track decodes retail's epoch-≥1 plaintext using
   the §8 Carrier format the reference proved.

**When reference and retail conflict, retail is the truth** (CHARTER §2). The
reference is how we understand retail, not what we are matching.

---

## Predictions — write these down before diffing (CHARTER §4)

| # | Prediction | If falsified |
| - | ---------- | ------------ |
| **P1** | Every **GridMate-controlled** field matches between retail and reference: single suite `0xC030`, the cookie exchange and its mechanics, and the DTLS 1.2 record/handshake framing (13-byte `RecordHeader`, 12-byte `HandshakeHeader`, §7/§9). | A GridMate-controlled field differs → the `SSL_CTX` setup was replaced, not just recompiled. The "stock GridMate" verdict must be **qualified** for that aspect even though T1 said GridMate. |
| **P2** | Every **remaining** difference (extension list, order, `supported_groups`, `signature_algorithms`) is explained by **OpenSSL 1.1.1k (retail) vs 3.x (reference)** defaults — i.e. a field `SecureSocketDriver.cpp` does **not** explicitly set. | A difference lands in a field the source *does* set → it is a real GridMate-level divergence, not library noise. Catalogue it as an exception to the match. |
| **P3** *(load-bearing, new)* | Stock GridMate's `SecureSocketDriver` **server** sets `SSL_VERIFY_PEER` and sends a **CertificateRequest**, so the reference server flight matches retail's observed mutual auth (type 13). | The reference server does **not** send CertificateRequest → **Amazon added mutual auth on top of GridMate.** That is both a divergence *and* a hard requirement for the server layer (S-track must present/accept a client cert). Record where retail's client cert would have to come from. |
| **P4** | `decode_carrier.py` parses **both** epoch-0 flights through the same code path with no per-capture special-casing (beyond the known ChangeCipherSpec type-20 gap, §12A). | Different code paths are needed → the two handshakes are not the same structural object; find which field breaks the shared parse before trusting any match. |

**P3 is the one that matters and the one T3 could not answer**, because it needs a
server you control. A clean match on P1/P2/P4 plus a resolved P3 is the verdict.
Do not soften "the handshakes match structurally" into "they look similar" — say
which fields matched, which differed, and which bucket each difference is in.

---

## Steps

### 0. Confirm both inputs exist; regenerate the reference if needed

```fish
ls -l ~/Documents/nwly-captures/t3_handshake_epoch0.pcap
ls -l ~/Documents/NWLY/build/carrier_dtls.pcap
```

If the reference pcap is absent (`build/` was cleaned — it is disposable per STATE
test #20), regenerate it from the harness that already exists:

```fish
cd ~/Documents/NWLY
./capture_carrier.sh --secure        # writes build/carrier_dtls.pcap
```

Do **not** rebuild the archives unless the probe binary is also gone; the capture
script runs the existing probe. If you must rebuild, the recipe is STATE §5.

### 1. Identify the reference DTLS port

Retail's port is fixed (the epoch-0 pcap is already filtered to it). The reference
is loopback with an ephemeral port — find it:

```fish
tshark -r ~/Documents/NWLY/build/carrier_dtls.pcap -q -z conv,udp | head
set -g REFPORT <the-loopback-DTLS-port>
```

### 2. Read the source *before* dumping bytes (CHARTER §4)

Predict the diff from `SecureSocketDriver.cpp`, so each wire difference has a
pre-assigned bucket. Pull the fields GridMate explicitly sets:

```fish
set -g SSD ~/Documents/lumberyard/dev/Code/Framework/GridMate/GridMate/Carrier/SecureSocketDriver.cpp
rg -n 'SSL_CTX_set_cipher_list|SSL_set_cipher_list|:1494' $SSD      # the single suite
rg -n 'SSL_CTX_set_verify|SSL_set_verify|SSL_VERIFY_' $SSD          # P3: mutual auth?
rg -n 'SSL_CTX_set_cookie|cookie_generate|cookie_verify' $SSD       # cookie mechanics
rg -n 'set_options|SSL_OP_|min_proto|max_proto|DTLS1_VERSION' $SSD  # version pinning
rg -n 'set_tlsext|SNI|ALPN|set1_groups|set1_curves|sigalg' $SSD     # any extension it touches
```

**Write down, from this read, the list of GridMate-controlled fields.** Anything
NOT in that list is an OpenSSL default and belongs in the P2 (noise) bucket by
construction.

### 3. Dump both ClientHellos as comparable field lists

Not full `-V` (it drowns the diff in frame/IP/loopback noise). Fields only:

```fish
# retail
tshark -r ~/Documents/nwly-captures/t3_handshake_epoch0.pcap \
  -d udp.port==27001,dtls -Y 'dtls.handshake.type==1' -T fields \
  -e dtls.handshake.version -e dtls.handshake.ciphersuite \
  -e dtls.handshake.extension.type -e dtls.handshake.sig_hash_alg \
  -e dtls.handshake.extensions_supported_group

# reference
tshark -r ~/Documents/NWLY/build/carrier_dtls.pcap \
  -d udp.port==$REFPORT,dtls -Y 'dtls.handshake.type==1' -T fields \
  -e dtls.handshake.version -e dtls.handshake.ciphersuite \
  -e dtls.handshake.extension.type -e dtls.handshake.sig_hash_alg \
  -e dtls.handshake.extensions_supported_group
```

Note: take the **first** ClientHello (pre-cookie) on each side for the like-for-like
extension comparison; the cookie-echo ClientHello adds only the cookie.

### 4. Diff, and sort every divergence into a bucket

For each field that differs between the two lists, decide from Step 2's list:

- **In the GridMate-controlled list** → this is a **real divergence** (P1/P2
  falsified for that field). Record it as an exception to the match.
- **Not in the list (OpenSSL default)** → **library noise**, 1.1.1k vs 3.x.
  Record it as expected, not evidence of anything.

The cipher suite (`0xC030` + `0x00FF` SCSV) and the DTLS version (`0xfefd`) **must**
be identical — they are GridMate-controlled. Expect the *extension block* to differ
(1.1.1k vs 3.x ship different default groups/sig-algs and ordering); that is fine
**only** if `SecureSocketDriver.cpp` doesn't set those extensions.

### 5. Server-side flight — resolve P3 (the new work)

From Step 2 you already know whether the source sets `SSL_VERIFY_PEER` on the
server context. Now confirm on the wire, both sides:

```fish
# retail: is there a CertificateRequest (type 13)?
tshark -r ~/Documents/nwly-captures/t3_handshake_epoch0.pcap \
  -d udp.port==27001,dtls -Y 'dtls.handshake.type==13' \
  -T fields -e frame.number -e dtls.handshake.type

# reference: same question
tshark -r ~/Documents/NWLY/build/carrier_dtls.pcap \
  -d udp.port==$REFPORT,dtls -Y 'dtls.handshake.type==13' \
  -T fields -e frame.number -e dtls.handshake.type
```

Cross the source read with the two wire results:

- Source sets `SSL_VERIFY_PEER` **and** both captures show type 13 → **mutual auth
  is stock GridMate.** Retail's cert requirement is modelled by the reference for
  free; S-track replicates it.
- Source does **not**, or the reference shows no type 13 while retail does →
  **Amazon added mutual auth.** Divergence + server-layer requirement. Then locate
  the **client's** Certificate message (type 11, client→server, still epoch 0) in
  the retail capture — it is sent in the clear before ChangeCipherSpec and tells
  you the client presents a cert at all:

  ```fish
  tshark -r ~/Documents/nwly-captures/t3_handshake_epoch0.pcap \
    -d udp.port==27001,dtls -Y 'dtls.handshake.type==11' \
    -T fields -e frame.number -e ip.src -e dtls.handshake.certificate_length
  ```

  A non-empty client Certificate from `192.168.1.33` (the client) is the S-track
  lead: the private server will have to accept it, and *where the client gets that
  cert* is an H/S-track question (a `Certificates.cpp`-equivalent embedded in
  `NewWorld.exe`). Record it; do not chase it here.

### 6. Structural parse check — P4

```fish
python ~/Documents/NWLY/decode_carrier.py ~/Documents/nwly-captures/t3_handshake_epoch0.pcap
python ~/Documents/NWLY/decode_carrier.py ~/Documents/NWLY/build/carrier_dtls.pcap
```

Confirm both epoch-0 flights decode through the same path — same `RecordHeader`
(13B) and `HandshakeHeader` (12B) layout, same handshake-type sequence. The known
type-20 (ChangeCipherSpec) gap from §12A is expected on both; it is not a
divergence between them.

### 7. Write the verdict

State it plainly, as the artefact that unblocks the rest of the project:

> Retail transport is **structurally stock GridMate `SecureSocketDriver`** / **or**
> a fork with the following catalogued exceptions: [list]. All handshake
> differences from the reference are attributable to OpenSSL 1.1.1k vs 3.x
> **except** [list of real divergences, or "none"]. Mutual auth is **stock /
> Amazon-added**. **The reference build is / is not a valid instrument for retail's
> transport**, with these caveats: [...].

---

## Definition of done

- Field-by-field ClientHello diff, retail vs reference, with **every divergence
  bucketed** GridMate-controlled (real) or OpenSSL-default (noise), each backed by
  the `SecureSocketDriver.cpp` read.
- P1–P4 each marked confirmed or falsified, with command output as evidence.
- The **mutual-auth question resolved**: stock GridMate vs Amazon-added, proved by
  source + both wire captures. If a client Certificate (type 11) is present in
  retail, record it and its implication for S-track.
- The **verdict** written (Step 7): fork-or-rewrite, exception list, and whether
  the reference remains a valid instrument — folded into STATE as a new confirmed
  section (append after §12A) and any overturned belief added to §13.
- If the reference pcap was regenerated, note it; the diff must be against a
  reference capture that still exists.

---

## Non-goals

- **No decryption.** Only the epoch-0 handshake is in scope; it is cleartext.
  Epoch ≥ 1 is ciphertext and needs session keys that T5 does not have (STATE §9).
- **No hooks, no injection, no Frida.** That is H-track. T5 is pcap + source only.
- **No message-body decoding.** That is P-track and needs H3 plaintext first.
- **No anti-cheat.** EAC/EOS endpoints are already excluded (STATE §12A); do not
  characterise them (CHARTER §3).
- Do not rebuild the reference archives unless the probe binary is missing; the
  capture script reuses the existing build.

---

## Watch for, and record if seen — H-track recon (do not act)

T5 is offline, so the H-track surface is thin, but two items are worth recording
if the diff surfaces them:

- **A modified `SSL_CTX` in retail** (any GridMate-controlled field that diverges,
  per P1/P2). That is also where a keylog callback would or would not have been
  wired — relevant to the §12A finding that the DTLS context does **not** honour
  `SSLKEYLOGFILE`. If the diff shows the retail context is otherwise stock, it
  strengthens "the callback was simply never added to that context."
- **The client Certificate (type 11)**, if present. Its origin inside
  `NewWorld.exe` is the interception/server lead noted in Step 5 — record the
  observation, keep it separate from the transport verdict, do not build on it.

The standing principle carried forward (STATE §10, §12A): retail OpenSSL is static,
so H3 reaches `SSL_read`/`SSL_write` by **signature scan**, not symbol lookup.
Nothing in T5 changes that; T5 only decides whether the reference is a trustworthy
model for where those functions sit.

---

## FINDINGS to record

Fold into a new confirmed section after §12A. Include:

- The build under test (22469132), both capture filenames, and the reference
  commit (`7d4f1ee6`) in every claim.
- The bucketed ClientHello diff and the P1–P4 results with evidence.
- The mutual-auth verdict and, if applicable, the client-cert observation and its
  S-track implication.
- **The headline verdict**: fork or rewrite, exception list, and whether the
  reference build remains a valid instrument for retail's transport — this is the
  sentence the rest of the project is waiting on.
- Anything the reference regeneration needed, so the next session does not
  rediscover it.
