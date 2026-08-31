# P0b — Decrypt the queue response

**Read `CHARTER.md` and `STATE.md` first. This file is the chunk; those two are the
context. Do not act on a summary of either.**

Created 2026-08-30, as the remainder of P0 (STATE §16). P0 located the world-address
handoff by position but could not read it. This chunk reads it. It is the single item
on the critical path between here and S0, and it is **perishable**: the servers retire
**31 January 2027** (STATE §16.0), after which no capture is possible.

---

## The one thing this chunk does

**Read the body of the login-queue response** — the reply to
`POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni`, which in the P0 capture
was frame 2648 on `d2oeuvxi3kfsrw.cloudfront.net`, a 2,970-byte TLS ApplicationData
record arriving 68 frames before the world DTLS ClientHello.

In `p0_cold` it did **not** decrypt. `tls.debug` said `Cannot find master secret`:
the TLS connection carried two sessions, and only the first was in the keylog. The
working hypothesis (STATE §16.7, DEF-2) is that the keylog callback fires on **full
handshakes only**, so a **resumed** session's key is never written.

**So the whole chunk is: force a full handshake on that connection, capture it, read
the response.** If the response names the world server, prediction 1 (STATE §16.5) is
confirmed and S0 unblocks. If it carries only a ticket or queue token and no address,
that is the finding, and S0's design changes accordingly.

---

## Why a cold launch is the mechanism

STATE §16.4: **login is Steam-inherited.** The client presents a per-session Steam
auth ticket and exchanges it (EOS `oauth/token` → `tokenservice` JWT → STS) for game
credentials. A **cold launch** — Steam session fresh, game prefix torn down — does two
things at once:

1. mints a fresh ticket, so the entire auth chain replays **inside** the capture
   window rather than being skipped as already-done; and
2. gives the queue connection **no session to resume**, forcing the full TLS
   handshake whose key the callback actually logs.

A resumed session gives neither. **Do not attempt this chunk from a warm client.**

To get cold, in increasing order of force — try the cheapest that works:

- Quit New World to desktop, wait ~15–20 min, relaunch. TLS session tickets expire;
  this alone may clear the resumption.
- Quit New World **and** Steam so the Proton `wineserver` for the prefix exits
  (`pgrep -a wineserver` returns nothing game-related), then relaunch both.
- Log out of Steam and back in. The sledgehammer; only if the first two still yield a
  resumed handshake.

---

## Step 0 — preserve, truncate, capture

```fish
cp /home/kaatlev/nwly-keylog.txt /home/kaatlev/nwly-keylog-p0b-pre.txt; and : > /home/kaatlev/nwly-keylog.txt
```

The keylog **appends**; truncating strands nothing because the prior capture's copy is
saved (STATE §16.1). Then, capture **before** launch:

```fish
set -l TS (date +%Y%m%d-%H%M%S); sudo tcpdump -i enp2s0 -s 0 -w ~/Documents/nwly-captures/p0b_b22469132_$TS.pcap
```

`;` not a newline — `set -l` is scoped to the command line, and a newline empties
`$TS` before tcpdump runs (STATE §16.1 records this exact bite). `enp2s0`, not
`-i any` — `-i any` gives SLL framing and breaks link-layer parity (STATE §5).

Then: launch Steam, launch New World, reach **Valhalla**, load in-world, move briefly,
quit, `^C`. Capture the socket table once at character select and once in-world:

```fish
ss -tunp | grep -iE 'newworld|wine' > ~/Documents/nwly-captures/p0b_sockets.txt; cat ~/Documents/nwly-captures/p0b_sockets.txt
```

---

## Step 1 — verify the handshake is FULL before believing anything

This is the gate. A resumed handshake means the capture failed at its one job and you
re-cold-launch; nothing else in this chunk matters until it passes.

```fish
set -g PCAP (find ~/Documents/nwly-captures -name 'p0b_*.pcap' | head -1)
set -g KEY /home/kaatlev/nwly-keylog.txt
echo "pcap: $PCAP"; find $KEY -printf '%p  %s bytes\n'
```

Find the queue POST and its TLS stream:

```fish
tshark -r $PCAP -o tls.keylog_file:$KEY -Y 'http.request.uri contains "login/queue"' -T fields -e frame.number -e tls.stream -e http.request.uri
```

Take the `tls.stream` of the **world variant** (the path containing a `{WorldId}_…`,
not the empty-world control) and dump its handshake:

```fish
tshark -r $PCAP -o tls.keylog_file:$KEY -Y "tls.stream == <QS> and tls.handshake" -T fields -e frame.number -e ip.src -e tls.handshake.type
```

