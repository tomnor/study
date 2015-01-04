#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The idea here is to make a tool to read transaction logs and help with
sorting and finding out where all money goes.

Reconsider. Regex the date in the beginning, the amounts in the end, and
then extract what is left in between. In the end there can be two
amounts, belopp and saldo, where saldo might or might not be present. It
is present if the user was not logged into the bank in "simplified"
mode.

This idea because the transaction information is very wild. It can look
however the one writing the message decides it should look.

Next thought will probably be to make a some strict interface for the
tuple holding the groups. Maybe the date, info and amount will be the
mandatory fields, and then the tool can be extended.
"""
import re
import datetime
import calendar
import glob
import collections
from operator import attrgetter

rx_date = r'\s*"?(\d{4}-\d{2}-\d{2})"?,'
rx_info = r'(.+?)'
rx_amounts = (r'"?([+-]?(?:\d+[,.])+\d{1,2})"?,?' + # amount
               r'(?:,"?([+-]?(?:\d+[,.])+\d{1,2})"?)?')  # balance

rx_date = r'\s*"?(?P<date>\d{4}-\d{2}-\d{2})"?,'
rx_info = r'(?P<info>.+?)'
rx_amounts = (r'"?(?P<amount>[+-]?(?:\d+[,.])+\d{1,2})"?,?' + # amount
               r'(?:,"?([+-]?(?:\d+[,.])+\d{1,2})"?)?')  # balance

rx_word = r'\b\w{2,}\b'

YEAR_DAYS = 365.
MONTH_DAYS = 30.
WEEK_DAYS = 7.

# Consider having a field 'raw' keeping the original line.
Trans = collections.namedtuple('Trans', ('date', 'info', 'amount'))

def wordcount(res):
    """Collect words from the info part. Return a counter of the
    words."""

    words = []
    for trans in res:
        words += re.findall(rx_word, trans.info, re.U)
    return collections.Counter(words)

def grep(res, *expressions, **kw):
    """Return matches in res where a re.search return a match in the
    attribute info, run on expressions. Each expression in expressions
    must have a match in the transaction.
    
    kw can hold flags and wprint and invert. invert is a sequence with 0:s and
    1:s with the same number of elements as the number of expressions. Or None
    (default). 
    """
    off = set(kw) - set(['flags', 'wprint', 'invert'])
    if off:
        raise KeyError(off.pop())

    flags = kw.get('flags', 0)
    wprint = kw.get('wprint', False)
    invert = kw.get('invert', [0 for ex in expressions])

    lns = []
    for trans in res:
        hits = []
        for expression, inv in zip(expressions, invert):
            if inv:
                hits.append(not re.search(expression, trans.info, flags=flags))
            else:
                hits.append(re.search(expression, trans.info, flags=flags))                
        if hits and all(hits):
            lns.append(trans)
            if wprint:
                print trans.date, trans.info, trans.amount
    return lns

def sanetrans(fo):
    """Return the transactions in a list as Trans tuples. If the match
    failed, Trans.info will hold the entire line and the
    attributes date and amount will be None.

    """
    
    rx_numstart = r'\s*"?\d+'
    
    rx = rx_date + rx_info + rx_amounts
    lns = fo.read()
    lns = lns.splitlines()
    
    # cleanups:
    lns = [ln for ln in lns if ln.strip()]
    lns = [ln for ln in lns if re.match(rx_numstart, ln)]

    res = []
    for ln in lns:
        m = re.match(rx, ln)
        if m:
            date = transdate(m.group('date'))
            amount = crazyfloat(m.group('amount'))
            res += [Trans(date, m.group('info'), amount)]
        else:
            res += [Trans(date=None, info=ln, amount=None)]

    return res

def scan(pat):
    """Return a list with Trans tuples on all files found with pat. pat
    is a glob pattern."""

    files = glob.glob(pat)
    res = []
    for f in files:
        with open(f) as fo:
            res += sanetrans(fo)

    return res

def crazyfloat(floatstr):
    """Convert the string to a float. Only the last ',' or '.' are kept
    and replaced with a '.' before floating. The prior ones are removed."""

    s = floatstr.replace(',', '.')
    n = s.count('.')
    if n > 1:
        s = s.replace('.', '', n - 1)
    return float(s)

def transdate(dstr):
    """Return a datetime.date object on the dstr. YYYY-MM-DD"""

    return datetime.date(*[int(n) for n in dstr.split('-')])

def stat(res):
    """Print useful information on the transactions in res, a list of
    Trans tuples."""

    res = sorted(res, key=attrgetter('date'))
    amounts = [t.amount for t in res]
    print 'Period:', res[0].date, res[-1].date
    print 'Number of transactions:', len(res)
    pos, neg = (sum([a for a in amounts if a > 0]), 
                sum([a for a in amounts if a < 0]))
    print 'sum:', pos + neg
    print 'pos:', pos
    print 'neg:', neg

def statdat(res):
    """Produce a dict with key figures on the result list res. Failing
    lines are not part of the calculations. See item 'failcnt'."""

    d = dict()
    res = [trans for trans in res if trans.date] # Succes
    fail = [trans.info for trans in res if not trans.date]
    res.sort(key=attrgetter('date'))
    d['sum'] = sum(trans.amount for trans in res)
    d['neg'] = sum(trans.amount for trans in res if trans.amount < 0)
    d['pos'] = sum(trans.amount for trans in res if trans.amount > 0)
    d['transcnt'] = len(res)
    d['failcnt'] = len(fail)
    d['startdate'] = (res or None) and res[0].date # None if res is empty
    d['enddate'] = (res or None) and res[-1].date
    diff = d['enddate'] - d['startdate']
    d['days'] = diff.days
    return d

def daterange(res, start, stop):
    """Return a subset of res that falls within the date range start
    stop inclusive. start stop are datetime.date objects."""

    sub = []
    for trans in res:
        if trans.date >= start and trans.date <= stop:
            sub.append(trans)
    return sub

def calenderfmt(res):
    """Produce a string that serves as a calender informing on number of
    transactions for the years in res. calenderdict function is used."""
    
    calstr = ''
    fmtstr = '{:<4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}{:>4}'
    calstr += fmtstr.format(*calendar.month_abbr) + '\n'
    caldict = calenderdict(res)
    for year in sorted(caldict):
        calstr += fmtstr.format(year, *caldict[year]) + '\n'
    
    return calstr.strip()       # last newline off

def calenderdict(res):
    """Produce a dict that serves as a calender informing on number of
    transactions for the years spanning in res."""

    s, e = min(t.date.year for t in res), max(t.date.year for t in res)
    years = range(s, e + 1)
    cal = {}
    for year in years:
        months = range(1, 13)
        for month in months:
            start = datetime.date(year, month, 1)
            stop = datetime.date(year, month, calendar.monthrange(year, month)[1])
            sub = daterange(res, start, stop)
            months[month - 1] = len(sub)
        cal[year] = months
    return cal

def statgen(pat):
    """Return a generator for each file found by pat. On each iteration,
    a stat print is done.

    .. Note: This is probably for debug only."""

    files = glob.glob(pat)
    fileresults = []
    for f in files:
        with open(f) as fo:
            fileresults.append(matches(fo))

    def sortkey(res):
        return max([transdate(m) for m in res])

    fileresults.sort(key=sortkey)
    for res in fileresults:
        yield stat(res)
    
