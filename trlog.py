#! /usr/bin/env python
import os, sys
import collections
import re
import datetime
import codecs
import argparse
import glob
import operator
import itertools

sys.path.insert(0, os.getcwd())
try:
    import trconf
    fn = os.path.basename(trconf.__file__)
    if not fn in os.listdir(os.getcwd()):
        sys.exit('E: No trconf.py file in current directory')
    rxdate = re.compile(trconf.rxpatterns['date'])
    rxinfo = re.compile(trconf.rxpatterns['info'])
    rxamount = re.compile(trconf.rxpatterns['amount'])
except ImportError:
    pass

Trans = collections.namedtuple('Trans', ('date', 'info', 'amount', 'line'))

class FileExtError(Exception):
    """Raise if a file with extension not listed in transconf is
    given"""
    pass

class EncodedOut:
    def __init__(self, enc):
        self.enc = enc
        self.stdout = sys.stdout
    def __enter__(self):
        if sys.stdout.encoding is None:
            w = codecs.getwriter(self.enc)
            sys.stdout = w(sys.stdout)
    def __exit__(self, exc_ty, exc_val, tb):
        sys.stdout = self.stdout

def parse(fo, skiprows):
    """fo the fileobject via codecs.open.."""

    lines = []
    for line in fo.readlines()[skiprows:]:

        line = line.strip()
        if not line:
            continue

        date = None
        res = rxdate.findall(line)
        if len(res) == 1:
            date = res[0]
        elif len(res) > 1:
            date = trconf.dateselect(res, line)
        try:
            date = datetime.date(*[int(n) for n in date.split('-')])
        except:
            date = None

        info = None
        res = rxinfo.findall(line)
        if len(res) == 1:
            info = res[0]
        elif len(res) > 1:
            info = trconf.infoselect(res, line)

        amount = None
        res = rxamount.findall(line)
        if len(res) == 1:
            amount = res[0]
        elif len(res) > 1:
            amount = trconf.amountselect(res, line)
        try:
            amount = trconf.crazyfloat(amount)
        except:
            amount = None

        lines.append(Trans(date, info, amount, line))

    return lines


def decodeparse(f, skiprows, encodings):
    """Open the file via codecs.open and parse for each given encoding
    in turn. Return the parsed list of Transes or fail with error"""

    for enc in encodings:
        try:
            return parse(codecs.open(f, encoding=enc), skiprows)
        except UnicodeDecodeError:
            pass
    raise

def decoderegex(rx, encoding):
    """Return a unicode of the regex (from args)"""
    return unicode(rx, encoding)

def init(fn, content):
    """Write the confile"""
    if fn in os.listdir('.') and not args.Init:
        print 'E:', fn, 'exist, ues -I to over-write.'
        sys.exit(1)
    try:
        os.remove(fn.replace('.py', '.pyc'))
    except OSError:
        pass
    with open(fn, 'w') as fo:
        fo.write(content)

def rxreduced(transes, regexes=None, ignorecase=False):
    """Reduce the transes. No reduction is done if regexes
    is None."""

    if regexes is None:
        return transes
    def qualify(trans):
        for rx in regexes:
            if not ignorecase:
                if re.search(rx, trans.line, re.U):
                    return True
            else:
                if re.search(rx, trans.line, re.U | re.I):
                    return True
        return False

    return [trans for trans in itertools.ifilter(qualify, transes)]

def main():

    if args.Init or args.init:
        init('trconf.py', conftxt)
        sys.exit(0)
    elif not 'trconf.py' in os.listdir(os.getcwd()):
        sys.exit('E: No trconf.py file in current directory')

    if len(args.filenames) == 0:
        for ext in trconf.exts:
            args.filenames += glob.glob('*' + ext)
    transes = []
    for filename in args.filenames:
        if not any(filename.endswith(ext) for ext in trconf.exts):
            sys.exit('E: extension not in trconf: ' + filename)
            # raise FileExtError('extension not in trconf: ' + filename)
        transes += decodeparse(filename, trconf.skiprows, trconf.encodings)

    transes.sort(key=operator.attrgetter('date'))

    with EncodedOut('utf-8'):
        if args.regexes is not None:
            regexes = [decoderegex(rx, sys.stdout.encoding or 'utf-8') for
                       rx in args.regexes] # should be stdin?
            for trans in rxreduced(transes, regexes, args.ignorecase):
                print trans.line
        else:
            for trans in transes:
                print trans.line

parser = argparse.ArgumentParser(description='Query bank transactions in'
                                 ' a local database')
parser.add_argument(dest='filenames', metavar='filename', nargs='*')

parser.add_argument('-E', '--regex', metavar='regex', dest='regexes',
                    action='append', help='regular expression python style, '
                    'the option with expression can be repeated')

parser.add_argument('-i', '--ignore-case', dest='ignorecase',
                    action='store_true', help='ignore case in the expression')

parser.add_argument('-s', '--summary', dest='summary', action='store_true',
                    help='output the summary only')

group = parser.add_mutually_exclusive_group()
group.add_argument('--init', dest='init', action='store_true',
                   help='Initialize the the directory, '
                    '(output a trconf.py file)')
group.add_argument('--Init', dest='Init', action='store_true',
                    help='Initialize the the directory, '
                    '(output a trconf.py file)'' overwrite existing file')


conftxt = '''
# A configuration file for the translog program or if it is cashlog. Even
# if not trivial, it shall be possible to build a regex for extracting
# data from any kind of log format. The default will be a format familiar
# to the developer.

# The rxpatterns are searched for with re.findall. If results are multiple,
# functions are provided here to select one of them from the list.

rxpatterns = {
# must have patterns 'date', 'info', 'amount'
# make each pattern a group
'date': r'(\d{4}-\d{2}-\d{2})',
'info': r'two'\
        r'three',
'amount': (r'"?([+-]?(?:\d+[,.])+\d{1,2})"?'),
}

# The left-to-right order in which the patterns occur
rxorder = ['date', 'info', 'amount']

# The rxpatterns are searched for with re.findall. If results are multiple,
# functions are provided here to select one of them from the list. Below
# functions are called only if the resulting list length exceeds one.
def dateselect(res, line):
    # Return the result from the list res (origin from line) that is to
    # be used as date
    return res[-1]

def infoselect(res, line):
    # Return the result from the list res (origin from line) that is to
    # be used as info.
    return res[-1]

def amountselect(res, line):
    # Return the result from the list res (origin from line) that is to
    # be used as amount.
    if len(res) == 2:
        return res[0]
    elif len(res) == 3:
        return res[1]

# The extension(s) of the files to read.
exts = ['.csv']

# The file encodings to try, in order.
encodings = ['utf-8', 'latin-1']

# Number of rows to skip (header)
skiprows = 1

# Use this to convert the amount string to a float.
def crazyfloat(s):
    # Convert the string s to a float
    s = s.replace(',', '.')
    n = s.count('.')
    if n > 1:
        s = s.replace('.', '', n - 1)
    return float(s)

# Use this to convert the date string to a datetime.date object.
def transdate(dstr):
    # Return a datetime.date object on the dstr. YYYY-MM-DD

    return datetime.date(*[int(n) for n in dstr.split('-')])'''

if __name__ == '__main__':
    args = parser.parse_args()
    main()

