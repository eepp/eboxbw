eboxbw
======

Python 3 library and command line interface for
[Electronic Box](http://www.electronicbox.net/) cable Internet bandwidth
usage (Québec only). It is based on
[this tool](http://consocable.electronicbox.net/index.php?lng=en).


installing
----------

Make sure you have Python 3 and
[setuptools](https://pypi.python.org/pypi/setuptools).

Clone using Git and run `setup.py`:

    git clone https://github.com/eepp/eboxbw.git
    cd eboxbw
    sudo python3 setup.py install

You might want to install the Python dependencies with your
distribution package manager. They are:

  * [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4)
  * [requests](https://pypi.python.org/pypi/requests)
  * [termcolor](https://pypi.python.org/pypi/termcolor)


using
-----


### command line interface (with colors!)

Simple lookup (all days of current month):

    eboxbw vlabcdef

Current month summary:

    eboxbw --summary vlabcdef
    eboxbw -s vlabcdef

Current month summary, MiB:

    eboxbw --sumary --unit m vlabcdef
    eboxbw -s -um vlabcdef

All days of current month, machine interface, MiB:

    eboxbw --mi --unit m vlabcdef
    eboxbw -m -um vlabcdef

Current month summary, machine interface:

    eboxbw --mi --summary vlabcdef
    eboxbw -ms vlabcdef

All options reference:

    eboxbw --help


### library

Simple example:

```python
from eboxbw import eboxbw

# use your VL code or your account number (this may take a few seconds)
bw = eboxbw.get_bw('vlabcdef')

# get current month
cur_month_bw = bw.get_cur_month()

# which month?
print('month: ' + cur_month_bw.get_date().strftime('%Y-%m'))

# totals for this month
print('total download (GiB): {}'.format(cur_month_bw.get_total_dl()))
print('total upload (GiB):   {}'.format(cur_month_bw.get_total_ul()))
print('total combined (GiB): {}'.format(cur_month_bw.get_total_combined()))

# per day (days_bw_info is a dict)
days_bw_info = cur_month_bw.get_days()

for day in sorted(days_bw_info.keys()):
    day_bw_info = days_bw_info[day]

    print(day.strftime('%Y-%m-%d:'))
    print('  download (GiB): {}'.format(day_bw_info.get_dl()))
    print('  upload (GiB):   {}'.format(day_bw_info.get_ul()))
    print('  combined (GiB): {}'.format(day_bw_info.get_combined()))
```

Possible exceptions (all from `eboxbw.eboxbw`):

```python
Error                           # eboxbw base error
    DownloadError               # cannot download page
    InvalidPageError            # cannot parse page
    TooManyConnectionsError     # too many attempted connections
    WrongIdError                # wrong client identifier
```
