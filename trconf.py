"""
A configuration file for the translog program or if it is cashlog. Even
if not trivial, it shall be possible to build a regex for extracting
data from any kind of log format. The default will be a format familiar
to the developer.

The rxpatterns are searched for with re.findall. If results are multiple,
functions are provided here to select one of them from the list.
"""
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
    """Return the result from the list res (origin from line) that is to
    be used as date."""
    return res[-1]

def infoselect(res, line):
    """Return the result from the list res (origin from line) that is to
    be used as info."""
    return res[-1]

def amountselect(res, line):
    """Return the result from the list res (origin from line) that is to
    be used as amount."""
    if len(res) == 2:
        return res[0]
    elif len(res) == 3:
        return res[1]

# The extension of the files to read.
ext = 'csv'

# Number of rows to skip (header)
skiprows = 1

# Use this to convert the amount string to a float.
def crazyfloat(s):
    """Convert the string s to a float"""
    s = s.replace(',', '.')
    n = s.count('.')
    if n > 1:
        s = s.replace('.', '', n - 1)
    return float(s)

# Use this to convert the date string to a datetime.date object.
def transdate(dstr):
    """Return a datetime.date object on the dstr. YYYY-MM-DD"""

    return datetime.date(*[int(n) for n in dstr.split('-')])

