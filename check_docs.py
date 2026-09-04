#!/usr/bin/env python3
"""
check_docs.py — nwproto document consistency verifier.

WHY THIS EXISTS
  Every failure this catches already had a rule written against it, and the rule
  was violated anyway:
    2026-08-29  a stale snapshot produced a duplicate §11              (CHARTER §6.1)
    2026-08-29  T3/T5 complete while CHUNKS still routed sessions to run them (§6.4)
    2026-08-30  three sessions concluded pushed work was unpushed      (§6.3)
    2026-08-30  STATE's own freshness header had 3 of 4 checks wrong   (§6.2)
    2026-08-30  P0_PROMPT.md missing from the standalone inventory     (§6.7)
    2026-09-04  H2 AND P2 ticked [x] while their notes still read "NEXT — ready
                to run" and carried no STATE pointer                   (§6.4)
    2026-09-04  P2_PROMPT.md missing from the inventory — third time   (§6.7)

  CHARTER §6.2's insight is the one that worked: "A session cannot be expected to
  notice that its inputs are three days old; it can be expected to compare two
  numbers." This extends that to every invariant §6 states. A session cannot be
  expected to remember seven closing steps. It can be expected to run one command.

USAGE
  python3 check_docs.py [repo_path]        # default: .
  python3 check_docs.py --quiet            # exit code only, for hooks

EXIT
  0 = all checks pass    1 = one or more FAIL    2 = could not run

Run it TWICE per session: at the start (before believing your inputs) and before
`git push` (before believing you are done).
"""

import os
import re
import sys

FAIL, WARN, OK = "FAIL", "WARN", "OK"
results = []


def record(status, check, detail="", action=None):
    results.append((status, check, detail, action))


def read(path):
    try:
        return open(path, encoding="utf-8").read()
    except OSError:
        return None


# ---------------------------------------------------------------- parsing

def parse_state_header(state):
    """Pull the four §6.2 numbers plus the chunk list out of the header."""
    h = {}
    m = re.search(r"\|\s*Section count[^|]*\|\s*\*\*(\d+)\*\*", state)
    h["sections"] = int(m.group(1)) if m else None
    m = re.search(r"\|\s*Highest test number[^|]*\|\s*\*\*(\d+)\*\*", state)
    h["tests"] = int(m.group(1)) if m else None
    m = re.search(r"\|\s*Correction row count[^|]*\|\s*\*\*(\d+)\*\*", state)
    h["corrections"] = int(m.group(1)) if m else None
    m = re.search(r"\|\s*Written against commit\s*\|\s*([^|]+)\|", state)
    h["commit"] = m.group(1).strip() if m else None
    m = re.search(r"\|\s*Chunks complete\s*\|\s*([^|]+)\|", state)
    if m:
        raw = m.group(1)
        h["complete"] = [c.strip().strip("*").strip()
                         for c in raw.split(",") if c.strip()]
    else:
        h["complete"] = []
    return h


def actual_state_numbers(state):
    lines = state.split("\n")
    sections = sum(1 for l in lines if l.startswith("## "))

    def block(start_pat, end_pat):
        s = e = None
        for i, l in enumerate(lines):
            if s is None and re.match(start_pat, l):
                s = i
            elif s is not None and re.match(end_pat, l):
                e = i
                break
        return lines[s:e] if s is not None else []

    tests = [int(m.group(1)) for l in block(r"^## 14\.", r"^## 15\.")
             if (m := re.match(r"\|\s*(\d+)\s*\|", l))]
    corr = [l for l in block(r"^## 13\.", r"^## 14\.")
            if l.startswith("| ") and not re.match(r"\|\s*(Old claim|-{2,})", l)]
    return {"sections": sections,
            "tests": max(tests) if tests else None,
            "corrections": len(corr)}


CHUNK_ROW = re.compile(r"^\|\s*`\[( |x|~|!)\]`\s*\|\s*\*\*([A-Za-z0-9]+)\*\*(.*)$")


