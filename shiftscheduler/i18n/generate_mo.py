
import pathlib
import sys

from Tools.i18n import msgfmt

LOCALE_DIRECTORY = '../../locales/{locale_code}/LC_MESSAGES'





def CreateMoFile(locale_code):

    locale_path = LOCALE_DIRECTORY.format(locale_code=locale_code)
    locale_path = pathlib.Path(locale_path).resolve()

    if not locale_path.exists():
        print('Path does not exist: ', locale_path)
        return


    po_filepaths = list(pathlib.Path(locale_path).glob('**/*.po'))

    for po_filepath in po_filepaths:
        path = str(po_filepath)
        msgfmt.make(path, None)


if __name__ == '__main__':
    locale_code = sys.argv[1]
    CreateMoFile(locale_code)
