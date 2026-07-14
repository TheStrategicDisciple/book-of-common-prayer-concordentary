# Agents.md — The Concordentary

> A version-controlled, schema-structured Markdown archive of the Book of Common Prayer across major editions. This file tells any AI agent how to read, navigate, and work within this repository.

---

## What This Repository Is

The Concordentary is a structured digital archive of the Book of Common Prayer in major American and English editions (1662, 1789, 1892, 1928, 1979). Each edition is encoded in plain Markdown with a locked YAML provenance schema. The project extends and preserves the digitization work of Charles Wohlers (Satucket Software, justus.anglican.org), adding scholarly structure, cross-edition traceability, and a liturgical calendar engine.

**Maintainer:** Alex Nutting / The Strategic Disciple LLC  
**License:** CC BY-NC-SA 4.0 (texts public domain; structure, schema, and editorial apparatus licensed)  
**Canonical URL:** repo.thestrategicdisciple.com  

---

## Folder Structure

```
/
├── AGENTS.md               ← you are here
├── VISION.md               ← project purpose and long-range goals
├── SCHEMA.md               ← full YAML frontmatter specification
├── SOURCES.md              ← source attribution and provenance chain
├── CITE.md                 ← citation guidance for scholars
├── CONTRIBUTING.md         ← contribution rules
├── README.md               ← season-aware, generated
├── today.md                ← generated daily by GitHub Action
│
├── 1662/                   ← Church of England edition
├── 1789/                   ← First American edition
├── 1892/                   ← PECUSA revision
├── 1928/                   ← Primary active edition (most complete)
│   ├── 01_morning-prayer.md
│   ├── 02_evening-prayer.md
│   ├── 03_prayers-and-thanksgivings.md
│   └── ... (25 files total, see file index below)
├── 1979/                   ← Episcopal Church edition (pending copyright clearance)
│
├── _atomic/                ← Cross-edition extracts (canticles, collects, creeds, prayers)
│   ├── canticles/
│   ├── collects/
│   ├── creeds/
│   └── prayers/
│
├── _study/                 ← Formation notes, one per canonical file
├── _hymnody/               ← Musical curation, linked from canonical files
│
└── _data/
    ├── calendar.json       ← Liturgical calendar data
    └── hymns-365.csv       ← 365-day hymn curation
```

---

## File Naming Convention

All canonical BCP files use a zero-padded numeric prefix for sort order:

```
NN_kebab-case-title.md
```

Example: `01_morning-prayer.md`, `15_offices-of-instruction.md`

Edition folders mirror the same filenames where the same rite appears across editions. This enables direct cross-edition comparison by filename.

---

## YAML Frontmatter Schema

Every canonical file opens with a YAML frontmatter block. Do not modify frontmatter fields without understanding the full schema (see `SCHEMA.md`). Key fields:

```yaml
---
title: ""                    # Full liturgical title
bcp_version: ""              # Edition year as string: "1928"
tradition: ""                # "PECUSA" | "Episcopal Church" | "Church of England"
section: ""                  # kebab-case section identifier
page_ref: ""                 # Page number in print edition
category: ""                 # liturgical category
repository: "The Concordentary"
collection: "Digital Concord of Prayer"
transcriber: "Charles Wohlers, Satucket Software"
markdown_curation: "Alex Nutting"
source_url: ""               # Wohlers' HTML source
license: "CC BY-NC-SA 4.0"

provenance:
  first_appeared: ""         # Edition year the rite first appears
  carried_forward:
    - edition: "1662"
      ref: "[[../1662/01_morning-prayer]]"
      ref_interim: ""        # External URL fallback until file is built
      status: "planned"      # complete | planned | pending-copyright | external
    - edition: "1928"
      ref: "[[01_morning-prayer]]"
      status: "complete"
  modified_in: ""            # Edition where significant changes occurred
  dropped_in: null           # Edition where rite was removed (null if still present)
  notes: ""

hymnody:
  companion: ""              # Backlink to _hymnody/ file
  notes: ""

version: "0.9.0"             # 0.9.0 = schema applied, awaiting hardcopy verification
                             # 1.0.0 = verified against hardcopy or authoritative scan
---
```

