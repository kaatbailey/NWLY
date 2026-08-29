# T3 — Transport recon (retail, capture only, no hooks)

> You have been given `CHARTER.md` and `STATE.md`. Work **only** this chunk. If you
> find something that belongs to another chunk, record it in FINDINGS under
> "Noticed, out of scope" and do not act on it.
>
> Do not rewrite `CHARTER.md`. Do not delete anything from `STATE.md`.
>
> Charter §3 rules out anti-cheat work absolutely. If a line of inquiry only pays
> off against an integrity or attestation system, stop and record it as off-charter
> in FINDINGS — do not pursue it.
>
> **The owner runs every command.** Give exact commands with real paths. Note the
> exact client build under test in every capture.

---

## Environment (resolved — do not re-derive)

| What | Value |
| ---- | ----- |
| Client build under test | New World: Aeternum, appid 1063730, **buildid 22469132**, `LastUpdated` 1787844457 (2026-08-27) |
| Install path | `/home/kaatlev/.local/share/Steam/steamapps/common/New World` |
| Depots pinned | 1063731 → `5202358862838894766`; 1063732 → `5672526915328587099`. Manifests + `Bin64/` copied to `~/Documents/nwly-pin/22469132/` |
| Runs under | **Proton** (`steamapps/compatdata/1063730` exists) — client is a PE process under Wine on this host |
| Capture interface | **`enp2s0`**, host `192.168.1.33`, gateway `192.168.1.1` |
| Existing decoder | `decode_carrier.py` in `~/Documents/NWLY` — recognises both Carrier framing (§8) and DTLS records (§9) |
| Shell | fish |

---

## Why this chunk

T3 is the **last input T5 needs**. T1 already named the engine (GridMate) and T2 the
crypto (OpenSSL 1.1.1k, static, `SSL_read`/`SSL_write`). T4 produced a known-good
reference handshake. What is missing is the retail client's own opening bytes.

It also settles a question STATE §7 flags as UNVERIFIED-for-retail: GridMate ships
**two** secure drivers — `SecureSocketDriver` (UDP/DTLS) and
`StreamSecureSocketDriver` (TCP/TLS). Which one carries the persistent world
connection decides the shape of every P-track chunk. A capture answers it in ten
minutes with no hooks.

**Scope is smaller than the original CHUNKS T3 text.** That text predates STATE §9
and assumes recon from zero — entropy profiling, "is there crypto at all." You now
own a decoder that recognises DTLS records. So the primary analysis is *point the
existing instrument at retail traffic*; the entropy work is the fallback for if it
does not parse.

---

## Predictions — write these down before capturing (CHARTER §4)

| # | Prediction | If falsified |
| - | ---------- | ------------ |
| **P1** | Game stream is **UDP**; auth and server-list are a separate TCP/443 HTTPS phase | If the world connection is TCP, retail uses `StreamSecureSocketDriver`, not `SecureSocketDriver`. Re-scope T5 to the stream driver's framing. |
| **P2** | UDP payloads parse as **DTLS 1.2 records**; `decode_carrier.py` recognises them with no modification | If they do not parse, the crypto layer is not stock DTLS despite T2's OpenSSL hit. Fall back to the entropy profile in the original T3 scope. |
| **P3** | Opening exchange is **ClientHello (`fe fd`) → HelloVerifyRequest (`fe ff`) → ClientHello with cookie echoed** | Absence of the cookie exchange means Amazon disabled `SSL_CTX_set_cookie_generate_cb`. Note it; it does not break T5. |
| **P4** | The retail ClientHello advertises **exactly one cipher suite, `0xC030`** (`ECDHE-RSA-AES256-GCM-SHA384`) | GridMate hardcodes this at `SecureSocketDriver.cpp:1494`. A normal multi-suite list means the `SSL_CTX` setup was replaced, and T5's "structural match" verdict must be qualified even though T1 said GridMate. |

**P4 is the load-bearing one.** A single-suite ClientHello matching the reference is
close to conclusive for a stock-ish GridMate transport, and it is readable at epoch 0
without a single hook. Do not soften it into "the framing looks similar."

**The HelloVerifyRequest at DTLS 1.0 is correct** (RFC 6347 §4.2.1, STATE §9). Not a
downgrade, not a bug. Do not spend time on it.

---

## Steps

### 1. Tooling

```fish
pacman -Qi wireshark-cli >/dev/null 2>&1; and echo HAVE-TSHARK; or echo NEED-TSHARK
which tcpdump
```

If needed: `sudo pacman -S wireshark-cli`. `tcpdump` is already present (it is what
`capture_carrier.sh` uses). Capture runs under `sudo tcpdump`, so no `wireshark`
group membership is required.

### 2. Start the capture BEFORE the client connects

This is the single procedural detail that decides whether the chunk succeeds. Test
#21 only caught the cookie exchange because the capture predated the session. A
mid-session capture is all epoch ≥ 1 ciphertext and is worthless for T5.

```fish
mkdir -p ~/Documents/nwly-captures
set -g PCAP ~/Documents/nwly-captures/t3_retail_b22469132_(date +%Y%m%d-%H%M%S).pcap
sudo tcpdump -i enp2s0 -s 0 -n -w $PCAP
```

