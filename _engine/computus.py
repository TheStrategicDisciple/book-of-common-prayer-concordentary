#!/usr/bin/env python3
"""
computus.py — The Concordentary Liturgical Calendar Engine
===========================================================
Computes Easter and moveable feasts using the BCP's own tables
as the authoritative data source (06_tables-and-rules.md).

The engine does not re-derive astronomical math. It looks up
answers from TABLE II (Golden Number -> paschal full moon date)
and uses TABLE I logic (Dominical Letter) exactly as the BCP intends.

Provenance:
    Book of Common Prayer, 1928 (PECUSA)
    Tables and Rules for the Movable and Immovable Feasts, pp. l-lii
    The Concordentary -- repo.thestrategicdisciple.com

Usage:
    python computus.py                          # today (via NIST)
    python computus.py --date 2026-12-21        # specific date
    python computus.py --validate --start 2026 --end 2030
"""

import argparse
import datetime
import sys

# ---------------------------------------------------------------------------
# TABLE II -- Golden Number -> Paschal Full Moon date
# ---------------------------------------------------------------------------
# Source: 06_tables-and-rules.md, TABLE II
# day > 20 -> March; day <= 20 -> April.

TABLE_II = {
    1600: [12,1,21,9,29,17,6,26,14,3,23,11,31,18,8,28,16,5,25],
    1700: [13,2,22,10,30,18,7,27,15,4,24,12,1,21,9,29,17,6,26],
    1900: [14,3,23,11,31,18,8,28,16,5,25,13,2,22,10,30,17,7,27],
    2200: [15,4,24,12,1,21,9,29,17,6,26,14,3,23,11,31,18,8,28],
    2300: [16,5,25,13,2,22,10,30,18,7,27,15,4,24,12,1,21,9,29],
    2600: [17,6,26,14,3,23,11,31,18,8,28,16,5,25,13,2,22,10,30],
    2900: [18,7,27,15,4,24,12,1,21,9,29,17,6,26,14,3,23,11,31],
    3100: [18,8,28,16,5,25,13,2,22,10,30,17,7,27,15,4,24,12,1],
    3400: [21,9,29,17,6,26,14,3,23,11,31,18,8,28,16,5,25,13,2],
    3500: [22,10,30,18,7,27,15,4,24,1,21,9,29,17,6,26,14,3,0],
    3800: [23,11,31,18,8,28,16,5,25,13,2,22,10,30,17,7,27,15,4],
    4100: [24,12,1,21,9,29,17,6,26,14,3,23,11,31,18,8,28,16,5],
    4200: [25,13,2,22,10,30,18,7,27,15,4,24,12,1,21,9,29,17,6],
    4500: [26,14,3,23,11,31,18,8,28,16,5,25,13,2,22,10,30,17,7],
    4700: [27,15,4,24,12,1,21,9,29,17,6,26,14,3,23,11,31,18,8],
    5000: [28,16,5,25,13,2,22,10,30,18,7,27,15,4,24,12,1,21,9],
    5100: [29,17,6,26,14,3,23,11,31,18,8,28,16,5,25,13,2,22,10],
    5400: [30,18,7,27,15,4,24,12,1,21,9,29,17,6,26,14,3,23,11],
    5700: [31,18,8,28,16,5,25,13,2,22,10,30,17,7,27,15,4,24,12],
    5900: [1,21,9,29,17,6,26,14,3,23,11,31,18,8,28,16,5,25,13],
    6200: [2,22,10,30,18,7,27,15,4,24,12,1,21,9,29,17,6,26,14],
    6300: [3,23,11,31,18,8,28,16,5,25,13,2,22,10,30,17,7,27,15],
    6600: [4,24,12,1,21,9,29,17,6,26,14,3,23,11,31,18,8,28,16],
    6700: [5,25,13,2,22,10,30,18,7,27,15,4,24,12,1,21,9,29,17],
    7000: [6,26,14,3,23,11,31,18,8,28,16,5,25,13,2,22,10,30,17],
    7300: [7,27,15,4,24,12,1,21,9,29,17,6,26,14,3,23,11,31,18],
    7500: [8,28,16,5,25,13,2,22,10,30,18,7,27,15,4,24,12,1,21],
    7800: [9,29,17,6,26,14,3,23,11,31,18,8,28,16,5,25,13,2,22],
    7900: [10,30,18,7,27,15,4,24,12,1,21,9,29,17,6,26,14,3,23],
    8200: [11,31,18,8,28,16,5,25,13,2,22,10,30,17,7,27,15,4,24],
}

