#!/usr/bin/env python3
"""
fold_d2.py -- fold the D2 findings into NWLY's STATE.md and CHUNKS.md.

No arguments. Finds the repo, backs up both files, writes the changes, and
tells you exactly what it did and what it could not do.

    python3 fold_d2.py

CHARTER.md is never written to. STATE.md is only inserted into or appended
to -- no existing line is deleted or reordered, except the two "*(none yet)*"
placeholder rows, which hold no belief.

Safe to run twice: it detects its own marker and stops.
"""

import pathlib
import re
import shutil
import sys
from datetime import datetime

MARKER = "<!-- D2-FOLDED -->"

# ---------------------------------------------------------------- find repo

def find_repo():
    home = pathlib.Path.home()
    candidates = [pathlib.Path.cwd(), pathlib.Path.cwd().parent,
                  home / "NWLY", home / "Documents" / "NWLY",
                  home / "Projects" / "NWLY", home / "src" / "NWLY"]
    for depth in range(1, 6):
        candidates.extend(home.glob("/".join(["*"] * depth) + "/NWLY"))
    seen = set()
    for c in candidates:
        try:
            c = c.resolve()
        except OSError:
            continue
        if c in seen or not c.is_dir():
            continue
        seen.add(c)
        if (c / "STATE.md").is_file() and (c / "CHUNKS.md").is_file():
            return c
    return None

# ---------------------------------------------------------------- content

