"""
Searching ms word documents for matches with the docx format is tricky
from outside word. The reason for this is that the file is some sort of
compressed zip thing. Before grepping it one has to unzip it. The
unzipped files are of XML type. The line numbers in those make no sense
in relation to the outline as perceived by viewing the document in the
graphical application.

This tool then would display what is matched, but not attempt to give
any information on line numbers or context.

It will provide some meta data on the number of occurences of respective
matching substring.
"""
import re
import zipfile
from collections import namedtuple

Submatch = namedtuple('Submatch', ('str', 'cnt'))

def grep(f, pat):
    """Return a list with strings matching pat in f.

    f is a file opened for reading."""

    rx = re.compile(pat)
    res = rx.findall(f.read())

    # for ln in f.readlines():
    #     m = rx.search(ln)
    #     if m:
    #         res.append(ln[m.start(): m.end()])

    return res

def scanzip(zipdoc, pat):
    """Scan through the files in zipdoc for pat. Return the results as a
    list of Submatches.

    The zipdoc is probably not opened for reading."""

    