TABLE_II_ANCHORS = sorted(TABLE_II.keys(), reverse=True)

# ---------------------------------------------------------------------------
# Moveable feast offsets from Easter Sunday
# ---------------------------------------------------------------------------
FEAST_OFFSETS = {
    'Septuagesima':             -63,
    'Sexagesima':               -56,
    'Quinquagesima':            -49,
    'Ash Wednesday':            -46,
    'Palm Sunday':              -7,
    'Maundy Thursday':          -3,
    'Good Friday':              -2,
    'Holy Saturday':            -1,
    'Easter Day':                0,
    'Low Sunday':                7,
    'Rogation Sunday':          35,
    'Ascension Day':            39,
    'Sunday after Ascension':   42,
    'Whitsunday':               49,
    'Trinity Sunday':           56,
}

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

# ---------------------------------------------------------------------------
# Core functions
# ---------------------------------------------------------------------------

def golden_number(year: int) -> int:
    gn = (year + 1) % 19
    return gn if gn != 0 else 19


def is_leap(year: int) -> bool:
    return year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)


def get_table_ii_anchor(year: int) -> int:
    century = (year // 100) * 100
    for anchor in TABLE_II_ANCHORS:
        if century >= anchor:
            return anchor
    raise ValueError(f"Year {year} out of TABLE II range (1600-8400)")


def paschal_full_moon(year: int) -> datetime.date:
    gn = golden_number(year)
    anchor = get_table_ii_anchor(year)
    day = TABLE_II[anchor][gn - 1]
    if day == 0:
        raise ValueError(f"TABLE II gap: year {year}, GN {gn}, anchor {anchor}")
    return datetime.date(year, 3, day) if day > 20 else datetime.date(year, 4, day)


def dominical_letter(year: int) -> str:
    """
    The Dominical Letter is the perpetual-calendar letter that falls on Sunday.
    In leap years, the letter shifts after Feb 28 — for Easter (always March/April)
    we need the post-Feb letter, which is one step earlier in the A-G cycle.
    """
    jan1 = datetime.date(year, 1, 1)
    days_to_sunday = (6 - jan1.weekday()) % 7  # Mon=0..Sun=6
    letter = LETTERS[days_to_sunday]
    if is_leap(year):
        # Post-Feb letter shifts back one step
        idx = LETTERS.index(letter)
        letter = LETTERS[(idx - 1) % 7]
    return letter


def perpetual_letter(date: datetime.date) -> str:
    """
    The perpetual-calendar letter for a specific date.
    Jan 1 = A, cycling A-G. In leap years, Feb 29 is unlabelled,
    so dates from March 1 onward shift back one step.
    """
    day_of_year = date.timetuple().tm_yday
    if is_leap(date.year) and date >= datetime.date(date.year, 3, 1):
        day_of_year -= 1
    return LETTERS[(day_of_year - 1) % 7]


def easter(year: int) -> datetime.date:
    """
    Compute Easter Sunday.
    1. Paschal full moon from TABLE II via Golden Number
    2. Dominical Letter (post-Feb for leap years)
    3. First Sunday AFTER the full moon; if full moon = Sunday, next Sunday
    """
    pfm = paschal_full_moon(year)
    dl = dominical_letter(year)
    pfm_letter = perpetual_letter(pfm)

    sunday_idx = LETTERS.index(dl)
    pfm_idx = LETTERS.index(pfm_letter)

    days_to_sunday = (sunday_idx - pfm_idx) % 7
    if days_to_sunday == 0:
        days_to_sunday = 7

    return pfm + datetime.timedelta(days=days_to_sunday)


def moveable_feasts(year: int) -> dict:
    e = easter(year)
    return {name: e + datetime.timedelta(days=offset)
            for name, offset in FEAST_OFFSETS.items()}


# ---------------------------------------------------------------------------
# Season determination (1928 BCP)
# ---------------------------------------------------------------------------

def advent_sunday_1(year: int) -> datetime.date:
    christmas = datetime.date(year, 12, 25)
    days_back = (christmas.weekday() + 1) % 7
    advent_4 = christmas - datetime.timedelta(days=days_back)
    return advent_4 - datetime.timedelta(weeks=3)


def liturgical_season(date: datetime.date) -> tuple:
    year = date.year
    feasts = moveable_feasts(year)
    e = feasts['Easter Day']
    ash_wed = feasts['Ash Wednesday']
    pentecost = feasts['Whitsunday']
    trinity = feasts['Trinity Sunday']
    septuagesima = feasts['Septuagesima']
    advent_1 = advent_sunday_1(year)
    prev_advent_1 = advent_sunday_1(year - 1)

    if prev_advent_1 <= date < datetime.date(year, 1, 6):
        return ('Advent', 'violet')
    elif datetime.date(year, 1, 1) <= date < datetime.date(year, 1, 6):
        return ('Christmastide', 'white')
    elif datetime.date(year, 1, 6) <= date < septuagesima:
        return ('Epiphany', 'green')
    elif septuagesima <= date < ash_wed:
        return ('Pre-Lent', 'green')
    elif ash_wed <= date < e - datetime.timedelta(days=7):
        return ('Lent', 'violet')
    elif e - datetime.timedelta(days=7) <= date < e:
        return ('Holy Week', 'crimson')
    elif e <= date < pentecost:
        return ('Eastertide', 'white')
    elif date == pentecost:
        return ('Whitsunday', 'red')
    elif pentecost < date <= trinity:
        return ('Whitsuntide', 'red')
    elif trinity < date < advent_1:
        return ('Trinity Season', 'green')
    elif advent_1 <= date < datetime.date(year, 12, 25):
        return ('Advent', 'violet')
    else:
        return ('Christmastide', 'white')


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def describe_day(date: datetime.date) -> str:
    year = date.year
    feasts = moveable_feasts(year)
    e = feasts['Easter Day']
    season, color = liturgical_season(date)

    lines = [
        f"Today is {date.strftime('%A, %B %-d, %Y')}.",
        f"Liturgical season: {season}.",
        f"Liturgical color: {color.capitalize()}.",
        f"Easter {year}: {e.strftime('%B %-d, %Y')}.",
    ]
    for name, feast_date in feasts.items():
        if feast_date == date:
            lines.append(f"Today is {name}.")
    return '\n'.join(lines)


# ---------------------------------------------------------------------------
# Date source
# ---------------------------------------------------------------------------

def get_date_from_nist() -> datetime.date:
    try:
        import urllib.request, json
        url = 'https://timeapi.io/api/time/current/zone?timeZone=America/New_York'
        with urllib.request.urlopen(url, timeout=5) as r:
            data = json.loads(r.read())
            return datetime.date.fromisoformat(data['date'])
    except Exception as ex:
        print(f"Warning: Could not fetch time ({ex}). Using system date.", file=sys.stderr)
        return datetime.date.today()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description='Concordentary Computus Engine -- BCP 1928 liturgical calendar'
    )
    parser.add_argument('--date', type=str,
                        help='Specific date (YYYY-MM-DD). Bypasses NIST.')
    parser.add_argument('--validate', action='store_true',
                        help='Output Easter dates for a range of years.')
    parser.add_argument('--start', type=int, default=2026)
    parser.add_argument('--end',   type=int, default=2030)
    args = parser.parse_args()

    if args.validate:
        print("Concordentary Computus Engine -- Easter Validation")
        print("Source: BCP 1928 TABLE I and TABLE II (06_tables-and-rules.md)")
        print(f"Range: {args.start}-{args.end}")
        print("Compare against: 1979 BCP printed Easter dates")
        print("=" * 55)
        for year in range(args.start, args.end + 1):
            try:
                e = easter(year)
                gn = golden_number(year)
                dl = dominical_letter(year)
                print(f"{year}  GN={gn:2d}  DL={dl}  Easter: {e.strftime('%B %-d')} ({e.strftime('%A')})")
            except Exception as ex:
                print(f"{year}  ERROR: {ex}")
        return

    if args.date:
        try:
            target = datetime.date.fromisoformat(args.date)
        except ValueError:
            print(f"Error: Invalid date '{args.date}'. Use YYYY-MM-DD.", file=sys.stderr)
            sys.exit(1)
    else:
        target = get_date_from_nist()

    print(describe_day(target))


if __name__ == '__main__':
    main()