**Full handshake = a Certificate, handshake type 11, is present.** A resumed session
jumps ServerHello → ChangeCipherSpec with no Certificate. If type 11 is absent, the
handshake resumed — escalate the cold-launch method (see above) and re-capture. Do not
proceed to Step 2 on a resumed handshake.

Confirm the key is now present:

```fish
tshark -r $PCAP -o tls.keylog_file:$KEY -Y "tls.stream == <QS>" -T fields -e tls.handshake.random | tr -d ':' | sort -u | while read -l r; echo -n "$r "; grep -c $r $KEY; end
```

Both randoms should return ≥1. In `p0_cold` the second returned 0 — that is the bug
this chunk exists to clear.

---

## Step 2 — read the response

With a full handshake, the response decrypts. Find it and read it:

```fish
tshark -r $PCAP -o tls.keylog_file:$KEY -Y "tls.stream == <QS> and http.response" -T fields -e frame.number -e http.response.code -e http.content_type -e http.content_length
```

```fish
tshark -r $PCAP -o tls.keylog_file:$KEY -q -z follow,tls,ascii,<QS> | sed -n '/login\/queue\/v2\/[0-9a-f]\{8\}/,$p'
```

**Search the decrypted body for an address, as text and as packed binary** — the world
host this session will differ from `35.71.190.194`, so grep for the *actual* host from
this capture's DTLS ClientHello:

```fish
tshark -r $PCAP -Y 'dtls.handshake.type==1' -T fields -e frame.number -e ip.dst -e udp.dstport
```

Then grep the queue-response body for that IP and port, both ASCII and hex (the P0
search terms were `2347bec2` / `aeb7` for the old host — recompute for the new one).

---

## Predictions — record before reading (CHARTER §4)

1. **The queue response contains the world server's address**, at a frame earlier than
   the first UDP datagram to that host. This is P0's prediction 1, now testable because
   the response is readable. Load-bearing.
2. It is **JSON**, and carries the address as a literal IP + port (not a hostname —
   STATE §16.6 found no DNS resolution for the world host).
3. It also carries a **session token / ticket** the world connection needs — the thing
   §12B found no room for in the DTLS handshake (P0 prediction 3, still open).
4. `GUID2` in `{WorldId}_{GUID2}` is **echoed or explained** by the response — instance,
   shard, or channel (OPEN-2).

**If prediction 1 is falsified** — the response carries a token but no address — that is
a real finding, not a failure. It would mean the address is derived client-side or
delivered on a flow still unread, and S0 must intercept at a different layer. Say so
plainly (STATE §16.6 already sketches the proxy alternative).

---

## Definition of done

- The queue-response body read and documented: fields, and specifically **whether it
  contains the world address, in what form**, at what frame relative to the world UDP
  datagram.
- Prediction 1 confirmed or falsified with command output as evidence.
- DEF-2 resolved or refined: did the full handshake log the key? Is "callback fires on
  full handshakes only" the correct account?
- OPEN-2 (`GUID2`) advanced if the response bears on it.
- A concrete statement of what S0 now does — proxy the queue endpoint and rewrite the
  address, or something else if prediction 1 falsified.

---

## Non-goals and hard boundaries

- **No EAC, no EOSSDK.** Their endpoints (`api.epicgames.dev`, `modules-cdn.eac-prod`)
  are in the capture; exclude them, record nothing further. CHARTER §3.
- **No world-stream work.** Epoch ≥ 1 is ciphertext the keylog does not open. §13.
- **Read only. No modification.** Redirection is S0, a separate chunk.
- **Redact secrets — this is stricter here than anywhere.** The queue exchange carries
  a live Steam auth ticket, an STS session token, and an RS256 JWT (STATE §16.4). Record
  **field names, formats, where a value flows — never the value.** These are live
  credentials for a real account and the documents are in a git repo. If a decrypted
  body is pasted anywhere, strip the ticket, token, and JWT first.

---

## FINDINGS to record

Fold into STATE §16 (extend it; do not create a new section unless the material
genuinely warrants one — check the freshness header's section count either way).
Include: which cold-launch method was needed; the handshake-full confirmation; the
queue-response fields; prediction 1's verdict with evidence; DEF-2's resolution; and
what S0 does next.

**Then, before closing (CHARTER §6.4):** tick P0b's row in `CHUNKS.md`, add a DONE
banner to this prompt, strike any claim here the chunk falsified, and — if prediction 1
confirms — move **S0 from `[!]` to `[ ]`** and clear **OPEN-1** from STATE §15.
Router before ledger.
