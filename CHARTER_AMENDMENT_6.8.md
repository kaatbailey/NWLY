# Proposed CHARTER amendment — §6.8

**This is a proposal, not an edit.** `CHARTER.md` §1 says it is never regenerated
by an AI and is edited by hand, by the owner, deliberately. I have not touched
`CHARTER.md`. Review this, change what you disagree with, and paste it yourself —
or discard it. The amendment log records that you suspended §1's rule once, for
the §6 amendment; this is the same shape of decision and it is yours.

Everything else from today is already applied: `CHUNKS.md`, `STATE.md`,
`P2_PROMPT.md`, and `check_docs.py`. The charter is the only file I left alone.

**Why it belongs in the charter rather than in `CHUNKS.md`:** §6's own reasoning.
*"A protocol for detecting stale documents cannot itself live in a document that
goes stale."* The closing sequence is in `CHUNKS.md` where the owner-facing
procedure lives, but the *rule that the check is mandatory* has to sit in the one
document guaranteed to be read.

---

## Proposed text — insert after §6.7, before §7

### 6.8 The rules are checked by a script, because rules alone have failed

Added 2026-09-04, after P2, when **two chunk rows were found ticked `[x]` while
their notes still routed a session to run them** and a prompt file was missing
from the inventory for the third time.

**The pattern that forced this section: every one of those failures already had a
rule written against it.** §6.4 says a ticked row carries a pointer to the STATE
section. §6.7 says a prompt that exists only on one machine cannot be handed to
anything. Both were written down, both were understood, and both were violated —
§6.7 three times. Adding an eighth rule to the seven that did not hold would be
the same move that already failed.

So this section adds a **mechanism**, not a rule. §6.2 is the precedent and the
only part of §6 that has never been violated, because it is the only part that
does not depend on anyone remembering it:

> *A session cannot be expected to notice that its inputs are three days old; it
> can be expected to compare two numbers.*

That generalises. A session cannot be expected to remember a six-step closing
sequence. It can be expected to run one command.

**`check_docs.py` lives in the repository root and is run twice per session:
once at the start, before its inputs are believed, and once before `git push`,
before the work is believed finished.** It verifies, mechanically:

- STATE's four freshness numbers against the file itself (§6.2)
- no duplicate section numbers (the 2026-08-29 duplicate §11)
- **`STATE.md` and `CHUNKS.md` name the same complete chunks** (§6.4)
- every `[x]` row carries a verdict, a date, **and a STATE § pointer** (§6.4(1))
- **no `[x]` row still contains live routing language** — the 2026-09-04 failure
- every `*_PROMPT.md` on disk is inventoried, and every inventoried one exists (§6.7)
- every complete chunk's prompt carries a DONE banner (§6.4(2))
- no completed chunk is still named as what to do next
- every open item in §15 has an owner cell (§6.6)
- §1's no-AI-regeneration sentence is still present in this file

**A FAIL means stop and resolve it. It does not mean proceed carefully.** Same
standard as §6.2, for the same reason.

**Three consequences worth stating explicitly.**

**(a) Ticking a row and rewriting its note are one action, not two.** The
2026-09-04 failure was not a missing tick — it was a tick *without* the rewrite,
on two rows at once. That is strictly worse than an untouched row: the `[x]`
suppresses the reader's suspicion while the note supplies the wrong instruction.
§6.4 already implies this by requiring a STATE pointer; it is made explicit here
because implication was not enough.

**(b) The checker is an instrument, and §4 applies to it.** *A belief validated
only against your own tooling is not validated.* A green `check_docs.py` means
the invariants it encodes hold — not that the documents are true. It cannot tell
whether a finding is correct, whether a verdict is justified, or whether a
correction row says the right thing. **It is a floor, not a ceiling**, and a
session that treats a green run as proof the handoff is sound has made exactly
the error §4 warns about. When it gains a check, record what that check cannot
see.

**(c) A chunk that falsifies its own premise is COMPLETE, not partial** —
provided its definition of done carries an "or confirmed absent" branch and the
negative is recorded with evidence. **P2 is the worked example**: it went looking
for protobuf schemas, found the premise false, and its value was the correction
(STATE §13, §17.9) plus the retargeting of Track P. Residuals go to §15 with an
owner. Marking such a chunk partial would leave the router ambiguous and invite a
future session to re-run work whose answer is already written down.

**(d) A session ends with a HANDOFF block, and nothing after it.** The owner's
action items are not findings and must not be distributed through the session's
prose — fixed shape, plain imperatives, ten lines maximum, last thing in the
message, derived from `check_docs.py --close` rather than from memory. Full form
in `CHUNKS.md`, "What the SESSION owes you at the end". This is a rule because on
2026-09-04 a session did the work correctly and then made the owner mine several
hundred words of reasoning to extract his own to-do list. **Findings are the
session's product; the action list is the owner's, and the two must be separable
in one glance.** An empty HANDOFF block is information; an absent one costs the
owner a read.

**(e) The check is enforced at the push, not only by habit.** `hooks/pre-push`
runs `check_docs.py --close` and blocks the push on FAIL. Install once:
`cp hooks/pre-push .git/hooks/pre-push; and chmod +x .git/hooks/pre-push`.
`git push --no-verify` bypasses it, deliberately and rarely — the hook exists so
that pushing an inconsistent state is a **decision** rather than an oversight.

---

## Proposed row for §7, the amendment log

| Date | Change |
| ---- | ------ |
| 2026-09-04 | **§6.8 added — the rules are checked by a script.** Written after P2, when **two rows (H2 and P2) were found ticked `[x]` while their notes still read "NEXT — ready to run"** and carried no STATE pointer, and `P2_PROMPT.md` was missing from the standalone inventory for the third time. The diagnosis is that every one of these failures already had a rule against it, so an eighth rule would repeat the move that failed; §6.2 — the only never-violated part of §6 — works because it requires comparing numbers rather than remembering intent. `check_docs.py` added to the repository root and made mandatory at session start and before push, encoding the §6.2/§6.4/§6.6/§6.7 invariants plus duplicate-section and stale-routing detection. Five consequences recorded: ticking a row and rewriting its note are one action; the checker is an instrument and §4 applies to it (a floor, not a ceiling); a chunk that falsifies its own premise closes COMPLETE, not partial; **a session ends with a ten-line HANDOFF block and nothing after it**, because on the same day a session made the owner mine several hundred words of prose for his own action list; and the check is enforced by a `pre-push` hook so that pushing an inconsistent state is a decision rather than an oversight. **§1–§5 untouched. §6.1–§6.7 untouched.** Authorised by the project owner. |

---

## If you would rather not amend the charter

The mechanism works without it — `check_docs.py` is in the repo and the closing
sequence is in `CHUNKS.md`'s "How to run a chunk". What you lose is the guarantee:
`CHUNKS.md` is the router, and a session that only reads the charter and one
prompt would never learn the check exists. Given that §6.7 says the charter is
what a session reads first, and given that this class of failure has now cost real
time three times, I think the guarantee is worth the amendment — but §1 makes that
your call, not mine.