Leave it running. Do not filter at capture time — filter offline, where a mistake
costs nothing.

### 3. Run a scripted session, noting wall-clock times

Charter §4, one thing at a time. Write the times down; they are what makes the
size/timing profile readable.

1. Launch the client. Note the time.
2. Reach the character-select / server-list screen. Note the time.
3. Enter the world. Note the time.
4. **Stand completely still for 60 seconds.** Hands off the keyboard and mouse. This
   isolates the heartbeat / idle replica traffic.
5. **Walk in a straight line for 30 seconds**, constant direction, no camera movement.
6. Stand still again for 30 seconds.
7. Log out. Stop the capture with Ctrl-C.

While in-world, in a second terminal, attribute the sockets directly rather than
inferring them from the capture:

```fish
ss -tunp | rg -i 'wine|NewWorld'
```

### 4. Identify the conversations

```fish
tshark -r $PCAP -q -z conv,udp | head -40
tshark -r $PCAP -q -z conv,tcp | head -40
```

The game stream is the UDP conversation with sustained bidirectional traffic across
the whole in-world window — not the largest by bytes (that may be a Steam or CDN
transfer). Cross-check against the `ss` output from step 3.

### 5. Test P2 and P3

```fish
tshark -r $PCAP -Y 'dtls' -T fields \
  -e ip.dst -e udp.dstport -e dtls.record.content_type -e dtls.record.version \
  | sort | uniq -c | sort -rn | head -20
```

Expect content types 22 (Handshake) at version `0xfefd`/`0xfeff` early, then 23
(ApplicationData) for the bulk.

### 6. Test P4 — the one that matters

```fish
tshark -r $PCAP -Y 'dtls.handshake.type == 1' -T fields \
  -e udp.dstport -e dtls.handshake.ciphersuite
```

Count the suites on one ClientHello. One suite, value `0xc030` → P4 confirmed.

Then the cookie exchange:

```fish
tshark -r $PCAP -Y 'dtls.handshake.type == 1 or dtls.handshake.type == 3' \
  -T fields -e frame.number -e dtls.handshake.type -e dtls.record.version \
  -e dtls.handshake.cookie
```

Type 3 is HelloVerifyRequest. Expect its version to be `0xfeff` while both
ClientHellos are `0xfefd`, and expect the cookie to be echoed verbatim.

### 7. Run the existing decoder against retail

This is the point of the chunk — the instrument built in T4 pointed at retail for
the first time.

```fish
cd ~/Documents/NWLY
python decode_carrier.py $PCAP
```

**Expected first failure, so predict it before running:** the reference captures were
loopback and retail is Ethernet on `enp2s0`. Both are `DLT_EN10MB` on Linux, so the
link layer should match — but if the decoder hardcodes an offset or filters on
`127.0.0.1`, that is where it breaks. That is a decoder bug, not a protocol finding.
Fix and re-run; do not record it as evidence about retail.

### 8. Size and timing profile

```fish
tshark -r $PCAP -Y "udp.port==<GAMEPORT>" -T fields \
  -e frame.time_relative -e udp.length -e ip.src \
  > ~/Documents/nwly-captures/t3_sizes.tsv
```

Report packet rate and size distribution separately for the stand-still window and
the walking window. A ~30–60 Hz stream of small packets is the GridMate replica-delta
shape. The delta between the two windows is a free head start on P3, but **do not
decode anything** — that is P-track and it needs H3 plaintext anyway.

---

## Definition of done

- Transport named (UDP vs TCP) for the world connection, with the port(s) and the
  server endpoint recorded.
- The auth/server-list phase separated from the game stream.
- P1–P4 each marked confirmed or falsified, with the command output as evidence.
- The epoch-0 handshake extracted and saved as its own artefact — this is the exact
  thing T5 diffs against the reference:

  ```fish
  tshark -r $PCAP -Y 'dtls.record.epoch == 0' -w ~/Documents/nwly-captures/t3_handshake_epoch0.pcap
  ```
- Packet size / inter-arrival profile for the still and walking windows.
- Whether `decode_carrier.py` handled retail unmodified, and any changes it needed.

---

## Non-goals

- No hooks, no injection, no Frida. Capture only.
- No decryption attempts. Epoch ≥ 1 is ciphertext; there is nothing there without
  session keys and no amount of staring will change that (STATE §9).
- No message-body decoding — that is P-track.
- **EAC/EOS traffic will be in the capture.** Identify its endpoints so they can be
  excluded from the game-stream analysis, and stop there. Charter §3: not analysed,
  not characterised, not recorded beyond "these endpoints are not the game stream."
- Do not modify traffic.

---

## FINDINGS to record

Fold into STATE §5 (environment) and a new confirmed section for the retail
transport. Include:

- The exact build under test and the capture filename, in every claim.
- Server endpoint(s) and port(s), and whether they are stable across two sessions.
- P1–P4 results with the evidence.
- Which secure driver retail uses — `SecureSocketDriver` or
  `StreamSecureSocketDriver` — and what proves it. This promotes or demotes the
  UNVERIFIED-for-retail note in STATE §7.
- The Proton-vs-native decision for dynamic tooling, now that the client is
  confirmed to run under Proton, and what that implies for H1's Frida setup.
- Anything the decoder needed changed, so the next session does not rediscover it.
