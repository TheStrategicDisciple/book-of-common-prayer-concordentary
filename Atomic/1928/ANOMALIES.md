# ANOMALIES.md
## Batch 09 — prayers-and-thanksgivings
### Date: 2026-08-22

---

## ANOMALY-001

- **File:** `09_prayers-and-thanksgivings.md`
- **Date:** 2026-08-22
- **Shape:** prayer / post-sermon collect
- **Issue:** The six post-sermon collects under `### COLLECTS.` have no individual headings in the source — they appear as bare paragraphs under a single section header. Their titles and `concord_id` values were slugged from their first distinctive line, not from a named heading.
- **Options:** Titles as assigned are stable and descriptive. No action required unless a future edition assigns formal titles.
- **Status:** OPEN

---

## ANOMALY-002

- **File:** `09_prayers-and-thanksgivings.md`
- **Date:** 2026-08-22
- **Shape:** prayer / bidding
- **Issue:** `page_ref` cannot be determined from the source Markdown file. Physical hardcopy verification required.
- **Options:** Verify against 1928 hardcopy and populate `page_ref` during the 1.0.0 review pass.
- **Status:** OPEN

---

## ANOMALY-003

- **File:** `09_prayers-and-thanksgivings.md`
- **Date:** 2026-08-22
- **Shape:** thanksgiving / personal
- **Issue:** `thanksgiving-after-childbirth.md` uses italicized placeholders (*this woman*, *servant*, *she*, *her*, *partaker*) indicating a fill-in-the-blank rubric pattern identical to personal prayers. The `subcategory` was set to `personal` to match this pattern. The 1928 BCP places it under `### THANKSGIVINGS.` with no subcategory distinction.
- **Options:** Current assignment is defensible. Flag for review if the engine needs finer subcategory granularity.
- **Status:** OPEN

---

## ANOMALY-004

- **File:** `09_prayers-and-thanksgivings.md`
- **Date:** 2026-08-22
- **Shape:** all
- **Issue:** `page_ref` is null for all 17 files produced in this session (bidding prayer, 6 post-sermon collects, 10 thanksgivings). The source Markdown does not carry page numbers. All require hardcopy verification during the 1.0.0 review pass.
- **Options:** Batch-populate `page_ref` after hardcopy review.
- **Status:** OPEN
