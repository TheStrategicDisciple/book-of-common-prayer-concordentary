#!/usr/bin/env python3
"""
computus.py — The Concordentary Liturgical Calendar Engine
===========================================================
Computes Easter and moveable feasts using the BCP's own tables
as the authoritative data source (06_tables-and-rules.md).

Psalm rotation: 30-day daily cycle (1928 BCP) with 1945 Sunday
psalm appointments from 03_psalms-and-lessons-tables.md on Sundays.

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
# Moveable feast offsets from Easter
# ---------------------------------------------------------------------------
FEAST_OFFSETS = {
    'Septuagesima':           -63,
    'Sexagesima':             -56,
    'Quinquagesima':          -49,
    'Ash Wednesday':          -46,
    'Palm Sunday':            -7,
    'Maundy Thursday':        -3,
    'Good Friday':            -2,
    'Holy Saturday':          -1,
    'Easter Day':              0,
    'Low Sunday':              7,
    'Rogation Sunday':        35,
    'Ascension Day':          39,
    'Sunday after Ascension': 42,
    'Whitsunday':             49,
    'Trinity Sunday':         56,
}

# ---------------------------------------------------------------------------
# Fixed feasts from 05_calendar.md
# ---------------------------------------------------------------------------
FIXED_FEASTS = {
    (1,1):  'The Circumcision of our Lord Jesus Christ',
    (1,6):  'The Epiphany',
    (1,25): 'The Conversion of St. Paul',
    (2,2):  'The Purification of the Blessed Virgin Mary',
    (2,24): 'St. Matthias the Apostle',
    (3,25): 'The Annunciation of the Blessed Virgin Mary',
    (4,25): 'St. Mark the Evangelist',
    (5,1):  'St. Philip and St. James, Apostles',
    (6,11): 'St. Barnabas the Apostle',
    (6,24): 'The Nativity of St. John Baptist',
    (6,29): 'St. Peter the Apostle',
    (7,4):  'Independence Day',
    (7,25): 'St. James the Apostle',
    (8,6):  'The Transfiguration of our Lord Jesus Christ',
    (8,24): 'St. Bartholomew the Apostle',
    (9,21): 'St. Matthew, Apostle and Evangelist',
    (9,29): 'St. Michael and All Angels',
    (10,18):'St. Luke the Evangelist',
    (10,28):'St. Simon and St. Jude, Apostles',
    (11,1): 'All Saints',
    (11,30):'St. Andrew the Apostle',
    (12,21):'St. Thomas the Apostle',
    (12,25):'The Nativity of our Lord Jesus Christ (Christmas Day)',
    (12,26):'St. Stephen, Deacon and Martyr',
    (12,27):'St. John, Apostle and Evangelist',
    (12,28):'The Holy Innocents',
}

# ---------------------------------------------------------------------------
# Sunday psalm appointments (1945 revision)
# Source: 03_psalms-and-lessons-tables.md
# ---------------------------------------------------------------------------
SUNDAY_PSALMS = {
    'First Sunday in Advent':           ('8, 50', '96, 97'),
    'Second Sunday in Advent':          ('80, 82', '25, 26'),
    'Third Sunday in Advent':           ('52, 53', '93, 94'),
    'Fourth Sunday in Advent':          ('98, 99', '101, 103'),
    'First Sunday after Christmas':     ('2, 8', '89:1-30'),
    'Second Sunday after Christmas':    ('85, 87', '90, 91'),
    'First Sunday after Epiphany':      ('47, 48', '66, 67'),
    'Second Sunday after Epiphany':     ('96, 97', '45, 46'),
    'Third Sunday after Epiphany':      ('20, 21', '27, 29'),
    'Fourth Sunday after Epiphany':     ('75, 76', '107'),
    'Fifth Sunday after Epiphany':      ('63, 65', '78'),
    'Sixth Sunday after Epiphany':      ('146, 147', '148, 149, 150'),
    'Septuagesima':                     ('8, 148', '104'),
    'Sexagesima':                       ('33, 93', '139'),
    'Quinquagesima':                    ('15, 16', '111, 112'),
    'First Sunday in Lent':             ('51, 54', '119:1-32'),
    'Second Sunday in Lent':            ('6, 38', '119:33-72'),
    'Third Sunday in Lent':             ('56, 86', '119:73-104'),
    'Fourth Sunday in Lent':            ('142, 143', '119:105-144'),
    'Fifth Sunday in Lent':             ('42, 43', '119:145-176'),
    'Palm Sunday':                      ('97, 110', '22, 23'),
    'Easter Day':                       ('2, 57, 111', '113, 116, 117'),
    'First Sunday after Easter':        ('110, 111', '2, 57'),
    'Second Sunday after Easter':       ('21, 23', '116, 117'),
    'Third Sunday after Easter':        ('120, 121, 122', '123, 124, 125'),
    'Fourth Sunday after Easter':       ('126, 127, 128', '129, 130, 131'),
    'Fifth Sunday after Easter':        ('146, 147', '132, 133, 134'),
    'Sunday after Ascension':           ('108, 110', '46, 47'),
    'Whitsunday':                       ('48, 68', '104, 145'),
    'Trinity Sunday':                   ('29, 33', '93, 97, 150'),
    'First Sunday after Trinity':       ('1, 5', '2, 3, 4'),
    'Second Sunday after Trinity':      ('12, 13', '10, 11'),
    'Third Sunday after Trinity':       ('16, 17', '18'),
    'Fourth Sunday after Trinity':      ('19, 20', '24, 25'),
    'Fifth Sunday after Trinity':       ('21, 23', '26, 27'),
    'Sixth Sunday after Trinity':       ('28, 29', '30, 31'),
    'Seventh Sunday after Trinity':     ('32, 36', '33, 34'),
    'Eighth Sunday after Trinity':      ('39, 41', '37'),
    'Ninth Sunday after Trinity':       ('46, 47', '44, 45'),
    'Tenth Sunday after Trinity':       ('61, 62', '48, 49'),
    'Eleventh Sunday after Trinity':    ('63, 64', '54, 55'),
    'Twelfth Sunday after Trinity':     ('76, 77', '71, 72'),
    'Thirteenth Sunday after Trinity':  ('81, 82', '73'),
    'Fourteenth Sunday after Trinity':  ('84, 85', '74'),
    'Fifteenth Sunday after Trinity':   ('96, 97', '79, 80'),
    'Sixteenth Sunday after Trinity':   ('98, 99', '89'),
    'Seventeenth Sunday after Trinity': ('91, 92', '105'),
    'Eighteenth Sunday after Trinity':  ('111, 112', '106'),
    'Nineteenth Sunday after Trinity':  ('114, 115', '107'),
    'Twentieth Sunday after Trinity':   ('116, 117', '118'),
    'Twenty-First Sunday after Trinity':('120, 121, 122', '133, 134, 135'),
    'Twenty-Second Sunday after Trinity':('123, 124, 125', '136, 138'),
    'Twenty-Third Sunday after Trinity':('126, 127, 128', '140, 141'),
    'Twenty-Fourth Sunday after Trinity':('129, 130, 131', '144, 145'),
    'Twenty-Fifth Sunday after Trinity':('75, 76', '107'),
    'Twenty-Sixth Sunday after Trinity':('63, 65', '78'),
    'Sunday Next before Advent':        ('146, 147', '148, 149, 150'),
}

# 30-day psalm rotation (morning, evening) by day of month
# Based on 1928 BCP daily office psalm table
DAILY_PSALMS = {
    1:  ('1, 2, 3, 4, 5', '6, 7, 8'),
    2:  ('9, 10, 11', '12, 13, 14'),
    3:  ('15, 16, 17', '18'),
    4:  ('19, 20, 21', '22, 23'),
    5:  ('24, 25, 26', '27, 28, 29'),
    6:  ('30, 31', '32, 33, 34'),
    7:  ('35, 36', '37'),
    8:  ('38, 39, 40', '41, 42, 43'),
    9:  ('44, 45, 46', '47, 48, 49'),
    10: ('50, 51', '52, 53, 54, 55'),
    11: ('56, 57, 58', '59, 60, 61'),
    12: ('62, 63, 64', '65, 66, 67'),
    13: ('68', '69, 70'),
    14: ('71, 72', '73, 74'),
    15: ('75, 76, 77', '78'),
    16: ('79, 80', '81, 82, 83'),
    17: ('84, 85, 86', '87, 88'),
    18: ('89', '90, 91'),
    19: ('92, 93, 94', '95, 96, 97'),
    20: ('98, 99, 100, 101', '102, 103'),
    21: ('104', '105'),
    22: ('106', '107'),
    23: ('108, 109', '110, 111, 112'),
    24: ('113, 114, 115', '116, 117, 118'),
    25: ('119:1-32', '119:33-72'),
    26: ('119:73-104', '119:105-144'),
    27: ('119:145-176', '120, 121, 122, 123, 124, 125'),
    28: ('126, 127, 128, 129, 130, 131', '132, 133, 134'),
    29: ('135, 136', '137, 138, 139'),
    30: ('140, 141, 142, 143', '144, 145'),
    31: ('146, 147', '148, 149, 150'),
}

# 1979 Proper numbers (by Easter date offset, Trinity season)
# Proper 1 begins the Sunday closest to May 11
# We map Trinity Sundays to Propers
TRINITY_TO_PROPER = {
    1: 4, 2: 5, 3: 6, 4: 7, 5: 8, 6: 9, 7: 10, 8: 11,
    9: 12, 10: 13, 11: 14, 12: 15, 13: 16, 14: 17, 15: 18,
    16: 19, 17: 20, 18: 21, 19: 22, 20: 23, 21: 24, 22: 25,
    23: 26, 24: 27, 25: 28, 26: 29,
}

LETTERS = ['A', 'B', 'C', 'D', 'E', 'F', 'G']

# ---------------------------------------------------------------------------
# Core computus functions
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
    raise ValueError(f"Year {year} out of TABLE II range")


def paschal_full_moon(year: int) -> datetime.date:
    gn = golden_number(year)
    anchor = get_table_ii_anchor(year)
    day = TABLE_II[anchor][gn - 1]
    if day == 0:
        raise ValueError(f"TABLE II gap: year {year}, GN {gn}")
    return datetime.date(year, 3, day) if day > 20 else datetime.date(year, 4, day)


def dominical_letter(year: int) -> str:
    jan1 = datetime.date(year, 1, 1)
    days_to_sunday = (6 - jan1.weekday()) % 7
    letter = LETTERS[days_to_sunday]
    if is_leap(year):
        idx = LETTERS.index(letter)
        letter = LETTERS[(idx - 1) % 7]
    return letter


def perpetual_letter(date: datetime.date) -> str:
    day_of_year = date.timetuple().tm_yday
    if is_leap(date.year) and date >= datetime.date(date.year, 3, 1):
        day_of_year -= 1
    return LETTERS[(day_of_year - 1) % 7]


def easter(year: int) -> datetime.date:
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
# Season and Sunday name
# ---------------------------------------------------------------------------

def advent_sunday_1(year: int) -> datetime.date:
    christmas = datetime.date(year, 12, 25)
    days_back = (christmas.weekday() + 1) % 7
    advent_4 = christmas - datetime.timedelta(days=days_back)
    return advent_4 - datetime.timedelta(weeks=3)


def liturgical_position(date: datetime.date) -> dict:
    """
    Returns full liturgical position for a date including:
    - season, color
    - 1928 Sunday name
    - 1979 equivalent
    - sunday number (for Trinity season)
    """
    year = date.year
    feasts = moveable_feasts(year)
    e = feasts['Easter Day']
    ash_wed = feasts['Ash Wednesday']
    pentecost = feasts['Whitsunday']
    trinity = feasts['Trinity Sunday']
    septuagesima = feasts['Septuagesima']
    sexagesima = feasts['Sexagesima']
    quinquagesima = feasts['Quinquagesima']
    palm = feasts['Palm Sunday']
    advent_1 = advent_sunday_1(year)
    prev_advent_1 = advent_sunday_1(year - 1)
    prev_christmas = datetime.date(year - 1, 12, 25)

    pos = {
        'season': '',
        'color': '',
        'name_1928': '',
        'name_1979': '',
        'trinity_number': None,
        'is_sunday': date.weekday() == 6,
    }

    # Advent (previous year's)
    if prev_advent_1 <= date < datetime.date(year, 1, 1):
        pos.update({'season': 'Advent', 'color': 'violet'})
        weeks = (date - prev_advent_1).days // 7 + 1
        names = ['First', 'Second', 'Third', 'Fourth']
        pos['name_1928'] = f"{names[min(weeks-1,3)]} Sunday in Advent"
        pos['name_1979'] = f"Advent {min(weeks,4)}"

    # Christmastide Jan 1-5
    elif datetime.date(year, 1, 1) <= date < datetime.date(year, 1, 6):
        pos.update({'season': 'Christmastide', 'color': 'white',
                    'name_1928': 'The Circumcision / Christmastide',
                    'name_1979': 'Christmas Season'})

    # Epiphany season
    elif datetime.date(year, 1, 6) <= date < septuagesima:
        pos.update({'season': 'Epiphany', 'color': 'green'})
        epiphany = datetime.date(year, 1, 6)
        # Find the Sunday on or after Epiphany
        days_to_sun = (6 - epiphany.weekday()) % 7
        first_sun = epiphany + datetime.timedelta(days=days_to_sun if days_to_sun else 7)
        if date < first_sun:
            pos['name_1928'] = 'The Epiphany'
            pos['name_1979'] = 'The Epiphany'
        else:
            weeks = (date - first_sun).days // 7 + 1
            ordinals = ['First','Second','Third','Fourth','Fifth','Sixth']
            pos['name_1928'] = f"{ordinals[min(weeks-1,5)]} Sunday after Epiphany"
            pos['name_1979'] = f"Epiphany {min(weeks,6)}"

    # Pre-Lent
    elif date == septuagesima:
        pos.update({'season': 'Pre-Lent', 'color': 'green',
                    'name_1928': 'Septuagesima', 'name_1979': 'Epiphany 9'})
    elif date == sexagesima:
        pos.update({'season': 'Pre-Lent', 'color': 'green',
                    'name_1928': 'Sexagesima', 'name_1979': 'Epiphany 10'})
    elif date == quinquagesima:
        pos.update({'season': 'Pre-Lent', 'color': 'green',
                    'name_1928': 'Quinquagesima', 'name_1979': 'Epiphany 11'})
    elif septuagesima < date < ash_wed:
        pos.update({'season': 'Pre-Lent', 'color': 'green'})

    # Lent
    elif ash_wed <= date < palm:
        pos.update({'season': 'Lent', 'color': 'violet'})
        if date == ash_wed:
            pos['name_1928'] = 'Ash Wednesday'
            pos['name_1979'] = 'Ash Wednesday'
        else:
            # Find which Sunday in Lent
            first_lent_sun = ash_wed + datetime.timedelta(days=(6 - ash_wed.weekday()) % 7)
            if date >= first_lent_sun:
                weeks = (date - first_lent_sun).days // 7 + 1
                ordinals = ['First','Second','Third','Fourth','Fifth']
                pos['name_1928'] = f"{ordinals[min(weeks-1,4)]} Sunday in Lent"
                pos['name_1979'] = f"Lent {min(weeks,5)}"

    # Holy Week
    elif palm <= date < e:
        pos.update({'season': 'Holy Week', 'color': 'crimson'})
        holy_names = {
            -7: 'Palm Sunday', -3: 'Maundy Thursday',
            -2: 'Good Friday', -1: 'Holy Saturday'
        }
        offset = (date - e).days
        pos['name_1928'] = holy_names.get(offset, 'Holy Week')
        pos['name_1979'] = holy_names.get(offset, 'Holy Week')

    # Eastertide
    elif e <= date < pentecost:
        pos.update({'season': 'Eastertide', 'color': 'white'})
        if date == e:
            pos['name_1928'] = 'Easter Day'
            pos['name_1979'] = 'Easter Day'
        else:
            weeks = (date - e).days // 7
            ordinals = ['First','Second','Third','Fourth','Fifth']
            if weeks == 6:
                pos['name_1928'] = 'Sunday after Ascension'
                pos['name_1979'] = 'Easter 7'
            elif weeks > 0:
                pos['name_1928'] = f"{ordinals[weeks-1]} Sunday after Easter"
                pos['name_1979'] = f"Easter {weeks}"

    # Whitsunday
    elif date == pentecost:
        pos.update({'season': 'Whitsunday', 'color': 'red',
                    'name_1928': 'Whitsunday (Pentecost)',
                    'name_1979': 'Day of Pentecost'})

    # Whitsuntide (week after Pentecost)
    elif pentecost < date < trinity:
        pos.update({'season': 'Whitsuntide', 'color': 'red',
                    'name_1928': 'Whitsuntide',
                    'name_1979': 'Pentecost Season'})

    # Trinity Sunday
    elif date == trinity:
        pos.update({'season': 'Trinity Season', 'color': 'white',
                    'name_1928': 'Trinity Sunday',
                    'name_1979': 'Trinity Sunday'})

    # Trinity Season
    elif trinity < date < advent_1:
        pos.update({'season': 'Trinity Season', 'color': 'green'})
        weeks = (date - trinity).days // 7
        ordinals = [
            'First','Second','Third','Fourth','Fifth','Sixth','Seventh',
            'Eighth','Ninth','Tenth','Eleventh','Twelfth','Thirteenth',
            'Fourteenth','Fifteenth','Sixteenth','Seventeenth','Eighteenth',
            'Nineteenth','Twentieth','Twenty-First','Twenty-Second',
            'Twenty-Third','Twenty-Fourth','Twenty-Fifth','Twenty-Sixth',
        ]
        # Check if it's the Sunday next before Advent
        next_sunday = date + datetime.timedelta(days=(6 - date.weekday()) % 7)
        if next_sunday >= advent_1 and date.weekday() == 6:
            pos['name_1928'] = 'Sunday Next before Advent'
            pos['name_1979'] = 'Proper 29 (Christ the King)'
        elif weeks > 0 and weeks <= len(ordinals):
            pos['name_1928'] = f"{ordinals[weeks-1]} Sunday after Trinity"
            pos['trinity_number'] = weeks
            proper = TRINITY_TO_PROPER.get(weeks, weeks + 3)
            pos['name_1979'] = f"Ordinary Time — Proper {proper}"

    # Advent (current year)
    elif advent_1 <= date < datetime.date(year, 12, 25):
        pos.update({'season': 'Advent', 'color': 'violet'})
        weeks = (date - advent_1).days // 7 + 1
        names = ['First', 'Second', 'Third', 'Fourth']
        pos['name_1928'] = f"{names[min(weeks-1,3)]} Sunday in Advent"
        pos['name_1979'] = f"Advent {min(weeks,4)}"

    # Christmastide
    else:
        pos.update({'season': 'Christmastide', 'color': 'white',
                    'name_1928': 'Christmastide',
                    'name_1979': 'Christmas Season'})
        if date == datetime.date(year, 12, 25):
            pos['name_1928'] = 'Christmas Day'
            pos['name_1979'] = 'Christmas Day'

    return pos


# ---------------------------------------------------------------------------
# Psalm rotation
# ---------------------------------------------------------------------------

def get_psalms(date: datetime.date, pos: dict) -> tuple:
    """
    Returns (morning_psalms, evening_psalms).
    Sundays: use 1945 Sunday psalm table if available.
    Weekdays: use 30-day daily rotation.
    """
    if date.weekday() == 6 and pos.get('name_1928') in SUNDAY_PSALMS:
        morning, evening = SUNDAY_PSALMS[pos['name_1928']]
        return (morning, evening, '1945 Sunday table')

    day = date.day
    if day > 30:
        day = 30
    morning, evening = DAILY_PSALMS.get(day, ('—', '—'))
    return (morning, evening, '30-day rotation')


# ---------------------------------------------------------------------------
# Fasting / abstinence
# ---------------------------------------------------------------------------

def fasting_note(date: datetime.date, pos: dict, feasts: dict) -> str:
    season = pos.get('season', '')
    # Fridays in Lent
    if season == 'Lent' and date.weekday() == 4:
        return 'Day of fasting and abstinence (Friday in Lent)'
    # Ash Wednesday
    if date == feasts.get('Ash Wednesday'):
        return 'Day of fasting and abstinence (Ash Wednesday)'
    # Good Friday
    if date == feasts.get('Good Friday'):
        return 'Day of fasting and abstinence (Good Friday)'
    # Rogation Days (Mon-Wed before Ascension)
    ascension = feasts.get('Ascension Day')
    if ascension:
        rogation_mon = ascension - datetime.timedelta(days=3)
        if rogation_mon <= date <= rogation_mon + datetime.timedelta(days=2):
            return 'Rogation Day — day of fasting and prayer'
    # Ember Days (Wed/Fri/Sat after: Pentecost, Sep 14 week, Dec 13 week, Lent 1)
    # Simplified: flag Wednesdays and Fridays in Ember weeks
    return ''


# ---------------------------------------------------------------------------
# Upcoming feasts
# ---------------------------------------------------------------------------

def upcoming_events(date: datetime.date, feasts: dict) -> list:
    """Return next 2 upcoming significant events within 60 days."""
    events = []

    # Fixed feasts
    for (month, day), name in FIXED_FEASTS.items():
        candidate = datetime.date(date.year, month, day)
        if candidate <= date:
            candidate = datetime.date(date.year + 1, month, day)
        diff = (candidate - date).days
        if 0 < diff <= 60:
            events.append((diff, name, candidate))

    # Moveable feasts (current and next year)
    for name, feast_date in feasts.items():
        if feast_date <= date:
            continue
        diff = (feast_date - date).days
        if 0 < diff <= 60:
            events.append((diff, name, feast_date))

    # Next season change
    year = date.year
    season_changes = [
        (datetime.date(year, 1, 6), 'Epiphany Season begins'),
        (advent_sunday_1(year - 1) + datetime.timedelta(weeks=4), 'Christmastide begins'),
        (moveable_feasts(year)['Septuagesima'], 'Pre-Lent begins (Septuagesima)'),
        (moveable_feasts(year)['Ash Wednesday'], 'Lent begins'),
        (moveable_feasts(year)['Easter Day'], 'Eastertide begins'),
        (moveable_feasts(year)['Whitsunday'], 'Whitsuntide begins'),
        (moveable_feasts(year)['Trinity Sunday'], 'Trinity Season begins'),
        (advent_sunday_1(year), 'Advent begins'),
        (datetime.date(year, 12, 25), 'Christmastide begins'),
    ]
    for sc_date, sc_name in season_changes:
        if sc_date <= date:
            continue
        diff = (sc_date - date).days
        if 0 < diff <= 90:
            events.append((diff, sc_name, sc_date))

    events.sort()
    return events[:3]


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def describe_day(date: datetime.date) -> str:
    year = date.year
    feasts = moveable_feasts(year)
    e = feasts['Easter Day']
    pfm = paschal_full_moon(year)
    gn = golden_number(year)
    dl = dominical_letter(year)
    pos = liturgical_position(date)
    morning_ps, evening_ps, ps_source = get_psalms(date, pos)
    fast = fasting_note(date, pos, feasts)
    upcoming = upcoming_events(date, feasts)

    lines = []
    lines.append(f"# {date.strftime('%A, %B %-d, %Y')}")
    lines.append('')
    lines.append(f"## {pos['season']} — {pos['color'].capitalize()}")

    if pos['name_1928']:
        lines.append(f"**1928:** {pos['name_1928']}")
    if pos['name_1979']:
        lines.append(f"**1979:** {pos['name_1979']}")

    lines.append('')

    # Fixed feast today
    fixed = FIXED_FEASTS.get((date.month, date.day))
    if fixed:
        lines.append(f"**Feast:** {fixed}")

    # Moveable feast today
    for fname, fdate in feasts.items():
        if fdate == date and fname not in ('Easter Day',):
            lines.append(f"**Feast:** {fname}")

    if fast:
        lines.append(f"**{fast}**")

    lines.append('')
    lines.append('### Psalms')
    lines.append(f"**Morning:** {morning_ps}")
    lines.append(f"**Evening:** {evening_ps}")
    lines.append(f"*({ps_source})*")

    if upcoming:
        lines.append('')
        lines.append('### Coming Up')
        for diff, name, event_date in upcoming:
            lines.append(f"**{name}** — {event_date.strftime('%B %-d')} ({diff} days)")

    lines.append('')
    lines.append('---')
    lines.append('')
    lines.append('### Computus')
    lines.append(f"**Golden Number:** {gn}")
    lines.append(f"**Dominical Letter:** {dl}")
    lines.append(f"**Paschal Full Moon:** {pfm.strftime('%B %-d, %Y')}")
    lines.append(f"**Easter {year}:** {e.strftime('%B %-d, %Y')}")
    lines.append(f"**Method:** BCP 1928, TABLE I and TABLE II — 06_tables-and-rules.md")

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