---

## Content Formatting Standards

Agents editing or generating content must follow these conventions exactly:

| Element | Format |
|---|---|
| Rubrics | `¶ *Italic text.*` |
| Versicles (minister) | `**Minister.**` |
| Versicles (response) | `*Answer.*` |
| Q&A labels | `*Question.*` / `*Answer.*` |
| Drop caps | `**X**` first letter only — NOT bold whole word |
| Psalm pointing | `\*` (escaped asterisk) |
| Section headings | `##` or `###` — no bold emphasis within headings |
| Greek text | Render correctly — e.g., φρόνημα σαρκός with correct word-final sigma ς |
| Footnotes | Wohlers' margin annotations preserved in provenance.notes |

---

## File Status and What Agents Should Not Touch

| Status | Meaning | Agent behavior |
|---|---|---|
| `version: 1.0.0` | Verified against hardcopy | Read-only. Do not edit content. |
| `version: 0.9.0` | Schema applied, unverified | Schema edits OK. Flag content questions. |
| `status: pending-copyright` | 1979 edition | Do not generate content for these files. |
| `status: planned` | File not yet built | Do not create stubs without instruction. |

---

## 1928 Edition File Index

The 1928 edition is the primary active build. Files in order:

```
01  Morning Prayer
02  Evening Prayer
03  Prayers and Thanksgivings
04  The Litany
05  Penitential Office (Ash Wednesday)
06  Holy Communion
07  Baptism
08  Confirmation
09  Matrimony
10  Churching of Women
11  Visitation of the Sick
12  Communion of the Sick
13  Burial of the Dead
14  Burial of a Child
15  Offices of Instruction
16  [Confirmation — split from Offices of Instruction]
17  Consecration of a Church
18  Institution of Ministers
19  The Psalter
20  Articles of Religion
21  The Ordinal
22  Catechism
23  Family Prayer
24  Tables and Rules (includes TABLE I and TABLE II — first complete digital editions)
25  The Calendar
    Concerning the Service
    Psalms and Lessons Tables
    Table of Lessons 1928
    The Propers (Collects, Epistles, Gospels) — in progress
```

---

## The Computus Engine

### Design principle
The engine uses the BCP's own tables as data — not re-derived astronomical math. TABLE I (Dominical Letter) and TABLE II (Golden Number / paschal full moon) in `1928/24_tables-and-rules.md` are the authoritative source. The script reads those structured Markdown tables and looks up the answer. It does not compute lunar cycles independently.

This is intentional. It means:
- The output is faithful to how the BCP intends Easter to be calculated
- Bugs have exactly two causes: transcription error in the table data, or bug in the lookup logic
- Every output is auditable back to a primary source in the repo

### Lookup chain

```
year → Golden Number: (year + 1) mod 19  (use 19 if result is 0)
year → Jan 1 weekday → Dominical Letter (count forward to Sunday, A–G)
Golden Number → paschal full moon date  (from TABLE II)
full moon date + Dominical Letter → Easter  (from TABLE I)
Easter → all moveable feasts by fixed offset
```

### Math reference

**Golden Number:** `(year + 1) mod 19` — position in the 19-year Metonic cycle

**Dominical Letter:** Jan 1 weekday determines the letter (A = Jan 1, cycling A–G). The letter that lands on Sunday is the Dominical Letter for that year. Leap years have two Dominical Letters (the second takes effect after Feb 28).

Example — 2026: Jan 1 = Thursday = A. Count to Sunday: B, C, D. Jan 4 = Sunday. **Dominical Letter = D.**

### Validation harness

The 1979 BCP prints Easter dates through 2099. That list is the test harness. Running the 1892 lookup engine against the full 1979 printed list should produce identical output — two completely different BCP methodologies, same tradition, same answer. Any mismatch is a bug.

**Validation mode** is triggered with `--validate` flag:

```bash
python computus.py --validate --start 2026 --end 2030
```

