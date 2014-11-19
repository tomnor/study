
"""
Play with the sox library (not a python thing)
"""

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
        One or more array-like objects to write. The first one is the
        time 'column'.

    """
    width, spacecnt = 16, 1
    # fmt = '{:15f}  '
    fmt = '{:' + str(width) + 'f}' + spacecnt * ' '
    fmt = len(data) * fmt + '\n'
    lines = [fmt.format(*tup) for tup in zip(*data)]

    # return lines
    fo.writelines(lines)
