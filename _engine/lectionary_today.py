#!/usr/bin/env python3
"""
lectionary_today.py
===================
Reads the today.md already written by computus.py, resolves today's
Daily Office lessons and collect slug, then outputs additional lines
to be appended to today.md.

Called from the GitHub Action immediately after computus.py:
    python _engine/computus.py  > today.md
    python _engine/lectionary_today.py >> today.md

Outputs lines in the format parseTodayMd() in today-updated.html expects:
    **Collect:** 1928/_atomic/propers/collects/trinity-12.md
    **Morning 1:** Isa. 55 | https://www.biblegateway.com/...
    **Morning 2:** Luke 1:57-end | https://www.biblegateway.com/...
    **Evening 1:** Isa. 60:1-11 | https://www.biblegateway.com/...
    **Evening 2:** John 1:15-28 | https://www.biblegateway.com/...
"""

import re
import sys
from pathlib import Path
from datetime import date, datetime

# ── Path setup ────────────────────────────────────────────────────────────────
REPO_ROOT     = Path(__file__).parent.parent
ENGINE_DIR    = Path(__file__).parent
TODAY_MD      = REPO_ROOT / 'today.md'
LECTIONARY_MD = REPO_ROOT / '1928' / '04_lectionary-christian-year.md'
SCRIPTURE_CSV = ENGINE_DIR / 'scripture-refs.csv'   # lives in _engine/ alongside lectionary.py

# lectionary.py lives alongside this file in _engine/
sys.path.insert(0, str(ENGINE_DIR))
from lectionary import LectionaryEngine, build_bible_gateway_url, _load_book_table

# ── Ordinal word → integer ────────────────────────────────────────────────────
ORDINALS = {
    'first': 1,       'second': 2,      'third': 3,       'fourth': 4,
    'fifth': 5,       'sixth': 6,       'seventh': 7,     'eighth': 8,
    'ninth': 9,       'tenth': 10,      'eleventh': 11,   'twelfth': 12,
    'thirteenth': 13, 'fourteenth': 14, 'fifteenth': 15,  'sixteenth': 16,
    'seventeenth': 17,'eighteenth': 18, 'nineteenth': 19, 'twentieth': 20,
    'twenty-first': 21, 'twenty-second': 22, 'twenty-third': 23,
    'twenty-fourth': 24, 'twenty-fifth': 25,
}

# ── Named feasts → collect slugs ─────────────────────────────────────────────
FEAST_SLUGS = {
    'christmas day': 'christmas-day',
    'christmas':     'christmas-day',
    'the epiphany':  'epiphany',
    'epiphany':      'epiphany',
    'ash wednesday': 'ash-wednesday',
    'palm sunday':   'palm-sunday',
    'monday in holy week':    'monday-in-holy-week',
    'tuesday in holy week':   'tuesday-in-holy-week',
    'wednesday in holy week': 'wednesday-in-holy-week',
    'maundy thursday':        'maundy-thursday',
    'good friday':            'good-friday',
    'easter day':             'easter-day',
    'easter':                 'easter-day',
    'ascension day':          'ascension-day',
    'whitsunday':             'whitsunday',
    'whit sunday':            'whitsunday',
    'trinity sunday':         'trinity-sunday',
    'all saints day':         'all-saints',
    'all saints':             'all-saints',
    'septuagesima':           'septuagesima',
    'sexagesima':             'sexagesima',
    'quinquagesima':          'quinquagesima',
    'sunday next before advent':  'sunday-next-before-advent',
    'sunday after ascension':     'sunday-after-ascension',
}


