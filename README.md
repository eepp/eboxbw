eboxbw
======

Python 3 library for [Electronic Box](http://www.electronicbox.net/)
cable Internet bandwidth usage (Québec only). It is based on
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

  * [BeautifulSoup 4](http://www.crummy.com/software/BeautifulSoup/)
  * [Requests](http://docs.python-requests.org/en/latest/)


using
-----

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
