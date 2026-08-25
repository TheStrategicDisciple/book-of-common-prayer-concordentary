#!/usr/bin/env python3
"""
lectionary.py — 1928 BCP Daily Office Lectionary Engine
========================================================
Reads 04_lectionary-christian-year.md and resolves the four daily
lesson references (Morning 1st, Morning 2nd, Evening 1st, Evening 2nd)
for any liturgical day.

SOURCE
    04_lectionary-christian-year.md (1945 revision)
    The 1945 revision changed lesson assignments across most of the church
    year and is the version found in most physical copies of the 1928 BCP.
    The original 1928 assignments are preserved in a separate file for
    future scholarly comparison.

KNOWN LIMITATIONS
    - Sundays after Trinity: the 1928 lectionary does not appoint specific
      weekday lessons for this season. Sunday lookups work; weekday lookups
      return None for Trinity Season weekdays. This is accurate to the source.
    - Lesson references preserve the source's abbreviated book names and
      verse notation (e.g. "Isa. 55", "Luke 1:v.57-end"). Normalization
      to modern format is handled downstream by the scripture reference CSV.
    - Trinity 25 and 26 reference "Lessons omitted from the Sundays after
      Epiphany" — these are returned as a note, not as specific references.

USAGE (command line)
    python lectionary.py --day "Eleventh Sunday after Trinity"
    python lectionary.py --day "First Sunday in Advent" --json
    python lectionary.py --day "Monday" --preceding-sunday "First Sunday in Advent"
    python lectionary.py --saint "St. Andrew"

USAGE (import)
    from lectionary import LectionaryEngine
    engine = LectionaryEngine()
    lessons = engine.get_lessons_for_sunday("Eleventh Sunday after Trinity")
    lessons = engine.get_lessons_for_weekday("Monday", "First Sunday in Advent")
    lessons = engine.get_holy_day_lessons("St. Andrew")

INTEGRATION WITH computus.py / today.md
    computus.py outputs name1928 (the week's Sunday/feast name) and the
    calendar date. Pass both to this engine:

        from lectionary import LectionaryEngine
        from datetime import date

        engine = LectionaryEngine()
        day_name  = "Eleventh Sunday after Trinity"   # from computus
        cal_date  = date(2026, 8, 23)                # today

        if cal_date.weekday() == 6:  # Sunday
            lessons = engine.get_lessons_for_sunday(day_name)
        else:
            weekday_name = cal_date.strftime("%A")   # "Monday" etc.
            lessons = engine.get_lessons_for_weekday(weekday_name, day_name)
"""

import re
import sys
import json
import argparse
from pathlib import Path
from datetime import date
from typing import Optional

# ── Path ─────────────────────────────────────────────────────────────────────
LECTIONARY_MD = Path(__file__).parent.parent / "1928" / "04_lectionary-christian-year.md"

# ── Constants ────────────────────────────────────────────────────────────────

# These day labels appear as rows in the table but are relative to a Sunday,
# not named feasts or Sundays in their own right.
RELATIVE_WEEKDAY_LABELS = {
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday",
}

# Special named weekday-ish entries that ARE relative to a preceding Sunday
# (not standalone feasts) — treated like weekdays for lookup purposes.
NAMED_RELATIVE_DAYS = {
    "ember day",
    "rogation monday", "rogation tuesday", "rogation wednesday",
    "whit monday", "whit tuesday",
    "easter monday", "easter tuesday",
    "easter even", "easter eve",
    "eve of ascension",
}

# Seasons that include weekday rows in the table.
# Sundays after Trinity does NOT — weekdays return None there.
SEASONS_WITH_WEEKDAYS = {
    "advent",
    "christmas and the days following",
    "epiphany",
    "pre-lent (septuagesima, sexagesima, quinquagesima)",
    "lent",
    "holy week and easter",
    "eastertide",
    "whitsuntide and trinity",
}

# ── Helpers ──────────────────────────────────────────────────────────────────

def _strip_bold(text: str) -> str:
    """Remove markdown bold markers and normalize whitespace."""
    text = re.sub(r"\*+", "", text)
    return re.sub(r"\s+", " ", text).strip()


def _parse_ref(cell: str) -> Optional[str]:
    """
    Clean a lesson reference cell.
    - Strips optional (*) and Christmas Eve (†) markers (flags noted separately).
    - Returns None for empty cells and dash entries.
    - Preserves source notation exactly — no Roman numeral conversion here.
    """
    cell = cell.strip().rstrip("*†").strip()
    if cell in ("", "—", "-"):
        return None
    return cell