Output is a plain list of `YEAR: Easter date` for the requested range. Compare manually against the 1979 BCP back-matter. Recommended progression: 5 years first, then 20, then full range to certify.

When validation passes, commit the output as `_data/validation_YYYY.md` — the passing run becomes part of the repo's audit trail.

### Daily cron

- Runs at 12:01 AM Eastern (5:01 UTC)
- Hits NIST time API for authoritative date
- Script reads TABLE I and TABLE II from structured Markdown in repo
- Outputs `{edition}today.md` per active edition
- Git commits the file — the commit log is the liturgical diary

### Sample output

```
Today is Monday, June 8, 2026.
You are in Ordinary Time.
This is the Second Sunday after Pentecost.
Proper 6.
Liturgical color: Green.
Psalm: 92.
Collect: "O God, whose never-failing providence..."
```

The script reads. It does not generate. The data does the work.

---

## Mirror Site Architecture

**Base:** `repo.thestrategicdisciple.com/today`

Each active edition gets its own path mirroring its `{edition}today.md` output:

| Path | Source file | Status |
|---|---|---|
| `/today/1928` | `1928today.md` | Active (primary) |
| `/today/1892` | `1892today.md` | Planned |
| `/today/1662` | `1662today.md` | Planned |
| `/today/1789` | `1789today.md` | Planned |
| `/today/1979` | `1979today.md` | Pending copyright |

The webpage renders the markdown. No database. The git commit history is the canonical record — version-controlled liturgical diary from day one.

Animated SVG in liturgical color sits above the text (green pulse in Ordinary Time, deep purple in Advent, stark white in Easter). See `_data/calendar.json` for season-to-color mappings.

**Cost: $0.** Cron job, free NIST API, Python reading Markdown from an existing repo.

---

## Common Agent Tasks

### Find a specific collect
Search `_atomic/collects/` first. If not extracted yet, search the edition folder by liturgical season or Sunday name.

### Compare a rite across editions
Files use the same filename across edition folders. Load `1892/01_morning-prayer.md` and `1928/01_morning-prayer.md` side by side. Check `provenance.carried_forward` for notes on what changed and when.

### Check what changed in an edition
Read `provenance.modified_in` and `provenance.notes`. Wohlers' variant annotations are preserved in these fields where captured.

### Find what was dropped
Query files where `provenance.dropped_in` is not null. These document rites that existed in one edition and were removed in another — theologically significant absences.

### Run the calendar engine
See `_data/calendar.json` and the GitHub Action in `.github/workflows/`. The computus script lives at `_engine/computus.py`. Depends on TABLE I and TABLE II in `1928/24_tables-and-rules.md`.

### Validate the engine
```bash
python _engine/computus.py --validate --start 2026 --end 2030
```
Compare output against 1979 BCP printed Easter dates. See validation harness section above.

### Work on the today.md generator
Requires the computus engine validated and all target edition Markdown files complete. Currently in private beta — build and test privately through fall/winter 2026–27 before any public output.

---

## Provenance Chain

```
John Goodwin & Michael Bushnell — ASCII transcription (1993)
  ↓
Charles Wohlers — WordPerfect / HTML digitization (1996–2026), Satucket Software
  ↓
Alex Nutting — custom Python script + editorial curation (2026), The Concordentary
```

All derivative work acknowledges this chain. Do not generate content that obscures or omits attribution.

---

## What This Repository Is Not

- Not a Bible or lectionary archive (BCP texts only)
- Not a commentary or theological interpretation project (formation notes in `_study/` are supplemental, not canonical)
- Not a dynamic web app (static Markdown files; the GitHub Action for `today.md` is the only dynamic layer)
- Not complete (the 1979 edition is pending copyright clearance; other editions are planned but not yet built)

---

## Scholarly Firsts Documented Here

- First complete structured Markdown Coverdale Psalter
- First digital TABLE I (Dominical Letter) in structured Markdown
- First digital TABLE II (Golden Number) covering years 1600–8400 in structured Markdown
- First digital Table of Lessons 1928 in structured Markdown

---

*Last updated: July 2026*  
*Questions: thestrategicdisciple@gmail.com*
