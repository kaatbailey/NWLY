# S0a — Does the client validate the queue token?

> ## ✅ DONE 2026-08-31 — VERDICT: **NO**, confirmed by direct trace.
> The client does **not** verify `Token.Signature` or check `Token.HostHash` before
> dialling `Token.RepAddress`. It stores both like any other string and never inspects
> them. **S0 is the small branch:** rewrite the one `RepAddress` string; no re-signing,
> no key, no residual. Findings in **STATE §16.15**; OPEN-3 + OPEN-3R closed in §15;
> tests #60–#62. **Prediction 1 confirmed; predictions below annotated.**
>
> **How it was actually settled (differs from Steps 1–2 as written — see strikes):**
> the field names are **not** literal JSON keys with a single deserialiser cluster
> (Step 1's premise — falsified, STATE §13). The queue body is parsed as a raw
> `Aws::JsonView`: there is no typed Result/Token model, only `Request` classes. The
> deserialiser was found by xref of the *response-unique* keys `AllowQueueTransfer` /
> `JwtClaims`, not by clustering `RepAddress`/`Signature`/`HostHash`. Two functions:
> `FUN_1474e4f20` (top-level) → `FUN_1474e5990` (the `Token`). In the Token parser,
> `Signature`(+0x64), `HostHash`(+0x24) and `RepAddress`(+0x5a) are each pulled by the
> **same** stock GetString helper (`FUN_1474654e0`), stored, and never read again — no
> verify, structurally impossible in SDK codegen. No Windows verify API is imported;
> the static-OpenSSL escape hatch was excluded by *reading the parser*, not by import
> absence. **No execution, no hooking, no EAC — CHARTER §3 held throughout.**

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are the
context. Do not act on a summary of either.**

Created 2026-08-30, out of P0b (STATE §16.12–§16.13, OPEN-3). P0b read the login-queue
response and found the world address in it as a single field, `Token.RepAddress =
"ip:port"`. The `Token` object is also **signed** — `Token.Signature`, 256 bytes,
RSA-2048 — and carries a second opaque 32-byte value, `Token.HostHash`. **This chunk
decides whether that signature matters to S0.**

It is **static, needs no login, no running client, no Proton, and has no deadline.**
It is placed first anyway because it is the cheapest thing on the board that changes a
downstream decision, and because it leaves behind the analysed Ghidra project **H2**
needs next.

---

## The one thing this chunk does

**Determine, from the retail binary, whether `NewWorld.exe` verifies
`Token.Signature` (or checks `Token.HostHash`) before it dials `Token.RepAddress`.**

The answer is a single bit with two consequences:

- **NO (expected).** S0 rewrites one string — `Token.RepAddress` in the queue response
  — and is otherwise a transparent TLS-terminating proxy for
  `d2oeuvxi3kfsrw.cloudfront.net`. The signature is checked by the *world server*, and
  under S0/S1a the world server is us, so a signature we don't re-sign is never seen by
  code that would reject it. OPEN-3 closes and S0 is a small chunk.
- **YES.** Rewriting `RepAddress` invalidates the signature and the client refuses to
  connect. S0 cannot be a naive field-rewrite; it needs the signing key (we won't get
  it) or a different interception layer entirely. OPEN-3 closes the other way and S0's
  scope grows sharply. **Better to know this now than to discover it when a proxy
  silently fails to redirect.**

Either result is a finding. This chunk is done when the bit is set with evidence.

---

## Why this is answerable statically

>
> **✗ FALSIFIED (STATE §13).** The field names are **not** literal keys the deserialiser
> clusters on. `LoginQueueResponse` has zero matches; `RepAddress` appears only in a log
> format string; `HostHash`/`TicketId` only as trailing-space label text; `Signature`
> only in an AWS SigV4/error neighbourhood. The parse is a raw `JsonView` `GetString(key)`
> sequence; the keys are call arguments, found via the response-unique `AllowQueueTransfer`
> / `JwtClaims`. The reasoning below (what a verify would look like) still held; only the
> *anchor* changed.

~~The queue response is JSON the client parses (§16.10). Three field names are the
entry points, and they are almost certainly present as **literal strings in the
binary** — the JSON deserialiser keys on them:~~

- `RepAddress` — the field the client reads to get its destination.
- `Signature` — if the client verifies, the code that reads this feeds an RSA verify.
- `HostHash` — if the client checks host integrity, this is where.

If `Signature` and `HostHash` appear **only** as string constants with no reference
into any crypto routine — no `RSA_verify`, no `EVP_DigestVerify`, no BCrypt/CNG
signature call, no SHA-256 over the surrounding buffer — that is strong evidence the
client does **not** validate and treats the whole `Token` as an opaque blob it
forwards to the world server. If instead `Signature`'s read site flows into a verify,
the client validates and S0's shape changes.

**This is a data-flow question from three string constants to a crypto call or its
absence.** It is exactly the kind of thing static analysis answers well and capture
cannot answer at all.

---

## Step 0 — confirm the instrument exists

```fish
set -g NW /path/to/retail/NewWorld.exe   # the version-locked b22469132 binary, STATE §5
find (dirname $NW) -maxdepth 1 -name 'NewWorld.exe' -printf '%p  %s bytes\n'
sha256sum $NW
```

Check the SHA-256 against `pins/22469132/Bin64.sha256` **[✗ was not committed when S0a ran — STATE §13; used the local `~/Documents/nwly-pin/22469132/Bin64.sha256` instead. Matched: `8654f01d…e0fdc8e`, `NewWorld.exe: OK`.]** (STATE §5) — **this must be the
same build P0b captured**, or the string offsets describe a different binary. If it
does not match, stop and say so (CHARTER §6.3); do not analyse a build the findings
won't apply to.

The crypto provider matters for what you're grepping for. STATE §10 established the
client statically links its TLS. **Confirm which library** before hunting verify
routines — the auth-phase TLS is OpenSSL (`aws-sdk-cpp`, §16.2), so `RSA_verify` /
`EVP_DigestVerify` are the first candidates, but the token check (if any) could equally
be CNG (`BCryptVerifySignature`) or a bundled library. Record which providers are
present as imports or statically-linked strings before following xrefs.

---

## Step 1 — find the three field-name strings and their xrefs

In Ghidra (the RTTI analyzer should already have run — STATE §10, H2 notes):

1. Defined Strings → filter for `RepAddress`, `Signature`, `HostHash`, and while
   you're there `LoginQueueResponse`, `RepAddress`, `TicketId`. Note their addresses.
2. Xref each. The JSON parse site will reference several of them close together — that
   cluster is the `LoginQueueResponse` deserialiser, and it is the anchor for
   everything below.
3. **Predict before following (CHARTER §4):** name what you expect the deserialiser to
   do with each field. `RepAddress` → stored, later handed to a socket connect.
   `Signature` → either stored-and-forwarded (no validation) or fed to a verify
   (validation). State which you expect and why before you trace it.

---

## Step 2 — the load-bearing trace

From the `Signature` read site, follow the value. Exactly one of these is true:

- **It is stored into a struct/object field and never reaches a crypto routine.** →
  Client does not validate. The `Token` is opaque cargo. This is the expected result;
  §16.13 predicts it because the world server is the natural verifier.
- **It reaches an RSA-verify / signature-verify call** (`RSA_verify`,
  `EVP_DigestVerify*`, `BCryptVerifySignature`, or a bundled equivalent). → Client
  validates. Note what the verify covers — which bytes are hashed, and where the
  **public key** comes from (embedded in the binary? delivered in a prior response?).
  A client-embedded public key is itself an S0-relevant finding: it bounds what a
  proxy could forge.

Do the same, more briefly, for `HostHash`: does its read site feed a comparison
against a locally-computed SHA-256, or is it stored and forwarded? §16.12 could not
find its preimage from the outside; the binary may name it.

**Falsification (CHARTER §4).** If the trace from `Signature` dead-ends in a way that
resembles neither "stored" nor "verified" — lost in a thunk, optimised into something
unrecognisable, or the xref cluster isn't actually the queue deserialiser — do **not**
guess the bit. Say the trace was inconclusive and what would settle it (e.g. a dynamic
check on the reference path, which would escalate scope). A wrong "NO" here sends S0
down a design that silently fails.

---

## Predictions — record before tracing (CHARTER §4)

1. **The client does not validate `Token.Signature`.** `RepAddress`, `Signature` and
   `HostHash` appear as JSON keys; `RepAddress` flows to a connect, `Signature` and
   `HostHash` are stored and forwarded, and no crypto routine consumes them on this
   path. Rationale: the world server is the verifier (§16.13), and a client that both
   received and checked the signature would be duplicating the server's job for no
   security benefit — the client is the party being authorised, not the authoriser.
   **Load-bearing.**
2. `RepAddress`'s consumer is a socket connect / GridMate `SecureSocketDriver` address
   setup — the same code path T5/§12B characterised — confirming the field is the
   literal destination and not an index into something else.
3. If any validation exists, it is `HostHash` (a cheap local hash compare) rather than
   `Signature` (a full RSA verify the client has no reason to perform). Weak
   prediction; stated so it's on the record.

**If prediction 1 is falsified** — the client does verify — that is the more important
result, not a failure. It reshapes S0 and must be stated plainly with the verify call
site and what it covers as evidence.

---

## Definition of done

- The three field strings located, with the deserialiser xref cluster identified as a
  signature (CHARTER §4 — a scannable pattern, **not** a bare offset that a patch
  invalidates).
- The `Signature` data-flow traced to either "stored/forwarded" or "verified", with
  the call site as evidence for whichever.
- `HostHash` likewise, at least to the same store-vs-compare distinction.
- **OPEN-3 answered**: does the client validate before dialling? One bit, with the
  trace behind it.
- A one-paragraph statement of what S0 now is, in each branch, so S0 can be scoped
  from this without re-opening Ghidra.

---

## Non-goals and hard boundaries

- **Static only. No execution, no hooking, no injection.** CHARTER §3. This chunk
  reads a binary we already have; it does not run it. If the trace turns out to need
  dynamic confirmation, that is a *finding* (an escalation S0 would own), not something
  to do here.
- **No anti-cheat, no EAC.** If any trace wanders into `EasyAntiCheat/` or an
  attestation/integrity routine, stop following it — that is off-charter permanently
  (CHARTER §3) and is not what `Token` validation means here.
- **Signatures, not offsets** (CHARTER §4). Every located address is recorded as a
  scannable byte/RTTI pattern so it survives the next client patch. A raw offset is a
  finding with a built-in expiry.
- **No world-stream work, no capture.** This chunk touches no pcap. It is pure static
  analysis.

---

## FINDINGS to record

Fold into STATE §16 (extend it; check the freshness header's section count either
way — adding a `## 17` would take it 19 → 20, but this material is almost certainly a
§16.15, not a new section). Include:

- Which crypto providers the binary links, and which the token path uses (if any).
- The deserialiser location as a signature, and the three field xrefs.
- The `Signature` and `HostHash` traces, with call sites.
- **OPEN-3's answer, with evidence**, and the resulting S0 scope in both branches.
- Anything bearing on H2 — this chunk warms the same Ghidra project H2 walks forward
  from `recvfrom`, so note the RTTI state and any dispatch-adjacent landmarks passed on
  the way.

**Then, before closing (CHARTER §6.4):** tick S0a's row in `CHUNKS.md`, add a DONE
banner here, strike any falsified claim, and **clear OPEN-3 from STATE §15** with its
resolution. If prediction 1 confirmed, note in S0's row that its scope is the small
one. Router before ledger.