def _cell_flags(cell: str) -> dict:
    """Extract optional/xmas_eve flags from a cell."""
    return {
        "optional": "*" in cell,
        "xmas_eve": "†" in cell,
    }


def _parse_table(lines: list[str]) -> list[list[str]]:
    """
    Parse markdown table lines into a list of cell-lists.
    Skips the header separator line (---).
    Returns all data rows including the header.
    """
    rows = []
    for line in lines:
        line = line.strip()
        if not line.startswith("|"):
            continue
        # Skip separator rows
        if re.match(r"^\|[-| ]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        rows.append(cells)
    return rows


def _is_relative_weekday(name: str) -> bool:
    """True if this day label is relative to a preceding Sunday."""
    n = name.lower()
    return n in RELATIVE_WEEKDAY_LABELS or n in NAMED_RELATIVE_DAYS


# ── Engine ───────────────────────────────────────────────────────────────────

class LectionaryEngine:
    """
    Parses and queries the 1928 BCP Daily Office lectionary tables.

    Internal data structures after loading:
        _christian_year_index:
            {normalized_sunday_name: {
                "sunday": {morning1, morning2, evening1, evening2},
                "monday": {morning1, morning2, evening1, evening2},
                ... (only days that appear in the table)
            }}

        _holy_days_index:
            {normalized_saint_name: {
                eve1, eve2, morning1, morning2, evening1, evening2
            }}

        _season_for_sunday:
            {normalized_sunday_name: season_name}
    """

    def __init__(self, md_path: Path = LECTIONARY_MD):
        self.md_path = md_path
        self._christian_year_index: dict = {}
        self._holy_days_index: dict = {}
        self._season_for_sunday: dict = {}
        self._loaded = False

    # ── Loading ───────────────────────────────────────────────────────────────

    def _ensure_loaded(self):
        if not self._loaded:
            self._load()

    def _load(self):
        text = self.md_path.read_text(encoding="utf-8")
        self._parse(text)
        self._loaded = True

    def _parse(self, text: str):
        """Walk the markdown and build both indexes."""
        # Split into sections on ## headings
        raw_sections = re.split(r"^(## .+)$", text, flags=re.MULTILINE)

        i = 0
        while i < len(raw_sections):
            chunk = raw_sections[i]
            if chunk.startswith("## "):
                season = chunk[3:].strip()
                body = raw_sections[i + 1] if i + 1 < len(raw_sections) else ""
                i += 2

                if "Fixed Holy Days" in season:
                    self._parse_holy_days_section(body)
                elif "Special Occasions" in season:
                    pass  # out of scope for daily lookup
                else:
                    self._parse_christian_year_section(season, body)
            else:
                i += 1

    def _parse_christian_year_section(self, season: str, body: str):
        """
        Parse one seasonal section of the Christian Year table.
        Maintains a running "current Sunday" key as it walks rows.
        """
        table_lines = [l for l in body.split("\n") if l.strip().startswith("|")]
        rows = _parse_table(table_lines)

        if not rows:
            return

        current_sunday_key = None

        for row in rows:
            if not row:
                continue
            day_cell = row[0]
            day_name = _strip_bold(day_cell)

            # Skip header row
            if day_name.lower() in ("day", "sunday/day", "holy day"):
                continue

            is_relative = _is_relative_weekday(day_name)

            if not is_relative:
                # This is a Sunday or named feast — becomes the new anchor
                current_sunday_key = day_name.lower()
                self._season_for_sunday[current_sunday_key] = season
                lookup_key = "sunday"
            else:
                # Relative weekday — belongs to current_sunday_key
                if current_sunday_key is None:
                    continue  # No Sunday anchor yet, skip
                lookup_key = day_name.lower()

            # Extract the four lesson cells
            m1_raw = row[1] if len(row) > 1 else ""
            m2_raw = row[2] if len(row) > 2 else ""
            e1_raw = row[3] if len(row) > 3 else ""
            e2_raw = row[4] if len(row) > 4 else ""

            # Special case: Trinity 25/26 reference omitted Epiphany lessons
            if "Use Lessons omitted" in m1_raw:
                entry = {
                    "morning1": None,
                    "morning2": None,
                    "evening1": None,
                    "evening2": None,
                    "note": "Use Lessons omitted from the Sundays after Epiphany",
                }
            else:
                entry = {
                    "morning1":          _parse_ref(m1_raw),
                    "morning2":          _parse_ref(m2_raw),
                    "evening1":          _parse_ref(e1_raw),
                    "evening2":          _parse_ref(e2_raw),
                    "morning1_optional": _cell_flags(m1_raw)["optional"],
                    "morning2_optional": _cell_flags(m2_raw)["optional"],
                    "evening1_optional": _cell_flags(e1_raw)["optional"],
                    "evening2_optional": _cell_flags(e2_raw)["optional"],
                    "morning1_xmas_eve": _cell_flags(m1_raw)["xmas_eve"],
                    "morning2_xmas_eve": _cell_flags(m2_raw)["xmas_eve"],
                }

            # Store under the sunday key
            if current_sunday_key not in self._christian_year_index:
                self._christian_year_index[current_sunday_key] = {}

            self._christian_year_index[current_sunday_key][lookup_key] = entry

    def _parse_holy_days_section(self, body: str):
        """
        Parse the Fixed Holy Days table.
        Columns: Holy Day | Eve 1st | Eve 2nd | Morning 1st | Morning 2nd | Evening 1st | Evening 2nd
        """
        table_lines = [l for l in body.split("\n") if l.strip().startswith("|")]
        rows = _parse_table(table_lines)

        for row in rows:
            if not row:
                continue
            saint = _strip_bold(row[0])
            if saint.lower() in ("holy day", ""):
                continue

            self._holy_days_index[saint.lower()] = {
                "day":      saint,
                "eve1":     _parse_ref(row[1] if len(row) > 1 else ""),
                "eve2":     _parse_ref(row[2] if len(row) > 2 else ""),
                "morning1": _parse_ref(row[3] if len(row) > 3 else ""),
                "morning2": _parse_ref(row[4] if len(row) > 4 else ""),
                "evening1": _parse_ref(row[5] if len(row) > 5 else ""),
                "evening2": _parse_ref(row[6] if len(row) > 6 else ""),
            }

    # ── Public query API ──────────────────────────────────────────────────────

    def get_lessons_for_sunday(self, sunday_name: str) -> Optional[dict]:
        """
        Return lessons for a Sunday or principal feast.

        Args:
            sunday_name: e.g. "Eleventh Sunday after Trinity",
                         "The Nativity of our Lord, or the Birthday of Christ, commonly called Christmas Day"

        Returns:
            Dict with morning1, morning2, evening1, evening2, or None.
        """
        self._ensure_loaded()
        key = sunday_name.strip().lower()

        # Direct lookup
        if key in self._christian_year_index:
            entry = self._christian_year_index[key].get("sunday", {})
            return self._format_result(entry, sunday_name, "christian_year_sunday")

        # Holy days table fallback
        if key in self._holy_days_index:
            hd = self._holy_days_index[key]
            return {
                "day":      hd["day"],
                "morning1": hd["morning1"],
                "morning2": hd["morning2"],
                "evening1": hd["evening1"],
                "evening2": hd["evening2"],
                "source":   "holy_days",
            }

        return None

    def get_lessons_for_weekday(self, weekday_name: str, preceding_sunday: str) -> Optional[dict]:
        """
        Return lessons for a weekday, identified by its name and preceding Sunday.

        Args:
            weekday_name:      "Monday", "Tuesday" ... "Saturday",
                               or named days like "Easter Monday", "Rogation Tuesday"
            preceding_sunday:  e.g. "First Sunday in Advent" (from computus.py)

        Returns:
            Dict with morning1, morning2, evening1, evening2, or None.
            Returns None with a note for Trinity Season weekdays (not in source).
        """
        self._ensure_loaded()

        sunday_key = preceding_sunday.strip().lower()
        day_key    = weekday_name.strip().lower()

        # Check if this Sunday is in Trinity Season (no weekday rows)
        season = self._season_for_sunday.get(sunday_key, "")
        if "trinity" in season.lower() and "whitsun" not in season.lower():
            return {
                "morning1": None, "morning2": None,
                "evening1": None, "evening2": None,
                "source":   "trinity_season_weekday",
                "note":     (
                    "The 1928 lectionary does not appoint specific weekday lessons "
                    "during Trinity Season. This is accurate to the source."
                ),
            }

        # Look up the weekday row under the preceding Sunday
        if sunday_key not in self._christian_year_index:
            return None

        week = self._christian_year_index[sunday_key]
        entry = week.get(day_key)

        if entry is None:
            return None

        return self._format_result(entry, weekday_name, "christian_year_weekday")

    def get_holy_day_lessons(self, saint_name: str) -> Optional[dict]:
        """
        Return lessons for a fixed Holy Day (saints' days etc.).
        Includes Eve lessons where appointed.

        Args:
            saint_name: e.g. "St. Andrew", "All Saints"

        Returns:
            Dict with eve1, eve2, morning1, morning2, evening1, evening2, or None.
        """
        self._ensure_loaded()
        key = saint_name.strip().lower()
        if key in self._holy_days_index:
            hd = self._holy_days_index[key]
            return {
                "day":      hd["day"],
                "eve1":     hd["eve1"],
                "eve2":     hd["eve2"],
                "morning1": hd["morning1"],
                "morning2": hd["morning2"],
                "evening1": hd["evening1"],
                "evening2": hd["evening2"],
                "source":   "holy_days",
            }
        return None

    def get_lessons_for_today(self,
                              liturgical_day: str,
                              calendar_date: date) -> Optional[dict]:
        """
        Convenience method for integration with computus.py / today.md.

        computus.py outputs the liturgical week name (the Sunday or feast)
        for both Sundays and weekdays. Pass it here along with the calendar
        date; this method resolves to the correct day-of-week row.

        Args:
            liturgical_day:  The 1928 BCP name from computus.py output
                             (e.g. "Eleventh Sunday after Trinity").
                             For weekdays, this should be the WEEK's Sunday name,
                             not "Monday" etc.
            calendar_date:   The actual calendar date (today).

        Returns:
            Dict with morning1, morning2, evening1, evening2.
        """
        weekday = calendar_date.weekday()  # 0=Monday, 6=Sunday

        if weekday == 6:
            # It's a Sunday — direct lookup
            return self.get_lessons_for_sunday(liturgical_day)
        else:
            # Weekday — liturgical_day is the week's Sunday name
            weekday_name = calendar_date.strftime("%A")  # "Monday" etc.
            return self.get_lessons_for_weekday(weekday_name, liturgical_day)

    # ── Internal ──────────────────────────────────────────────────────────────

    @staticmethod
    def _format_result(entry: dict, day: str, source: str) -> dict:
        result = {
            "day":      day,
            "morning1": entry.get("morning1"),
            "morning2": entry.get("morning2"),
            "evening1": entry.get("evening1"),
            "evening2": entry.get("evening2"),
            "source":   source,
        }
        # Pass through any note (Trinity 25/26 etc.)
        if "note" in entry:
            result["note"] = entry["note"]
        # Pass through optional markers if present
        for flag in ("morning1_optional", "morning2_optional",
                     "evening1_optional", "evening2_optional"):
            if entry.get(flag):
                result[flag] = True
        return result

    def debug_dump(self) -> dict:
        """Return the full parsed index for inspection."""
        self._ensure_loaded()
        return {
            "christian_year_entries": len(self._christian_year_index),
            "holy_days_entries":      len(self._holy_days_index),
            "sundays_indexed":        list(self._christian_year_index.keys()),
            "holy_days_indexed":      list(self._holy_days_index.keys()),
        }


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="1928 BCP Daily Office Lectionary Engine",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python lectionary.py --day "Eleventh Sunday after Trinity"
  python lectionary.py --day "Monday" --preceding-sunday "First Sunday in Advent"
  python lectionary.py --saint "St. Andrew"
  python lectionary.py --day "First Sunday in Advent" --json
  python lectionary.py --debug
        """
    )
    parser.add_argument(
        "--day",
        help='Liturgical day name or weekday (e.g. "Eleventh Sunday after Trinity")',
    )
    parser.add_argument(
        "--preceding-sunday",
        dest="preceding_sunday",
        help='For weekday lookup: the preceding Sunday\'s liturgical name',
    )
    parser.add_argument(
        "--saint",
        help='Holy Day name (e.g. "St. Andrew", "All Saints")',
    )
    parser.add_argument(
        "--date",
        help="Calendar date YYYY-MM-DD (for get_lessons_for_today)",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Dump parse statistics and exit",
    )
    parser.add_argument(
        "--lectionary-file",
        dest="lectionary_file",
        help="Override path to lectionary markdown file",
    )
    args = parser.parse_args()

    md_path = Path(args.lectionary_file) if args.lectionary_file else LECTIONARY_MD
    engine = LectionaryEngine(md_path=md_path)

    if args.debug:
        info = engine.debug_dump()
        print(json.dumps(info, indent=2))
        return

    lessons = None

    if args.saint:
        lessons = engine.get_holy_day_lessons(args.saint)

    elif args.day and args.date:
        cal_date = date.fromisoformat(args.date)
        lessons = engine.get_lessons_for_today(args.day, cal_date)

    elif args.day and args.preceding_sunday:
        lessons = engine.get_lessons_for_weekday(args.day, args.preceding_sunday)

    elif args.day:
        lessons = engine.get_lessons_for_sunday(args.day)

    else:
        parser.print_help()
        sys.exit(1)

    if args.json:
        print(json.dumps(lessons, indent=2, ensure_ascii=False))
        return

    if lessons is None:
        print(f"No lessons found.", file=sys.stderr)
        sys.exit(1)

    # Human-readable output
    print(f"Day:       {lessons.get('day', '—')}")
    print(f"Source:    {lessons.get('source', '—')}")
    if lessons.get("note"):
        print(f"Note:      {lessons['note']}")
    print()

    def fmt(label, ref, optional=False, xmas_eve=False):
        flags = ""
        if optional:
            flags += " [optional Ember Day lesson]"
        if xmas_eve:
            flags += " [may be used Christmas Eve]"
        print(f"  {label:<14} {ref or '—'}{flags}")

    if lessons.get("eve1") is not None or lessons.get("eve2") is not None:
        print("Eve:")
        fmt("1st Lesson", lessons.get("eve1"))
        fmt("2nd Lesson", lessons.get("eve2"))
        print()

    print("Morning:")
    fmt("1st Lesson",  lessons.get("morning1"),
        optional=lessons.get("morning1_optional", False),
        xmas_eve=lessons.get("morning1_xmas_eve", False))
    fmt("2nd Lesson",  lessons.get("morning2"),
        optional=lessons.get("morning2_optional", False))
    print()
    print("Evening:")
    fmt("1st Lesson",  lessons.get("evening1"),
        optional=lessons.get("evening1_optional", False))
    fmt("2nd Lesson",  lessons.get("evening2"),
        optional=lessons.get("evening2_optional", False))


if __name__ == "__main__":
    main()


# ── Scripture reference URL builder ──────────────────────────────────────────

import csv
import urllib.parse

# Path to the CSV — adjust if needed
SCRIPTURE_CSV = Path(__file__).parent / 'scripture-refs.csv'

# Roman numeral → integer (chapter references in source)
_ROMAN = {
    'I': 1, 'II': 2, 'III': 3, 'IV': 4, 'V': 5,
    'VI': 6, 'VII': 7, 'VIII': 8, 'IX': 9, 'X': 10,
    'XI': 11, 'XII': 12, 'XIII': 13, 'XIV': 14, 'XV': 15,
    'XVI': 16, 'XVII': 17, 'XVIII': 18, 'XIX': 19, 'XX': 20,
    'XXI': 21, 'XXII': 22, 'XXIII': 23, 'XXIV': 24, 'XXV': 25,
    'XXVI': 26, 'XXVII': 27, 'XXVIII': 28, 'XXIX': 29, 'XXX': 30,
    'XXXI': 31, 'XXXII': 32, 'XXXIII': 33, 'XXXIV': 34, 'XXXV': 35,
    'XXXVI': 36, 'XXXVII': 37, 'XXXVIII': 38, 'XXXIX': 39, 'XL': 40,
    'XLI': 41, 'XLII': 42, 'XLIII': 43, 'XLIV': 44, 'XLV': 45,
    'XLVI': 46, 'XLVII': 47, 'XLVIII': 48, 'XLIX': 49, 'L': 50,
    'LI': 51, 'LII': 52, 'LIII': 53, 'LIV': 54, 'LV': 55,
    'LVI': 56, 'LVII': 57, 'LVIII': 58, 'LIX': 59, 'LX': 60,
    'LXI': 61, 'LXII': 62, 'LXIII': 63, 'LXIV': 64, 'LXV': 65,
    'LXVI': 66,
}


def _load_book_table(csv_path: Path = SCRIPTURE_CSV) -> dict:
    """Load the scripture-refs.csv into a lookup dict keyed by abbreviation."""
    table = {}
    if not csv_path.exists():
        return table
    with open(csv_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            table[row['abbreviation'].strip()] = row
    return table


def _roman_to_int(s: str) -> Optional[int]:
    """Convert a Roman numeral string to an integer, or return None."""
    s = s.strip().upper()
    return _ROMAN.get(s)


def _parse_verse_ref(ref_str: str) -> tuple[Optional[str], Optional[str]]:
    """
    Parse a chapter:verse or chapter reference from a source notation string.

    Source notation examples:
        '55'            → chapter 55, no verse
        'xiii. 8'       → chapter 13, verse 8
        '1:v.57–end'    → chapter 1, verse 57 (end dropped — BG shows to chapter end)
        '1:1–2:3'       → chapter 1:1 to 2:3 (cross-chapter range)
        'v.21'          → verse 21 (no chapter — unusual, use as-is)

    Returns: (chapter_verse_string, version_note) or (None, None)
    """
    if not ref_str:
        return None, None

    ref_str = ref_str.strip()

    # Remove trailing 'end' from ranges like '1:v.57–end'
    ref_str = re.sub(r'[–-]end\b', '', ref_str).strip()
    ref_str = ref_str.rstrip('.,;')

    # Replace em-dash and en-dash with hyphen
    ref_str = ref_str.replace('–', '-').replace('—', '-')

    # Remove 'v.' verse prefix (old notation)
    ref_str = re.sub(r'\bv\.', '', ref_str).strip()

    # Check for Roman numeral chapter: 'xiii. 8' or 'xxi. 1'
    roman_match = re.match(r'^([IVXLCDMivxlcdm]+)\.\s*(\d+)(.*)$', ref_str)
    if roman_match:
        roman = roman_match.group(1).upper()
        verse = roman_match.group(2)
        rest  = roman_match.group(3).strip()
        chapter_int = _roman_to_int(roman)
        if chapter_int:
            cv = f"{chapter_int}:{verse}"
            if rest:
                # Handle continuation like '-14' or '-2:3'
                rest = rest.lstrip('-').strip()
                if rest:
                    cv += f"-{rest}"
            return cv, None

    # Already in modern format: '13:8' or '1:1-2:3' or just '55'
    return ref_str, None


def build_bible_gateway_url(source_ref: str,
                             book_table: Optional[dict] = None,
                             csv_path: Path = SCRIPTURE_CSV) -> Optional[dict]:
    """
    Build a Bible Gateway URL from a source-notation scripture reference.

    Args:
        source_ref:  Raw reference from the 1928 source
                     e.g. 'Isa. 55', 'Romans xiii. 8', 'I Kgs. 11:1-13'
        book_table:  Pre-loaded CSV lookup dict (pass for performance in loops)
        csv_path:    Path to scripture-refs.csv if book_table not provided

    Returns:
        Dict with:
            url        — Bible Gateway URL string
            full_name  — Full book name for display
            ref_modern — Normalized reference (e.g. 'Isaiah 55')
            version    — 'KJV' or 'NRSVUE'
            apocrypha  — True if deuterocanonical
        Or None if the book is not found in the lookup table.
    """
    if book_table is None:
        book_table = _load_book_table(csv_path)

    if not source_ref:
        return None

    source_ref = source_ref.strip().rstrip('*†').strip()

    # Split off book abbreviation from the chapter:verse portion
    # Try to match known abbreviations first (longest first to avoid prefix conflicts)
    matched_abbrev = None
    matched_row    = None
    remainder      = ""

    # Sort by length descending so 'St. Matthew' matches before 'Matt.'
    for abbrev in sorted(book_table.keys(), key=len, reverse=True):
        if source_ref.startswith(abbrev):
            matched_abbrev = abbrev
            matched_row    = book_table[abbrev]
            remainder      = source_ref[len(abbrev):].strip().lstrip('.,').strip()
            break

    if matched_row is None:
        return None

    full_name = matched_row['full_name']
    bg_name   = matched_row['bg_name']
    version   = matched_row['bg_version']
    apocrypha = matched_row['apocrypha'].lower() == 'true'

    # Parse chapter:verse from remainder
    if remainder:
        cv, _ = _parse_verse_ref(remainder)
    else:
        cv = None  # Whole book (e.g. Philemon)

    # Build reference string for display
    if cv:
        ref_modern = f"{full_name} {cv}"
    else:
        ref_modern = full_name

    # Build URL
    search_param = bg_name
    if cv:
        # Replace spaces and encode
        cv_encoded = urllib.parse.quote(cv, safe=':,-')
        search_param = f"{bg_name}+{cv_encoded}"

    url = (
        f"https://www.biblegateway.com/passage/"
        f"?search={search_param}&version={version}"
    )

    return {
        "url":        url,
        "full_name":  full_name,
        "ref_modern": ref_modern,
        "version":    version,
        "apocrypha":  apocrypha,
    }
