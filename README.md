# The Concordentary

*A version-controlled, schema-structured Markdown archive of the Book of Common Prayer across major editions.*

---

The Concordentary gathers public-domain prayer book sources across the major English and American editions of the Book of Common Prayer — structured so that prayers, phrases, rites, and liturgical patterns can be studied in relation rather than isolation, cited with confidence, and read by both humans and machines.

This is not a replacement for the pew edition. The best version of the BCP is still found in a pew.

This is an attempt to carry it forward.

---

## Structure

```
1662/         Church of England edition
1789/         First American edition
1892/         PECUSA revision
1928/         Primary active edition (most complete)
1979/         Episcopal Church edition (pending copyright clearance)

_atomic/      Cross-edition extracts — collects, epistles, gospels, canticles, prayers
_engine/      Computus engine and daily office scripts
_data/        Calendar data, hymn curation, validation records
_study/       Formation notes, one per canonical file
_hymnody/     Musical curation, linked from canonical files
```

Files use zero-padded numeric prefixes for book order (`01_morning-prayer.md`, `02_evening-prayer.md`). Edition folders mirror the same filenames where the same rite appears across editions — enabling direct cross-edition comparison by filename.

---

## The Preservation Story

In the 1990s, volunteers painstakingly transcribed these texts into ASCII, later evolving into WordPerfect, Word, RTF, HTML, and PDF versions. Their work — shared through sites like [justus.anglican.org](http://justus.anglican.org/resources/bcp/) — was extraordinary. At a time when few imagined digital liturgy, they preserved the Book of Common Prayer for anyone with a dial-up connection.

Three decades later, those files are harder to use. WordPerfect is obsolete. Many links have decayed. Some PDFs were split into fragments for slow downloads. Even the original editors encouraged others to adapt and edit the texts freely.

The Concordentary continues that work — adapting the same material into structured Markdown with a locked provenance schema, a validated computus engine, and cross-edition traceability. The aim is simple: make the prayers readable and usable today, and carry them forward for tomorrow.

---

## License

**BCP text content** — transcription and digitization by Charles Wohlers, Satucket Software. Original texts are public domain. Distributed per the notice in `HEADER`.

**Markdown conversion, YAML schema, provenance apparatus, engine, and editorial curation** — © 2026 Alex Nutting, The Strategic Disciple LLC. Licensed CC BY-NC-SA 4.0.

You may redistribute this material electronically provided no fee is charged and the header remains intact. See `LICENSE`, `HEADER`, and `CITE.md`.

---

## Acknowledgments

**Charles Wohlers**, Satucket Software — thirty years of digitization work this project rests on entirely.

**John Goodwin & Michael Bushnell** — ASCII transcription, 1993. The earliest digital layer.

---

## Status

This project is under active construction. The 1928 edition is the primary active build. Other editions are planned. See `AGENTS.md` for full project status and agent navigation instructions.

Corrections welcome: thestrategicdisciple@gmail.com

---

*"It is a most invaluable part of that blessed liberty wherewith Christ hath made us free, that in his worship, different forms and usages may without offence be allowed, provided the substance of the Faith be kept entire."*

— Preface, Book of Common Prayer, 1789