def parse_chunk_rows(chunks):
    rows = {}
    for line in chunks.split("\n"):
        m = CHUNK_ROW.match(line)
        if m:
            rows[m.group(2)] = {"mark": m.group(1), "line": line, "rest": m.group(3)}
    return rows


def strip_struck(text):
    """Remove ~~struck~~ spans — struck text is history, not live instruction."""
    return re.sub(r"~~.*?~~", "", text, flags=re.S)


# ---------------------------------------------------------------- checks

def check_state_header(state):
    h = parse_state_header(state)
    a = actual_state_numbers(state)
    for key, label in (("sections", "section count"),
                       ("tests", "highest test number"),
                       ("corrections", "correction row count")):
        if h[key] is None:
            record(FAIL, "STATE header: %s missing" % label)
        elif h[key] != a[key]:
            record(FAIL, "STATE header: %s" % label,
                   "header says %s, file has %s" % (h[key], a[key]),
                   "STATE.md — set the %s in the freshness header to %s" % (label, a[key]))
        else:
            record(OK, "STATE header: %s (%s)" % (label, a[key]))

    c = h.get("commit") or ""
    if not c or c.lower() in ("blank", "-"):
        record(FAIL, "STATE header: commit field is blank",
               "CHARTER §6.2 requires all four numbers to exist")
    elif "FILL" in c.upper() or "TODO" in c.upper():
        record(WARN, "STATE header: commit field is a placeholder",
               "%s — fill it before pushing" % c,
               "STATE.md — replace the commit placeholder with the real hash "
               "(git rev-parse --short HEAD) before pushing")
    else:
        record(OK, "STATE header: commit recorded (%s)" % c)
    return h


def check_duplicate_sections(state):
    nums = re.findall(r"^## (\d+[A-Za-z]?)\.", state, re.M)
    dupes = sorted({n for n in nums if nums.count(n) > 1})
    if dupes:
        record(FAIL, "STATE: duplicate section numbers", ", ".join("§" + d for d in dupes),
               "STATE.md — two sections share a number (%s). A session folded "
               "findings into an existing section. Renumber the newer one."
               % ", ".join(dupes))
    else:
        record(OK, "STATE: no duplicate section numbers")


def check_router_agrees(header, rows):
    """The §6.4 check. STATE and CHUNKS must name the same complete chunks."""
    state_done = {c.lower() for c in header["complete"]}
    chunk_done = {k.lower() for k, v in rows.items() if v["mark"] == "x"}
    if not rows:
        record(FAIL, "CHUNKS: no chunk index rows parsed", "has the table format changed?")
        return
    only_state = state_done - chunk_done
    only_chunks = chunk_done - state_done
    if only_state:
        record(FAIL, "ROUTER: STATE says complete, CHUNKS does not",
               ", ".join(sorted(only_state)),
               "CHUNKS.md — tick the row for %s (verdict + date + STATE section "
               "pointer, and rewrite the note in the SAME edit)"
               % ", ".join(sorted(only_state)).upper())
    if only_chunks:
        record(FAIL, "ROUTER: CHUNKS ticked, STATE header does not list complete",
               ", ".join(sorted(only_chunks)),
               "Decide which is true for %s: if the chunk IS done, add it to "
               "STATE's 'Chunks complete' header; if NOT, un-tick the CHUNKS row. "
               "A false [x] misdirects as badly as a false [ ] (CHARTER §6.5)"
               % ", ".join(sorted(only_chunks)).upper())
    if not only_state and not only_chunks:
        record(OK, "ROUTER: STATE and CHUNKS agree (%d complete)" % len(state_done))


