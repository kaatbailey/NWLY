#!/usr/bin/env python3
"""
add_d2_section.py -- insert the D2 findings as STATE §11 and refill the §5
build placeholder.

Both were lost when STATE.md was rolled back to a pre-fold backup. The §13
and §14 rows survived (they were written after the rollback) and are NOT
touched here.

Inserts §11 above the "## 8+. Reserved" placeholder, where §8/§9/§10 sit.
No arguments. Backs the file up first. Safe to run twice.

    python3 add_d2_section.py
"""

import pathlib
import re
import shutil
import sys
from datetime import datetime

SECTION = """\
## 11. Client game data (`.datasheet`) — CONFIRMED from D2

Folded from FINDINGS — D2 — 2026-08-29. Pure offline file work: no client
launch, no injection, read-only against the install (CHARTER §3 satisfied).

**Build under test:** New World: Aeternum, Steam appid 1063730, **buildid
22469132**, installdir `New World`, SizeOnDisk 76,416,676,920 (~71.2 GiB), at
`/home/kaatlev/.local/share/Steam/steamapps/common/New World`.

### The pak container is standard ZIP

- `50 4b 03 04` at offset 0; the first local header parses cleanly — 41 bytes
  stored, filename length 0x24 = `libs/flownodes/flownodeblacklist.xml`.
- **130 `.pak`** under `assets/`, ~72G on disk, naming `<Name>[-partN].pak`.
  All 130 open as zip; **0 failures**.
- **Compression method 15 = Oodle.** Not a standard ZIP method id (0 store,
  8 deflate, 9 deflate64, 12 bzip2, 14 LZMA, 93 zstd). Python `zipfile` can
  enumerate method-15 entries but cannot `read()` them — it is a census tool
  here, not an extraction tool.
- **No Zip64 anywhere.** EOCD 16-bit entry counts are genuine, not saturated:
  a direct `PK\\x01\\x02` central-directory walk gave `walked == eocd` on
  every pak, including the four sitting exactly on 65535. The packer rolls to
  a new `-partN` at the 65535 ceiling — that is what the part numbering is
  for. See §13 and §14 for the falsified saturation hypothesis.

### Where the datasheets are

**2250 total**, confined entirely to `SharedDataStrm*`. `GameData.pak` holds
none, despite the name (§13).

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

- **Two independent code paths agree on 2250** — the hand-rolled
  central-directory census and `pak-extracter`. Neither is silently dropping
  entries.
- **Verified column-by-column**, not by file count.
  `MasterItemDefinitions_Faction`: **127 columns × 4121 rows**, legible
  headers (`ItemID`, `ItemType`, `TradingCategory`, `GearScoreOverride`,
  `PerkSlot1`). Not plausible-looking garbage, which is the D2 prompt's named
  failure mode.
- **Localization is a separate 184-file tree** under `localization/en-us`.
  Datasheet string fields are `@Key` lookups (e.g. `@DyeB179_Name`) resolved
  by the converter's `-localization` flag.

### Tooling (re-derivable per CHARTER §4)

- **github.com/new-world-tools/new-world-tools**, MIT, pure Go, v0.13.10,
  commit **`e51c79a9af4fba51daecd97c5e190c0b5ee953a5`**
  (Wed Nov 5 04:04:28 2025 +0300), cloned to `~/Documents/new-world-tools`.
- Builds natively on Garuda with `go build -o ./bin/ ./cmd/...` — produces
  `pak-extracter`, `datasheet-converter`, `object-stream-converter`,
  `asset-catalog-parser`. No wine, no cgo.
- **The tool downloads binary libraries from the network on first run** —
  Oodle v2.9.13 and `libtexconv.so`, `dlopen`ed via `ebitengine/purego`.
  Not found under the repo, `~/.cache`, `~/.local/share` or `~/.config` at
  depth 5; **location unresolved**. Matters for any air-gapped or
  reproducible re-run.
- The tool README documents `assets/server/server.pak` as the datasheet
  source. **That path does not exist in this build** (§13).

**The recipe:**

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

Runtimes: extract **540ms** (peak 7.5Mb) · convert **15.4s** (peak
**2297Mb** — the converter is the memory hog, worth knowing on a smaller box).

Outputs, gitignored and outside the repo (CHARTER §3 — not redistributed):
`~/Documents/nwly-extract` (211M raw), `~/Documents/nwly-datasheets`
(499M JSON, 2250 files).

### UNVERIFIED — the loose ends

- **No installer/depot pinned.** buildid 22469132 *identifies* this build but
  will not re-download it. Manifest ids are in
  `~/.local/share/Steam/depotcache/` or the appmanifest's `InstalledDepots`
  block. **Pin them before the next game patch** (CHARTER §4 version-lock).
  This is the only item here with a clock on it.
- That the `-partN` split is *driven by* the 65535 ceiling. Consistent with
  every count observed, but correlation. Tested by whether a future build
  exceeds it.
- Whether datasheet *schemas* are stable across builds. Governs how much
  Track S work a patch invalidates.

### Noticed, out of scope

- `object-stream-converter` (slices, timelines, `.*db`, AZCS) and
  `asset-catalog-parser` ship in the same toolkit and would likely say a lot
  about the replicated-object model — **that is P5, not D2.** Recorded, not
  acted on, per the CHUNKS shared preamble.
- Nothing anti-cheat-adjacent was encountered or pursued.

### What this unblocks

Track S has its content source. The item/vitals/ability tables are
server-authoritative content (gear score bounds, perk slots, base vitals) —
what S2/S3 need. **Nothing here bears on T1–T5**; the transport track is
unaffected.

---

"""

