#!/usr/bin/env python

"""
Count lines of code excludig blanks and comments and give a hint on how
much of the code is docstrings.

Usage: sloc <file>.py

Given that this file runs on the command sloc.

"""

import re
import sys
import os

RX_docstr1 = r'"""(?:.|\n)*?"""'
RX_docstr2 = r"'''(?:.|\n)*?'''"
RX_blanks = r'[\t ]*\B'

if __name__ == '__main__':
    
    fn = sys.argv[-1]

    if fn == '--help' or fn == __file__:
        print __doc__
        exit()

    with open(os.path.abspath(fn)) as fo:
        S = fo.read()

    lines = S.splitlines()      # keepends=False
    tot = len(lines)
    docstr = max(len(re.findall(RX_docstr1, S)), len(re.findall(RX_docstr2, S)))

    statmess = '{}\nTOT: {}, DOCSTRING BLOBS: {}'
    print statmess.format(fn, tot, docstr)