def check_ticked_rows_are_closed(rows):
    """§6.4: a ticked row carries a verdict, a date, and a STATE pointer."""
    for cid, v in sorted(rows.items()):
        if v["mark"] != "x":
            continue
        live = strip_struck(v["rest"])
        problems = []
        if not re.search(r"\b(DONE|COMPLETE)\b", live):
            problems.append("no DONE/COMPLETE verdict")
        if not re.search(r"\d{4}-\d{2}-\d{2}", live):
            problems.append("no date")
        if not re.search(r"(STATE §|§\d)", live):
            problems.append("no STATE § pointer")
        if re.search(r"(NEXT — ready to run|← NEXT|\bNEXT\b.*ready|ready to run)", live):
            problems.append("STILL ROUTES A SESSION TO RUN IT")
        if problems:
            record(FAIL, "CHUNKS row [x] %s" % cid, "; ".join(problems),
                   "CHUNKS.md — fix %s's row: %s" % (cid, "; ".join(problems)))
        else:
            record(OK, "CHUNKS row [x] %s closed properly" % cid)


def check_prompt_inventory(repo, chunks, rows):
    """§6.7: every prompt file on disk is inventoried, and vice versa."""
    on_disk = {f for f in os.listdir(repo) if re.match(r"^[A-Za-z0-9]+_PROMPT\.md$", f)}
    listed = set(re.findall(r"`([A-Za-z0-9]+_PROMPT\.md)`", chunks))
    missing = on_disk - listed
    phantom = listed - on_disk
    if missing:
        record(FAIL, "PROMPTS: on disk but not inventoried in CHUNKS",
               ", ".join(sorted(missing)),
               "CHUNKS.md — add %s to the 'Standalone prompt files' list"
               % ", ".join(sorted(missing)))
    if phantom:
        record(FAIL, "PROMPTS: inventoried but not on disk",
               ", ".join(sorted(phantom)),
               "Find or recreate %s — a prompt that exists on one machine cannot "
               "be handed to anything (CHARTER §6.7)" % ", ".join(sorted(phantom)))
    if not missing and not phantom:
        record(OK, "PROMPTS: inventory matches disk (%d files)" % len(on_disk))

    for cid, v in sorted(rows.items()):
        if v["mark"] != "x":
            continue
        for cand in ("%s_PROMPT.md" % cid.upper(), "%s_PROMPT.md" % cid):
            if cand in on_disk:
                body = read(os.path.join(repo, cand)) or ""
                head = body[:4000]
                if not re.search(r"(✅\s*DONE|DONE —|\bDONE\b.*\d{4}-\d{2}-\d{2})", head):
                    record(FAIL, "PROMPTS: %s has no DONE banner" % cand,
                           "chunk %s is complete" % cid,
                           "%s — add a DONE banner at the top, and strike through "
                           "(never delete) any claim inside it the chunk falsified"
                           % cand)
                else:
                    record(OK, "PROMPTS: %s carries a DONE banner" % cand)
                break


def check_order_not_stale(header, chunks):
    """A completed chunk must not still be named as what to do next."""
    done = {c.lower() for c in header["complete"]}
    for m in re.finditer(r"\*\*Next is ([A-Za-z0-9]+)\*\*", strip_struck(chunks)):
        if m.group(1).lower() in done:
            record(FAIL, "CHUNKS Order: 'Next is %s' but it is complete" % m.group(1),
                   "stale routing",
                   "CHUNKS.md — the Order section still says 'Next is %s'. Strike "
                   "it and name what is actually next." % m.group(1))
            return
    record(OK, "CHUNKS Order: no completed chunk named as next")


