#!/usr/bin/env python3
"""
fix_d2_fold.py -- repair and finish the D2 fold.

fold_d2.py was written against the GitHub copy of STATE.md, which was far
behind the working tree. It inserted the D2 section as a SECOND "## 8." and
cross-referenced it as S8. Locally, S8/S9 are the Carrier and DTLS wire
formats and S10 is T1+T2, so D2 is S11.

This script:
  1. renumbers the duplicate "## 8. Client game data" heading to "## 11."
  2. moves it above the "## 8+. Reserved" placeholder, where S8/S9/S10 sit
  3. fixes the "see S8" cross-reference in S5 to "see S11"
  4. appends the 5 D2 correction rows to the existing S13 table (which
     already has 6 T4 rows -- they are untouched)
  5. appends the 5 D2 test rows to S14 numbered 13-17, continuing from 12
  6. fixes "STATE S8" -> "STATE S11" in CHUNKS.md

No arguments. Backs both files up first. Safe to run twice.

    python3 fix_d2_fold.py
"""

import pathlib
import re
import shutil
import sys
from datetime import datetime

MARKER = "<!-- D2-FOLDED -->"
NEW_NUM = 11

CORRECTION_ROWS = [
    "| \"D2 datasheets will be in `assets/GameData.pak`\" — inferred from the "
    "name before looking. | **WRONG.** `GameData.pak` holds zero. All 2250 are "
    "in `SharedDataStrm-part{1..11}.pak` + base. Cause of the error: inferred "
    "location from a filename instead of reading the central directory. A "
    "census across all 130 paks settles it in one pass and should have been "
    "step one. |",

    "| \"new-world-tools' documented path `assets/server/server.pak` is the "
    "datasheet source.\" — taken from the tool README. | **STALE for build "
    "22469132.** No `assets/server/` directory exists in this install. The "
    "README predates the Aeternum relaunch. A session following it verbatim "
    "stalls here; go by the census, not the README. |",

    "| \"EOCD entry counts of exactly 65535 are 16-bit saturation, so the 2250 "
    "datasheet count is a floor.\" — raised in session on seeing four paks "
    "report 65535. | **WRONG.** A direct `PK\\x01\\x02` central-directory walk "
    "gave `walked == eocd` on every pak including all four. No Zip64 anywhere. "
    "2250 is exact. The `-partN` split exists precisely to stay under the "
    "65535 ceiling. Reasonable suspicion, wrong conclusion — and the check was "
    "cheap. |",

    "| \"Oodle (ZIP method 15) needs the MSVC redistributable, so Linux "
    "extraction is Proton-or-nothing.\" — inferred from the tool README "
    "listing MSVC as a dependency. | **WRONG.** `go-oodle-lz` + "
    "`ebitengine/purego` `dlopen` a **native** Oodle v2.9.13 fetched at first "
    "run. No wine, no PE DLL, no cgo. Built and extracted clean on Garuda. "
    "Cause of the error: read a dependency note written for the Windows "
    "release binaries and assumed it described the source. |",

    "| \"645 datasheets extracted in 173ms is suspiciously fast — likely a "
    "silent failure.\" — raised in session. | **WRONG.** Output verified "
    "column-by-column: `MasterItemDefinitions_Faction`, 127 columns × 4121 "
    "rows, legible headers. Oodle is simply that fast. Worth the check "
    "regardless — it is the D2 prompt's named failure mode — but speed alone "
    "was not evidence of anything. |",
]

LOG_ROWS = [
    "| {n} | D2: identify the pak container from header bytes of "
    "`assets/GameData.pak`. | Standard ZIP, magic `50 4b 03 04` at offset 0. | "
    "**Confirmed.** `50 4b 03 04`; first local header parses (41 bytes stored, "
    "name len 0x24 = `libs/flownodes/flownodeblacklist.xml`). All 130 paks open "
    "as zip, 0 failures. |",

    "| {n} | D2: locate the `.datasheet` files across all 130 paks. | In "
    "`GameData.pak`, by name inference. | **Falsified.** Zero in `GameData.pak`. "
    "All 2250 in the `SharedDataStrm*` family; part6=645, part4=628, part5=569 "
    "carry 82% of them. See §13. |",

    "| {n} | D2: test whether EOCD counts of 65535 are 16-bit saturation, by "
    "walking `PK\\x01\\x02` records directly. | Saturated; 2250 is a floor and "
    "the true count is higher. | **Falsified.** `walked == eocd` on every pak. "
    "No Zip64. 2250 exact. `-part12`/`-part13` are 22-byte empty-archive stubs; "
    "`-part14` has 3928 entries and 0 datasheets. |",

    "| {n} | D2: build new-world-tools `@e51c79a9` natively on Garuda and "
    "extract method-15 (Oodle) entries. | Fails — MSVC/PE-DLL dependency forces "
    "Proton. | **Falsified.** `go build` clean; runtime `dlopen` of a native "
    "Oodle v2.9.13 (+ `libtexconv.so`), both auto-downloaded on first run. "
    "Extraction succeeded. Note: the tool fetches binaries from the network — "
    "relevant to any air-gapped re-run. |",

    "| {n} | D2: bulk-extract every `.datasheet` and compare against the "
    "independent census. | 2250, matching the central-directory count. | "
    "**Confirmed.** `pak-extracter` produced exactly 2250 → 2250 JSON. Two "
    "independent code paths agree, so neither is silently dropping entries. "
    "198 of 2250 stored (method 0), 2052 Oodle. |",
]


