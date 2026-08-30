# P0 — Auth-phase decode (TCP/443)

> # ✅ DONE — 2026-08-30. VERDICT: PARTIAL.
> **Findings folded into `STATE.md` §16.** Read that, not this.
>
> **What was achieved:** the auth sequence documented end to end (§16.2); the
> **selection call identified** — `POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni`
> (§16.4), with an unplanned two-variant differential from a refused US West selection;
> the world list read and shown to be **GUID-only with no address field** (§16.3);
> predictions 1–4 resolved (§16.5); S0's requirements derived (§16.6).
>
> **What was not:** **the world address was never read.** The response that must carry
> it — frame 2648, 68 frames before the world DTLS ClientHello — **does not decrypt**
> (`Cannot find master secret`; the keylog is missing that session's key). Recorded as
> **OPEN-1**, owned by a follow-on chunk **P0b**.
>
> **Also produced:** three §13 correction rows (two against §12A, one against this
> prompt), test rows #50–#54, **DEF-2**, **OPEN-1**, **OPEN-2**, **FIND-3**, and
> **§16.0 — the game is being retired 31 Jan 2027**, which puts a hard deadline on all
> capture-dependent work.
>
> Struck-through text below is what this prompt got wrong. Struck, never deleted
> (CHARTER §5).

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are the
context. Do not act on a summary of either.**

Created 2026-08-30, following the GATE-1 decision (STATE §3, §15). This is the
first chunk of the "reachable without contacting EAC" work order and it unblocks
the longest chain in the project: **P0 → S0 → S1a**, the sequence that replaces H3
for the client→server half of the protocol.

---

## Deliverable

**A document describing the auth/API phase: what the client asks, what the server
answers, and — the load-bearing part — exactly how the client learns which world
server to connect to.**

Everything else in this chunk is supporting detail. **S0 (redirection feasibility)
rests entirely on the world-address handoff**, and S0 in turn gates S1a. If you get
only one thing out of this chunk, get that.

---

## Why this is possible with no hook

STATE §12A / test #41: the client **honours `SSLKEYLOGFILE`** for its general
TLS/HTTPS context. The keylog callback is compiled into the shipped OpenSSL. The
TCP/443 auth traffic decrypts in Wireshark with keys the client itself wrote to a
file.

It does **not** decrypt the DTLS world stream — GridMate's `SecureSocketDriver`
builds its `SSL_CTX` separately and never calls `SSL_CTX_set_keylog_callback`
(§12B, confirmed in source). That gap is real, it is not this chunk's problem, and
**do not try to close it here.** A prior session overcalled exactly this and it is
the §13 correction opening *"`SSLKEYLOGFILE` is honoured, so the client's decrypted
stream is readable from a file with no hook"* (T3, 2026-08-29).
~~correction row 7 in §13~~ — **wrong pointer, corrected 2026-08-30.** That is row
**15**; row 7 is the unrelated `AllocatorInstance` correction. §13 is unnumbered and
append-only, so every insertion shifts positional references: **cite by claim text,
never by index.**

Nothing is injected, patched or modified. We read a file the client produced.

---

## Step 0 — confirm the inputs exist before doing anything else

The keylog was written to a path set via Steam launch options. ~~The captures live
in the repo.~~ **WRONG — corrected 2026-08-30 at the console.** Retail captures live
at **`~/Documents/nwly-captures/`**, deliberately *outside* the repo (§5, "Capture
output"). A glob against `~/Documents/NWLY/*.pcap` matches nothing, and fish aborts
the whole command substitution on a failed glob rather than returning empty — which
is §5's third gotcha, and the reason the check below uses `find`.

Both inputs predate this session. **Check, do not assume:**

```fish
set -g KEY /home/kaatlev/nwly-keylog.txt
find /home/kaatlev -maxdepth 1 -name 'nwly-keylog.txt' -printf '%p  %s bytes\n'
find ~/Documents/nwly-captures -name '*.pcap' -printf '%T@ %p\n' | sort -rn | cut -d' ' -f2-
set -g PCAP ~/Documents/nwly-captures/t3_retail_b22469132_20260829-203901.pcap
```

`t3_retail_b22469132_20260829-203901.pcap` is the named good capture (§5, §12A,
test #37) — the one whose tcpdump started before launch. `t3_handshake_epoch0.pcap`
is a **world-stream extract** and is not this chunk's input.

**Existence is not the test.** A non-empty keylog proves nothing about whether its
keys open *this* pcap. Run the pairing check that test #41 already used on the world
stream, pointed at TCP/443 — one line, no continuations:

```fish
for r in (tshark -r $PCAP -Y 'tcp.port==443 && tls.handshake.type==1' -T fields -e tls.handshake.random | tr -d ':' | sort -u)
    echo -n "$r  keylog hits: "; grep -c $r $KEY
end
```

Grep the **bare random**, not the `CLIENT_RANDOM ` prefix — the keylog also carries
TLS 1.3 `*_TRAFFIC_SECRET_0` lines keyed on the same field, and matching the prefix
would miss them. **`grep -c` exits 1 on a zero count** (§5 gotcha, test #22), so fish
reports a failure on the "absent" result; the number is the answer, not the exit
status.

- **Every random has ≥1 hit** → the keys open this capture. Proceed to Step 1.
  **This is the expected branch:** test #41 reports `dissect_ssl_payload decrypted`
  on the TCP/443 flows of this same pcap, so the pairing is already proven. If the
  check disagrees, something changed since 2026-08-29 — **say so before proceeding**
  (CHARTER §6.3), do not quietly re-capture.
- **Some hit, some do not** → the pcap spans launches the keylog does not cover, or
  the file was truncated. Work the sessions that decrypt; do not re-capture yet.
- **Zero hits, or no `tls.handshake.type==1` on port 443 at all** → re-capture. One
  launch, `SSLKEYLOGFILE` set via the Steam launch option
  (`SSLKEYLOGFILE=/home/kaatlev/nwly-keylog.txt %command%`), **tcpdump started
  before the client** on `enp2s0` (§5 — not `-i any`, which yields SLL framing),
  reach character-select/server-list, then reach the world. You need the whole login
  sequence, not a mid-session slice. A capture that starts after auth has already
  happened contains nothing this chunk needs.

**Record which of these three you were in.** If a re-capture was needed, that is a
new test-log row and a new build/keylog pairing.

**One correction to the pairing trap:** `SSLKEYLOGFILE` opens the file in **append**
mode, so unless it was truncated a single keylog can hold keys from several launches.
The constraint is **per-session, not per-file** — the check above tests exactly the
right thing, and "one keylog, one launch" would send you re-capturing when you did
not need to.

---

## Scope

~~Work only the TCP/443 flows to AWS: `44.220.67.249`, `13.217.79.62`,
`18.238.35.71` (§12A).~~ **WRONG — all three, and §12A is corrected in §13.** By SNI:
`44.220.67.249` is **kinesis telemetry**, `18.238.35.71` is **CloudFront CDN**, and
`13.217.79.62` is absent from the T3 capture entirely (the `13.217.79.*` range is
**`sts.us-east-1`**). **The real auth host set is §16.2** — `tokenservice`,
`prod.identity-service`, `sts.us-east-1`, `entitlementservice`, and above all
`d2oeuvxi3kfsrw.cloudfront.net`, which serves both `getlogininfo` and the queue POST.

**Cloudflare 443 — `104.18.124.108`, `162.159.*` — is CDN/API and not the game
backend**; exclude it. Confirmed, and `162.159.135.234` specifically was Discord.

Expect **TLS 1.2, cipher `0xC02F`** on these flows (§12A) — confirmed.
~~Application data is probably HTTP/2 and probably compressed; tell tshark so, rather
than concluding the bodies are binary.~~ **WRONG, and this advice actively caused
harm.** It is **HTTP/1.1** throughout (`aws-sdk-cpp/1.7.193`). The `http2.*` filters
built on this returned empty against 148 successful decrypts, which read as "no
traffic." **The correct rule is §16.8: on any empty tshark result, read
`tls.debug_file` before believing it.**

Suggested starting point — adapt rather than copy blindly:

```fish
# $PCAP is already set from Step 0. Do not re-derive it with a glob.
tshark -r $PCAP \
  -o tls.keylog_file:/home/kaatlev/nwly-keylog.txt \
  -o tls.debug_file:/tmp/p0_tlsdbg.txt \
  -Y 'tcp.port==443 and http2' \
  -T fields -e frame.number -e ip.dst -e http2.headers.method \
  -e http2.headers.path -e http2.headers.status | head -50
```

Then read `/tmp/p0_tlsdbg.txt` for `dissect_ssl_payload decrypted` to confirm the
keys are actually working before believing an empty result means "no traffic."

**Trace the sequence, in order:** login/authentication → whatever token or session
identifier comes back → server/world list → the selection call → **the response
that names the world server**. Note request paths, methods, response shapes, and
which fields carry identifiers that reappear later.

---

## Predictions — record these before you look (CHARTER §4)

1. **The world server's address arrives in a decrypted auth response**, before the
   first UDP datagram to that host. The client is told where to go.
2. That response is **JSON over HTTP/2**, containing a server list with an address
   or hostname per entry.
3. A **session token or ticket** issued during login is carried into the world
   connection somehow — and the DTLS handshake (§12B) has no obvious place for it,
   which means it is either in the first epoch-1 Carrier message or in a field we
   have not looked at.
4. The auth host set is **stable across sessions**. Whether the **world server
   address** is stable is genuinely open, and ~~§12A already warns the port is
   ephemeral~~ **misreads §12A — corrected 2026-08-30.** §12A's ephemeral-port
   warning is about the **local** port (`27001`, "do not hardcode"); about the
   *server* it says the opposite — `52.223.16.88:54888`, **"Same IP:port on both of
   the day's captures."** So the only two datapoints in hand point at *stability*.
   State which you expect and why before looking; predicting instability here is
   predicting against the evidence, and §13 is largely rows of exactly that.

**Prediction 1 is the load-bearing one and it has a sharp test:** the auth response
naming the world host must appear at an *earlier frame number* than the first UDP
datagram to that host. Check the ordering, do not just check that the string is
present somewhere.

**If prediction 1 is falsified** — the address never appears in decrypted auth
traffic — that is a significant finding, not a failure. It would mean the client
resolves a hostname by DNS, or is told by a flow we have not identified, or derives
it some other way. **Say so plainly and follow the DNS traffic**, because S0's whole
design depends on which it is.

---

## Definition of done

- The auth flow documented as an ordered sequence of requests and responses, with
  hosts, paths and methods.
- **The world-address handoff identified specifically:** which response, which
  field, what form the address takes (literal IP, hostname, region identifier), and
  its frame number relative to the first world UDP datagram.
- Predictions 1–4 each confirmed or falsified with command output as evidence.
- A statement of what S0 will need to do to redirect the client, derived from the
  above rather than assumed.
- Whether a session token is visible, and where it goes.

---

## Non-goals and hard boundaries

- **No EAC, no EOSSDK.** Their traffic is in the capture. Identify their endpoints
  only far enough to exclude them; record nothing further. CHARTER §3.
- **No world-stream work.** Epoch ≥ 1 is ciphertext and the keylog does not open it.
  Do not retry that; §13 row 7.
- **Do not modify traffic.** Read only. S0 is where redirection gets tested, and it
  is a separate chunk for a reason.
- **Do not record credentials, tokens, or cookie values verbatim in `STATE.md`.**
  Record *structure* — field names, formats, lengths, where a value flows — never
  the secret itself. These are live credentials for your own account and the
  documents are in a git repo. Note the shape, redact the value.
  **This is a change of practice, not a reminder.** §12A pastes a DTLS cookie
  (`eb14bc1b…`) and a client random verbatim. Those are non-secret and need no
  correction — but a session copying that house style will reach for hex without
  thinking, and the auth phase carries values where that is not free.
- No client modification of any kind.

---

## FINDINGS to record

Fold into a new `## 16` section in `STATE.md` (§15 is the register; check the
freshness header's section count and update it). Adding `## 16` takes the count
**18 → 19**; update the header field **and** the `# expect` comment together — they
disagreed with each other before this chunk, which is precisely the failure §6.2
exists to catch. Include:

- Which Step 0 branch you were in, and if re-captured: new pcap filename, keylog
  path, build id, and the fact that keylog and pcap must be from the same launch.
- The ordered auth sequence, with hosts and paths.
- **The world-address handoff**, in enough detail that S0 can be written from it
  without re-reading the capture.
- Predictions 1–4 with evidence.
- Anything that bears on S1a — particularly whether the client sends anything at
  connect time that our DTLS server would have to recognise or echo.

**Then, before closing the session (CHARTER §6.4):** tick P0's row in `CHUNKS.md`,
add a DONE banner to this prompt, strike through any claim in it this chunk
falsified, and move FIND-1 out of §15's register. Router before ledger.
