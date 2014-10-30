#!/usr/bin/env python
"""
An interactive trick.

A session of play, the letter on my mind was 'T'::

    tomas@RV515:~/pyfiles/study$ python trick.py
    Think of a letter and remember it, then press enter
    ['M', 'A', 'N', 'R', 'L', 'P', 'B', 'F', 'D', 'H', 'E', 'C', 'G', 'O', 'Q',
    'U', 'T', 'I', 'K', 'J', 'S']
    --> 
    1 ['M', 'R', 'B', 'H', 'G', 'U', 'K']
    2 ['A', 'L', 'F', 'E', 'O', 'T', 'J']
    3 ['N', 'P', 'D', 'C', 'Q', 'I', 'S']
    What row, 1, 2 or 3?
    --> 2
    1 ['M', 'H', 'K', 'F', 'T', 'P', 'Q']
    2 ['R', 'G', 'A', 'E', 'J', 'D', 'I']
    3 ['B', 'U', 'L', 'O', 'N', 'C', 'S']
    What row, 1, 2 or 3?
    --> 1
    1 ['R', 'E', 'I', 'K', 'P', 'U', 'N']
    2 ['G', 'J', 'M', 'F', 'Q', 'L', 'C']
    3 ['A', 'D', 'H', 'T', 'B', 'O', 'S']
    What row, 1, 2 or 3?
    --> 3
    >>>>>>>>>>>>>>>>>>>>>>>>>>>>>> T <<<<<<<<<<<<<<<<<<<<<<<<<<<<<<

"""
from collections import namedtuple
import random

Row = namedtuple('Row', ('c1', 'c2', 'c3'))

def rowsfromvals(vals):
    return [Row(*vals[i:i+3]) for i in range(0, 21, 3)]

def valsfromrows(rows, keycol):
    """keycol is the column with the selected val, 0, 1 or 2."""
    order = [0, 1, 2]
    random.shuffle(order)
    order.remove(keycol)
    order.insert(1, keycol)
    L = []
    for c in order:
        L += [row[c] for row in rows]
    return L

def play():
    vals = [chr(o) for o in range(65, 65 + 21)]
    random.shuffle(vals)
    print 'Think of a letter and remember it, then press enter'
    print vals
    raw_input('--> ')

    for i in range(3):
        rows = rowsfromvals(vals)
        print 1, [r.c1 for r in rows]
        print 2, [r.c2 for r in rows]
        print 3, [r.c3 for r in rows]
        print 'What row, 1, 2 or 3?'
        keycol = int(raw_input('--> ')) - 1
        vals = valsfromrows(rows, keycol)

    print 30 * '>', vals[10], 30 * '<'

if __name__ == '__main__':
    play()
