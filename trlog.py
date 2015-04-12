#! /usr/bin/env python
import os, sys
import collections
import re
import datetime
import codecs

sys.path.insert(0, os.getcwd())
import trconf

Trans = collections.namedtuple('Trans', ('date', 'info', 'amount', 'line'))
rxdate = re.compile(trconf.rxpatterns['date'])
rxinfo = re.compile(trconf.rxpatterns['info'])
rxamount = re.compile(trconf.rxpatterns['amount'])

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

def parse(txt, skiprows):
    """txt has the lines of transaction."""

    lines = []
    for line in txt.splitlines()[skiprows:]:

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

def decodefile(f):
    """Try to find out the proper encoding (by reading the whole file)
    and return it as a string"""

    u = txt = open(f).read()

    try:
        u = unicode(txt, 'utf-8')
        print 'utf-8'
        return u
    except UnicodeDecodeError:
        pass
    try:
        u = unicode(txt, 'latin-1')
        print 'latin-1'
        return u
    except UnicodeDecodeError:
        pass

    return u

def main():
    # try things
    f = sys.argv[-1]
    print sys.argv[0]

    transes = parse(decodefile(f), 1)

    with EncodedOut('utf-8'):
        for trans in transes:
            print trans.line
            print '\t', trans.date
            print '\t', trans.info
            print '\t', trans.amount

if __name__ == '__main__':
    main()