def check_open_items_owned(state):
    """§6.6: every open item has an owner or is explicitly marked unowned."""
    lines = state.split("\n")
    try:
        start = next(i for i, l in enumerate(lines) if l.startswith("## 15."))
        end = next(i for i, l in enumerate(lines[start + 1:], start + 1)
                   if l.startswith("## "))
    except StopIteration:
        record(WARN, "STATE §15 not located", "skipping owner check")
        return
    bad = []
    for l in lines[start:end]:
        m = re.match(r"^\|\s*(~~)?\*\*([A-Z][A-Za-z0-9-]+)\*\*", l)
        if not m:
            continue
        cells = [c.strip() for c in l.split("|")]
        if len(cells) >= 5:
            owner = cells[3]
            if not owner or owner in ("-", "—"):
                bad.append(m.group(2))
    if bad:
        record(FAIL, "STATE §15: open items with no owner cell", ", ".join(bad),
               "STATE.md §15 — give %s an owning chunk, or mark it explicitly "
               "Unowned (CHARTER §6.6)" % ", ".join(bad))
    else:
        record(OK, "STATE §15: all open items carry an owner")


def check_charter_untouched(repo):
    """§1: the charter is hand-edited only. Flag AI-ish regeneration markers."""
    ch = read(os.path.join(repo, "CHARTER.md"))
    if ch is None:
        record(FAIL, "CHARTER.md not found")
        return
    if "never regenerated by an AI" not in ch:
        record(FAIL, "CHARTER: §1's no-AI-regeneration rule is missing",
               "the charter may have been rewritten")
    else:
        record(OK, "CHARTER: no-regeneration rule intact")


# ---------------------------------------------------------------- main

def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    quiet = "--quiet" in sys.argv
    close_mode = "--close" in sys.argv
    repo = args[0] if args else "."

    state = read(os.path.join(repo, "STATE.md"))
    chunks = read(os.path.join(repo, "CHUNKS.md"))
    if state is None or chunks is None:
        print("could not read STATE.md / CHUNKS.md in %s" % os.path.abspath(repo))
        return 2

    check_charter_untouched(repo)
    header = check_state_header(state)
    check_duplicate_sections(state)
    rows = parse_chunk_rows(chunks)
    check_router_agrees(header, rows)
    check_ticked_rows_are_closed(rows)
    check_prompt_inventory(repo, chunks, rows)
    check_order_not_stale(header, chunks)
    check_open_items_owned(state)

    fails = [r for r in results if r[0] == FAIL]
    warns = [r for r in results if r[0] == WARN]
    todo = [r for r in results if r[0] in (FAIL, WARN) and r[3]]

    if quiet:
        return 1 if fails else 0

    # ---- ACTIONS FIRST. Diagnostics are secondary and go underneath. ----
    print()
    if todo:
        print("  " + "=" * 68)
        print("  DO THIS NOW — %d item%s, in this order:" %
              (len(todo), "" if len(todo) == 1 else "s"))
        print("  " + "=" * 68)
        for i, (status, _c, _d, action) in enumerate(todo, 1):
            tag = "" if status == FAIL else "(before push) "
            wrapped = _wrap(tag + action, 68, indent=7)
            print("   %d. %s" % (i, wrapped))
        print()
        print("  Then: python3 check_docs.py   and only then   git push")
    else:
        print("  ✅ ALL %d CHECKS PASS — documents are consistent." % len(results))
        print("     (A floor, not a ceiling: this proves the invariants hold,")
        print("      not that the findings are right. CHARTER §4.)")
    print()

    if close_mode:
        return 1 if fails else 0

    print("  %d pass · %d warn · %d FAIL" %
          (len(results) - len(fails) - len(warns), len(warns), len(fails)))
    if fails or warns:
        print()
        for status, check, detail, _a in results:
            if status == OK:
                continue
            print("     %-5s %s%s" % (status, check, ("  —  " + detail) if detail else ""))
    if fails:
        print()
        print("  A FAIL means stop and resolve it. It does not mean proceed")
        print("  carefully. (CHARTER §6.2)")
    return 1 if fails else 0


def _wrap(text, width, indent):
    words, lines, cur = text.split(), [], ""
    for w in words:
        if len(cur) + len(w) + 1 > width:
            lines.append(cur)
            cur = w
        else:
            cur = (cur + " " + w).strip()
    lines.append(cur)
    return ("\n" + " " * indent).join(lines)


if __name__ == "__main__":
    sys.exit(main())
