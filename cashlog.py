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
import glob
import collections
import os
import pickle

rx_date = r'\s*"?(\d{4}-\d{2}-\d{2})"?,'
rx_info = r'(.+?)'
rx_amounts = (r'"?([+-]?(?:\d+[,.])+\d{1,2})"?,?' + # amount
               r'(?:,"?([+-]?(?:\d+[,.])+\d{1,2})"?)?')  # balance

rx_word = r'\b\w{2,}\b'

YEAR_DAYS = 365.
MONTH_DAYS = 30.
WEEK_DAYS = 7.

def debugprint(res, numaccept):
    """res a list of matches. Print something informative on each
    match. numaccept is a sequence of acceptable len's of the match's
    groups tuple."""

    for i, m in enumerate(res):
        if not m:
            print i, 'was not a match'
            continue
        try:
            print m.groups(), len(m.groups()) in numaccept
        except AttributeError:
            print m

def wordcount(res):
    """Collect words from the info part. Return a counter of the
    words."""

    words = []
    for m in res:
        words += re.findall(rx_word, m.group(2), re.U)
    return collections.Counter(words)

def grep(expression, res, flags=0, group=2, wprint=False):
    """Return matches in res where a re.search return a match in the
    group group run on expression. The tuples are returned in a list.
    """

    lns = []
    for m in res:
        if re.search(expression, m.group(group), flags=flags):
            lns.append(m)
            if wprint:
                print m.groups()
    return lns

def matches(fo):
    """Return all the matches in a list, including matches that are
    None. fo a file opened for reading.

    Ignore first line if it's first non-white character is not a
    number. Ignore lines that are empty after a strip."""

    rx_numstart = r'\s*"?\d+'

    # rx = rx_date + rx_trans
    rx = rx_date + rx_info + rx_amounts
    lns = fo.read()
    lns = lns.splitlines()
    lns = [ln for ln in lns if ln.strip()]
    if not re.match(rx_numstart, lns[0]):
        lns.pop(0)
    res = [re.match(rx, ln) for ln in lns]
    return res

def scan(pat):
    """Return a list with matches on all files found with pat. pat is a
    glob pattern."""

    files = glob.glob(pat)
    res = []
    for f in files:
        with open(f) as fo:
            res += matches(fo)
            # res += [fo.name]

    return res

def crazyfloat(m, group=3):
    """Convert the group's string to a float. Only the last ',' or '.'
    are kept and replaced with a '.' before floating. The prior ones are
    removed."""

    s = m.group(group)
    s = s.replace(',', '.')
    n = s.count('.')
    if n > 1:
        s = s.replace('.', '', n - 1)
    return float(s)

def date(m):
    """Return a datetime.date object on the match object m. Date is in
    group 1 in m."""

    d = m.group(1)
    return datetime.date(*[int(n) for n in d.split('-')])

def stat(res):
    """Print NEG, POS, SUM, PERIOD for the matches in res."""

    dates = [date(m) for m in res]
    period = (min(dates), max(dates))
    tot = [crazyfloat(m) for m in res]
    negs = [n for n in tot if n < 0]
    poss = [n for n in tot if n > 0]

    print 'Stat for period:', period
    print 'Sum for period:', sum(tot)
    print 'Positive <--> negative:', sum(poss), '<-->', sum(negs)
    print 50 * '-'
    delta = period[1] - period[0]
    days = delta.days
    y, m, w = YEAR_DAYS / days, MONTH_DAYS / days, WEEK_DAYS / days
    print 'Yearly:', y * sum(poss), '<-->', y * sum(negs)
    print 'Monthly:', m * sum(poss), '<-->', m * sum(negs)
    print 'Weekly:', w * sum(poss), '<-->', w * sum(negs)

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
        return max([date(m) for m in res])

    fileresults.sort(key=sortkey)
    for res in fileresults:
        yield stat(res)
    
