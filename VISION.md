# The Concordentary
## Project Vision & Founding Document
*Drafted: May 2026*

---

> *"It is a most invaluable part of that blessed liberty wherewith Christ hath made us free..."*
> — BCP Preface, 1789

---

## What This Is

The Concordentary is a structured, version-controlled, machine-readable Markdown repository of the Book of Common Prayer across its major editions — built for preservation, scholarly comparison, and living daily use.

The name holds the mission: **Concordance** (the text, structured and searchable) + **Commentary** (the apparatus, the lineage, the editorial voice) = **Concordentary**.

It is not a replacement for the pew edition. It is the thing that exists after the servers go dark.

---

## Why It Exists

In the 1990s, John Goodwin, Michael Bushnell, and others typed the Book of Common Prayer into ASCII and gave it freely to anyone who could find it. Charles Wohlers of Satucket Software took those files, converted them to WordPerfect, built a comparative HTML apparatus across multiple editions, and hosted them through the Society of Archbishop Justus at justus.anglican.org for thirty years.

That site is slowly becoming less functional. No HTTPS. No mobile. PDFs fragmented for slow connections that no longer exist. The root domain returns 404 when clicked from major search engines. It is still there, but it is much harder to get to.

The Concordentary is the handoff.

It carries forward what they started: same spirit, same conditions, updated for a world that reads on phones, queries APIs, and builds on GitHub.

---

## The Dual Mission

**1. Preservation**
Rescue and properly structure the full BCP corpus — 1662, 1789, 1892, 1928, 1979 — before the existing digital sources decay further. Make the texts durable, citable, and future-proof in plain Markdown that will be readable in fifty years regardless of what software exists.

**2. Accessibility**
Make the preserved text genuinely useful to a modern audience. A priest doing Morning Prayer on their phone at 6am. A seminarian comparing how a collect changed across editions. A developer building a worship planning app. A layperson who has never heard of the 1928 BCP but wants to pray something ancient and beautiful today.

The form must serve both missions simultaneously.

---

## Editions in Scope

| Edition | Tradition | Status |
|---------|-----------|--------|
| 1662 | Church of England | Planned |
| 1789 | PECUSA | Planned |
| 1892 | PECUSA | Planned |
| 1928 | PECUSA | In progress — primary build target |
| 1979 | Episcopal Church | Pending copyright |

The 1928 is the anchor edition. All schema decisions are made against it first. Every other edition slots into the established structure.

Note: 1552, 1559, 1604 are tracked in provenance lineage for scholarly completeness but are not primary build targets at this time.

---

## The Attribution Chain

| Generation | Contributor | Medium | Era |
|---|---|---|---|
| 1 | John Goodwin, Michael Bushnell, and others | ASCII | 1993 |
| 2 | Charles Wohlers, Satucket Software | WordPerfect / HTML | 1996–2026 |
| 3 | Society of Archbishop Justus | Hosting / preservation | 1994–present |
| 4 | Alex Nutting, Liturgic Labs Studio | Markdown / schema / formation layer | 2026– |

Each generation carried the text forward in the medium of their moment. The Concordentary is the fourth generation.

---

## Key Outputs

### 1. The Repository
A clean, structured, versioned Markdown corpus. The most usable, properly-schemed BCP text collection that exists digitally. Citable in academic work via semantic versioning (v1.0.0, v1.1.0, etc.).

### 2. `today.md`
Regenerated every morning by a GitHub Action. Structure:

```
# [Season] — [Color]
[One sentence of liturgical context]

## Today's Hymn
[Title] — Hymnal 1982 #N
[Hymnary link] [Spotify link]

## Collect of the Week
[Text]

## Daily Psalms
Morning: Psalm N, N
Evening: Psalm N, N

## Lessons
Morning: [OT reference] · [NT reference]
Evening: [OT reference] · [NT reference]

## Full Office
[[01_morning-prayer]] · [[02_evening-prayer]]
[[_hymnody/season-hymnody]]
```

Five minutes to orient. Two clicks to go deeper. Everything else is there if they want it.

### 3. The Animated README
A season-aware SVG banner regenerated nightly. Violet in Advent and Lent. White and gold at Christmas and Easter. Deep crimson at Pentecost. Quiet green through Ordinary Time. Illuminated manuscript aesthetic. The repository breathes with the church year.

