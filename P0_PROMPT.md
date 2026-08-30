# P0 — Auth-phase decode (TCP/443)

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
correction row 7 in §13.

Nothing is injected, patched or modified. We read a file the client produced.

---

## Step 0 — confirm the inputs exist before doing anything else

The keylog was written to a path set via Steam launch options, and the captures live
in the repo. Both predate this session. **Check, do not assume:**

```fish
ls -la /home/kaatlev/nwly-keylog.txt
cd ~/Documents/NWLY; and ls -la *.pcap
```

- **Keylog present and the pcap contains TCP/443 to AWS** → proceed to Step 1.
- **Keylog missing or empty** → re-capture. One launch, `SSLKEYLOGFILE` set via the
  Steam launch option (`SSLKEYLOGFILE=/home/kaatlev/nwly-keylog.txt %command%`),
  **tcpdump started before the client**, reach character-select/server-list, then
  reach the world. You need the whole login sequence, not a mid-session slice.
- **Pcap has no TCP/443, or the capture began after login** → re-capture likewise.
  A capture that starts after auth has already happened contains nothing this chunk
  needs.

**Record which of these three you were in.** If a re-capture was needed, that is a
new test-log row and a new build/keylog pairing — the keys only decrypt the sessions
they were captured with, so a keylog from one launch will not open a pcap from
another.

---

## Scope

Work only the TCP/443 flows to AWS: `44.220.67.249`, `13.217.79.62`,
`18.238.35.71` (§12A). **Cloudflare 443 — `104.18.124.108`, `162.159.*` — is CDN/API
and not the game backend**; exclude it or you will spend the chunk reading asset
delivery.

Expect **TLS 1.2, cipher `0xC02F`** on these flows (§12A). Application data is
probably HTTP/2 and probably compressed; tell tshark so, rather than concluding the
bodies are binary.

Suggested starting point — adapt rather than copy blindly:

```fish
set PCAP (ls -t ~/Documents/NWLY/*.pcap | head -1)
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
4. The auth host set is **stable across sessions**; the world server address is
   **not** (§12A already warns the port is ephemeral).

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
- No client modification of any kind.

---

## FINDINGS to record

Fold into a new `## 16` section in `STATE.md` (§15 is the register; check the
freshness header's section count and update it). Include:

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
