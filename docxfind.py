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
import argparse

Submatch = namedtuple('Submatch', ('str', 'cnt', 'fn'))
opening = r'(?:<w:t>'
closing = r'</w:t>)'

reflags = re.UNICODE

def grep(f, pat):
    """Return a list with strings matching pat in f.

    f is a file opened for reading."""

    rx = re.compile(pat, flags=reflags)
    res = rx.findall(f.read())

    return res

def scanzip(zipdoc, pat, wrap=False):
    """Scan through the files in zipdoc for pat. Return the results as a
    list of Submatches.

    The zipdoc is probably not opened for reading."""

    # z = zipfile.ZipFile(zipdoc)
    with zipfile.ZipFile(zipdoc) as z:
        resd = dict()
        for info in z.infolist():
            if not wrap:
                resd[info.filename] = grep(z.open(info), pat)
            else:
                resd[info.filename] = grep(z.open(info), opening + pat + closing)

    poppers = [k for k in resd if not resd[k]]
    [resd.pop(k) for k in poppers]

    retres = []
    for k in resd:
        uniqs = set(resd[k])
        retres += [Submatch(s, resd[k].count(s), k) for s in uniqs]
    # retres = [

    return resd, retres

parser = argparse.ArgumentParser(description=('Match some words in a ms word '
                                              'document of the docx format'))

mess = """Try to limit the matches to the document substance by wrapping the
pattern inside some tag pattern.
"""
parser.add_argument('-w', '--wrap', action='store_true', dest='wrap', 
                    help=mess)

args = parser.parse_args()

print 'value of wrap:', args.wrap