STATE_SECTION = """\
## 8. Client game data (`.datasheet`) -- CONFIRMED from D2 __MARKER__

Folded from FINDINGS -- D2 -- 2026-08-29. Pure offline file work: no client
launch, no injection, read-only against the install (CHARTER S3 satisfied).

**Build under test:** New World: Aeternum, Steam appid 1063730, **buildid
22469132**, installdir `New World`, SizeOnDisk 76,416,676,920 (~71.2 GiB), at
`/home/kaatlev/.local/share/Steam/steamapps/common/New World`.

### The pak container is standard ZIP

- `50 4b 03 04` at offset 0; the first local header parses cleanly (41 bytes
  stored, filename length 0x24 = `libs/flownodes/flownodeblacklist.xml`).
- **130 `.pak`** under `assets/`, ~72G on disk. Naming `<Name>[-partN].pak`.
  All 130 open as zip; **0 failures**.
- **Compression method 15 = Oodle.** Not a standard ZIP method id (0 store,
  8 deflate, 9 deflate64, 12 bzip2, 14 LZMA, 93 zstd). Python `zipfile` can
  enumerate method-15 entries but cannot `read()` them -- it is a census
  tool here, not an extraction tool.
- **No Zip64 anywhere.** EOCD 16-bit entry counts are genuine, not
  saturated: a direct `PK\\x01\\x02` central-directory walk gave
  `walked == eocd` on every pak, including the four sitting exactly on
  65535. The packer rolls to a new `-partN` at the 65535 ceiling -- that is
  what the part numbering is for.

### Where the datasheets are

**2250 total**, confined entirely to `SharedDataStrm*`. `GameData.pak` holds
none (see S13).

| Pak | Datasheets |
| --- | ---------- |
| `SharedDataStrm-part6.pak` | 645 |
| `SharedDataStrm-part4.pak` | 628 |
| `SharedDataStrm-part5.pak` | 569 |
| `SharedDataStrm-part7.pak` | 152 |
| `SharedDataStrm-part9.pak` | 60 |
| `SharedDataStrm-part8.pak` | 45 |
| `SharedDataStrm-part11.pak` | 45 |
| `SharedDataStrm-part10.pak` | 37 |
| `SharedDataStrm-part3.pak` | 29 |
| `SharedDataStrm-part1.pak` | 21 |
| `SharedDataStrm.pak` | 12 |
| `SharedDataStrm-part2.pak` | 7 |

- `-part12` and `-part13` are **22-byte empty-archive stubs** (EOCD record
  only, 0 entries). `-part14` has 3928 entries and 0 datasheets.
- **198 of 2250 are stored (method 0); 2052 are Oodle.**

### Verification

- **Two independent code paths agree on 2250** -- the hand-rolled
  central-directory census and `pak-extracter`. Neither is silently
  dropping entries.
- **Verified column-by-column**, not by file count.
  `MasterItemDefinitions_Faction`: **127 columns x 4121 rows**, legible
  headers (`ItemID`, `ItemType`, `TradingCategory`, `GearScoreOverride`,
  `PerkSlot1`). Not plausible-looking garbage.
- **Localization is a separate 184-file tree** under `localization/en-us`.
  String fields are `@Key` lookups (e.g. `@DyeB179_Name`) resolved by the
  converter's `-localization` flag.

### Tooling (re-derivable per CHARTER S4)

- **github.com/new-world-tools/new-world-tools**, MIT, pure Go, v0.13.10.
- Commit **`e51c79a9af4fba51daecd97c5e190c0b5ee953a5`**
  (Wed Nov 5 04:04:28 2025 +0300), cloned to `~/Documents/new-world-tools`.
- Builds natively on Garuda: `go build -o ./bin/ ./cmd/...` produces
  `pak-extracter`, `datasheet-converter`, `object-stream-converter`,
  `asset-catalog-parser`.
- **The tool downloads binary libraries from the network on first run** --
  Oodle v2.9.13 and `libtexconv.so`. Not found under the repo, `~/.cache`,
  `~/.local/share` or `~/.config` at depth 5; **location unresolved**.
  Matters for any air-gapped or reproducible re-run.

```fish
set -g NW /home/kaatlev/.local/share/Steam/steamapps/common/"New World"
cd ~/Documents/new-world-tools && go build -o ./bin/ ./cmd/...

./bin/pak-extracter -input $NW/assets -output ~/Documents/nwly-extract \\
  -include '\\.datasheet$' -threads 6
./bin/pak-extracter -input $NW/assets -output ~/Documents/nwly-extract \\
  -include '^localization/en-us' -threads 6
./bin/datasheet-converter -input ~/Documents/nwly-extract \\
  -output ~/Documents/nwly-datasheets -format json -threads 6 \\
  -localization ~/Documents/nwly-extract/localization/en-us -keep-structure
```

Runtimes: extract **540ms** (peak 7.5Mb) - convert **15.4s** (peak
**2297Mb**). The converter is the memory hog; worth knowing on a smaller box.

Outputs, gitignored and outside the repo: `~/Documents/nwly-extract` (211M
raw), `~/Documents/nwly-datasheets` (499M JSON).

### UNVERIFIED -- the loose ends

- **No installer/depot pinned.** buildid 22469132 *identifies* this build but
  will not re-download it. Manifest ids are in
  `~/.local/share/Steam/depotcache/` or the appmanifest's `InstalledDepots`
  block. **Pin them before the next game patch** (CHARTER S4 version-lock).
  This is the one item here with a clock on it.
- That the `-partN` split is *driven by* the 65535 ceiling. Consistent with
  every count observed, but that is correlation. Tested by whether a future
  build exceeds it.
- Whether datasheet *schemas* are stable across builds. Governs how much
  Track S work a patch invalidates.

### Noticed, out of scope

- `object-stream-converter` (slices, timelines, `.*db`, AZCS) and
  `asset-catalog-parser` ship in the same toolkit and would likely say a lot
  about the replicated-object model. **That is P5, not D2** -- recorded, not
  acted on, per the CHUNKS shared preamble.
- Nothing anti-cheat-adjacent was encountered or pursued.

### What this unblocks

Track S has its content source. The item/vitals/ability tables are
server-authoritative content (gear score bounds, perk slots, base vitals) --
what S2/S3 need. **Nothing here bears on T1-T5**; the transport track is
unaffected.

---

""".replace("__MARKER__", MARKER)

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

BUILD_FILLED = ("**New World: Aeternum**, appid 1063730, **buildid 22469132**, "
                "installdir `New World`. Installer/depot **NOT yet pinned** "
                "-- see S8.")

CHUNKS_STUB = (
    "- **D2 Client game-data extraction.** **DONE 2026-08-29** -- prompt in "
    "`D2_PROMPT.md`, findings in STATE S8. Paks are standard ZIP; "
    "compression method 15 is Oodle. **2250 datasheets**, all in "
    "`SharedDataStrm-part{1..11}.pak` + base -- *not* `GameData.pak`, and "
    "there is no `assets/server/server.pak` in build 22469132 despite the "
    "tool README. Extracted and converted to JSON with localization applied "
    "via new-world-tools @ `e51c79a9`, built natively on Linux. Track S has "
    "its content source."
)

