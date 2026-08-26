Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International (CC BY-NC-SA 4.0)

Copyright (c) 2026 Alex Nutting, The Strategic Disciple, LLC / Liturgic Labs Studio.

This repository is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License, with the following repository-specific clarifications.

You are free to:
  Share — copy and redistribute the material in any medium or format
  Adapt — remix, transform, and build upon the material

Under the following terms:
  Attribution — You must give appropriate credit to Alex Nutting (The Strategic Disciple, LLC / Liturgic Labs Studio), and to Charles Wohlers (Satucket Software) where his transcription work is used.
  NonCommercial — You may not use the material for commercial purposes.
  ShareAlike — If you remix, transform, or build upon the material, you must distribute your contributions under the same license as the original.

This repository contains materials governed by different licenses depending on their nature and origin. When in doubt, the more restrictive terms apply.

## Part I — BCP Source Text

The liturgical text of the Book of Common Prayer (1662, 1789, 1892, 1928 editions) digitized in this repository derives from the transcription work of Charles Wohlers, Satucket Software. That text is redistributed here under his original terms, reproduced verbatim below and preserved intact in every source file to which it applies.

### Wohlers / Satucket Software Original Header

> You may redistribute this document electronically provided no fee is charged and this header remains part of the document. While every attempt was made to ensure accuracy, certain errors may exist in the text. Please contact us if any errors are found.
>
> This document was created as a service to the community by Satucket Software:
> Web Design & computer consulting for small business, churches, & non-profits
>
> Contact:
> Charles Wohlers
> P. O. Box 227
> East Bridgewater, Mass. 02333 USA
> chadwohl@satucket.com
> http://satucket.com

What this means in practice:

- The BCP source text files (`.md` files in edition folders: `1662/`, `1789/`, `1892/`, `1928/`) may be redistributed electronically at no charge, provided the Wohlers header remains part of the document.
- No commercial fee may be charged for redistribution of the text itself.
- This applies to the text content of those files. It does not apply to the YAML schema, the structural formatting, the provenance annotations, or any other original work added by Liturgic Labs Studio.

The underlying BCP editions (1662, 1789, 1892, 1928) are in the public domain in the United States.

The 1979 Book of Common Prayer is under copyright held by the Episcopal Church and is not included in this repository.

## Part II — Code, Scripts, and Utilities

All rights reserved. © 2026 Alex Nutting, The Strategic Disciple LLC / Liturgic Labs Studio.

The following are proprietary and may not be copied, modified, distributed, sublicensed, or used in any form without explicit written permission from Alex Nutting:

- All Python scripts and utilities (`computus.py`, `lectionary.py`, `lectionary_today.py`, `onboard_edition.py`, `format_bcp_markdown_v5.py`, and any other `.py` files in this repository)
- GitHub Actions workflow files (`.github/workflows/`)
- JavaScript rendering logic in `today-updated.html`, `prayerbook.html`, `kalendar-kompanion.html`, and associated HTML/CSS/JS files
- Any future API, backend service, or application built on this data

These tools represent original engineering work and are the commercial infrastructure of the Concordentary project. They are not open source.

## Part III — Original Scholarly and Comparative Works

All rights reserved. © 2026 Alex Nutting, The Strategic Disciple LLC / Liturgic Labs Studio.

The following original works are proprietary and close-hold:

- `DISCOVERIES.md` and all discovery log entries
- `ANOMALIES.md` and all anomaly log entries documenting original research findings
- `compare.md` and all cross-edition comparison files and commentary
- `_study/` formation notes and companion files
- `_hymnody/` companion files
- All editorial annotations, provenance notes, and scholarly commentary added by Alex Nutting or contributors to this project
- The YAML frontmatter content (field values, notes, tags, concord_id assignments) as a structured original dataset — distinct from the BCP text itself

The comparative and commentary layer (the "Concordentary" layer proper) constitutes the primary original scholarly contribution of this project and is reserved for commercial and academic publication.

## Part IV — Schema, Documentation, and Structural Files

Licensed under CC BY-NC-SA 4.0.

The following may be shared and adapted for non-commercial purposes, with attribution and under the same license:

- `RULES.md` — the atomization and schema enforcement rules
- `HEADER.md` — the provenance header template
- `SOURCES.md` — source documentation
- The YAML schema structure and field definitions (as documented in `RULES.md` §3), but not the field values applied to specific texts
- `README.md` and general project documentation

Attribution required:
> Alex Nutting, The Strategic Disciple LLC / Liturgic Labs Studio.
> The Concordentary — Book of Common Prayer Digital Edition Project.
> https://github.com/TheStrategicDisciple/book-of-common-prayer-concordentary

ShareAlike: Any adaptation of these schema and documentation files must be distributed under CC BY-NC-SA 4.0.

Full license text: https://creativecommons.org/licenses/by-nc-sa/4.0/legalcode

## Attribution Chain

This project stands on the following chain of digitization work:

1. 1993 — John Goodwin, Michael Bushnell, and others. ASCII transcription of BCP editions. First known digital form.
2. 1996–2026 — Charles Wohlers, Satucket Software. HTML and WordPerfect transcriptions. Maintained at justus.anglican.org. The upstream source for this project. Original header reproduced above and preserved in all source files.
3. 2026– — Alex Nutting, The Strategic Disciple LLC / Liturgic Labs Studio. Structured Markdown conversion, YAML provenance schema, cross-edition apparatus, calendar engine, and derivative tools. This project.

Any use of this material must preserve this attribution chain.

## Contact

Alex Nutting
The Strategic Disciple LLC / Liturgic Labs Studio
thestrategicdisciple@gmail.com
https://concordentary.org

*This license was last reviewed August 2026. It is subject to revision as the project develops. Consult an attorney familiar with open source and intellectual property law before relying on these terms for any commercial or legal purpose.*

---

This work is licensed under the Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License.

This means:
- Text, documentation, notes, images, and source-text files in this repository are licensed under CC BY-NC-SA 4.0 unless otherwise noted.
- Any software scripts or utilities added later may be licensed separately.
- The above repository-specific clarifications are part of the licensing terms and supersede any general statement that would imply unrestricted open-source usage for the entire project.

See `HEADER` for details.
