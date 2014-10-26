#!/usr/bin/env python

"""
Count lines of code. The file(s) are assumed to have a structure that can be
expressed like this:

lines = code-lines + comment-lines + white-lines

Shebangs evaluate to comment.

# Unfortunatly those two lines will evaluate to comments. Can somebody
# fix that nicely? Those two lines are part of this docstring.

Docstrings in python are also code. This utility gives a suggestion of
how many of the total lines are docstrings.

line stat for <filename>
============================================
TOT: <N>
CODE: <N>
COMMENT: <N>
WHITE: <N>
CODE RATE: <N> %

DOCSTRING BLOBS: <N> DOCSTRING LINES: <N>
---------------------------------------------

The docstring lines are part of the total lines, not only part of code.

Usage: sloc "<pat>"

Given that this file runs on the command sloc. Replace pat with a file
name path pattern. The quotes might be required to protect your pattern
from being expanded by the shell.

Or maybe:
python sloc.py "<pat>"
"""

import re
import sys
import os
import glob

RX_docstr1 = r'"""(?:.|\n)*?"""'
RX_docstr2 = r"'''(?:.|\n)*?'''"
RX_blanks = r'\s*$'
RX_nocode = r'^\s*#+.*'
RX_usage = r'Usage:(?:.|\n)+'

def printstat(fn):

    with open(os.path.abspath(fn)) as fo:
        S = fo.read()

    lines = S.splitlines()      # keepends=False
    docs = max(re.findall(RX_docstr1, S), re.findall(RX_docstr2, S), key=len)

    statfmt = ('line stat for ' + os.path.basename(fn) + '\n' + (45 * '=') + '\n'
               'TOT: {}\n'
               'CODE: {}\n'
               'COMMENT: {}\n'
               'WHITE: {}\n'
               'CODE RATE: {:.1f} %\n\n'
               'DOCSTRING BLOBS: {} DOCSTRING LINES: {}\n' + 45 * '-')

    tot = len(lines)
    white = sum([1 if re.match(RX_blanks, ln) else 0 for ln in lines])
    comment = sum([1 if re.match(RX_nocode, ln) else 0 for ln in lines])
    code = tot - comment - white
    rate = float(code) / tot * 100
    docblobs = len(docs)
    doclines = sum([len(doc.splitlines()) for doc in docs])

    print statfmt.format(tot, code, comment, white, rate, docblobs, doclines)

if __name__ == '__main__':

    pat = sys.argv[-1]

    if pat == '--help' or pat == '-h' or pat == __file__:
        print re.search(RX_usage, __doc__).group(0)
        exit()

    run = False
    for fn in glob.glob(pat):
        printstat(fn)
        run = True
    
    if not run:
        print 'Input error:', pat
        print re.search(RX_usage, __doc__).group(0)
