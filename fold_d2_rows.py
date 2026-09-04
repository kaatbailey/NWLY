#!/usr/bin/env python3
"""
fold_d2_rows.py -- finish the job fold_d2.py started.

Adds the S13 Corrections rows and the S14 Test/capture log rows. The first
script's regexes assumed table-cell padding that the raw file does not have;
this one matches on the "*(none yet)*" text alone and counts pipes to decide
which table a row belongs to, so padding is irrelevant.

No arguments:

    python3 fold_d2_rows.py

Safe to run twice -- it checks whether the rows are already present.
"""

import pathlib
import re
import shutil
import sys
from datetime import datetime

CORRECTION_ROWS = """\
| D2 datasheets expected in `GameData.pak` (name inference) | **Wrong.** They are in `SharedDataStrm-part{1..11}.pak` + base; `GameData.pak` holds zero. Evidence: central-directory census, build 22469132. |
| new-world-tools README documents `assets/server/server.pak` as the datasheet source | **Stale for this build.** No `assets/server/` directory exists. A session following the README verbatim will stall. |
| EOCD counts of exactly 65535 are 16-bit saturation, so 2250 is a floor | **Wrong.** Not saturated: `walked == eocd` on every pak. 2250 is exact; the `-partN` split exists to stay under the ceiling. |
| Oodle (method 15) needs the MSVC redistributable, so Linux extraction is Proton-or-nothing | **Wrong.** `go-oodle-lz` + `ebitengine/purego` dlopen a *native* Oodle v2.9.13 fetched at first run. No wine, no PE DLL, no cgo. |
| 645 datasheets in 173ms is suspiciously fast, possible silent failure | **Wrong.** Output verified sane column-by-column. Oodle is simply that fast. |
"""

LOG_ROWS = """\
| 1 | D2/1 Pak container format | ZIP magic `50 4b 03 04` at offset 0 | **Confirmed.** All 130 open as zip, 0 failures. |
| 2 | D2/2 Datasheet location | `GameData.pak` (name inference) | **Refuted.** Zero there; all 2250 in `SharedDataStrm*`. |
| 3 | D2/3 EOCD saturation | Counts of 65535 are saturation; 2250 a floor | **Refuted.** `walked == eocd`; 2250 exact. |
| 4 | D2/4 Oodle on Linux | MSVC/PE-DLL dependency blocks native extraction | **Refuted.** Native Oodle v2.9.13 via purego; built and ran clean. |
| 5 | D2/5 Bulk extraction count | 2250, from the independent census | **Confirmed.** `pak-extracter` produced exactly 2250. |
"""


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
    path = repo / "STATE.md"
    text = path.read_text("utf-8")
    original = text
    print("repo: %s\n" % repo)

    if "D2/1 Pak container format" in text and "GameData.pak` (name inf" in text:
        sys.exit("Rows already present. Nothing to do.")

    lines = text.split("\n")
    out = []
    added = []

    for line in lines:
        # Any table row whose only real content is the "(none yet)"
        # placeholder. Pipe count tells us which table it is:
        # 2 cells -> S13 Corrections, 4 cells -> S14 test log.
        stripped = line.strip()
        if stripped.startswith("|") and "*(none yet)*" in stripped:
            cells = [c.strip() for c in stripped.strip("|").split("|")]
            if len(cells) <= 2 and "Corrections" not in " ".join(added):
                out.append(CORRECTION_ROWS.rstrip("\n"))
                added.append("S13 Corrections: 5 rows "
                             "(3 against my own earlier claims)")
                continue
            elif len(cells) >= 3:
                out.append(LOG_ROWS.rstrip("\n"))
                added.append("S14 Test / capture log: 5 rows")
                continue
        out.append(line)

    text = "\n".join(out)

    if text == original:
        print("  FAIL  No '*(none yet)*' rows found at all.")
        print("\nShow me what is actually there:")
        print("  rg -n -B2 -A4 'none yet' STATE.md | cat -A")
        return

    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    shutil.copy2(path, path.parent / (path.name + ".bak-" + stamp))
    path.write_text(text, "utf-8")

    for a in added:
        print("  ok    " + a)
    missing = []
    if not any("S13" in a for a in added):
        missing.append("S13 Corrections")
    if not any("S14" in a for a in added):
        missing.append("S14 Test / capture log")
    for m in missing:
        print("  FAIL  " + m + ": placeholder row not matched")

    print("\nBackup: STATE.md.bak-%s" % stamp)
    print("Check:  git -C %s diff STATE.md" % repo)


if __name__ == "__main__":
    main()
