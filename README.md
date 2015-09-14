eboxbw
======

[![](https://img.shields.io/pypi/v/eboxbw.svg)](https://pypi.python.org/pypi/eboxbw)

**eboxbw** is a Python 3 package and a command line interface for
getting [Electronic Box](http://www.electronicbox.net/) cable Internet
bandwidth usage (Québec only). It is based on
[this tool](http://consocable.electronicbox.net/index.php?lng=en).

eboxbw supports Electronic Box's _Super off peak_ option.


reliability
-----------

Unfortunately, Electronic Box does not provide any sort of public API
to obtain a user's bandwidth usage data; eboxbw has to rely on parsing
the web interface's HTML output. This exact HTML output changes from
time to time, when Electronic Box decides so, which often results in
eboxbw not working anymore.

There have been several attempts to ask Electronic Box to create a
public API, but so far they won't.


installing
----------

### easy way

    sudo pip install eboxbw

If Python 3 isn't the default Python of your setup:

    sudo pip3 install eboxbw

You might want to install the Python dependencies with your distribution
package manager. They are:

  * [beautifulsoup4](https://pypi.python.org/pypi/beautifulsoup4)
  * [requests](https://pypi.python.org/pypi/requests)
  * [termcolor](https://pypi.python.org/pypi/termcolor)


### manual way

Make sure you have Python 3 and
[setuptools](https://pypi.python.org/pypi/setuptools).

Clone using Git and run `setup.py`:

    git clone https://github.com/eepp/eboxbw.git
    cd eboxbw
    sudo python3 setup.py install


using
-----


### command line interface (with colors!)

Simple lookup (current month summary):

    eboxbw vlabcdef

Current month details:

    eboxbw --details vlabcdef
    eboxbw -d vlabcdef

Current month summary, MiB:

    eboxbw --unit m vlabcdef
    eboxbw -um vlabcdef

All options reference:

    eboxbw --help

Detailed output example:

![Detailed output screenshot](http://ss.0x3b.org/nonflagellate530.png)