### 4. The Formation Layer (`_study/`)
One companion note per canonical file. Written in plain language. Explains why the prayers are shaped the way they are, where they came from, what they do to a person over time. The thing that turns atmosphere into formation.

### 5. The Hymnody Layer (`_hymnody/`)
Musical curation linked to each canonical file. Curated from the Hymnal 1940, Hymnal 1982, and LEVAS. Referenced via Hymnary.org and Spotify. The 365-day hymn spreadsheet feeds `today.md` automatically.

### 6. The Raw API
Via GitHub Pages — structured Markdown with consistent frontmatter is already structured data. A simple JSON feed makes The Concordentary the infrastructure layer for any developer building liturgical tools.

### 7. concordentary.org
The accessibility bridge. Three things:
- What this is in plain English
- How to get it — GitHub, Obsidian vault download, eventually a plugin
- What you will see when you open it

No jargon. No assumptions. A priest who has never heard of GitHub should be able to get there in three clicks.

---

## The User Journey

**Casual user — five minutes**
Color, hymn, collect, psalms. Done. Oriented for the day.

**Curious user — fifteen minutes**
Taps one link. Reads the formation note. Learns why the collect is shaped that way. Understands something they have been praying without knowing.

**Scholar — open ended**
Follows the provenance thread. Sees the 1662 variant. Reads Charles's annotation via ref_interim link. Follows through to the 1883 committee report. Spends an hour.

Same entry point. Three depths. Nobody excluded. Nobody forced deeper than they want to go.

---

## Calendar Architecture

The liturgical calendar is the engine. Everything computes from Easter.

### What the engine produces for any given date:
- Liturgical season
- Liturgical color
- The governing Sunday collect
- Morning and Evening Prayer lectionary readings
- The day's psalms (30-day Psalter rotation)
- Upcoming feasts and fasts
- Today's hymn from the 365-day spreadsheet

### The Rosetta Stone field — `sunday_normalized`
Different editions name Sundays differently. 1662 and 1928 count Sundays after Trinity. 1979 counts Sundays after Pentecost. The engine uses one normalized key. Human-readable tradition-specific labels appear alongside it.

```yaml
sunday_normalized: "easter+7w"
sunday_1928: "sunday-after-ascension"
sunday_1979: "easter-7"
sunday_1662: "sunday-after-ascension"
```

---

## The Locked Schema

Every file in the repository carries consistent YAML frontmatter:

```yaml
---
title: ""
edition: "1928"
tradition: PECUSA
collection: BCP 1928
source_url: ""
transcriber_original: "John Goodwin, Michael Bushnell, and others — ASCII, 1993"
transcriber: "Charles Wohlers, Satucket Software"
markdown_curation: "Alex Nutting, Liturgic Labs Studio"
license: CC BY-NC-SA 4.0
license_url: "https://creativecommons.org/licenses/by-nc-sa/4.0/"
source_terms: "Non-commercial redistribution permitted with header intact — Charles Wohlers, Satucket Software"
converted_at_utc: ""

provenance:
  first_appeared: ""
  carried_forward:
    - edition: "1662"
      ref: "[[../1662/]]"
      ref_interim: ""
      status: "planned"
    - edition: "1789"
      ref: "[[../1789/]]"
      ref_interim: ""
      status: "planned"
    - edition: "1892"
      ref: "[[../1892/]]"
      ref_interim: ""
      status: "planned"
    - edition: "1928"
      ref: "[[]]"
      ref_interim: null
      status: "complete"
    - edition: "1979"
      ref: "[[../1979/]]"
      ref_interim: null
      status: "pending-copyright"
  modified_in: null
  dropped_in: null
  notes: ""

category: ""
subcategory: ""
page_ref: ""
liturgical_season: null
liturgical_color: null
sunday_normalized: null
sunday_1928: null
sunday_1979: null
sunday_1662: null
feast: null
fast: null
tags: []

active_in_edition: true
language: en
language_variant: early-modern

hymnody:
  companion: null
  notes: ""

file_version: 0.9.0
last_reviewed: null
reviewed_against: null
review_notes: ""
---
```

### File version convention:
- `0.9.0` — cleaned, schema applied, awaiting hardcopy verification
- `1.0.0` — verified against hardcopy or authoritative scan
- `1.x.0` — minor corrections post-verification
- `2.0.0` — major revision (provenance fields populated after comparison pass)