BUILD_FILLED = ("**New World: Aeternum**, appid 1063730, **buildid 22469132**, "
                "installdir `New World`, ~71.2 GiB. Installer/depot **NOT yet "
                "pinned** — see §11.")

PLACEHOLDER = "`<record exact version + kept installer>`"


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

    p = repo / "STATE.md"
    text = p.read_text("utf-8")
    original = text
    done, failed = [], []

    # 1. insert §11
    if re.search(r"^## 11\. Client game data", text, re.M):
        done.append("§11 already present")
    else:
        lines = text.split("\n")
        anchor = next((i for i, l in enumerate(lines)
                       if l.startswith("## 8+.")), None)
        where = "above the '## 8+. Reserved' placeholder, with §8–§10"
        if anchor is None:
            anchor = next((i for i, l in enumerate(lines)
                           if l.startswith("## 13.")), None)
            where = "before §13"
        if anchor is None:
            failed.append("no '## 8+.' or '## 13.' anchor found. "
                          "§11 NOT inserted.")
        else:
            lines[anchor:anchor] = SECTION.split("\n")
            text = "\n".join(lines)
            done.append("inserted §11 %s" % where)

    # 2. refill the §5 build placeholder
    if PLACEHOLDER in text:
        text = text.replace(PLACEHOLDER, BUILD_FILLED, 1)
        done.append("refilled the §5 'Client build under test' placeholder "
                    "(buildid 22469132, cross-referenced to §11)")
    elif "buildid 22469132" in text.split("## 6.")[0]:
        done.append("§5 build placeholder already filled")
    else:
        failed.append("§5 placeholder not found and not obviously filled — "
                      "check line ~130 by hand.")

    if text != original:
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        shutil.copy2(p, p.parent / (p.name + ".bak3-" + stamp))
        p.write_text(text, "utf-8")
        print("wrote STATE.md  (backup: STATE.md.bak3-%s)\n" % stamp)

    for d in done:
        print("  ok    " + d)
    for f in failed:
        print("  FAIL  " + f)

    print("\nVerify:")
    print("  rg -n '^## ' STATE.md")
    print("  rg -n 'D2|22469132' STATE.md | head")
    print("\nExpect §11 between §10 and '## 8+.', and no duplicate numbers.")


if __name__ == "__main__":
    main()
