
import configparser
import gettext
import os


_LOCALE_DIR = 'locales'
_LANGUAGE_INI_FILEPATH = 'shiftscheduler/i18n/language.ini'
_code = None

def GetTextFn(domain_name):
    code = GetLanguageCode()
    language = gettext.translation(domain_name, localedir=_LOCALE_DIR, languages=[code])
    return language.gettext


def GetLanguageCode():
    global _code
    if _code is None:
        config = configparser.ConfigParser()
        config.read_file(open(_LANGUAGE_INI_FILEPATH))
        _code = config.get('DEFAULT', 'LanguageCode')

    return _code
