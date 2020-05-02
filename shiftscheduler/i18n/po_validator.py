'''

PO validator

. 템플릿은 있는데 po 파일이 없는 경우
. 템플릿이 없는데 po 파일이 있는 경우
. msgid에 맞는 msgstr이 존재 하는지
. msgstr이 "" 이거나 빈칸만 있는 경우
. msgstr이 msgid랑 똑같은 경우  - msgid가 여러줄일때
. msgstr에 있는 field가 없거나 추가로 있는 경우  (string.Formatter 이용. 없는 경우는 warning)
. 같은 msgid 여러개인지
. 템플릿에 있는 msgid가 po파일에 없는 경우  - msgid가 여러줄일때
. 템플릿에 없는 msgid가 po파일에 있는 경우  - msgid가 여러줄일때

'''
import pathlib
import string
import sys

import msgfmt_modified as msgfmt



TEMPLATES_DIRECTORY = '../../locales/templates'
LOCALE_DIRECTORY = '../../locales/{locale_code}/LC_MESSAGES'

FORMATTER = string.Formatter()


def getFields(message):
    fields = set()
    message = str(message)
    if not message:
        return fields
    results = FORMATTER.parse(message)
    for parsed in results:
        fields.add(parsed[1])

    return fields


def IsEmptyOrWhiteSpace(msgstr):
    return msgstr.isspace()


def IsSameAsMsgId(msgid, msgstr):
    return msgid.strip() == msgstr.strip()


def GetExtraOrMissingFields(msgid, msgstr):
    msgid_fields = getFields(msgid)
    msgstr_fields = getFields(msgstr)

    extra_fields = msgstr_fields - msgid_fields
    missing_fields = msgid_fields - msgstr_fields

    return (extra_fields, missing_fields)


def getDirs(locale_code):
    template_path = pathlib.Path(TEMPLATES_DIRECTORY)
    template_path = template_path.resolve()
    locale_path = pathlib.Path(LOCALE_DIRECTORY.format(locale_code=locale_code))
    locale_path = locale_path.resolve()

    return (template_path, locale_path)


# When dir1 and dir2 should have the same directory structure and file paths,
# return all files that exist in dir1 but have no matching files in dir2
def getExtraFiles(dir1, dir2, ext1, ext2):
    extra_files = []
    matching_files = getMatchingFiles(dir1, dir2, ext1, ext2)
    for src_filepath, dst_filepath in matching_files:
        if not dst_filepath.exists():
            extra_files.append(src_filepath)

    return extra_files


def getMatchingFiles(dir1, dir2, ext1, ext2):
    dir1_parts = dir1.parts
    dir1_filepaths = list(dir1.glob('**/*' + ext1))
    dir2_filepaths = []

    for dir1_filepath in dir1_filepaths:
        stem = dir1_filepath.stem
        parts = list(dir1_filepath.parts)
        parts = parts[len(dir1.parts):]
        parts[-1] = stem + ext2
        print('parts:', parts)
        dir2_filepath = dir2.joinpath(*parts)
        dir2_filepaths.append(dir2_filepath)

    return zip(dir1_filepaths, dir2_filepaths)


def GetFiles(locale_code):
    template_path, locale_path = getDirs(locale_code)
    return getMatchingFiles(template_path, locale_path, '.pot', '.po')


def GetMissingPoFiles(locale_code):
    template_path, locale_path = getDirs(locale_code)
    return getExtraFiles(template_path, locale_path, '.pot', '.po')


def GetExtraPoFiles(locale_code):
    template_path, locale_path = getDirs(locale_code)
    return getExtraFiles(locale_path, template_path, '.po', '.pot')


def GetExtraOrMissingMsgIds(pot_msgids, po_msgids):
    pot_msgids = set(pot_msgids)
    po_msgids = set(po_msgids)
    
    extra_msgids = po_msgids - pot_msgids
    missing_msgids = pot_msgids - po_msgids

    return (extra_msgids, missing_msgids)


def GetDuplicateMsgIds(msgids):
    visited = set()
    duplicates = set()
    for msgid in msgids:
        if msgid in visited:
            duplicates.add(msgid)
        else:
            visited.add(msgid)

    return duplicates


def ParseFile(filepath):
    parser = msgfmt.PoFileParser(filepath)
    parser.make()
    return parser


def Validate(locale_code):
    #missing_po_files = GetMissingPoFiles(locale_code)
    #extra_po_files = GetExtraPoFiles(locale_code)
    missing_po_files = []
    extra_po_files = []

    if missing_po_files:
        print('Missing PO files for templates:', missing_po_files)
    if extra_po_files:
        print('PO files for non-existent templates:', extra_po_files)

    if missing_po_files or extra_po_files:
        return

    matching_files = GetFiles(locale_code)
    errors = []
    warnings = []
    for pot_filepath, po_filepath in matching_files:
        po_parser = msgfmt.PoFileParser(str(po_filepath.resolve()))
        po_parser.make()
        pot_parser = msgfmt.PoFileParser(str(pot_filepath.resolve()))
        pot_parser.make()

        po_ids = set(po_parser.ids)
        pot_ids = set(pot_parser.ids)

        extra_ids, missing_ids = GetExtraOrMissingMsgIds(pot_ids, po_ids)
        if extra_ids:
            errors.append('msgids exist in PO file but not in template: %s' % extra_ids)
        if missing_ids:
            errors.append('Missing msgids in PO file: %s' % missing_ids)

        if extra_ids or missing_ids:
            continue

        duplicate_ids = GetDuplicateMsgIds(po_parser.ids)
        if duplicate_ids:
            errors.append('Multiple identical msgids exist: %s' % duplicate_ids)
            continue
        
        # If msgstr exists for all msgids
        for msgid, msgstr in po_parser.messages.items():
            has_error = False
            if msgstr is None:
                errors.append('msgstr does not exists for msgid "%s"' % msgid)
                has_error = True
            elif IsEmptyOrWhiteSpace(msgstr):
                errors.append('msgstr is empty for msgid "%s"' % msgid)
                has_error = True
            elif IsSameAsMsgId(msgid, msgstr):
                errors.append('msgid and msgstr are identical for msgid "%s"' % msgid)
                has_error = True
            
            if has_error:
                continue

            extra_fields, missing_fields = GetExtraOrMissingFields(msgid, msgstr)
            if extra_fields:
                errors.append('msgstr has fields that are not in msgid "%s": %s' % (msgid, extra_fields))
            if missing_fields:
                warnings.append('msgstr does not have some fields in msgid "%s": %s' % (msgid, missing_fields))

    return errors, warnings
        


if __name__ == '__main__':
    locale_code = sys.argv[1]
    errors, warnings = Validate(locale_code)
    print('%d errors, %d warnings' % (len(errors), len(warnings)))
    print('errors:', errors)