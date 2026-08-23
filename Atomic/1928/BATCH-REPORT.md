# BATCH-REPORT.md
## Batch 09 — 09_prayers-and-thanksgivings.md
### Completed: 2026-08-22

---

## 1. Files Processed

- `09_prayers-and-thanksgivings.md`

---

## 2. Atoms Produced

**Total: 45 atomic files**

| Folder | Count |
|--------|-------|
| `prayers/civic/` | 9 |
| `prayers/general/` | 11 |
| `prayers/occasional/` | 8 |
| `prayers/personal/` | 8 |
| `prayers/bidding/` | 1 |
| `prayers/post-sermon/` | 6 |
| `thanksgivings/` | 10 |
| **Total** | **45** |

---

## 3. Anomalies Logged

4 anomalies — ANOMALY-001 through ANOMALY-004. All OPEN.

- ANOMALY-001: Post-sermon collects lacked individual headings; titles slugged from first line.
- ANOMALY-002: `page_ref` unknown for bidding prayer.
- ANOMALY-003: `thanksgiving-after-childbirth.md` subcategory assignment judgment call.
- ANOMALY-004: `page_ref` null for all 17 files produced in session 2; requires hardcopy verification.

---

## 4. Schema Decisions

- **Post-sermon collects** (`subcategory: "post-sermon"`): The 1928 source groups these under a `### COLLECTS.` heading distinct from the main Prayers section. A new subcategory `post-sermon` was created to reflect this. The folder `prayers/post-sermon/` mirrors that distinction.
- **Bidding prayer** (`subcategory: "bidding"`): Treated as its own subcategory given its unique liturgical form (congregational address, minister-directed, clausally variable). Not a collect, not a personal prayer.
- **Thanksgivings category**: `category: "thanksgiving"` honored throughout, per Example B in Section 12. The 1928 BCP distinguishes Prayers from Thanksgivings as separate sections.
- **`prov_first`**: Set to `"1662"` for all items traceable to the 1662 BCP. Set to `"1928"` for the bidding prayer, which is an American form without clear 1662 precedent in this exact form.
- **Alt prayers** (`for-missions-alt.md`, `for-holy-orders-alt.md`, `for-fruitful-seasons-alt.md`): The source offers alternative texts under `*¶ Or this.*` rubrics. Each alternative received its own atomic file with `-alt` suffix.

---

## 5. Recommended Next Steps

1. **Hardcopy verification pass**: Populate `page_ref` for all 45 files. Bump verified files from `file_version: "0.9.0"` to `"1.0.0"`.
2. **Provenance review**: Confirm `prov_first` values against liturgical history sources, particularly for the civic prayers (Congress, Army, Navy, Memorial Days) which are American additions.
3. **Modern equivalents**: Populate `modern_equivalent` for files where a BCP 1979 equivalent is identifiable. Currently null for most thanksgivings.
4. **Next source file**: Proceed to `13_collects-epistles-gospels.md` for the Sunday Proper collects. A worked example for that content shape is required before the batch runs (per Section 12 of RULES.md).

---

## Session Notes

This batch ran across two conversation sessions due to context window limits. Session 1 produced 28 files (civic, general, occasional, personal prayers). Session 2 produced 17 files (bidding prayer, post-sermon collects, thanksgivings) using a Python writer script (`write_atom.py`) developed to resolve tool call streaming failures with large parameter strings. The writer script protocol is documented in RULES.md Section 14.
