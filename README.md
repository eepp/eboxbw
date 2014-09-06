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

# get bandwidth info for current month
cur_month_bw = bw.get_cur_month()

print('total download (GiB): ' + cur_month_bw.get_total_dl())
print('total upload (GiB):   ' + cur_month_bw.get_total_ul())
print('total combined (GiB): ' + cur_month_bw.get_total_combined())

# available months
months_count = bw.get_months_count()

# previous month (0 is first, 1 is previous, 2 is penultimate)
prev_month = bw.get_month(1)
penultimate_month = bw.get_month(2)
```

Possible exceptions (all in `eboxbw.eboxbw`):

```python
Error                   # eboxbw error
    DownloadError       # cannot download page
    InvalidPageError    # cannot parse page
    WrongIdError        # wrong client identifier
```