def day_to_slug(day_name: str) -> str | None:
    """
    Convert a 1928 BCP liturgical day name to a collect file slug.
    Returns None if the slug cannot be determined confidently.

    Examples:
        "Twelfth Sunday after Trinity"   → "trinity-12"
        "First Sunday in Advent"         → "advent-1"
        "Christmas Day"                  → "christmas-day"
        "The Third Sunday after Easter"  → "easter-3"
    """
    name = day_name.strip().lower()
    # Remove leading "the "
    name_clean = re.sub(r'^the\s+', '', name)

    # Direct named feast lookup (try both with and without "the")
    if name in FEAST_SLUGS:
        return FEAST_SLUGS[name]
    if name_clean in FEAST_SLUGS:
        return FEAST_SLUGS[name_clean]

    # Pattern helpers
    def ordinal_num(word):
        return ORDINALS.get(word.lower().replace('\u2013', '-'))

    # [Ordinal] Sunday in Advent
    m = re.match(r'^(?:the )?(\w+) sunday in advent$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'advent-{n}' if n else None

    # [Ordinal] Sunday after Christmas
    m = re.match(r'^(?:the )?(\w+) sunday after christmas.*$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'christmas-{n}' if n else None

    # [Ordinal] Sunday after Epiphany
    m = re.match(r'^(?:the )?(\w+) sunday after epiphany.*$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'epiphany-{n}' if n else None

    # [Ordinal] Sunday in Lent
    m = re.match(r'^(?:the )?(\w+) sunday in lent$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'lent-{n}' if n else None

    # [Ordinal] Sunday after Trinity
    m = re.match(r'^(?:the )?(\w[\w-]*) sunday after trinity$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'trinity-{n}' if n else None

    # [Ordinal] Sunday after Easter
    m = re.match(r'^(?:the )?(\w+) sunday after easter.*$', name)
    if m:
        n = ordinal_num(m.group(1))
        return f'easter-{n}' if n else None

    # Whitsunday / Whit Sunday
    if 'whitsun' in name or 'whit sunday' in name:
        return 'whitsunday'

    return None


def parse_today_md(path: Path) -> dict:
    """
    Parse the already-written today.md to extract what computus.py wrote.
    Returns dict with: name1928, date (date object), season.
    """
    info = {}
    if not path.exists():
        return info

    text = path.read_text(encoding='utf-8')
    for line in text.split('\n'):

        # # Monday, August 25, 2026
        m = re.match(r'^#\s+\w+,\s+(\w+ \d+, \d{4})\s*$', line)
        if m and 'date' not in info:
            try:
                info['date'] = datetime.strptime(m.group(1), '%B %d, %Y').date()
            except ValueError:
                pass

        # ## Trinity Season — Green
        m = re.match(r'^##\s+(.+?)(?:\s*—\s*.+)?\s*$', line)
        if m and 'season' not in info:
            info['season'] = m.group(1).strip()

        # **1928:** Twelfth Sunday after Trinity
        m = re.match(r'^\*\*1928:\*\*\s*(.+)\s*$', line)
        if m:
            info['name1928'] = m.group(1).strip()

    return info


def format_lesson(field: str, ref: str | None, book_table: dict) -> str:
    """Format one lesson line: **Field:** ref | URL"""
    if not ref:
        return f'**{field}:** —'
    result = build_bible_gateway_url(ref, book_table=book_table)
    if result:
        return f'**{field}:** {ref} | {result["url"]}'
    return f'**{field}:** {ref}'


def main():
    # Parse what computus.py already wrote
    info = parse_today_md(TODAY_MD)
    name1928   = info.get('name1928', '')
    today_date = info.get('date', date.today())

    # Collect slug
    slug = day_to_slug(name1928) if name1928 else None

    # Load engine and reference table
    engine     = LectionaryEngine(md_path=LECTIONARY_MD)
    book_table = _load_book_table(SCRIPTURE_CSV)

    # Resolve lessons for today
    lessons = None
    if name1928:
        if isinstance(today_date, date):
            lessons = engine.get_lessons_for_today(name1928, today_date)
        else:
            lessons = engine.get_lessons_for_sunday(name1928)

    # ── Output lines to append to today.md ───────────────────────────────────
    print()  # blank line between computus output and lectionary output

    # Collect path (relative to repo root — HTML fetches this atom directly)
    if slug:
        print(f'**Collect:** 1928/_atomic/propers/collects/{slug}.md')
    else:
        print(f'**Collect:** —')

    # Lessons
    if lessons:
        print(format_lesson('Morning 1', lessons.get('morning1'), book_table))
        print(format_lesson('Morning 2', lessons.get('morning2'), book_table))
        print(format_lesson('Evening 1', lessons.get('evening1'), book_table))
        print(format_lesson('Evening 2', lessons.get('evening2'), book_table))
        if lessons.get('note'):
            print(f'**Lectionary Note:** {lessons["note"]}')
    else:
        print('**Morning 1:** —')
        print('**Morning 2:** —')
        print('**Evening 1:** —')
        print('**Evening 2:** —')


if __name__ == '__main__':
    main()