def find_repo():
    home = pathlib.Path.home()
    cands = [pathlib.Path.cwd(), pathlib.Path.cwd().parent,
             home / "Documents" / "NWLY", home / "NWLY"]
    for depth in range(1, 6):
        cands.extend(home.glob("/".join(["*"] * depth) + "/NWLY"))
    for c in cands:
        try:
            c = c.resolve()
        except OSError:
            continue
        if c.is_dir() and (c / "STATE.md").is_file():
            return c
    return None


def main():
    repo = find_repo()
    if repo is None:
        sys.exit("Could not find the NWLY checkout. Run this inside it.")
    print("repo: %s\n" % repo)

    state_p, chunks_p = repo / "STATE.md", repo / "CHUNKS.md"
    state = state_p.read_text("utf-8")
    chunks = chunks_p.read_text("utf-8") if chunks_p.is_file() else ""
    o_state, o_chunks = state, chunks
    done, failed = [], []

    lines = state.split("\n")

    # ---- 1/2. find the misnumbered D2 section, renumber, relocate --------
    start = next((i for i, l in enumerate(lines)
                  if l.startswith("## ") and MARKER in l), None)
    if start is None:
        if re.search(r"^## %d\. Client game data" % NEW_NUM, state, re.M):
            done.append("D2 section already renumbered to §%d" % NEW_NUM)
        else:
            failed.append("D2 section not found (no marker). Nothing moved.")
    else:
        end = next((i for i in range(start + 1, len(lines))
                    if lines[i].startswith("## ")), len(lines))
        block = lines[start:end]
        block[0] = ("## %d. Client game data (`.datasheet`) — CONFIRMED from D2"
                    % NEW_NUM)
        del lines[start:end]

        anchor = next((i for i, l in enumerate(lines)
                       if l.startswith("## 8+.")), None)
        if anchor is None:
            anchor = next((i for i, l in enumerate(lines)
                           if l.startswith("## 13.")), len(lines))
            note = "before §13"
        else:
            note = "above the '## 8+. Reserved' placeholder, with §8–§10"
        lines[anchor:anchor] = block
        done.append("renumbered the duplicate '## 8.' to '## %d.' and moved it "
                    "%s" % (NEW_NUM, note))

    state = "\n".join(lines)

    # ---- 3. fix the S5 cross-reference ----------------------------------
    if "-- see S8." in state or "— see S8." in state:
        state = state.replace("-- see S8.", "— see §%d." % NEW_NUM)
        state = state.replace("— see S8.", "— see §%d." % NEW_NUM)
        done.append("fixed the §5 build-placeholder cross-reference to §%d"
                    % NEW_NUM)
    state = state.replace("(see S13)", "(see §13)")
    state = state.replace("CHARTER S3", "CHARTER §3").replace(
        "CHARTER S4", "CHARTER §4")

    # ---- 4. append correction rows to S13 -------------------------------
    if "D2 datasheets will be in" in state:
        done.append("§13 D2 rows already present")
    else:
        m = re.search(r"(^## 13\..*?)(\n\n---)", state, re.S | re.M)
        if not m:
            failed.append("could not find the end of the §13 table. "
                          "Corrections NOT added.")
        else:
            block = m.group(1).rstrip("\n")
            block += "\n" + "\n".join(CORRECTION_ROWS)
            state = state[:m.start(1)] + block + state[m.end(1):]
            done.append("appended 5 D2 rows to §13 (the 6 existing T4 rows "
                        "untouched); 4 of the 5 are against my own claims")

    # ---- 5. append test rows to S14, continuing the numbering -----------
    if "identify the pak container from header bytes" in state:
        done.append("§14 D2 rows already present")
    else:
        nums = [int(n) for n in re.findall(r"^\|\s*(\d+)\s*\|", state, re.M)]
        nxt = (max(nums) + 1) if nums else 1
        rows = "\n".join(r.format(n=nxt + i) for i, r in enumerate(LOG_ROWS))
        state = state.rstrip("\n") + "\n" + rows + "\n"
        done.append("appended 5 D2 rows to §14, numbered %d–%d"
                    % (nxt, nxt + 4))

    # ---- 6. CHUNKS cross-reference --------------------------------------
    if chunks:
        if "STATE S8" in chunks:
            chunks = chunks.replace("STATE S8", "STATE §%d" % NEW_NUM)
            done.append("CHUNKS.md: fixed 'STATE S8' → 'STATE §%d'" % NEW_NUM)
        elif "STATE §%d" % NEW_NUM in chunks:
            done.append("CHUNKS.md: cross-reference already correct")
        else:
            failed.append("CHUNKS.md: D2 cross-reference not found.")

    # ---- write -----------------------------------------------------------
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for p, new, old in ((state_p, state, o_state), (chunks_p, chunks, o_chunks)):
        if new != old:
            shutil.copy2(p, p.parent / (p.name + ".bak2-" + stamp))
            p.write_text(new, "utf-8")

    for d in done:
        print("  ok    " + d)
    for f in failed:
        print("  FAIL  " + f)

    print("\nBackups: *.bak2-%s" % stamp)
    print("\nVerify — there must be exactly one heading per number:")
    print("  rg -n '^## ' STATE.md")
    print("  git -C %s diff --stat" % repo)


if __name__ == "__main__":
    main()