# ---------------------------------------------------------------- edits

def main():
    repo = find_repo()
    if repo is None:
        sys.exit("Could not find the NWLY checkout (a directory containing "
                 "STATE.md and CHUNKS.md).\nRun this from inside the repo.")
    print("repo: %s\n" % repo)

    state_p, chunks_p = repo / "STATE.md", repo / "CHUNKS.md"
    state, chunks = state_p.read_text("utf-8"), chunks_p.read_text("utf-8")
    orig_state, orig_chunks = state, chunks
    done, failed = [], []

    if MARKER in state:
        sys.exit("Already folded (D2 marker present in STATE.md). Nothing "
                 "to do.")

    # STATE: insert S8 before S13
    m = re.search(r"^##\s*13\.\s*Corrections", state, re.M)
    if m:
        state = state[:m.start()] + STATE_SECTION + state[m.start():]
        done.append("STATE.md: inserted S8 immediately before S13 "
                    "(append-only, nothing above it touched)")
    else:
        failed.append("STATE.md: '## 13. Corrections' not found. S8 NOT "
                      "inserted.")

    # STATE: S13 corrections
    before = state
    state = re.sub(r"^\|\s*\*\(none yet\)\*\s*\|\s*\|[ \t]*\n",
                   CORRECTION_ROWS, state, count=1, flags=re.M)
    if state != before:
        done.append("STATE.md: added 5 rows to S13 Corrections "
                    "(3 against my own earlier claims)")
    else:
        failed.append("STATE.md: S13 '*(none yet)*' row not found. "
                      "Corrections NOT added.")

    # STATE: S14 test log
    before = state
    state = re.sub(r"^\|\s*\*\(none yet\)\*\s*\|\s*\|\s*\|\s*\|[ \t]*\n",
                   LOG_ROWS, state, count=1, flags=re.M)
    if state != before:
        done.append("STATE.md: added 5 rows to S14 Test / capture log")
    else:
        failed.append("STATE.md: S14 '*(none yet)*' row not found. "
                      "Log rows NOT added.")

    # STATE: S5 build placeholder
    ph = "`<record exact version + kept installer>`"
    if ph in state:
        state = state.replace(ph, BUILD_FILLED, 1)
        done.append("STATE.md: filled the S5 'Client build under test' "
                    "placeholder with buildid 22469132")
    else:
        failed.append("STATE.md: S5 build placeholder not found. Left alone.")

    # CHUNKS: tick D2
    before = chunks
    chunks = re.sub(r"(\|\s*)`\[ \]`(\s*\|\s*\*\*D2\*\*)",
                    r"\1`[x]`\2", chunks, count=1)
    if chunks != before:
        done.append("CHUNKS.md: ticked D2 in the Track D index")
    else:
        failed.append("CHUNKS.md: could not tick the D2 row. Change `[ ]` "
                      "to `[x]` by hand.")

    # CHUNKS: replace the D2 stub bullet
    before = chunks
    chunks = re.sub(
        r"-\s*\*\*D2 Client game-data extraction\.\*\*.*?(?=\n-\s\*\*|\n\n|\Z)",
        lambda _: CHUNKS_STUB, chunks, count=1, flags=re.S)
    if chunks != before:
        done.append("CHUNKS.md: replaced the D2 stub with the completion note")
    else:
        failed.append("CHUNKS.md: D2 stub bullet not found. Left alone.")

    # write
    stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    for path, new, old in ((state_p, state, orig_state),
                           (chunks_p, chunks, orig_chunks)):
        if new != old:
            shutil.copy2(path, path.parent / (path.name + ".bak-" + stamp))
            path.write_text(new, "utf-8")

    for d in done:
        print("  ok    " + d)
    for f in failed:
        print("  FAIL  " + f)

    if not done:
        print("\nNothing written -- every edit failed to match.")
        return

    print("\nBackups: *.md.bak-%s" % stamp)
    print("Check with:  git -C %s diff" % repo)
    print("\nStill outstanding, neither of which a script can do:")
    print("  - D2_PROMPT.md cites a STATE S10 that does not exist")
    print("  - the Steam depot manifest is not pinned; buildid alone will")
    print("    not re-download this tree once Steam moves on")


if __name__ == "__main__":
    main()
