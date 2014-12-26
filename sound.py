
"""
Play with the sox library (not a python thing)
"""
import numpy as np

def write_soxdat(fo, rate, *data):
    """Write data to opened file f.

    The intention is to write a file that can be played with the sox
    library. It seems picky on the layout of the file. Need fixed width
    kind of lay-out it seems.

    fo: file
        File object opened for writing.

    rate: int
        The sampling rate.

    data: array-likes
        One or more array-like objects to write. Those are the
        "channels" in the .dat file.

    """
    width, spacecnt = 16, 1
    fmt = '{:' + str(width) + 'f}' + spacecnt * ' '
    fmt = (len(data) + 1) * fmt + '\n'
    T = np.linspace(0, 1.0 / rate * len(data[0]), num=len(data[0]),
                    endpoint=False)
    lines = [fmt.format(*tup) for tup in zip(T, *data)]

    header = ('; Sample Rate ' + str(rate) + '\n' +
              '; Channels {}\n'.format(len(data)))
    fo.write(header)
    fo.writelines(lines)

def adjust_normalize(a, tozero=np.mean, fromto=(10, 90)):
    """Return a version of array a, offset so that the magnitude
    produced by tozero is zero. Also make peak values be between +/-
    1. Base the conversion on fromto of the array, (percentage).

    a: numpy 1d array
        ...

    tozero: func
        ...

    fromto: tuple
        ...

    """

    fromto = slice(int(fromto[0] * 0.01 * len(a)),
                   int(fromto[1] * 0.01 * len(a)))
    base = tozero(a[fromto])
    a = a - base
    peak = max(abs(min(a[fromto])), abs(max(a[fromto])))
    x = 1.0 / peak
    a = a * x
    return a


# Given a sine wave described with 50 points and a desired freqency of
# 500 Hz:
# p = 1 / f = 1 / 500 = 0.002     # period
# pq = p / 50 = 0.002 / 50 = 4 x 10^(-5) (0.00004) # time increment per sample
# # point
# rate = 1 / pq = 1 / 0.00004 = 25000              # 25 kHz
