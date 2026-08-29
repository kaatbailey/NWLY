# D2 — Client game-data extraction (`.datasheet`)

*Paste order for the session: `CHARTER.md`, then `STATE.md`, then this prompt.
D2 has no chunk dependencies and takes no upstream FINDINGS block as input.*

---

## What this chunk is

New World ships its game data — item stats, recipes, spawn tables, damage
numbers, everything Track S will eventually need to serve — as `.datasheet` files
packed inside the client's pak archives. **D2 extracts that data into a readable,
queryable form.** It is a parallel track: it depends on nothing and nothing in
Track T/H/P depends on it, but Track S cannot serve a world without it, so it is
worth banking early while the transport work proceeds.

**Deliverable is data plus a short document**: the extracted datasheets in a
structured format (CSV/JSON per sheet, or a small SQLite db), and a page in STATE
recording how they were extracted, what the format is, and what is in it.

## Why now

CHUNKS calls this low-effort and community-tooled, and T1 just confirmed the
engine is stock GridMate/Lumberyard (STATE §10) — which means the asset pipeline
is stock Lumberyard too, and the community tools written for it should apply
directly. This is the cheapest available forward motion that does not touch EAC.

## Hard constraints (CHARTER §3 — read before starting)

- **This is extraction for interoperability research, not redistribution.** The
  charter forbids shipping Amazon's client, assets, or binaries. Extracted data
  stays local, feeds the server's own re-implementation, and is **not committed to
  the repo** and **not redistributed**. Record *how* to extract and *what the
  schema is*; do not check in the extracted content itself.
- **Read-only against the install.** Do not modify anything under the game
  directory. Copy paks out before operating on them if a tool needs write access.
- **No client launch, no injection, no anti-cheat contact.** D2 is pure offline
  file work. If any tool wants to hook or run the client, it is the wrong tool.
- Add `*.datasheet`, extracted data dirs, and any copied `.pak` to `.gitignore`
  as the first step, so nothing lands in git by accident.

## Method

1. **Locate the paks.** Find the archive files under the install:
   `find ~/.steam/steam/steamapps/common/"New World" -iname '*.pak' -o -iname '*.rda' 2>/dev/null | head`.
   Record the layout in the findings — directory, file count, rough total size,
   naming scheme.
2. **Identify the container format.** New World's paks are a known format; confirm
   which by the header bytes of one file rather than assuming. State the magic
   bytes observed.
3. **Pick community tooling and name it explicitly.** There are established New
   World datasheet extractors and pak unpackers. Whichever is used, record the
   exact tool, version, and command line — the charter's re-derivability rule
   (§4) means a future session must be able to repeat this, and "some tool I
   found" is not repeatable.
4. **Extract one datasheet end to end first.** Prove the pipeline on a single
   sheet before bulk-extracting: unpack → locate a `.datasheet` → convert to
   readable form → open it and confirm the columns make sense. A wrong tool that
   produces plausible-looking garbage is the failure mode to guard against.
5. **Then bulk-extract**, and inventory what came out: how many sheets, roughly
   what categories (items / recipes / vitals / spawns / …), and the row/column
   shape of a few representative ones.

## Definition of done

- The pak format named, with the observed magic bytes.
- The extraction tool and exact command recorded, repeatably.
- At least one datasheet extracted, opened, and confirmed sane column-by-column.
- A bulk extraction completed and inventoried (count + categories + a couple of
  example schemas).
- A STATE findings block (§ next free number) capturing all of the above.
- `.gitignore` updated so no extracted asset or pak is tracked.

## Falsification / things that would change the picture

- **Predict before extracting:** stock Lumberyard `.datasheet` format, readable by
  existing community tools with no custom parser needed. If instead the format is
  bespoke or the community tools fail on this build, that is the finding — record
  what broke, and whether it looks like a New-World-specific change or an
  anti-tamper wrapper (if the latter, note it and **stop** — §3 puts anti-tamper
  out of scope).
- If the datasheets turn out to be encrypted or obfuscated at rest, say so; that
  materially changes Track S's cost and is worth knowing now.

## Non-goals for D2

- No parsing of *every* sheet's semantics — that is later, per-feature work. D2
  gets the data *out* and proves the pipeline; understanding each sheet's meaning
  happens when a server feature needs it.
- No transport, no hooking, no protobuf work (that flag from T1/§10 belongs to
  the P-track, not here).
- Nothing committed that is Amazon's content.

## When done

Write the FINDINGS block in the format at the foot of `CHUNKS.md`, hand it back,
and fold it into `STATE.md` (adding, never deleting) before starting anything
else. Do not start another chunk in the same session.
