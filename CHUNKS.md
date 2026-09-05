# nwproto — Chunk index and prompts

Companion to `CHARTER.md` and `STATE.md`. This file holds the work breakdown and
the ready-to-paste prompt for each chunk.

> **Repair note — 2026-08-30. The exact failure this file's own closing section
> warns about, repeated.** T3 and T5 both completed on 2026-08-29 and both index
> rows were still sitting at `[ ]`, with T3 marked `← NEXT` and the Order section
> still reading "Next: T3 → T5" — while `STATE.md` carried both as complete (§12A,
> §12B). A session pasted this file alongside `STATE.md` would have received two
> contradictory accounts of where the project is, and the cheapest wrong move
> available was re-running a chunk that was already done. Changes: **T3 and T5
> ticked `[x]`** with pointers into STATE; **DONE banners added to both prompt
> bodies**, bodies kept verbatim; claims inside those prompts that their own chunk
> or T5 falsified marked **SUPERSEDED** inline; `T5_PROMPT.md` added to the
> standalone-prompt list; the T5-depends-on-T3 repair note marked resolved; the
> Track H note about H2 running "mostly blind" superseded (T5 landed, so H2's
> falsification check is armed); H1's signature-scan suggestion **promoted to a
> requirement**; P1's scope narrowed to what T5 did not already document; the
> Order section replaced (stale planning prose, no findings in it — same treatment
> and same rationale as `STATE.md` §1–§3 on 2026-08-29). One **proposal** added
> under Track S, explicitly marked as awaiting an owner decision and not acted on
> *(that proposal was subsequently **adopted** later the same day — see below)*.
>
> **Second amendment, same day — GATE-1 resolved by owner decision.** H3 removed
> from the critical path and ordered last; three chunks created (**P0** auth-phase
> decode, **S0** redirection feasibility, **S1a** DTLS server); S1 split into
> S1a/S1b; P1's dependency changed from H3 to "S1a or H3"; H3's index row and prompt
> re-banned­ered as LAST RESORT with a terminal-result bound; Order section rewritten
> around the no-EAC-first sequence. Reasoning is STATE §3; the work order is
> STATE §15. **No chunk was marked complete and no finding was altered — this is a
> sequencing change.**
>
> **Third amendment, same day — P0 run, verdict PARTIAL; the game's retirement date
> becomes a routing constraint.** P0 ticked `[x]` with a pointer to STATE §16 and a
> DONE banner on `P0_PROMPT.md`; **`P0_PROMPT.md` added to the standalone-prompt
> list**, where it should have been when the chunk was created. Two chunks created
> from P0's remainder: **P0b** (re-capture to decrypt the queue response — OPEN-1)
> and **P0c** (decode `Characters[].PublishedData` — FIND-3). **S0 moved to `[!]`
> blocked**, because its one hard input is the thing P0 could not read. Order section
> amended. Three claims inside `P0_PROMPT.md` struck as falsified, including two the
> prompt inherited from STATE §12A.
>
> **And the constraint that now sits above all of it: Amazon retires the servers
> 31 January 2027** (STATE §16.0, read from the client's own news payload). Every
> capture-dependent chunk has a deadline; every file-dependent chunk does not. The
> order below is amended accordingly. **No chunk was un-ticked and no finding
> altered.**
>
> **No prose was deleted.** The only text overwritten in place is the six index-table
> status rows and the T3 prompt's `← NEXT` header — which is precisely what "tick the
> row, add a DONE banner" means, and none of it carried a finding. Everything else
> that changed is struck through with its replacement beside it, including the four
> paragraphs of the old Order section, quoted back verbatim.

> **Fourth amendment, same day — P0b run, verdict COMPLETE; S0 unblocked and the
> critical path is clear.** P0b ticked `[x]`; **S0 moved from `[!]` back to `[ ]`**,
> its blocker OPEN-1 closed by reading `Token.RepAddress`. **OPEN-2 closed** in the
> same chunk — `GUID2` is the queue ticket id, not instance/shard/channel. One chunk
> created: **S0a**, a narrow static check answering **OPEN-3**, the question of
> whether the client validates the token signature — which now gates S0's *design*
> rather than its confidence. **P0B_PROMPT.md (since renamed `P0b_PROMPT.md`) and `S0A_PROMPT.md` added to the
> standalone-prompt list.** Order section amended: the perishable window has now been
> spent on the one thing that needed it, so what remains is mostly file-based work
> that survives 31 Jan 2027. Two claims inside **P0B_PROMPT.md** annotated — one
> corrected, one marked untested rather than wrong. **No finding was altered and no
> chunk un-ticked.**

> **Fifth amendment, 2026-08-31 — S0a run, verdict NO (confirmed by trace); OPEN-3 and
> OPEN-3R both resolved, S0 is the small branch.** S0a ticked `[x]`. Static Ghidra trace of
> `NewWorld.exe` (b22469132): **no asymmetric-verify API is imported** (BCRYPT/CAPI/
> CRYPT32 present, but no `BCryptVerifySignature`/`BCryptImportKeyPair`, no
> `CryptVerifySignature`/`CryptImportKey`), and **five functions on the address path
> are crypto-free** — the dial (`FUN_14644a070` case 9), the connect (`FUN_146425f20`),
> the queue-login launcher (`FUN_146465060`), the request guard (`FUN_146435e40`), and
> the disconnect reporter (`FUN_14643c570`). None reads a `Signature`/`HostHash` field;
> none calls a verify. **`OPEN-3` moved to RESOLVED (provisional NO)** in STATE §15; S0
> proceeds as the field-rewrite proxy. Initially recorded as a provisional NO (consume
> side only); the residual was then closed in the same session by reading the deserializer
> directly, so the verdict is a **traced** NO with no outstanding residual. Two corrections added to STATE §13 (the committed
> `pins/` claim; the S0a-prompt "field names are literal JSON keys" assumption). Findings
> folded to STATE §16.15; tests #60–#61 logged. **`S0A_PROMPT.md` still needs its DONE
> banner** — a one-block edit noted below. No finding altered, no> chunk un-ticked.

> **Sixth amendment, 2026-08-31 — `H2_PROMPT.md` created; H2 marked NEXT.** Written at
> creation time (before H2 runs), added to the standalone-prompt inventory the same
> moment — the practice CHARTER §6.7 teaches. H2 is the static-Ghidra protocol-structure
> chunk, warm from S0a's project: walk the receive path `recvfrom → SSL_read → GridMate
> Carrier → dispatch`, identify the routing mechanism, enumerate message types, mark the
> protobuf choke point (FIND-2). Its load-bearing prediction (transport matches reference
> GridMate source down to the message boundary) doubles as a falsification check on
> T5/§12B. Unblocks P2 and S1a's send-side. No finding altered, no chunk ticked or
> un-ticked — this only adds a prompt and points the Order at it.

> **Ninth amendment, 2026-09-05 — P6 done (partial), P7 opened, and the error class
> caught a FOURTH time, inside the chunk rather than between chunks.** P6 answered
> OI-P5-1 in its first step — `CreateString`, so the vocabulary is extracted — and
> then spent four extraction passes discovering that **the mechanism it had anchored
> on was the wrong one.** Walking `CreateString`'s call sites recovers 5,907 types at
> 99.4% resolution and **not one of the ten session-layer message types**. Hub
> registers through `FUN_1407de270` with the parse inlined; there is no call site.
>
> **This is `X is in the binary, therefore the protocol is X` in its fourth form**
> (P2 → protobuf; §17.9 → GridMate; P5 → replica chunks; P6 → `AZ_TYPE_INFO`), and
> the new variant is worth naming precisely: **a mechanism used by most types in the
> binary is not therefore the mechanism the layer you care about uses.** A 5,907-row
> map with 99.4% resolution and three passing witnesses looked exactly like success.
>
> **P6's prediction 0 was written to leave room for "neither — something not yet
> named," and that room is what it landed in.** Not UUID-on-the-wire versus
> negotiated index, but **two identity mechanisms coexisting**. The instruction
> introduced after P5 did its job: it is the first time the premise-targeting
> prediction caught the redirect instead of being outrun by it.
>
> **A second lesson, from inside the chunk.** Six hypotheses were advanced and
> falsified before the mechanism was found — brace style as a discriminator, two
> populations, qualified names, a caller-column join, a second parser, small-string
> capacity. **Every one generalised from a single example**, the same cap §18.6
> flagged and test #68 records. The session's own error rate is recorded in §19.10
> rather than quietly omitted.
>
> Changes: **P6 row ticked** with verdict, date and a §19 pointer, note rewritten in
> the same edit. **Order item 4b marked done and 4c (P7) added.** The closing "Next
> is P6" superseded. **The P6 stub below marked DONE and superseded by the P7 stub.**
> **`P7_PROMPT.md` NOT yet written** — flagged here so the §6.7 omission is visible
> rather than discovered later, which is the fourth time that list has needed
> repair. No finding from another chunk altered; §18.3 restated as single-instance
> per §13.

> **Eighth amendment, 2026-09-04 — P5 done, P6 opened, and the SAME ERROR CLASS
> CAUGHT A THIRD TIME.** P5 set out to document GridMate's replica wire format and
> found that **the game's state does not live there either**: there is a third
> layer, **`Amazon::Hub`**, above GridMate — ~3,600 registered types, **3,629
> symbols and zero functions**, entirely inlined. STATE **§18**.
>
> **P5's prediction 0 was written specifically to target its own premise, and it
> still failed**, because it enumerated only two answers — the world stream
> carries `ReplicaChunk` traffic, or it does not — and reality was a third layer
> neither option named. That is *X is in the binary, therefore the protocol is X*
> for the **third time in two chunks** (P2 → protobuf; §17.9 → GridMate; P5's own
> premise → GridMate again). **The rule this file now carries: a
> premise-targeting prediction must leave room for "neither — it is something not
> yet named."** It is written into P6's prediction 0.
>
> Changes: **P5 row ticked** with its verdict and a pointer to §18, note rewritten
> in the same edit. **P6 row added as the Track P front.** **`P6_PROMPT.md` added
> to the standalone inventory at creation time** — the fourth chance to not repeat
> the §6.7 omission, and the second time running it has been taken. Order item 4a
> marked DONE and **4b added**; the closing "Next is P5" superseded. **The P5 stub
> and P3's dependency note corrected**: GridMate's default transform marshalers
> write **raw IEEE floats**, not quantized values (STATE §13), which changes what
> P3 should look for.
>
> **P5 also corrected P2's §17.9**, written the previous day: the 94
> `InitializeReplicatedFields` references are **Hub** symbols, absent from all of
> `dev/Code/Framework`, and never supported the GridMate retarget. The retarget
> was right to leave protobuf and wrong about the destination. *Lesson recorded in
> STATE §13: an instrument cross-check that confirms a number does not confirm
> what the number is about.*

> **Seventh amendment, 2026-09-04 — H2 and P2 both complete, and TWO FALSE `[x]`
> MARKS REPAIRED. This is the failure this file's own repair note describes,
> arriving a third time and in its worse form.** On 2026-08-30 the recorded failure
> was rows sitting at `[ ]` after completion. This time both rows were **already
> ticked `[x]` while their notes still routed a session to go run them** — H2's read
> "**NEXT — ready to run 2026-08-31**" and P2's carried no verdict, no date and no
> STATE pointer, only pre-work planning text. A ticked row with a "go run this" note
> is worse than an unticked one: the tick suppresses the reader's suspicion while the
> note supplies the wrong instruction. CHARTER §6.5's corollary names the tick
> half — *a chunk row is never ticked on the strength of remembered work* — and
> §6.4(1) names the other: a row is not ticked until it carries **a pointer to the
> STATE section**.
>
> Changes: **H2 row rewritten** with its DONE verdict and a pointer to STATE §17;
> **P2 row rewritten** with its DONE verdict and a pointer to STATE §17.9, and
> **renamed** — it was still titled "Message-type census," which H2 actually
> performed (§17.5) and which P2 had been repurposed away from months of drift ago
> (STATE §15 work-order item 2 has called it "Protobuf descriptor extraction" since
> 2026-08-30). **`P2_PROMPT.md` added to the standalone-prompt inventory** — it was
> missing, the same failure CHARTER §6.7 names and this file has now recorded three
> times. Order items 3 and 4 marked DONE; the closing "Next is H2 or S0" superseded.
> The "what this order does not yield" paragraph **corrected**: it named FIND-2 as
> the substitute for observing the inbound half, and FIND-2 closed **negative**.
>
> **The one routing change that matters: Track P is retargeted off protobuf.** P2
> found no game protocol in any descriptor (STATE §17.9). The world stream is
> GridMate `ReplicaChunk` marshalling — for which **we hold the source** at
> `7d4f1ee6`. **P5's dependency is corrected from `T1, H4` to `T1` alone**: reading
> the fork's marshalers needs no reflection reader and no capture, so H4 is an
> accelerator, not a gate. P5 is promoted to the Track P front.

> **Repair note — 2026-08-29.** This file was corrected alongside `STATE.md`.
> Changes: **T5's dependency list fixed** (it needs T3's retail capture, which was
> missing); the Standing environment notes filled in with real values; completed
> chunks marked DONE with pointers into STATE; three claims inside the T4 prompt
> marked SUPERSEDED per STATE §13; T3's scope narrowed to match the instrument
> that now exists; the suggested order rewritten. Completed prompts are kept
> verbatim as historical record — a DONE banner is added, the body is not deleted.

---

## How to run a chunk

1. Open a new session.
2. Paste, in this order: **`CHARTER.md`**, then **`STATE.md`**, then **the one
   chunk prompt** you are working on, then **the `FINDINGS` block from the chunk
   you just finished** if it is listed as an input.
3. Work the chunk. Do not start the next one.
4. At the end, the session writes a `FINDINGS` block in the format at the bottom
   of this file.
5. You fold the findings into `STATE.md` — adding, never deleting — and tick the
   chunk here.

### The two commands that bracket a session — added 2026-09-04

**Run `python3 check_docs.py` at the start of a session and again before
`git push`.** It is the mechanical form of CHARTER §6, and it exists because
**every failure it catches already had a rule written against it and the rule was
violated anyway** — three times for the prompt inventory, three times for stale
router rows. CHARTER §6.2's insight generalises: a session cannot be expected to
remember seven closing steps, but it can be expected to run one command.

```fish
cd ~/Documents/NWLY; and git pull
python3 check_docs.py          # START — before believing your inputs
#   ... run the chunk ...
python3 check_docs.py          # END — before believing you are done
```

It checks: STATE's four freshness numbers against the file · no duplicate section
numbers · **STATE and CHUNKS naming the same complete chunks** · every `[x]` row
carrying a verdict, a date and a STATE pointer · **no `[x]` row still routing a
session to run it** · every `*_PROMPT.md` inventoried, and present on disk · every
complete chunk's prompt carrying a DONE banner · no completed chunk named as
"Next is" · every §15 open item owned · CHARTER §1's no-regeneration rule intact.

**A FAIL means stop and resolve it. It does not mean proceed carefully.**

### What the owner does, in order — the closing sequence

The session writes findings; **you** close the chunk. Do these in this order,
because they fail differently (CHARTER §6.4 — router before ledger):

| # | Do this | Why this order |
|---|---|---|
| 1 | **Tick the row in this file**, with the verdict, the date, and a `STATE §x` pointer | A stale router **misdirects** the next session, which has one chunk and no way to notice the contradiction. A stale ledger only clutters. |
| 2 | **DONE banner on the `*_PROMPT.md`**, and strike through — never delete — every claim inside it the chunk falsified | §6.4(2)(3). The next reader of that prompt must not act on a falsified premise. |
| 3 | **Add the prompt file to the standalone inventory above** if it is not already there | §6.7. Missed three times. This is now checked. |
| 4 | **Fold FINDINGS into `STATE.md`** — add a section, add correction rows for anything overturned, update §15's register | §6.5: unwritten work did not happen. |
| 5 | **Update STATE's freshness header** — date, commit, section count, highest test, correction count | §6.2. All four, or the next session halts on a false alarm. |
| 6 | **Run `check_docs.py`. Then `git push`.** | The push is what makes it real for the next session (§6.1, §6.3). |

**Three rules that are easy to get wrong:**

- **A `[x]` with a "go run this" note is worse than a `[ ]`.** It happened to both
  H2 and P2 on 2026-09-04. The tick suppresses the reader's suspicion while the
  note supplies the wrong instruction. **If you tick a row, rewrite its note in the
  same edit** — they are one action, not two.
- **Never tick a row from memory** (§6.5 corollary). If the evidence is not written
  down, the row stays open.
- **A chunk that falsifies its own premise is COMPLETE, not partial**, provided its
  definition of done has an "or confirmed absent" branch and the negative is
  recorded with evidence. P2 is the worked example. Residuals go to §15 with an
  owner; that is how a chunk closes cleanly rather than staying open forever.

**If a session hands you a rewritten `CHARTER.md`, refuse it** (§1). Amendments to
the charter are proposed as a separate file and applied by you, by hand.

### What the SESSION owes you at the end — the HANDOFF block

**A session must end with a HANDOFF block and nothing after it.** Not a summary,
not analysis, not "and here are some thoughts on next steps." Fixed shape, plain
imperatives, **ten lines maximum**:

```
HANDOFF — <chunk id> — <verdict in five words or fewer>
  1. CHUNKS.md  — <exact edit>
  2. <FILE>     — <exact edit>
  3. STATE.md   — <exact edit>
  Run: python3 check_docs.py    then: git push
  Not done: <anything the session could not finish, or "nothing">
```

**Why this is a rule.** On 2026-09-04 a session did every piece of the work
correctly and then reported it in several hundred words of reasoning with the
owner's action items distributed through the prose. The owner had to *mine* the
response for his own to-do list. **Findings are the session's product; the action
list is the owner's, and it must be separable in one glance.** Analysis belongs
above the HANDOFF block, and the block is the last thing in the message.

**The session does not get to decide the block is unnecessary.** If everything is
already applied and `check_docs.py` is green, the block says so in one line. An
empty HANDOFF is information; an absent one is the owner reading paragraphs to
find out whether he has work.

**Corollary — the session runs `check_docs.py` itself where it can**, and derives
the HANDOFF block from the output rather than from memory. `--close` prints the
action list in exactly the form the block needs. A session that cannot reach the
repository says so plainly and writes the block from what it knows, marked as
unverified — it does **not** claim to have run a check it did not run (CHARTER
§6.3: claims about our own repository are findings and obey §4).

**Never paste more than one chunk prompt.** A session that can see three chunks
will half-do all three and hand you back something none of them defined as done.

**Why prompts are short and the charter is long:** the charter is the part that
must survive; the prompt is disposable. If a future session only reads one
document, it should be the charter.

**Standalone prompt files.** Some chunks have a fuller ready-to-run prompt kept as
its own file (`T3_PROMPT.md`, `T4_PROMPT.md`, `T5_PROMPT.md`, `D2_PROMPT.md`,
**`P0_PROMPT.md`**, **`P0b_PROMPT.md`**, **`S0A_PROMPT.md`**, **`H2_PROMPT.md`**,
**`P2_PROMPT.md`**, **`P5_PROMPT.md`**, **`P6_PROMPT.md`**, **`P7_PROMPT.md`** — the
first added 2026-08-30 after it was missing from this list while P0 ran, which is the
same "a prompt that exists only on one machine cannot be handed to anything" failure
CHARTER §6.7 names; the latter three added the same day **at creation time**, which is
the practice that failure was supposed to teach — `H2_PROMPT.md` created 2026-08-31,
before H2 was started. **`P2_PROMPT.md` added 2026-09-04 — retroactively, after P2
had already run, which is the same omission this list exists to prevent and the
third time it has happened. The prompt file existed; it was simply never inventoried
here.** `P6_PROMPT.md` added 2026-09-04 at creation time, before P6 was started —
**the second consecutive chunk for which this list was maintained rather than
repaired afterwards.** `P5_PROMPT.md` added 2026-09-04 **at creation time, before P5 was
started** — the practice §6.7 teaches, and now also enforced by `check_docs.py`).
Where one exists,
**that file is authoritative** and the section here is a summary. Paste the file,
not the summary.

> **Casing corrected 2026-09-05, and a duplicate found.** This list read
> **P0B_PROMPT.md** (uppercase B) while the live file on disk is **`P0b_PROMPT.md`** — and because
> Linux is case-sensitive, **both existed**. `check_docs.py` caught it from two
> directions at once: `P0b_PROMPT.md` on disk but not inventoried, and
> the uppercase file carrying no DONE banner. The lowercase file is the live one and
> carries its banner (P0b, 2026-08-30). **The uppercase file is a stale duplicate and
> should be `git rm`'d.** This is the same class as the 2026-08-29 duplicate §11 —
> a stale copy surviving beside the real one — which is what `check_docs.py` exists
> to catch. **`P7_PROMPT.md` added 2026-09-05 at creation time, before P7 was
> started** — third consecutive chunk for which this list was maintained rather than
> repaired afterwards.


---

## Chunk index

Status: `[ ]` not started · `[~]` in progress · `[x]` done · `[!]` blocked

### Track T — Transport. Identify how the client secures and frames network data.

|       | Chunk                                             | Depends on   | Deliverable                                                              |
| ----- | ------------------------------------------------- | ------------ | ------------------------------------------------------------------------ |
| `[x]` | **T1** Engine fingerprint (static)                | —            | **DONE 2026-08-29.** GridMate confirmed. STATE §10                        |
| `[x]` | **T2** Crypto-library fingerprint                 | —            | **DONE 2026-08-29.** OpenSSL 1.1.1k, static, `SSL_read`/`SSL_write`. STATE §10 |
| `[x]` | **T3** Transport recon (retail capture, no hooks) | —            | **DONE 2026-08-29.** UDP/DTLS 1.2 via `SecureSocketDriver`; P1–P4 confirmed; epoch-0 pcap saved. STATE §12A. Prompt: `T3_PROMPT.md` |
| `[x]` | **T4** Build the reference `Carrier` from the fork | —           | **DONE 2026-08-29.** Plaintext + DTLS both pass and captured. STATE §7–§9 |
| `[x]` | **T5** Reference vs retail handshake diff         | T1, **T3**, T4 | **DONE 2026-08-29. THE MILESTONE — the charter's core question is answered.** Stock GridMate `SecureSocketDriver`, zero catalogued exceptions; reference validated as an instrument. STATE §12B. Prompt: `T5_PROMPT.md` |

> **Track T is complete.** T1, T2, T3, T4, T5 all landed. What remains in the
> transport layer is Track H, which supplies the epoch-≥1 plaintext that T5's
> verdict licenses P-track to interpret.

> ~~**T5's dependency on T3 was missing from this table until 2026-08-29.** T5 diffs
> the reference epoch-0 handshake (T4, STATE §9) against the *retail* epoch-0
> handshake, and the only source of the latter is T3's capture. T5 cannot start
> before T3 lands.~~ **RESOLVED 2026-08-29** — the dependency was correct and was
> honoured: T3 ran first and produced `t3_handshake_epoch0.pcap`, which was T5's
> retail input. Kept as the record of a real near-miss in the work breakdown.

### Track H — Hooking. Get to plaintext, framed messages. Proven on the reference build first.

|       | Chunk                                          | Depends on | Deliverable                                                          |
| ----- | ---------------------------------------------- | ---------- | ------------------------------------------------------------------- |
| `[ ]` | **H1** Frida crypto hook on the reference build | T2, T4     | `SSL_read`/`SSL_write` plaintext logged from a target we control. **Now also: prove the signature scan here** — see the prompt |
| `[x]` | **H2** Map the inbound world-message path and its dispatch (static) | T1, ~~(T5)~~ **T5 done** | **DONE 2026-09-04. World-message dispatch map complete. STATE §17.** Inbound path resolved end to end (`WSARecvFrom → TransportLayerLibUV → TransportLayerGridMate → REPConnection::OnConnect/OnRecv → Aws::JavelinGatewayService`); **stock/game boundary identified at `REPConnection`**; dispatch confirmed **registration-based, not a switch** (prediction 2 confirmed); **10 Javelin Gateway message types enumerated by RTTI**; **GameConnection state table complete, all 15 states**; signatures recorded. Opened OI-H2-1…5. **LibUV finding strains T5/§12B's "zero catalogued exceptions" wording** — precision gap, not falsification (§17.1). ~~**NEXT — ready to run 2026-08-31.** Ghidra, warm from S0a (same b22469132 project, RTTI done). Walk `recvfrom → SSL_read → GridMate Carrier → dispatch`; identify the routing mechanism (type-keyed table / switch / ReplicaManager marshaler) and enumerate message types; mark where protobuf enters (FIND-2). Scope ambitiously — a primary source of protocol structure, not just a hook point. Falsification check armed: prediction that transport matches reference GridMate source down to the message boundary; if not, T5/§12B strained. Unblocks **P2** (message census) and **S1a** (send-side).~~ **One H2 claim has since been corrected: §17.5's "protobuf choke point" was wrong (P2, STATE §13, §17.9).** Prompt: `H2_PROMPT.md` |
| `[~]` | **H3** Crypto/dispatch hook on retail           | H1, H2, T2 | **LAST RESORT — deliberately deprioritised 2026-08-30, not blocked.** Only if P0/S0/S1a/H2/H4 are exhausted. One attempt; EAC prevention is terminal. STATE §3, §15 |
| `[ ]` | **H4** The reflection reader (`SerializeContext`) | T1       | **Decision gate + prototype.** Only if the ABI proves traversable    |

> ~~**H2 can start now.** Its hard input is T1, which is complete. T5 is only needed
> for H2's *falsification* check at the end (does the xref chain resemble
> `Carrier::Receive` → `ReplicaManager`), so H2 can run mostly blind and be
> confirmed once T5 lands. It needs no login, no running client, and no live
> servers — which makes it the fallback if T3 stalls.~~
>
> **SUPERSEDED 2026-08-30 — T3 and T5 both landed.** H2 no longer runs blind and is
> no longer a fallback for a stalled T3. Both consequences are live:
> **(a)** the falsification check is now a real test with a known answer behind it —
> T5 proved the transport is stock GridMate `SecureSocketDriver` (STATE §12B), so an
> xref chain that does *not* resemble `Carrier::Receive` → `ReplicaManager` means the
> static analysis is wrong, no longer that T1 might be. **(b)** H2 remains the one
> H-track chunk needing no login, no running client, and no Proton — which is now an
> argument for sequencing it *first*, not a contingency. See the note under Order.

### Track P — Protocol. What the messages mean. Built on captures, not guesses.

|       | Chunk                                     | Depends on | Deliverable                                     |
| ----- | ----------------------------------------- | ---------- | ----------------------------------------------- |
| `[x]` | **P0** Auth-phase decode (TCP/443)        | —          | **DONE 2026-08-30. VERDICT: PARTIAL.** Auth sequence documented end to end; **selection call identified** — `POST /prod/game/login/queue/v2/{WorldId}_{GUID2}/jwt/omni`; world list read and proven **GUID-only, no address field**. **The world address was NOT read:** the response carrying it does not decrypt (`Cannot find master secret`) → **OPEN-1**. STATE §16. Prompt: `P0_PROMPT.md` |
| `[x]` | **P0b** Decrypt the queue response       | P0         | **DONE 2026-08-30. VERDICT: COMPLETE.** A cold launch (Steam logged out and back in) forced a **full** TLS handshake on the queue stream; the key was logged and the response decrypted. **The world address is `LoginQueueResponse.Token.RepAddress`, a literal `"ip:port"` string**, at frame 1660 — 63 frames before the client's first DTLS ClientHello to that host:port, and present in **exactly one** of 20+ exported HTTP objects. **OPEN-1 closed. OPEN-2 closed** (`GUID2` = the queue ticket id). Predictions 1–4 all confirmed. **Also found: the queue is a poll loop**, which changes what S0 must answer. STATE §16.9–§16.14, tests #55–#59. Prompt: `P0b_PROMPT.md`. ~~**NEW 2026-08-30.** The one thing standing between here and S0.** Re-capture forcing a **full** TLS handshake on the queue connection so the keylog records its key. Hypothesis: the callback fires on full handshakes only, so resumed sessions go unlogged (**DEF-2**). **Must be a cold launch** — login is Steam-inherited, so a fresh session replays the whole ticket→JWT→STS chain in-window *and* forces the full handshake; a resumed session gives neither. ~15 minutes, retryable — **but only until 31 Jan 2027.** STATE §16.7, test #54~~ |
| `[ ]` | **P0c** Decode `PublishedData`           | P0         | **NEW 2026-08-30. Cheap, and it is server→client state.** Base64 + zlib (`eNr…`) blobs in `Characters[]` of the `getlogininfo` response — a response we can **already read**, no keys and no new capture needed. FIND-3, STATE §16.3 |
| `[ ]` | **P1** Handshake sequence                 | ~~T5~~ **T5 done**, ~~H3~~ **S1a or H3** | The connect exchange, byte-documented. **Scope narrowed — the epoch-0 DTLS half is already byte-documented in STATE §12B; what remains is the GridMate `Carrier` handshake inside epoch ≥ 1.** Reachable from S1a's plaintext for the client→server half without H3 |
| `[x]` | **P2** ~~Message-type census~~ **Protobuf descriptor extraction (static)** | ~~H3~~ ~~**H2, or S1a, or FIND-2**~~ **H2 (done)** | **DONE 2026-09-04. VERDICT: NEGATIVE — and the negative is the deliverable. STATE §17.9.** Whole-binary scan found **3 `FileDescriptorProto` blobs, none of them game protocol**: `campfire_event_default.proto` (Amazon Campfire telemetry — 1 message, 1 nested context struct, 1 enum), plus stock `google/protobuf/empty.proto` and `google/protobuf/descriptor.proto`. **No Javelin descriptor. No `service` block. `application/x-protobuf` = 0 against `application/json` = 236.** **All three predictions in `P2_PROMPT.md` falsified**, including prediction 3 ("the single most valuable find P2 can make"). Consequences: **FIND-2 closed negative**; **§17.5's "protobuf choke point" corrected** (STATE §13); **OI-H2-3 answered mundanely** — AWS SDK `XResult` types are non-polymorphic, so no vtable and no RTTI, not an exotic inbound path; **Track P retargeted onto GridMate `ReplicaChunk` marshalling → see P5**. Residual: **OI-P2-1** (registration mechanism unconfirmed — the one definition-of-done bullet not satisfied), **OI-P2-2** (are the 10 Javelin types the same REST routes P0 decoded?). Tests #63–#65. ~~The dispatch table as a list of known types. **Dependency corrected 2026-08-30** — H2's static table and FIND-2's protobuf descriptors both reach this without H3.~~ **Note the rename: the message-type census was performed by H2 (§17.5), not by P2.** Prompt: `P2_PROMPT.md` |
| `[x]` | **P6** Hub message layer — type vocabulary and fragment wire format | T1, H2, P2, P5 | **DONE (PARTIAL) 2026-09-05. STATE §19.** **OI-P5-1 ANSWERED: `FUN_1413e84b0` is `AZ::Uuid::CreateStringSkipWarnings` — the UUIDs are literals, the vocabulary is extracted.** P5's prediction 1 confirmed. **But the answer did not deliver the vocabulary the question assumed.** Walking `CreateString`'s 15,914 call sites yields the **engine's `AZ_TYPE_INFO` map — 5,907 types at 99.4% resolution — and NOT ONE of the ten session-layer message types is in it.** Hub message types register through **`FUN_1407de270`** (3,511 call sites vs 3,482 `InstallRegistrationHook` instantiations) with the UUID parse **inlined**, so they have no call site to find. Walking the registrar gives **3,509 distinct Hub identities**. **311 named / 3,199 anonymous — and the anonymity is BY DESIGN**: anonymous hooks construct an explicitly empty string (`local_18 = 0`) and pass it anyway. The names do not exist in the binary, so 8.9% is the answer, not a shortfall — four unrelated extraction strategies converged on it. The split is **regional**: named hooks occur only in `1407xxxxx` and `146axxxxx`, exactly the regions holding the wire-facing session layer. **Hub attaches runtime names only to the message layer; everything else is UUID-only.** **OI-P5-4 ANSWERED: NO** — `FragmentUpdateMsg`'s handler table has **4** slots against `ReplicateClient`'s **8**, so **§18.3 is restated as a single-instance observation**; prediction 3 falsified. **Step 5 delivered** — all three `RegistrationRequest` revisions, `RegistrationResponseMsg`, `TimeSynchMsg` and the connection messages enumerated with UUIDs, hooks and handler vftables (§19.6). **Step 4 NOT STARTED** — predictions 2 and 4 untested, so **prediction 0's wire question is still open**. Two `P6_PROMPT.md` claims falsified before the work began (`CreateName` is SHA-1 not MD5; literals are not uniformly brace-delimited) — §13. **Three dead routes recorded in §19.8; do not retry them.** Residuals **OI-P6-1…5**. Tests #69–#78. → **P7.** Prompt: `P6_PROMPT.md` |
| `[ ]` | **P3** Position/movement message          | ~~H3~~ **S1a or H3**, P2 | The controlled-walk experiment, decoded. Outbound position messages arrive as plaintext at an S1a server; H3 only adds the inbound half. **CORRECTED 2026-09-04 (P5, STATE §13):** look for a smoothly varying **raw float triple** — GridMate's default transform marshalers do **not** quantize. Whether New World opts into compression per DataSet is **OI-P5-3** |
| `[ ]` | **P4** Initial world-state sync           | **H3**, P2 | The login state dump. **Genuinely needs H3** — this one is server→client, the direction S1a cannot observe. Expect to construct rather than capture it |
| `[x]` | **P5** Replica/chunk model | ~~T1, H4~~ **T1** | **DONE 2026-09-04 — COMPLETE, with a redirect larger than the chunk. STATE §18.** GridMate's replica wire format is documented from the pin (envelope; **`PackedSize` is bit-granular, and every length in the envelope is a BIT count**; GridMate's VLQ is **not** protobuf's varint; chunk ids are `AZ::Crc32`; DataSets are dirty-bit gated) — **but it is not where the game's state lives.** P5 found a **third layer: `Amazon::Hub`**, Amazon's own actor/fragment replication framework above GridMate, **3,629 symbols and zero functions**, entirely inlined. Game state is Hub fragments; the inbound world-state update is **`ReplicateClient::FragmentUpdateMsg`**; the world handshake is enumerated by name — `REPClient::RegistrationRequestMsg`/`V2Msg`/`V3Msg`, `RegistrationResponseMsg`, `PingMsg`, `TimeSynchMsg`, plus `REPConnectionListener::ClientConnection`/`DisconnectionMsg`. **Prediction 1 and 2 confirmed; prediction 3 FALSIFIED** — transforms are **raw IEEE floats** (12 B per Vector3, 48 B per Transform), quantization is opt-in per DataSet, which corrects the P3 note below (STATE §13). **Prediction 0 asked the wrong question** — see the eighth amendment. **Also corrects P2's §17.9** on `InitializeReplicatedFields`. Residuals **OI-P5-1…4**; **OI-P5-1 is the highest-value open question on the board.** Tests #66–#68. → **P6.** ~~**PROMOTED 2026-09-04 to the Track P front, by P2's negative result (STATE §17.9).** How replicated objects map to the wire. **P2 ruled protobuf out**, and the world stream is GridMate `ReplicaChunk` marshalling (`ReplicaChunk` 23, `InitializeReplicatedFields` 94, plus §10's `VTransformReplicaChunk` / `VTriggerAreaReplicaChunk` / `ScriptComponentReplicaChunk`).~~ **That framing was wrong twice over: `InitializeReplicatedFields` is a Hub symbol, not GridMate's, and the world stream is Hub.** Prompt: `P5_PROMPT.md` |

### Track S — Server. Speak back to the client.

|       | Chunk                                       | Depends on | Deliverable                          |
| ----- | ------------------------------------------- | ---------- | ------------------------------------ |
| `[ ]` | **S0** Redirection feasibility              | ~~P0~~ ~~P0b~~ **none — P0b done** | **UNBLOCKED 2026-08-30.** P0b read the handoff: the client is handed **`Token.RepAddress`** (literal `ip:port`) in the reply to the ticket-redeem POST, 63 frames before it dials that host. Requirements in **STATE §16.13**. **New constraint from P0b: the queue is a poll loop** — on a populated world the client re-POSTs the ticket path every `RefreshInterval` seconds and gets no `Token` until admitted, so a proxy that answers once is fragile (STATE §16.11). ~~**New gate: OPEN-3** — does the client validate `Token.Signature`? Owned by **S0a**; answer it before committing to a design.~~ **OPEN-3 RESOLVED NO 2026-08-31 (S0a, STATE §16.15) — confirmed by direct trace of the deserializer, no residual.** The client stores `Token.Signature`/`HostHash` without ever verifying them, so rewriting `RepAddress` breaks nothing the client checks. **S0 is the small branch: rewrite the one `RepAddress` string.** OPEN-3R closed same session; no empirical test needed. ~~**BLOCKED 2026-08-30 on OPEN-1**, and the dependency has moved from P0 to **P0b**. P0 established *where* the handoff is but not *what it says*. Two findings already reshape this chunk: **(a) a hosts/DNS redirect will not work** — no DNS query resolves the world host in five captures, so there is no name to catch; **(b) the interception point is the queue response**, which means a **TLS-terminating proxy for `d2oeuvxi3kfsrw.cloudfront.net`** (that host *is* DNS-resolvable), with Wine-prefix certificate trust as the obstacle to scope. Requirements derived in STATE §16.6~~ **(a) and (b) both still stand and are now confirmed rather than inferred.)** |
| `[x]` | **S0a** Does the client validate the queue token? | — | **DONE 2026-08-31. VERDICT: NO — confirmed by direct trace.** Static Ghidra trace of `NewWorld.exe` b22469132: five consume-side functions crypto-free, no asymmetric-verify API imported, **and the deserializer itself read** (`FUN_1474e4f20` → `FUN_1474e5990`) — `Signature`/`HostHash`/`RepAddress` are stock AWS-SDK `JsonView` GetString-and-store, never inspected. Client treats `RepAddress` as opaque cargo (Token +0x5a) → **S0 is the small field-rewrite branch.** OPEN-3 and its residual OPEN-3R both closed same session; `HostHash` characterised (store, not compare). STATE §16.15, §15; tests #60–#62. Prompt: `S0A_PROMPT.md` |
| `[ ]` | **S1a** DTLS server (epoch 0)               | T5         | **NEW 2026-08-30, unblocked, no EAC contact.** Fully specified by §12B. **The inversion: when the client handshakes with us we hold the session keys, so its messages arrive as plaintext on our socket** — this replaces H3 for the client→server half |
| `[!]` | **S1b** Carrier handshake (epoch ≥ 1)       | S1a, P1    | The GridMate `DefaultHandshake` / connection request-ack inside the encrypted channel |
| `[!]` | **S2** Stand a character in the world       | S1b, P4    | A character loads and renders         |
| `[!]` | **S3** Movement round-trips                 | S2, P3     | The client can move and see it persist |

> ~~**PROPOSAL — 2026-08-30, not acted on. Owner decision required; the index above is
> unchanged pending it.**~~ **ADOPTED 2026-08-30.** The proposal below argued for
> splitting S1 into an unblocked DTLS half and a blocked Carrier half. The GATE-1
> decision settled it: with H3 off the critical path, S1a is no longer a parallel
> nicety — **it is the primary route to client→server plaintext.** Rows created
> above. The counter-case recorded below (that it opens a fourth track and CHARTER
> §1's layering exists to stop server work outrunning protocol understanding) still
> stands and is answered thus: S1a builds only what T5 already *proved*, and it is
> the instrument by which protocol understanding is obtained rather than a guess
> that runs ahead of it. Original text kept:
>
> STATE §12B fully specifies the **DTLS layer** of a server, from source plus two
> captures: `DTLSv1_2_method` (pinned, not `DTLS_method`), single suite `0xC030`,
> `SSL_OP_NO_QUERY_MTU`, GridMate's own 20-byte HMAC-SHA1 cookie generated and
> verified **at the datagram layer before OpenSSL sees it**, a hand-built
> HelloVerifyRequest with `RecordHeader::m_version` hardcoded to `fe ff`, a
> HelloRequest sent once the cookie verifies with exponential backoff capped at
> 1000 ms, and a CertificateRequest that accepts an **empty** client Certificate.
> None of that needs H3. All of it is testable against the reference `Carrier`
> client we already build — which is CHARTER §4's "prove it on the reference build
> first" reaching S-track for the first time.
>
> What genuinely needs P1/H3 is the **GridMate `Carrier` handshake inside epoch 1**.
>
> Splitting **S1a** (DTLS server — unblocked, testable now against the reference
> client) from **S1b** (Carrier handshake — blocked on P1) would put real S-track
> work on the board in parallel with H-track, rather than holding the entire server
> behind a hook that has an unsolved Proton problem in front of it. The counter-case
> is that it opens a fourth active track and CHARTER §1's layering exists precisely
> to stop server work outrunning protocol understanding. Recorded here so the option
> is not lost; **do not create S1a/S1b rows without an explicit decision.**

### Track D — Sustaining.

|       | Chunk                                        | Depends on | Deliverable                             |
| ----- | -------------------------------------------- | ---------- | --------------------------------------- |
| `[ ]` | **D1** Signature-scan harness                | —          | Offsets survive a client patch. **Head start:** `pins/22469132/Bin64.sha256` already answers "which binaries did this patch touch" (STATE §5) |
| `[x]` | **D2** Client game-data extraction (`.datasheet`) | —      | **DONE 2026-08-29.** 2250 datasheets → JSON. STATE §11 |

### Order — where the project actually is

**Rewritten 2026-08-30.** The previous text ("Next: T3 → T5") described the
pre-T3 position and contained no findings, only stale planning — replaced on the
same rationale and with the same precedent as `STATE.md` §1–§3. It read, verbatim:

> ~~**T1, T2, T4 and D2 are complete.** The engine question is settled (GridMate), the
> crypto boundary is located (`SSL_read`/`SSL_write`, statically linked), the
> reference instrument is built and captured, and Track S has its content source.~~
>
> ~~**Next: T3 → T5.** T3 is the last input T5 needs. T5 is the milestone — it answers
> the charter's one-sentence question by diffing the retail epoch-0 handshake
> against the reference one.~~
>
> ~~**Then Track H opens.** H2 can in fact run in parallel with T3 (see the note
> above) and is the fallback if T3 is blocked on account or server availability.~~
>
> ~~D1 can start whenever; it has a free head start from the pin baseline.~~

**Track T is finished. T1, T2, T3, T4, T5 and D2 are all complete.** The engine
question is settled (GridMate, STATE §10), the crypto boundary is located
(`SSL_read`/`SSL_write`, statically linked, STATE §10), the reference instrument is
built and captured (STATE §7–§9), Track S has its content source (STATE §11), and
**the charter's core question is answered**: retail transport is structurally stock
GridMate `SecureSocketDriver` with zero catalogued exceptions, and the reference
build is a valid instrument for it (STATE §12B).

**Track H is no longer the whole front.** GATE-1 resolved 2026-08-30 (STATE §3,
§15): **do everything reachable without contacting EAC first; H3 is a last resort.**
Not because H3 is off-charter — reading plaintext your own client decrypted is
reading your own data — but because injection into an EAC-protected process risks
the account everything else depends on, and working directly in front of a detection
system watching for exactly that is poor practice. If H3 is ever attempted it is
attempted **once**; EAC preventing the hook is a **terminal result**, and any step
aimed at surviving detection is circumvention, off-charter under §3, and does not
get pursued or recorded.

> **DEADLINE, added 2026-08-30 (STATE §16.0).** Amazon retires the servers **31 Jan
> 2027**. This splits the order by input type: **capture-dependent chunks perish on
> that date** (P0b, and any future live-traffic observation); **file-dependent chunks
> do not** (H2, P2/FIND-2, S1a against the reference, H1, H4). When in doubt about
> what to run next, run the perishable thing.
>
> **Amended after P0b, 2026-08-30 — the perishable window has now been spent on the
> thing that needed it.** P0b was the last chunk whose *input* could only come from a
> live backend, and it landed. What remains is almost entirely file-based and survives
> the retirement date. **The one residual exposure is S0**: its design work is
> file-based, but *proving* a redirect works needs a live client **and** a live
> backend to proxy. Schedule S0's empirical half before 31 Jan 2027 even though
> nothing about it is urgent today. **A second, cheaper hedge: take more captures than
> seem necessary now.** A pcap and its paired keylog are re-readable forever; the
> servers are not.

**The order, none of items 1–9 contacting a running retail client. Amended
2026-08-30 after P0, and again the same day after P0b:**

1. ~~**P0** — auth-phase decode.~~ **DONE (PARTIAL), STATE §16.** Left a single
   blocker on the critical path: **OPEN-1**, the undecrypted queue response.
2. ~~**P0b** — decrypt the queue response.~~ **DONE (COMPLETE), STATE §16.9–§16.14.**
   OPEN-1 and OPEN-2 both closed; the world address is `Token.RepAddress`. **The
   critical path is clear.**
2a. ~~**S0a** — does the client validate `Token.Signature`?~~ **DONE (NO, confirmed by
   trace), STATE §16.15.** OPEN-3 and OPEN-3R both closed: the deserializer was read and
   `Signature`/`HostHash` are stored-not-verified. S0 is the field-rewrite branch with no
   residual. The Ghidra project is analysed and warm for H2 (RTTI ran; the GameConnection
   state machine, the connect, the object layout, and both JSON deserializers are
   landmarked in §16.15).
3. ~~**H2** — static Ghidra. Scope it **ambitiously**: a primary source of protocol
   structure, not just a hook-targeting step. File-based, no deadline. **Shares S0a's
   instrument** — if S0a ran first, H2 starts warm.~~ **DONE 2026-09-04, STATE §17.**
   Dispatch mapped, 10 message types enumerated, state table complete. Opened
   OI-H2-1…5; one of its claims (the "protobuf choke point") since corrected by P2.
4. ~~**P2 / FIND-2** — protobuf `FileDescriptorProto` extraction. File-based.~~
   **DONE 2026-09-04, STATE §17.9. NEGATIVE RESULT.** 3 descriptors, none game
   protocol; no Javelin schema, no `service` block. **FIND-2 closed negative**;
   §17.5 corrected; OI-H2-3 answered. **Track P retargets onto P5** (GridMate
   `ReplicaChunk` marshalling, source-readable from the fork).
4a. ~~**P5** — replica/chunk model. **The new Track P front**, promoted by item 4's
   negative result. Read the fork's marshalers; no capture, no client, no H4.~~
   **DONE 2026-09-04, STATE §18.** Format documented — **and it is not where game
   state lives.** Found a third layer, **`Amazon::Hub`**, above GridMate. Prediction 3
   falsified (raw floats, not quantized). Corrects P2's §17.9. → **P6.**
4b. ~~**P6** — the Hub message layer. **The Track P front.** Recover the ~3,600-type
   name↔UUID vocabulary, frame `ReplicateClient::FragmentUpdateMsg`, and pin down
   which `RegistrationRequest` revision the client sends. Static, no deadline.~~
   **DONE (PARTIAL) 2026-09-05, STATE §19.** OI-P5-1 and OI-P5-4 both answered.
   **3,509 Hub identities recovered via the registrar `FUN_1407de270`** — not via
   `CreateString`, whose call sites give the engine's map instead. Names exist for
   **311 by design**; the other 3,199 register anonymously. Step 5 delivered.
   **Step 4 not started — that is P7.**
4c. **P7** — frame the fragment message. **The Track P front.** OI-P6-3: serialize/
   deserialize path, UUID-or-index on the wire, payload delimiting, and whether Hub
   rides inside GridMate replica chunks or beside them. Entry point is the handler
   vftables in §19.6. Also OI-P6-1 (which `FragmentUpdateMsg`) and **OI-P6-2 (which
   registration revision the client sends — the most S1a-actionable item on the
   board)**. Static, no deadline.
5. **P0c** — decode `PublishedData` (FIND-3). Cheap, no capture, server→client state.
6. **S0** — redirection feasibility. ~~**Unblocks once P0b lands.**~~ **UNBLOCKED.**
   Requirements in **STATE §16.13**, revised from §16.6. Proxy the queue endpoint, not
   a DNS name; rewrite `Token.RepAddress`; **answer the poll loop, not one exchange**;
   scope Wine certificate trust first. **Partly perishable** — see the deadline note.
7. **S1a** — the DTLS server. **The inversion:** the client handshakes with us, we
   hold the keys, its messages arrive as plaintext on our socket. Reference-testable
   now, no deadline. **P0b sharpened its input:** the `Token` object is the world
   credential and must arrive in the first epoch-1 Carrier message (STATE §16.13).
8. **H1** — reference-build hook and signature scan. **H4** — reflection-reader
   decision gate. Both static, independent, no deadline.
9. **H3** — last resort only.

~~**Start with S0a.**~~ **Superseded 2026-08-31 — S0a is done (NO, confirmed by trace;
STATE §16.15).** ~~**Start with P0b.** It is short, it is on the critical path, and
it is the one remaining chunk whose input disappears on a fixed date. Everything else
here still works in February 2027; P0b does not.~~ ~~**Superseded — P0b is done.** S0a
is now the cheapest thing on the board that changes a downstream decision: it is
static, needs no client and no network, and it determines whether S0's proxy design
survives contact. Running it first may save S0 an entire wasted iteration, and it
warms H2's instrument either way.~~ ~~**Next is H2** (static Ghidra, now warm from S0a —
scope it ambitiously) **or S0** (design the field-rewrite proxy on the small branch,
carrying OPEN-3R). Both file-based, no deadline.~~ **Superseded 2026-09-04 — H2 and
P2 are both done (STATE §17, §17.9).** ~~**Next is P5** (read the fork's `ReplicaChunk`
marshalers — the Track P front now that protobuf is ruled out, and the cheapest
unexplored source of protocol structure on the board) **or S0** (design the
field-rewrite proxy) **or P0c** (decode `PublishedData`, FIND-3 — still the cheapest
server→client state we can already read). **OI-P2-2 is cheaper than any of them and
could force another correction**: diff the 10 Javelin type names against `p0_cold`'s
routes; if they match, §17.5's "world message layer" framing is wrong too and the
inbound Javelin schema was already in P0's captures.~~ **Superseded 2026-09-05 — P6 is done (STATE §19); the vocabulary is recovered and OI-P5-1/OI-P5-4 are answered.** **Next is P7** (frame the fragment message — Step 4, which P6 did not reach: the serializer, whether the 16-byte UUID or a negotiated index goes on the wire, and **which `RegistrationRequest` revision b22469132 sends**, which is what S1a needs first). Entry point: the handler vftables in §19.6. **OI-P2-2 remains the cheapest item on the board** and could still
force another §13 correction. **S0** and **P0c** are unchanged and unblocked. **S0 has no perishable thread left** — OPEN-3 was closed
statically, so S0 needs no live-backend confirmation to commit to its design.

**What this order does not yield** is the server→client direction in captured form.
Items 1–7 give the client's outbound messages plus whatever comes out of the binary;
the inbound half is what S-track must construct regardless, ~~with H2 and FIND-2 as
the substitute for observing it.~~ **CORRECTED 2026-09-04: FIND-2 is not a substitute
for anything — it closed negative (STATE §17.9). The substitutes that remain are H2's
dispatch map (§17), the GridMate fork source for the replica model (P5), and P0's
already-decrypted auth traffic for the Javelin JSON responses (OI-P2-2).** The
server→client half is now the project's largest single unknown, and none of the
routes to it are perishable.

**D1 can start whenever**; it has a free head start from the `pins/22469132/Bin64.sha256`
baseline (STATE §5), and it earns its keep the moment any offset is hardcoded.

**Open items now live in `STATE.md`'s register, per CHARTER §6.6** — including the
H3 gate, the `decode_carrier.py` ChangeCipherSpec gap, and the unused auth-phase
decryption. Do not track them here; this file routes chunks, it does not hold state.

> **Correction, 2026-08-30.** A paragraph here previously described `SSLKEYLOGFILE`
> as an unexploited opportunity that "no chunk owns." That was wrong and it was
> written by a session reasoning from its own inference rather than from a document
> — the exact failure CHARTER §6.3 now names. The keylog was a scoped T3 recon item;
> it ran on 2026-08-29, produced a split result (auth decrypts, world stream does
> not), received its falsification check, and is recorded in STATE §12A, test #41,
> and a §13 correction row. What is genuinely open is narrower: **nobody has decoded
> the auth flow's contents.** That is now an entry in the STATE register, not a note
> here.

---

## Shared preamble

Every prompt below assumes this, and every prompt written later must include it:

> You have been given `CHARTER.md` and `STATE.md`. Work **only** the chunk below.
> If you find something that belongs to another chunk, record it in FINDINGS under
> "Noticed, out of scope" and do not act on it.
>
> Do not rewrite `CHARTER.md`. Do not delete anything from `STATE.md`.
>
> Charter §3 rules out anti-cheat work absolutely. If a line of inquiry only pays
> off against an integrity or attestation system, stop and record it as
> off-charter in FINDINGS — do not pursue it.
>
> Before doing anything on the retail client: prove the technique on the reference
> build first, state the check that would prove your result wrong, and run it.
>
> **The owner runs every command.** Give exact commands with real paths. Note the
> exact client build under test in every capture — offsets and possibly the
> protocol move between builds.
>
> **Keep the loop tight.** Predict → run **one** command → read the exact error →
> fix → re-probe. Do not reason from memory across several turns without asking
> for something to be run. This is what took T4 from "provision an isolated
> toolchain" to "two flags and a five-line patch" in about twenty minutes.

### Standing environment notes

Filled 2026-08-29. Full detail in STATE §5; this is the working subset.

- **Client build under test:** New World: Aeternum, Steam appid **1063730**,
  **buildid 22469132**, `LastUpdated` 2026-08-27. Installed at
  `/home/kaatlev/.local/share/Steam/steamapps/common/New World`
  (`~/.steam/steam/steamapps/...` is a symlink to the same place).
  **Pinned** at `~/Documents/nwly-pin/22469132/` — depot manifests plus a byte
  copy of `Bin64/` with a 22-file sha256 baseline.
- **Client runs under Proton** (`steamapps/compatdata/1063730`). The retail client
  is a PE process under Wine on this host. Neutral for packet capture; a real
  complication for Frida in H1/H3.
- **Reference-build tree:** `~/Documents/lumberyard`, branch `master`. GridMate at
  `dev/Code/Framework/GridMate/`, AzCore at `dev/Code/Framework/AzCore/`.
  **The tree is patched** — `RTTI/TypeInfo.h` reads `false_v<>` where Amazon's
  original reads `false_v<T>`, committed. The pin `413ecaf24d7a...` therefore does
  **not** describe the tree that builds. See STATE §13.
- **Build recipe:** `clang++ -std=c++17 -include utility -fdelayed-template-parsing -w`
  with `-I AzCore -I AzCore/Platform/Linux`, run from `dev/Code/Framework`. GridMate
  adds `-I GridMate -I GridMate/Platform/Linux -DDTLS1_RT_HEARTBEAT=24`.
  Scripts: `build_gridmate.sh` (build), `triage.sh` (bulk compile triage),
  `CMakeLists.txt` (CLion/clangd path).
- **Capture interface:** `enp2s0`, host `192.168.1.33`, gateway `192.168.1.1`.
  Not `-i any` — that yields Linux-cooked (SLL) framing and breaks link-layer
  parity with the T4 loopback captures.
- **Ghidra project:** not yet created. Run the PE RTTI analyzer on first import —
  RTTI survived in `NewWorld.exe` (STATE §10), so it recovers the `ReplicaChunk`
  class tree cheaply. This is H2's starting point.
- **Frida vs compiled hook:** Frida for all exploration (reload JS without
  restarting). Move to a MinHook/Detours DLL writing to a named pipe only once the
  hook target is known and stable. **Note:** retail runs under Proton, so H1/H3
  must solve attaching to a PE process inside Wine.
- **Never parse in the hook.** Log raw bytes + timestamp + direction + conn-id to a
  binary file; parse offline. You will re-parse the same capture many times.
- **Shell gotchas:** fish. `fd` is not installed — use `find`. `grep -c` exits 1 on
  a zero count, so a successful "absent" check looks like an error. fish aborts a
  failed glob before evaluating the `or`, so use `find` for existence checks.

---

# Track T prompts

## T1 — Engine fingerprint (static) ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §10. Do not re-run.**
> Verdict: **GridMate**, decisively — `TransportLayerGridMate` is New World's own
> wrapper class, so GridMate is the live network layer. 43 GridMate-family hits.
> O3DE `AzNetworking` absent; the single O3DE-looking hit was the gameplay struct
> `TransformLinkConnectionData`, exactly the generic-name trap this prompt warned
> about. Crypto fell out of the same scan (most of T2). Protobuf present in
> `NewWorld.exe` — flagged for P2. RTTI survived.
> Prompt kept below as historical record.

**Deliverable is a document**, not code and not a hook.

**Why this is first.** Everything downstream assumes an engine. GridMate means a
`Carrier`/`ReplicaManager`/DTLS shape; O3DE `AzNetworking` means a different one;
a full rewrite means neither, and the reference-build strategy narrows to "shared
AZ DNA only." The wrong assumption here wastes every later chunk.

**Scope.** Static analysis of the client executable and its DLLs in Ghidra.
String-search for the three fingerprint families and report which is present:

- **GridMate:** `GridMate`, `Carrier`, `CarrierThread`, `SocketDriver`,
  `SecureSocketDriver`, `ReplicaMgr`, `ReplicaChunk`, `ReplicaChunkDescriptor`,
  `DataSet`, `Marshaler`, `DefaultHandshake`, `DefaultTrafficControl`,
  `GridSession`.
- **O3DE-era (GridMate replaced):** `AzNetworking`, `NetworkEntity`,
  `NetBindComponent`, `IConnectionListener`, `MultiplayerComponent`,
  `NetworkInput`, `ConnectionData`.
- **AZ baseline (how much LY DNA survives):** `AZ::`, `AzCore`, `AzFramework`,
  `SerializeContext`, `BehaviorContext`, `ComponentApplication`, `AZ_CRC`, `EBus`.
- **Third-party netcode / serialization:** `enet`, `RakNet`, `yojimbo`,
  `google::protobuf`, `flatbuffers`, `msgpack`.

**Method.**
- Run the Windows PE RTTI analyzer first. If RTTI survived, search mangled names
  `.?AV...@GridMate@@` — a single hit like `.?AVCarrier@GridMate@@` closes this
  chunk on its own.
- Check the import table: `sendto`/`recvfrom`/`WSASendTo` → UDP datagram design
  (GridMate shape); `send`/`recv` only → TCP stream (not GridMate's SocketDriver).
- If `google::protobuf` appears, note it loudly — the embedded `FileDescriptorProto`
  blobs may hand over the entire message schema (P2 becomes far cheaper). Do not
  extract them here; just flag it.

**Definition of done.** A document naming the engine family with the specific
strings/RTTI symbols that prove it, the transport shape from the import table, and
a flag on whether protobuf/flatbuffers descriptors are present.

**Falsification.** Predict GridMate before searching (the 2016 LY origin says so),
and say what a rewrite would look like instead — absence of every GridMate string
*and* presence of the O3DE set. "Some AZ strings present" does not prove GridMate;
those survive a rewrite.

**Non-goals.** No hooking. No dynamic analysis. No touching the crypto layer yet.

---

## T2 — Crypto-library fingerprint ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §10. Do not re-run.**
> Verdict: **OpenSSL 1.1.1k (25 Mar 2021), statically linked.** Plaintext boundary
> is `SSL_read` / `SSL_write`; `dtls1_` and `DTLSv1` confirm DTLS. Static linkage
> is the harder of the two outcomes: **no DLL proxying is possible**, so the
> H-track must use an inline hook located by signature and patched in memory.
> The linkage claim now rests on a positive 22-file `Bin64/` inventory, not on an
> empty `find` (STATE §10, test #29).
> Prompt kept below as historical record.

**Deliverable is a document.** Where is the plaintext boundary, and what function
sits on it?

**Why.** Charter §4: hook above the crypto, never at the socket. This chunk finds
the hook target. GridMate's `SecureSocketDriver` wraps datagrams in OpenSSL DTLS;
a rewrite may use mbedTLS or Windows CNG instead.

**Scope.** In Ghidra, look for:
- **OpenSSL:** strings `"SSL routines"`, `"OpenSSL"`, `EVP_DecryptUpdate`,
  `SSL_read`, `SSL_write`, `DTLSv1`, `dtls1_`.
- **mbedTLS:** `mbedtls_ssl_read`, `mbedtls_ssl_write`, mbedTLS version strings.
- **Windows CNG:** imports of `bcrypt.dll` / `ncrypt.dll` (`BCryptDecrypt`,
  `BCryptEncrypt`) — attractive because these are system DLLs, always dynamically
  linked, hookable even when everything else is static.
- Determine **static vs dynamic linking** for whichever it is. A real `libssl`/
  `libcrypto` DLL in the install → DLL proxying is possible (H-track). Statically
  linked into the main exe → inline hook by signature only.

**Definition of done.** The crypto library named, the specific plaintext-boundary
function identified (`SSL_read`/`SSL_write` or equivalent), and static-vs-dynamic
linkage stated for it.

**Falsification.** If no known crypto library's fingerprint is present, that is a
finding, not a dead end — say so and note whether the T3 entropy profile shows
encryption at all. A low-entropy stream would mean there is no crypto layer to
hook above, which changes the whole H-track.

**Non-goals.** No hooking yet. Do not locate anti-cheat crypto — charter §3.

---

## T3 — Transport recon (retail capture, no hooks) ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §12A. Do not re-run.**
> Verdict: the world connection is **UDP/DTLS 1.2 via `SecureSocketDriver`**, not
> `StreamSecureSocketDriver`/TCP-TLS — settling the STATE §7 question. Flow
> `192.168.1.33:27001 ↔ 52.223.16.88:54888` (AWS). Predictions 1–4 all confirmed;
> **prediction 4 held**, the retail ClientHello offers exactly one real suite
> `0xC030` plus `0x00FF` (SCSV, not a cipher). `decode_carrier.py` handled retail
> **unmodified** (test #40 — the predicted loopback/offset break did not occur).
> Epoch-0 handshake saved as `t3_handshake_epoch0.pcap`, which became T5's retail
> input. **Two claims below are marked SUPERSEDED inline** — both were corrected by
> T5, and both are in STATE §13. Prompt kept as historical record.

> **The full ready-to-run prompt is `T3_PROMPT.md`. Paste that file, not this
> summary.** What follows is the scope in brief, plus the reasons this chunk is
> narrower than it was originally written.

**Deliverable: the retail transport profile, and the retail epoch-0 handshake as
its own artefact.** That artefact is T5's input.

**Scope is smaller than the original T3 text.** The original assumed recon from
zero — entropy profiling, "is there crypto at all." That predates STATE §9 and
`decode_carrier.py`, which already recognises both Carrier framing and DTLS
records. So the primary analysis is **point the existing instrument at retail
traffic**; entropy profiling is the fallback if it does not parse.

**It also settles a STATE §7 question:** GridMate ships two secure drivers —
`SecureSocketDriver` (UDP/DTLS) and `StreamSecureSocketDriver` (TCP/TLS). Which
one carries the persistent world connection decides the shape of every P-track
chunk, and a capture answers it with no hooks.

**Predictions to record before capturing (CHARTER §4):**

1. Game stream is **UDP**; auth and server-list are a separate TCP/443 phase.
2. UDP payloads parse as **DTLS 1.2 records**, `decode_carrier.py` unmodified.
3. ~~Opening exchange is ClientHello (`fe fd`) → HelloVerifyRequest (`fe ff`) →
   ClientHello with cookie echoed. **The 1.0 HVR is correct**, RFC 6347 §4.2.1 —
   not a downgrade, do not chase it.~~
   **CONFIRMED but INCOMPLETE in two ways — SUPERSEDED by T5, STATE §13.**
   (a) The RFC explanation is permitted but is not the actual cause: GridMate
   **hardcodes** `RecordHeader::m_version = DTLS1_VERSION` (`0xFEFF`) in its
   hand-packed records (`SecureSocketDriver.cpp:308`, `:312`, `:343`). That moves
   `fe ff` out of the "library/RFC default" bucket and into the **GridMate-controlled**
   bucket, where it matches retail exactly. Diagnostic value: **every `fe ff` record
   in a capture is a GridMate hand-pack**, and there are exactly two per handshake
   (HelloVerifyRequest, HelloRequest). The advice not to chase it still stands.
   (b) The exchange does not stop there. The real sequence, identical on retail and
   reference, is `CH(seq0, no cookie) → HVR(seq0) → CH(seq1, cookie=20) →
   HelloRequest(seq0) → CH(seq0, no cookie) → ServerHello…`. **Three ClientHellos,
   not two**, and the handshake OpenSSL actually completes carries **no cookie at
   all**.
4. **The retail ClientHello advertises exactly one cipher suite, `0xC030`**
   (`ECDHE-RSA-AES256-GCM-SHA384`), because GridMate hardcodes it at
   `SecureSocketDriver.cpp:1494`.

**Prediction 4 is the load-bearing one.** A single-suite ClientHello matching the
reference is close to conclusive for a stock-ish GridMate transport, and it is
readable at epoch 0 without a hook. A normal multi-suite list means Amazon
replaced the `SSL_CTX` setup, and T5's verdict needs qualifying even though T1
said GridMate.

**Two procedural details that decide whether the chunk succeeds:**

- **Start the capture before the client connects.** Test #21 only caught the
  cookie exchange because of this. A mid-session capture is all epoch ≥ 1
  ciphertext and useless for T5.
- **Disable voice chat in the client first.** `vivoxsdk.dll` (STATE §10) opens its
  own UDP media flow that resembles a game stream and parses as neither DTLS nor
  Carrier. Eliminate it at the source rather than filtering it later.

**Expect three or four UDP conversations, not one:** the game stream, Vivox (if not
disabled), EOSSDK/EAC, and Steam background traffic. Attribute them with
`ss -tunp` during the session rather than guessing from traffic shape.

**Definition of done.** Transport named (UDP vs TCP) with ports and endpoints;
auth phase separated from the game stream; predictions 1–4 each confirmed or
falsified with command output as evidence; the epoch-0 handshake saved as its own
pcap; size/timing profile for a stand-still window and a walking window; and
whether `decode_carrier.py` handled retail unmodified.

**Non-goals.** No hooks, no injection, no Frida. No decryption attempts — epoch ≥ 1
is ciphertext and there is nothing there without session keys (STATE §9). No
message-body decoding (P-track). **EAC/EOSSDK traffic will be in the capture** —
identify its endpoints so they can be excluded, record nothing further about it.
Charter §3. Do not modify traffic.

---

## T4 — Build the reference `Carrier` from the fork ✅ DONE 2026-08-29

> **COMPLETE. Findings in STATE §7, §8, §9. Do not re-run.**
> Both plaintext and DTLS sessions pass, are captured, and are decoded. 168/202
> AzCore TUs, 41/41 GridMate TUs. Reproducible from a wiped `build/` (test #20).
> **Three claims in the prompt below turned out wrong and are marked SUPERSEDED
> inline — read those before reusing any of this.** Prompt kept as historical
> record and because the Path A/B reasoning is still the right shape for a rebuild.

**Deliverable:** two GridMate `Carrier`s connecting locally in a process we
control, captured both plaintext and DTLS-secured. This is the reference
instrument the whole project leans on (CHARTER §2).

### What is already known from the tree (do not re-derive — see STATE §7)

- **Dependency surface is clean.** GridMate includes only `<AzCore/...>` and the
  standard library — nothing from other frameworks. The carve-out is: compile
  **AzCore** + **GridMate**, ignore the rest of the tree. *(Confirmed by build —
  every AzCore failure was a missing 3rdParty header, none on GridMate's surface.)*
- ~~**C++ standard is C++14** (`-std=c++1y` in `compile_settings_clang.py`).~~
  **SUPERSEDED — STATE §13.** The source needs **C++17**. `Math/Crc.inl:114` uses
  an `auto` template parameter and `-std=c++14` is a hard error with no rescuing
  flag. The Waf setting is what the 2019 clang was told, not what the code needs.
- ~~**No hard clang version gate.** Try system clang 22 with `-std=c++14 -Wno-error`.
  Provision `/opt/llvm14` ONLY on real compile errors from removed C++14-era
  features.~~ **PARTLY SUPERSEDED.** The no-gate observation holds and
  `/opt/llvm14` was correctly rejected — but the working invocation is
  **`-std=c++17 -include utility -fdelayed-template-parsing -w`**, verified on
  clang 18 and clang 22. Do not disturb the system clang PZMapMaker uses.
- **Crypto is OpenSSL DTLS, confirmed in source.** `SecureSocketDriver.cpp`
  includes `<openssl/ssl.h>` etc. and uses `DTLS1_VERSION`, `DTLS1_RT_HEADER_LENGTH`
  (13), `DTLS1_HM_HEADER_LENGTH` (12), `SSL3_MT_CLIENT_HELLO`. Link `libssl` +
  `libcrypto`. The `RecordHeader` / `HandshakeHeader` structs in that file are the
  DTLS wire framing and become T5's reference layout — read them, do not reverse
  them. **Add `-DDTLS1_RT_HEARTBEAT=24`** — the constant was removed from OpenSSL 3
  after Heartbleed and `SecureSocketDriver.cpp:416` still uses it (STATE §7, §13).
- **Platform-header include paths** (the thing bypassing Waf usually breaks) are
  known. Waf prepends the `Platform/<OS>/` dir to the include search path. For
  Linux, add these `-I` dirs (fork at `/home/kaatlev/Documents/lumberyard`):
  - `dev/Code/Framework/AzCore/Platform/Linux`
  - `dev/Code/Framework/GridMate/Tests/Platform/Linux` (only if using the harness)
  - **`Platform/Common/` must exist in the checkout** — a sparse checkout that
    omits it fails with a confusing error pointing at the *Linux* header instead.
- **Test certs exist:** `dev/Code/Framework/GridMate/Tests/Certificates.cpp` defines
  `g_untrustedCertPEM` / `g_untrustedPrivateKeyPEM`. Compile that file to resolve the
  `extern`s DTLS needs.
- ~~**The secure test path was likely never run on Linux.** You must define
  `-DAZ_TRAIT_GRIDMATE_TEST_WITH_SECURE_SOCKET_DRIVER=1` and should EXPECT to shake
  out Linux-specific bugs on the DTLS path.~~ **SUPERSEDED — STATE §13, test #17.**
  The trait does need defining, but **DTLS passed on the first run**, on both clang
  majors, identical to plaintext. Zero Linux-path bugs. The trait gates the *test
  harness*, not the driver, and the driver sits on `SocketDriverCommon` which the
  plaintext path exercises constantly. *Untested is not broken* — do not budget
  time against this.
- **The fork tree is patched.** `RTTI/TypeInfo.h` reads `false_v<>`, committed.
  A rebuild from bare `413ecaf` is **not** what was tested. STATE §13.

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

1. **Toolchain probe.** Compile one AzCore `.cpp` (a Math or Memory unit) with the
   recipe above. *(Result: clean on clang 18 and 22. `/opt/llvm14` not needed.)*
2. **AzCore static lib.** Compile the AzCore subset GridMate names into
   `libazcore.a`. Link pthreads. *(Result: 168/202, `libazcore.a` 31M. Use
   `triage.sh` to group failures by error kind rather than investigating each.)*
3. **GridMate static lib.** Compile GridMate against the AzCore headers into
   `libgridmate.a`. *(Result: 41/41, `libgridmate.a` 4.9M.)*
4. **Plaintext Carrier test (the milestone).** Path B `main()`, plain
   `SocketDriver`, two Carriers on localhost, exchange a message, capture the wire.
   **Two runtime traps live here, neither a compile error, both segfault a binary
   that links fine:** `OSAllocator` must be created before `SystemAllocator`, and
   EBus handlers must be destroyed before `GridMateDestroy`. STATE §7.
5. **DTLS Carrier test.** Define the secure trait, swap in `SecureSocketDriver`
   with `Certificates.cpp`, link OpenSSL. **Then search the capture for the literal
   payload string** — "PASS" only proves a session was established, not that
   anything was encrypted. STATE §9.

### Definition of done

A reproducible local GridMate session; a captured plaintext handshake; the
`Carrier` packet header layout read out of `Carrier.cpp`/`Carrier.h` and confirmed
against the plaintext capture; and the DTLS path either working or its Linux
failure characterised exactly.

### Falsification

The header you read from `Carrier.h` must match the bytes on the wire in the
plaintext capture. Predict the first few header bytes before capturing. If they
don't match, either the build config differs from what you read or the fork
diverged — resolve that before T5 relies on this layout.

### Non-goals

Not the retail client. Do not tune anything to match retail — this is the
*known-good*, established on its own terms. No hooking yet (that's H1).

### FINDINGS to record

Fork commit under test; whether clang 22 sufficed or `/opt/llvm14` was needed; the
exact `-I` and `-l` flags that produced a working build; the Carrier header layout;
and the state of the DTLS-on-Linux path. Fold into STATE §5 and §7.

---

## T5 — Reference vs retail handshake diff ✅ DONE 2026-08-29 — THE MILESTONE

> **COMPLETE. Findings in STATE §12B. Do not re-run.**
> **The full ready-to-run prompt is `T5_PROMPT.md`** — richer than this summary,
> and it is the one that was actually executed.
> **Verdict: retail transport is structurally stock GridMate `SecureSocketDriver`
> with zero catalogued exceptions.** Every handshake difference between retail
> (buildid 22469132) and the reference (`7d4f1ee6`) is OpenSSL 1.1.1k-vs-3.6.4
> noise in fields `SecureSocketDriver.cpp` does not set. **Mutual auth is stock
> GridMate, not Amazon-added**, and rests on an inverted branch at `:1525` that
> *assigns* `SSL_VERIFY_FAIL_IF_NO_PEER_CERT` instead of OR-ing it. **The reference
> build is a valid instrument for retail's transport**, epoch 0 only. P1–P4 all
> confirmed. Offline throughout: two pcaps and one source file, no client launch,
> no hooks, no decryption — CHARTER §3 satisfied.
> **Outcome 1 of the three in "Definition of done" below is the one obtained.**
> Strongest single result: a **byte-identical 25-byte HelloRequest** across retail
> and reference, a GridMate hand-pack that no OpenSSL version difference could
> produce. Four beliefs were overturned and are in STATE §13. Prompt kept as
> historical record.

**This is the chunk that answers the charter's core question.** Depends on T1
(done), ~~**T3** (the retail capture — not yet run)~~ **T3 (done 2026-08-29 —
`t3_handshake_epoch0.pcap` was the retail input)**, and T4 (done).

**Both inputs are specific artefacts, not vibes:**

- **Reference:** the epoch-0 handshake from T4's `--secure` capture, documented in
  STATE §9 — ClientHello (`fe fd`) / HelloVerifyRequest (`fe ff`) / ClientHello
  with a 20-byte cookie echoed.
- **Retail:** the epoch-0 pcap T3 saves as its own artefact.

**Scope.** Diff structurally: does the retail client's pre-encryption handshake
line up with GridMate's `DefaultHandshake` + `Carrier` header — same fields in the
same order, even if magic values or field widths differ?

**Filter the `'G'` wakeup byte first.** A 1-byte `0x47` datagram addressed to the
socket's own port is `AZ_SOCKET_WAKEUP_MSG_VALUE`, not protocol, and roughly a
third of reference loopback frames are these (STATE §8). Diffing without filtering
them invents a phantom message type.

**T3's cipher-suite result largely pre-answers this.** If T3 found a single-suite
ClientHello offering `0xC030`, the structural match is close to established before
the diff starts, and T5 becomes confirmation plus field-level documentation.

**Definition of done.** One of:
- **Structural match** → the client is GridMate or a close fork; the `Carrier`
  header layout is now the retail protocol's header layout, documented for free.
  **← THIS IS THE OUTCOME OBTAINED, 2026-08-29. STATE §12B.**
- **No match, O3DE strings present** → an `AzNetworking` rewrite. *Note: T1 already
  ruled this out, so this outcome would mean T1 was wrong — investigate the
  contradiction rather than accepting it.* **Did not occur.**
- **No match, neither** → a bespoke protocol; the reference build degrades to "AZ
  reflection may still help" and P-track is fully empirical. **Did not occur.**

**Caveat on the match, carried forward (STATE §12B).** It is proven for **epoch 0**,
the cleartext handshake. Epoch ≥ 1 Carrier framing inside DTLS is proven on the
reference and **inferred** for retail; H3's plaintext is what promotes it. Content
(certificate sizes 958 vs 1380, cookie values, randoms) is per-deployment and
per-connection — do not treat any observed value as constant. Fragmentation
differences between the two captures are PMTU-dependent, not protocol-dependent.

**Falsification.** T1 said GridMate, which predicts a structural match. **If the
handshakes don't line up at all, one of T1 or T5 is wrong — find out which before
building on either.** Do not quietly prefer the newer result.

**Non-goals.** No decoding of message *bodies* yet — that's P-track. Handshake
framing only.

---

# Track H prompts

## H1 — Frida crypto hook on the reference build

Depends on T2 (target function, done) and T4 (a build we control, done). **Prove
the hook on the reference build before H3 points it at retail.**

**Scope.** `Interceptor.attach` on `SSL_read`/`SSL_write` in the reference
`Carrier` process. Log the plaintext buffer, direction, timestamp, and connection
id to a binary file. Confirm the logged plaintext matches the
`SecureSocketDriver`-disabled capture from T4.

**Two environment facts that shape this chunk:**

- The reference build is a **native Linux binary** with full symbols — Frida
  attaches trivially. Retail (H3) is a **PE process under Proton/Wine**, which is
  a different and harder problem. Solve it in H3, not here, but know it is coming.
- Retail's OpenSSL is **statically linked** (STATE §10), so H3 will need a
  signature scan rather than a symbol lookup. ~~Consider proving the
  signature-scanning approach here too, where a known-good answer exists to check
  it against.~~ **AMENDED 2026-08-30 — this is now a requirement, not a
  suggestion.** Two things changed it. First, T5 established that the reference is
  a valid instrument for retail's transport (STATE §12B), so a technique proven
  here can be trusted to transfer — which is the whole reason to prove it here.
  Second, and more practically: **H1 is the last chunk in which a free oracle
  exists.** The reference binary has full symbols, so `Module.findExportByName`
  gives the known-good address that the signature scan must independently
  reproduce. In H3 there is no symbol to check the scan against, so a scan that is
  subtly wrong there is indistinguishable from "the client didn't send it" —
  CHARTER §4's instrument-cap rule, in the specific. Build the scanner here, or
  build it blind later.

**Definition of done.** A Frida script that captures the full bidirectional
plaintext stream from the reference build, verified against the known plaintext.
This script is the template H3 adapts for retail. **Plus (added 2026-08-30): a
signature scan that locates `SSL_read`/`SSL_write` in the reference binary and is
verified to land on the same addresses the symbol table gives.**

**Falsification.** The plaintext you log with `SecureSocketDriver` enabled must
match the cleartext capture with it disabled. If it doesn't, the hook is on the
wrong function or after the wrong transform.

**Non-goals.** Do not parse in the hook (charter §4). Do not touch retail.

---

## H2 — Locate the dispatch point in retail (static)

Depends on T1 (done). ~~T5 is needed only for the falsification check at the end —
**this chunk can start now**, and is the fallback if T3 is blocked.~~
**AMENDED 2026-08-30 — T5 is done (STATE §12B), so the falsification check below is
armed rather than deferred, and this chunk is no longer a fallback for anything.**
It is static, needs no login, no running client and no Proton, which now makes it
the natural first H-track chunk rather than a contingency. **Static only** — no
execution, no login, no running client.

**Scope.** In Ghidra, work forward from `recvfrom`/`WSARecvFrom`: xref the call
site (the `SocketDriver::Receive` equivalent), follow the output buffer through
decrypt → header parse → reliability/reassembly → **dispatch**. The dispatch
function is the target: either a large `switch` on a message-type id or an indexed
jump through a function-pointer table. That table is the message-handler map.

**Start with the RTTI analyzer.** RTTI survived in `NewWorld.exe` (STATE §10) —
mangled-name fragments like `UEAAXPEAVReplicaChunkBase` are present. Ghidra's PE
RTTI analyzer recovers the `ReplicaChunk` class tree, which is a far cheaper entry
point than following xrefs blind.

**Two modules to know about before following xrefs** (STATE §10): `vivoxsdk.dll`
has its own network stack, and `libcds-amd64-vcv141.dll` is unidentified. Neither
is the game transport.

**Definition of done.** The dispatch function's address (as a signature, not a raw
offset — charter §4), and, if it's a table, the table extracted as a list of
(type-id → handler-address) pairs. Each entry is a message type that exists.

**Falsification.** ~~If GridMate (T1 says so, T5 will confirm), the path should pass
through `Carrier::Receive` and a `ReplicaManager` receive entry. If the xref chain
doesn't resemble that, revisit whether T1's verdict was right — do not just accept
the mismatch.~~
**AMENDED 2026-08-30 — T5 confirmed it.** The path should pass through
`Carrier::Receive` and a `ReplicaManager` receive entry. **The "maybe T1 was wrong"
branch is closed:** T1 said GridMate from strings and RTTI, and T5 then proved the
transport is stock GridMate `SecureSocketDriver` on the wire, byte-for-byte against
a build we control (STATE §12B). Two independent methods agree. So an xref chain
that does not resemble that shape means **the static analysis is wrong** — wrong
`recvfrom` call site, wrong module, or the chain lost in a thunk — not that the
engine verdict is in doubt. Do not accept the mismatch, and do not reopen T1 to
explain it.

**Non-goals.** No hooking. No decoding handler bodies — P2 does that with captures.
Nothing touching EAC, which lives in `<install>/EasyAntiCheat/` (charter §3).

---

## H3 — Crypto/dispatch hook on retail ⏸ LAST RESORT

> **DEPRIORITISED 2026-08-30 by owner decision (GATE-1, STATE §3 §15). Not blocked
> — deliberately ordered last.** Do not run this until H2, P2/FIND-2, P0, S0, S1a,
> H1 and H4 are exhausted. Two reasons, neither being that H3 is off-charter:
> **(a)** injection into an EAC-protected process is a well-known ban trigger
> regardless of intent, and the account is load-bearing for auth captures, world
> captures and any handshake testing; **(b)** operating directly in front of a
> detection system watching for exactly this is poor practice even where permitted.
>
> **The bound, if it is ever attempted:** one attempt, plainly made. **EAC
> preventing the hook is a TERMINAL RESULT** — record it and stop. Any step whose
> purpose is to make the hook survive detection is circumvention, off-charter under
> CHARTER §3, and does not get pursued, recorded, or built on. No second attempt
> with a different technique.
>
> **What replaces it:** S1a inverts the problem — the client handshakes with a
> server we run, we hold the session keys, and its messages arrive as plaintext on
> our socket with no hook at all. That covers the client→server half; H2 and FIND-2
> cover structure. H3's unique remaining value is the **server→client** direction
> observed live, which is the only reason it survives at all.

**Blocked on H1 and H2.** Do not start until both land.

When unblocked: adapt the H1 Frida script to the retail client, attaching at the
T2 crypto boundary and/or the H2 dispatch function. **Signature-scan for the
target; never hardcode the address** — retail's OpenSSL is statically linked, so
there is no symbol to look up (STATE §10). Mirror captures to a loopback UDP socket
so they can be piped into Wireshark with a growing Lua dissector.

**The Proton problem is this chunk's first real obstacle.** The retail client runs
as a PE process under Wine (STATE §5). Attaching Frida to that is materially
different from attaching to the native reference build, and it should be treated
as the opening question of the chunk rather than a detail.

**What T5 changed here, and what it did not (added 2026-08-30).** T5 changed one
thing: the reference build is now a *validated* model for retail's transport (STATE
§12B), so an H1 hook proven against it can be trusted to transfer, and the epoch-≥1
plaintext this chunk produces is expected to be §8 `Carrier` framing. T5 changed
**nothing** about the mechanics — retail's OpenSSL is still static, the target is
still a PE under Wine, and the hook must still be located by signature. Note also
that T5 removed one possible shortcut permanently: the keylog callback is absent
from the DTLS context because **stock GridMate never had one** (STATE §12B, §13),
not because Amazon stripped it. There is nothing to re-enable. This hook is the only
route to the world stream's plaintext.

**Before starting this chunk, settle the §3 question explicitly rather than in
passing.** H1 and H2 are clean — one targets a native binary we compile, the other
is static analysis of a file on disk. H3 is the first chunk that attaches to the
running retail client, and `<install>/EasyAntiCheat/` is loaded in that process.
CHARTER §3 rules out anti-cheat work absolutely and permanently, which means this
chunk cannot be allowed to drift into "and then work around what fights the hook."
Decide up front what H3 is permitted to be — and if the answer is that it cannot run
without engaging an integrity system, that is a finding to record, not an obstacle
to route around.

Expect the retail client to carry runtime protections the reference build does not
— note what fights the hook, but per charter §3 do not engage anything that is an
integrity/attestation system.

---

## H4 — The reflection reader (`SerializeContext`) — DECISION GATE

Depends on T1 (done). **Deliverable is a written decision, then a prototype only
if the decision is go.**

**Why this could collapse P-track.** The client holds a global
`ComponentApplication` with a `SerializeContext` (class names, field names, member
offsets for every reflected type) and GridMate holds a `ReplicaChunkDescriptorTable`
mapping wire CRCs → chunk descriptors. Compiled in-process against matching `AzCore`
headers from our fork, we may be able to walk that metadata and read structured,
named, typed objects instead of guessing byte offsets.

**The gate.** The blocker is header/ABI drift between our fork and the shipped
build — struct layouts must match closely enough to traverse. Decide, with
evidence, whether the ABI is close enough to attempt this. If not, say so and
P-track stays fully empirical.

**Evidence now available that this prompt predates:** T1 confirmed the retail
client carries `GridMateAllocatorMP` / `GridMateAllocator` and ~94
`InitializeReplicatedFields` references, and that RTTI survived (STATE §10). The
fork builds and runs (STATE §7). Both sides of the ABI comparison are therefore
inspectable — this decision can be made on evidence rather than guesswork.

**Definition of done.** A decision with the ABI evidence attached. If go, a
prototype that locates the global `ComponentApplication` on the reference build and
enumerates one reflected type by name.

**Falsification.** Prove it on the reference build first. If the walker can't
traverse `SerializeContext` on the build we compiled against, it will not traverse
the retail client's, and that kills the approach cleanly.

**Non-goals.** Not a client mod. Reading metadata to interpret captures, not
altering the client.

---

# Track P / Track S / Track D — stubs

Write the full prompt when the chunk comes up, using the shape above.

- **P1 Handshake sequence.** Byte-document the connect exchange from H3 captures,
  cross-referenced against T5's header layout. **Scope narrowed 2026-08-30: the
  epoch-0 DTLS half is already done.** STATE §12B documents that flight completely
  and identically on both sides — `CH(seq0, no cookie) → HVR(seq0) → CH(seq1,
  cookie=20) → HelloRequest(seq0) → CH(seq0, no cookie) → SH(0) Cert(1) SKE(2)
  CertReq(3) SHD(4) → Cert(1, empty) CKE(2) → [CCS] → NewSessionTicket(5)` — with a
  13-byte `RecordHeader` and 12-byte `HandshakeHeader`. What P1 still owes is the
  **GridMate `Carrier` handshake inside epoch 1** (`DefaultHandshake`, connection
  request/ack, and the `Carrier` header on real traffic), and that is what needs H3.
- **P2 Protobuf descriptor extraction. ✅ DONE 2026-09-04 — see `P2_PROMPT.md` and
  STATE §17.9. VERDICT: NEGATIVE.** The blobs are real and carry no game protocol:
  Campfire telemetry plus two stock well-known types. `descriptor.proto` is present
  only because `google::protobuf::Reflection` requires it — **that is the entire
  explanation for T1's flag**, and the flag rested on a single `GOOGLE_CHECK` assert
  string. ~~Turn H3's dispatch-table hits into a list of known message types with
  frequencies. **T1 found `google::protobuf::Reflection::` in `NewWorld.exe`
  itself** (not in EAC or Vivox — both scanned, both zero), so embedded
  `FileDescriptorProto` blobs may hand over the schema rather than requiring reverse
  engineering. This is where they get extracted. STATE §10.~~ **The message-type
  census this bullet described was performed by H2 instead (§17.5, 10 types by
  RTTI), and the H3 dependency was stale twice over.** Instrument kept:
  `p2_scan.py` — scans for the `FileDescriptorProto` artefact rather than a
  registration function, so it is protobuf-version-independent; validated against
  synthetic, 171 MB positive and 40 MB negative controls before use (test #63).
- **P3 Position/movement message.** The controlled-walk experiment (walk a straight
  line at constant speed; the smoothly-varying float triple or quantized int is the
  position). GridMate's transform marshalers quantize — see `CompressionMarshal.h`
  / `MathMarshal.h` in the fork for the exact scheme. **T3 collects a stand-still
  and a walking window**, so the timing/size delta is a free head start.
- **P4 Initial world-state sync.** The login state dump is the biggest, most
  informative single message — capture it with a log-out/log-in cycle.
- **P5 Replica/chunk model. ← THE TRACK P FRONT, promoted 2026-09-04 by P2's
  negative result (STATE §17.9).** Map `ReplicaChunk` types (identified on the wire
  by `AZ::Crc32` of the chunk name) to their marshalers. ~~to the descriptor table
  dumped via H4~~ — **H4 is no longer a gate.** With protobuf ruled out, this is the
  world stream's actual encoding, and **the source is in the fork at `7d4f1ee6`**:
  `Marshaler` / `DataSetBase` / `CompressionMarshal.h` / `MathMarshal.h` under
  `dev/Code/Framework/GridMate/`. Read the source first (CHARTER §4, *prefer the
  source to the sample*), then confirm against the retail binary's 23 `ReplicaChunk`
  and 94 `InitializeReplicatedFields` references (STATE §10, §17.9). **No capture, no
  client, no hook, no deadline** — the strongest position the project has had on the
  inbound half. ~~Note P3 depends on this: GridMate's transform marshalers
  **quantize**, so a raw float triple is the wrong thing to look for.~~
  **CORRECTED 2026-09-04 (STATE §13, §18.4): the default `Marshaler<AZ::Vector3>`
  writes three RAW IEEE floats (12 bytes) and `Marshaler<AZ::Transform>` 48 bytes
  uncompressed. Quantization is opt-in per DataSet. P3 should look for a raw float
  triple after all.** ~~confirm against the retail binary's 23 `ReplicaChunk` and 94
  `InitializeReplicatedFields` references~~ — **the 94 are Hub symbols, not
  GridMate's; that cross-check was invalid (STATE §13).** **DONE 2026-09-04 — see
  STATE §18 and the P6 stub below.** **Noticed during D2:**
  `object-stream-converter` and `asset-catalog-parser` in the new-world-tools kit
  would likely say a lot about the replicated-object model. Recorded, not acted on.
  STATE §11.

- ~~**P6 Hub message layer. ← THE TRACK P FRONT, opened 2026-09-04 by P5.**~~
  **DONE (PARTIAL) 2026-09-05 — STATE §19.** Steps 1, 2, 3 and 5 complete; step 4
  not started. See the P7 stub below.
- **P7 Fragment message framing. ← THE TRACK P FRONT, opened 2026-09-05 by P6
  (STATE §19).** P6 recovered the vocabulary and the registration mechanism but did
  not reach Step 4, so **the wire format is still unread and prediction 0's central
  question is still open.** What P7 inherits, ready to use: **3,509 Hub identities**
  (`hub_vocabulary.csv`), the registrar **`FUN_1407de270`**, and the session-layer
  table in **§19.6** — every handshake type with its UUID, hook and **handler
  vftable**, which is the entry point. **Do this first: OI-P6-2, which
  `RegistrationRequest` revision b22469132 actually sends.** All three are
  registered (`8673a3cc-…` at `1407f27f0`, `da4e5889-…` at `1407f2a20`,
  `0b826b33-…` at `1407f2c50`, contiguous at 0x230 spacing); registration is not
  use, and the answer is in whichever construction site is reachable from
  `GameConnection` state 10 (§17.7, OI-H2-5). **That is what S1a needs first** —
  prefer it if the chunk runs long. Then Step 4 proper (**OI-P6-3**): how a message
  serializes, **whether the 16-byte UUID or a negotiated index goes on the wire**
  (prediction 2, untested), how a fragment payload is delimited, and whether Hub
  rides inside GridMate replica chunks or beside them on the same Carrier
  (prediction 4, untested — relates to OI-P5-2, OI-H2-1). Also **OI-P6-1**: two
  distinct `FragmentUpdateMsg` types exist and Step 4 must name which it framed;
  `P6_PROMPT`'s attribution of descriptor `14a134340` is unverified and its only
  code xref is neither hook. **Read §19.8 before starting — three routes are already
  dead** (`.rdata` adjacency, `InstallRegistrationHook` RTTI descriptors,
  hook→vftable→COL) and re-deriving them costs a session. **Hard boundary unchanged:
  `EasyAntiCheatTrait`, `EasyAntiCheatClientTrait` and `EOSAntiCheatClientTrait`
  appear in the vocabulary — names only. Do not trace, do not decompile, stop if a
  trace wanders that way (CHARTER §3).** Scope bound: actor migration, persistence,
  routing, phasing and AOI remain **noticed, not pursued** — and **OI-P6-5** records
  a naming-convention inference (`*ReplicatedState`, `ComponentClientFacet_*`,
  `ComponentServerFacet_*`) that would give P3 and P4 their targets by name if it
  holds. **Prompt: NOT YET WRITTEN.** STATE §19.
- **S1–S3.** Server work, all blocked on the corresponding P-track chunks. Prompts
  when P1/P3/P4 resolve. Content source is ready (D2). **T5 handed S-track three
  hard requirements and removed one (STATE §12B):** the server must run GridMate's
  own 20-byte cookie exchange at the datagram layer — enabling OpenSSL's cookie
  callbacks is **not** equivalent and will not interoperate; it must send a
  HelloRequest once the cookie verifies, with backoff, or the client stalls at
  `message_seq 1` waiting for a ServerHello that never comes; and it must send a
  CertificateRequest and accept an **empty** client Certificate. **Removed:** there
  is no client-certificate PKI and no embedded cert to find in `NewWorld.exe` — the
  client presents nothing. Neither of the first two behaviours is derivable from
  RFC 6347; they are GridMate's own sequencing. **See the marked PROPOSAL under
  Track S** on splitting S1 into an unblocked DTLS half and a blocked Carrier half.
- **D1 Signature-scan harness.** So offsets survive a client patch. **Head start:**
  `pins/22469132/Bin64.sha256` plus `sha256sum -c` already gives a per-file list of
  which binaries a patch touched (STATE §5). Worth finishing the moment H3 has more
  than one hardcoded offset.
- **D2 Client game-data extraction.** **DONE 2026-08-29** — prompt in
  `D2_PROMPT.md`, findings in STATE §11. Paks are standard ZIP; compression method
  15 is Oodle. **2250 datasheets**, all in `SharedDataStrm-part{1..11}.pak` + base
  — *not* `GameData.pak`, and there is no `assets/server/server.pak` in build
  22469132 despite the tool README. Extracted and converted to JSON with
  localization applied via new-world-tools @ `e51c79a9`, built natively on Linux.
  Track S has its content source.

---

## FINDINGS block format

Every chunk ends by producing this. Paste it into the next session if it is listed
as an input, and fold it into `STATE.md` before starting anything else.

```
## FINDINGS — <chunk id> — <date>

**Client build under test:** <exact version>

**Status:** complete / partial / blocked

**What was done:**
- …

**Confirmed** (verified against the reference build, the decompiler, or a capture):
- …

**Unverified** (believed, not tested — say what would test it):
- …

**Corrections** (something in STATE.md is wrong):
- Old claim → what is actually true → evidence

**Files / addresses worth keeping** (signatures, not bare offsets):
- …

**Commands worth keeping:**
- …

**Noticed, out of scope** (incl. anything that turned out to be anti-cheat-only — charter §3):
- …

**What the next chunk needs to know:**
- …
```

The **Corrections** and **Unverified** sections earn their keep. A session that
records what it merely *believes*, separately from what it *checked*, is handing
the next session the list of things worth checking.

**Also update this file when a chunk lands:** tick the index row, add a DONE banner
to the prompt, and mark any claim inside the prompt that the chunk falsified. A
stale prompt is how a future session rebuilds something that already exists — the
T1/T2/T4 rows sat at `[ ]` for a full session after they were complete.

**This has now happened twice. 2026-08-30.** T3 and T5 both landed on 2026-08-29,
both were folded into `STATE.md` as §12A and §12B, and both index rows here were
still `[ ]` — with T3 additionally flagged `← NEXT` and the Order section still
routing the reader to it. The warning above was written *about the first
occurrence* and did not prevent the second, which says the problem is not that the
rule is unknown but that folding into `STATE.md` feels like completion and this
file gets left behind.

Two observations, for whatever they are worth. **First: the update is a different
motion from the fold, and it is the one with no natural trigger.** Writing FINDINGS
and folding them into `STATE.md` is where the session's attention already is; this
file is a separate document that nothing in that motion forces you to open.
**Second: the two files fail differently.** `STATE.md` is append-only, so its worst
case is clutter — a stale claim sits next to its correction and a reader can see
both. This file is a *router*: it tells a session what to do next. A stale row here
does not clutter, it **misdirects**, and it misdirects a session that has been
deliberately given only one chunk and no way to notice the contradiction. That
asymmetry is the argument for updating this file *before* folding findings, not
after — the fold is the part you will not forget.

**As of 2026-08-30 this is CHARTER §6.4, and it is binding rather than advisory.**
§6 exists specifically because the two paragraphs above were true, were written
down, and still did not prevent the second occurrence. The rules that bear on this
file: **§6.4** — tick the row, banner the prompt, and strike through whatever the
chunk falsified, *before* folding findings into `STATE.md`; a chunk is not complete
until all three are done. **§6.5** — never tick a row on the strength of remembered
work; a false `[x]` misdirects exactly as badly as a false `[ ]`. **§6.6** — open
items belong in STATE's register, not in this file. **§6.7** — where a standalone
`*_PROMPT.md` exists it *is* the prompt, and it belongs in the repository, not on
one machine.
