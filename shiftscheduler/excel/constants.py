"""Constants for Excel"""

import gettext
_ = gettext.gettext


# Config values for each person. The order must be preserved
CONFIG_PERSON_HEADER_NAMES = (
    _('최대 근무일 (연속)'),
    _('최대 나이트 (연속)'),
    _('최소 근무일 (전체)'),
    _('최대 근무일 (전체)'),
)


# Config values for each date. The order must be preserved
CONFIG_DATE_HEADER_NAMES = (
    _('데이 근무자 수'),
    _('이브닝 근무자 수'),
    _('나이트 근무자 수'),
)


# Background colors to use for timetable
COLOR_DAY = 'fdbcb4'  # Peach-like soft red
COLOR_EVENING = 'fdfd96'  # Pastel yellow
COLOR_NIGHT = 'c9ffe5'  # Aero blue
COLOR_OFF = 'bbbbbb'  # Light gray


# Sheet names in Excel files
SHEET_TIMETABLE = _('일정표')
SHEET_PERSON_CONFIG = _('간호사별 설정')
SHEET_DATE_CONFIG = _('날짜별 설정')
SHEET_SOFTWARE_CONFIG = _('Config')