---

## The `dropped_in` Principle

Rites that disappear across editions are as theologically significant as rites that survive.

```yaml
provenance:
  first_appeared: "1662"
  dropped_in: "1928"
  notes: "Removed in the 1928 revision. No equivalent appears in subsequent PECUSA editions. The pastoral theology of accompanying the condemned, present in Anglican practice for nearly 300 years, was quietly retired without documented explanation."
```

The Concordentary does not erase absences. It documents them.

---

## Folder Structure

```
/
├── VISION.md               ← this document
├── README.md               ← public face
├── AGENTS.md               ← agent navigation
├── SCHEMA.md               ← full schema reference
├── SOURCES.md              ← source attribution
├── CITE.md                 ← citation guidance
├── CONTRIBUTING.md         ← contribution rules
├── humans.md               ← human story
├── robots.md               ← AI intent statement
├── HEADER                  ← Wohlers distribution notice
├── LICENSE                 ← CC BY-NC-SA 4.0
├── today.md                ← generated daily by GitHub Action
│
├── 1662/
├── 1789/
├── 1892/
├── 1928/
│   ├── 01_morning-prayer.md
│   ├── 02_evening-prayer.md
│   └── ... (25 files total)
├── 1979/
│
├── _atomic/
│   ├── offices/
│   ├── collects/
│   ├── epistles/
│   ├── gospels/
│   ├── canticles/
│   ├── creeds/
│   ├── litany/
│   ├── prayers/
│   └── psalter/
│
├── _engine/
│   └── computus.py
│
├── _study/
├── _hymnody/
│
└── _data/
    ├── calendar.json
    ├── validation/
    └── hymns-365.csv
```

---

## Build Sequence

**Phase 1 — 1928 Canonical Files** ← in progress
25 files. One at a time. Verified 1.0.0 against hardcopy or authoritative scan.

**Phase 2 — Supporting Files**
SOURCES.md, CITE.md, CONTRIBUTING.md, SCHEMA.md

**Phase 3 — Calendar Engine & GitHub Action**
Computus engine. `today.md` generation. Animated SVG README. First live output.

**Phase 4 — Hymn Spreadsheet**
365-day hymn curation. One liturgical year. Cycles annually.

**Phase 5 — Atomic Extracts**
One batch pass after all canonical files are at 1.0.0.

**Phase 6 — Formation Layer**
`_study/` notes. One per canonical file. Written in plain language.

**Phase 7 — Hymnody Layer**
`_hymnody/` companion notes. Linked from canonical files.

**Phase 8 — Additional Editions**
1662 → 1789 → 1892. Each slots into established schema.

**Phase 9 — API**
GitHub Pages JSON feed. Developer documentation.

**Phase 10 — concordentary.org**
Landing page. Obsidian primer. GitHub primer.

---

## Evidence Artifacts

Three screenshots taken the night this project began, May 22–23, 2026:

**Exhibit A — The 404**
justus.anglican.org returning Not Found on mobile. The authoritative Anglican digital resource. Not Secure. Not Found.

**Exhibit B — The Tribute**
Google's AI Overview describing Charles Wohlers as the compiler of "one of the most comprehensive digital resources for the Book of Common Prayer." The legacy acknowledged. The infrastructure failing.

**Exhibit C — The Landscape**
Search results for "1928 BCP": Wikipedia describing the wrong book. A site frozen since 2007. Reddit threads of confused Episcopalians. The gap where something important should be.

---

## Licensing

**CC BY-NC-SA 4.0**

- *"No fee charged"* → Non-Commercial (NC)
- *"This header remains"* → Attribution (BY)
- Spirit carried forward → Share-Alike (SA)

The BCP texts themselves are public domain. The structure, schema, editorial decisions, provenance apparatus, formation notes, hymnody curation, and Concordentary architecture are the intellectual work of this project, licensed CC BY-NC-SA 4.0.

Institutions or developers seeking alternative licensing: thestrategicdisciple@gmail.com

---

*The Book of Common Prayer belongs to the Church.*
*This repository simply preserves it in a living, accessible form.*

*Corrections, contributions, and notes: thestrategicdisciple@gmail.com*
*concordentary.org — coming 2026*
