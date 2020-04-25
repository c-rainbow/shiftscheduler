"""Constants for Excel"""

from shiftscheduler.i18n import gettext

_ = gettext.GetTextFn('excel/constants')


# Config values for each person. The order must be preserved
CONFIG_PERSON_HEADER_NAMES = (
    _('Max consecutive workdays'),
    _('Max consecutive nights'),
    _('Min total workdays'),
    _('Max total workdays'),
)


# Config values for each date. The order must be preserved
CONFIG_DATE_HEADER_NAMES = (
    _('Number of day workers'),
    _('Number of evening workers'),
    _('Number of night workers'),
)


# Background colors to use for timetable
COLOR_DAY = 'fdbcb4'  # Peach-like soft red
COLOR_EVENING = 'fdfd96'  # Pastel yellow
COLOR_NIGHT = 'c9ffe5'  # Aero blue
COLOR_OFF = 'bbbbbb'  # Light gray


# Sheet names in Excel files
SHEET_TIMETABLE = _('Timetable')
SHEET_PERSON_CONFIG = _('Person Config')
SHEET_DATE_CONFIG = _('Date Config')
SHEET_SOFTWARE_CONFIG = _('Software Config')