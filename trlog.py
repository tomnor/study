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

Trans = collections.namedtuple('Trans', ('date', 'amount', 'line'))

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
    """fo the fileobject via codecs.open. Return a list of transes and a
    list of error transes --> (transes, etranses)"""

    transes, etranses = [], []
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
        except (TypeError, AttributeError):
            date = None

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

        if None in (date, amount, line):
            etranses.append(Trans(date, amount, line))
        else:
            transes.append(Trans(date, amount, line))

    return transes, etranses


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
        print 'E:', fn, 'exist, ues --Init to over-write.'
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

    re_flags = ignorecase and (re.U | re.I) or re.U

    def qualify(trans):
        for rx in regexes:
            match = re.search(rx, trans.line, re_flags)
            if match and not (args.positive or args.negative):
                return True
            elif match and args.positive:
                return trans.amount >= 0
            elif match:         # args.negative is True
                return trans.amount < 0
        return False

    return [trans for trans in itertools.ifilter(qualify, transes)]

def summary(redtranses, transes, etranses):
    """Output a summary of the transes. redtranses is the transes to
    compute on, transes are all transes parsed, etranses are the transes
    with parsing errors."""

    res, tot, e = len(redtranses), len(transes) + len(etranses), len(etranses)
    print 50 * '-'

    fmt = 'Total parsed records: {}, parse-errors: {}, matching: {}'
    print fmt.format(tot, e, res)
    if e:
        print 'W: matching excludes parse-error records'

    if not len(redtranses):
        return

    d1, d2  = redtranses[0].date, redtranses[-1].date,
    print 'Period: ', d1, '-', d2, 'spanning', (d2 - d1).days + 1, 'days'
    fmt = 'distinct: {} years, {} months, {} days'
    dd = set(trans.date for trans in redtranses)
    dm = set((date.year, date.month) for date in dd)
    dy = set(tup[0] for tup in dm)
    print fmt.format(len(dy), len(dm), len(dd))

    fmt = 'sum: {:.2f} average: {:.2f}'
    summ =  sum(t.amount for t in redtranses)
    print fmt.format(summ, summ / len(redtranses))
    print 'percentiles:'
    asort = sorted(redtranses, key=operator.attrgetter('amount'),
                   reverse=trconf.reversedpercentiles)
    fmt = '{:3d} {:.2f}'
    for perc in (0.0, 0.25, 0.50, 0.75, 1.0):
        i = int(round(perc * (len(asort) - 1)))
        print fmt.format(int(perc * 100), asort[i].amount)

def main():

    if args.Init or args.init:
        init('trconf.py', conftxt)
        sys.exit(0)

    if len(args.filenames) == 0:
        for ext in trconf.exts:
            args.filenames += glob.glob('*' + ext)

    transes, etranses = [], []
    for filename in args.filenames:
        if not any(filename.endswith(ext) for ext in trconf.exts):
            sys.exit('E: extension not in trconf: ' + filename)
        res = decodeparse(filename, trconf.skiprows, trconf.encodings)
        transes += res[0]
        etranses += res[1]

    transes.sort(key=operator.attrgetter('date'))

    with EncodedOut('utf-8'):
        if args.regexes is not None and not args.debug:
            regexes = [decoderegex(rx, sys.stdout.encoding or 'utf-8') for
                       rx in args.regexes] # should be stdin?
            rxtranses = rxreduced(transes, regexes, args.ignorecase)
            if not args.summary:
                for trans in rxtranses:
                    print trans.line
            if not args.nosummary:
                summary(rxtranses, transes, etranses)
        elif args.debug:
            for trans in etranses:
                print trans.line
                print '    date:', trans.date, 'amount:', trans.amount
        else:
            if not args.summary:
                for trans in transes:
                    print trans.line
            if not args.nosummary:
                summary(transes, transes, etranses)

parser = argparse.ArgumentParser(description='Query bank transactions in'
                                 ' a local database')
parser.add_argument(dest='filenames', metavar='filename', nargs='*')

parser.add_argument('-E', '--regex', metavar='regex', dest='regexes',
                    action='append', help='regular expression python style, '
                    'the option with expression can be repeated')

parser.add_argument('-i', '--ignore-case', dest='ignorecase',
                    action='store_true', help='ignore case in the expression')

group = parser.add_mutually_exclusive_group()
group.add_argument('-s', '--summary', dest='summary', action='store_true',
                    help='output the summary only')

group.add_argument('-S', '--no-summary', dest='nosummary',
                    action='store_true', help='supress the summary')

group = parser.add_mutually_exclusive_group()
group.add_argument('-p', '--positive', dest='positive', action='store_true',
                   help='Match positive transactions only.')

group.add_argument('-n', '--negative', dest='negative', action='store_true',
                    help='Match negative transactions only.')

parser.add_argument('-d', '--debug', dest='debug', action='store_true',
                    help='print only the lines that failed parsing with '
                    'informative data added')

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
import re                       # should you need it
rxpatterns = {
# must have patterns 'date', 'amount'
# make each pattern a group
'date': r'(\d{4}-\d{2}-\d{2})',
'amount': (r'"?([+-]?(?:\d+[,.])+\d{1,2})"?'),
}

# The left-to-right order in which the patterns occur
rxorder = ['date', 'amount']

# The rxpatterns are searched for with re.findall. If results are
# multiple, functions are provided here to select one of them from the
# list. Below functions are called only if the resulting list length
# exceeds one.
def dateselect(res, line):
    # Return the result from the list res (origin from line) that is to
    # be used as date
    return res[0]

def amountselect(res, line):
    # Return the result from the list res (origin from line) that is to
    # be used as amount.
    if len(res) == 2:
        return res[0]
    elif len(res) >= 3:
        return res[-2]

##Here is a version of amountselect that deals with a timestamp
##interpreted as amount:
# rxclock = re.compile(r'[0-2][0-9]\.[0-5][0-9]')
# def amountselect(res, line):
#     # Return the result from the list res (origin from line) that is to
#     # be used as amount.

#     m = rxclock.search(line)

#     try:
#         res.remove(m.group())
#         if len(res) == 1:
#             return res[0]
#     except (AttributeError, ValueError):
#         pass

#     if len(res) == 2:
#         return res[0]
#     elif len(res) >= 3:
#         return res[-2]

# The extension(s) of the files to read.
exts = ['.csv']

# The file encodings to try, in order.
encodings = ['utf-8', 'latin-1']

# Number of rows to skip (header)
skiprows = 1

# Reverse the sorting for percentiles
reversedpercentiles = True

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

    sys.path.insert(0, os.getcwd())
    try:
        import trconf
        fn = os.path.basename(trconf.__file__)
        if not fn in os.listdir(os.getcwd()):
            raise ImportError
        rxdate = re.compile(trconf.rxpatterns['date'])
        rxamount = re.compile(trconf.rxpatterns['amount'])
    except ImportError:
        if not args.init and not args.Init:
            sys.exit('E: No trconf.py file in current directory')

    main()
