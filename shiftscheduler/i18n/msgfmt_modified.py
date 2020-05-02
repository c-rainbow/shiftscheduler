#! /usr/bin/env python3
# Written by Martin v. Löwis <loewis@informatik.hu-berlin.de>

"""Generate binary message catalog from textual translation description.

This program converts a textual Uniforum-style message catalog (.po file) into
a binary GNU catalog (.mo file).  This is essentially the same function as the
GNU msgfmt program, however, it is a simpler implementation.  Currently it
does not handle plural forms but it does handle message contexts.

Usage: msgfmt.py [OPTIONS] filename.po

Options:
    -o file
    --output-file=file
        Specify the output file to write to.  If omitted, output will go to a
        file named filename.mo (based off the input file name).

    -h
    --help
        Print this message and exit.

    -V
    --version
        Display version information and exit.
"""

import os
import sys
import ast
import getopt
import struct
import array
from email.parser import HeaderParser

__version__ = "1.2"



class PoFileParser():
    def __init__(self, filepath):
        self.messages = {}
        self.ids = []
        self.filepath = filepath  # Must be string


    def add(self, ctxt, id, str, fuzzy):
        "Add a non-fuzzy translation to the dictionary."
        self.ids.append(id)
        if not fuzzy and str:
            if ctxt is None:
                self.messages[id] = str
            else:
                self.messages[b"%b\x04%b" % (ctxt, id)] = str


    def make(self):

        filename = self.filepath

        ID = 1
        STR = 2
        CTXT = 3

        # Compute .mo name from .po name and arguments
        infile = filename

        try:
            with open(infile, 'rb') as f:
                lines = f.readlines()
        except IOError as msg:
            print(msg, file=sys.stderr)
            sys.exit(1)

        section = msgctxt = msgid = msgstr = None
        fuzzy = 0

        # Start off assuming Latin-1, so everything decodes without failure,
        # until we know the exact encoding
        encoding = 'latin-1'

        # Parse the catalog
        lno = 0
        for l in lines:
            l = l.decode(encoding)
            lno += 1
            # If we get a comment line after a msgstr, this is a new entry
            if l[0] == '#' and section == STR:
                self.add(msgctxt, msgid, msgstr, fuzzy)
                section = msgctxt = None
                fuzzy = 0
            # Record a fuzzy mark
            if l[:2] == '#,' and 'fuzzy' in l:
                fuzzy = 1
            # Skip comments
            if l[0] == '#':
                continue
            # Now we are in a msgid or msgctxt section, output previous section
            if l.startswith('msgctxt'):
                if section == STR:
                    self.add(msgctxt, msgid, msgstr, fuzzy)
                section = CTXT
                l = l[7:]
                msgctxt = b''
            elif l.startswith('msgid') and not l.startswith('msgid_plural'):
                if section == ID:
                    # msgid after msgid. Error.
                    self.add(msgctxt, msgid, None, fuzzy)
                elif section == STR:
                    self.add(msgctxt, msgid, msgstr, fuzzy)
                    if not msgid:
                        # See whether there is an encoding declaration
                        p = HeaderParser()
                        charset = p.parsestr(msgstr.decode(encoding)).get_content_charset()
                        if charset:
                            encoding = charset
                section = ID
                l = l[5:]
                msgid = msgstr = b''
                is_plural = False
            # This is a message with plural forms
            elif l.startswith('msgid_plural'):
                if section != ID:
                    print('msgid_plural not preceded by msgid on %s:%d' % (infile, lno),
                        file=sys.stderr)
                    sys.exit(1)
                l = l[12:]
                msgid += b'\0' # separator of singular and plural
                is_plural = True
            # Now we are in a msgstr section
            elif l.startswith('msgstr'):
                section = STR
                if l.startswith('msgstr['):
                    if not is_plural:
                        print('plural without msgid_plural on %s:%d' % (infile, lno),
                            file=sys.stderr)
                        sys.exit(1)
                    l = l.split(']', 1)[1]
                    if msgstr:
                        msgstr += b'\0' # Separator of the various plural forms
                else:
                    if is_plural:
                        print('indexed msgstr required for plural on  %s:%d' % (infile, lno),
                            file=sys.stderr)
                        sys.exit(1)
                    l = l[6:]
            # Skip empty lines
            l = l.strip()
            if not l:
                continue
            l = ast.literal_eval(l)
            if section == CTXT:
                msgctxt += l.encode(encoding)
            elif section == ID:
                msgid += l.encode(encoding)
            elif section == STR:
                msgstr += l.encode(encoding)
            else:
                print('Syntax error on %s:%d' % (infile, lno), \
                    'before:', file=sys.stderr)
                print(l, file=sys.stderr)
                sys.exit(1)
        # Add last entry
        if section == STR:
            self.add(msgctxt, msgid, msgstr, fuzzy)

