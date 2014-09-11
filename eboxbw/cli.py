# The MIT License (MIT)
#
# Copyright (c) 2014 Philippe Proulx <eepp.ca>
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.

import argparse
import sys
from termcolor import cprint, colored
import eboxbw
import eboxbw.eboxbw


def _parse_args():
    desc = \
"""Output format is always, for each line:
date, download, upload and combined bandwidth usage."""

    ap = argparse.ArgumentParser(description=desc)

    ap.add_argument('-m', '--mi', action='store_true',
                    help='machine interface mode (for scripts)')
    ap.add_argument('-s', '--summary', action='store_true',
                    help='display only a summary of bandwidth usage')
    ap.add_argument('-u', '--unit', action='store', type=str,
                    default='g', metavar='UNIT',
                    help='set display unit to UNIT (\"g\" for GiB or \"m\" for MiB)')
    ap.add_argument('-V', '--version', action='version',
                    version='%(prog)s v{}'.format(eboxbw.__version__))
    ap.add_argument('id', metavar='ID', action='store', type=str,
                    help='user ID (VL code or user account ID)')

    # parse args
    args = ap.parse_args()

    # validate unit
    unit = args.unit.lower()
    if unit not in ['g', 'm']:
        print('error: wrong display unit',
              file=sys.stderr)
        sys.exit(1)

    return args


def _print_error(msg):
    cprint('error: {}'.format(msg), 'red', attrs=['bold'], file=sys.stderr)
    sys.exit(1)


def _print_mi(month, conv_func, summary):
    def print_row(date, dl, ul, cb, date_cb):
        dl = '{:.3f}'.format(dl)
        ul = '{:.3f}'.format(ul)
        cb = '{:.3f}'.format(cb)
        row = '{} {} {} {}'.format(date_cb(date), dl, ul, cb)

        print(row)

    if summary:
        tdl = conv_func(month.get_total_dl())
        tul = conv_func(month.get_total_ul())
        tcb = conv_func(month.get_total_combined())
        date = month.get_date()

        print_row(date, tdl, tul, tcb, lambda d: d.strftime('%Y-%m'))
    else:
        for date in sorted(month.get_days().keys()):
            day_bw = month.get_days()[date]
            dl = conv_func(day_bw.get_dl())
            ul = conv_func(day_bw.get_ul())
            cb = conv_func(day_bw.get_combined())

            print_row(date, dl, ul, cb, lambda d: d.strftime('%Y-%m-%d'))


def _print_human(month, conv_func, punit, summary):
    def print_row(date, dl, ul, cb, date_cb):
        cdl = colored('{:16.3f}'.format(dl), 'green', attrs=['bold'])
        cul = colored('{:16.3f}'.format(ul), 'red', attrs=['bold'])
        ccb = colored('{:16.3f}'.format(cb), 'yellow', attrs=['bold'])
        row = date_cb(date) + cdl + cul + ccb

        print(row)


    if summary:
        tdl = conv_func(month.get_total_dl())
        tul = conv_func(month.get_total_ul())
        tcb = conv_func(month.get_total_combined())
        date = month.get_date()

        print_row(date, tdl, tul, tcb, lambda d: d.strftime('%Y-%m   '))
    else:
        for date in sorted(month.get_days().keys()):
            day_bw = month.get_days()[date]
            dl = conv_func(day_bw.get_dl())
            ul = conv_func(day_bw.get_ul())
            cb = conv_func(day_bw.get_combined())

            print_row(date, dl, ul, cb, lambda d: d.strftime('%Y-%m-%d'))


def _do_eboxbw(args):
    try:
        bw = eboxbw.eboxbw.get_bw(args.id)
    except eboxbw.eboxbw.WrongIdError:
        _print_error('cannot read bandwidth usage: wrong ID')
    except eboxbw.eboxbw.TooManyConnectionsError:
        _print_error('cannot read bandwidth usage: too many connection attempts')
    except:
        _print_error('cannot read bandwidth usage')

    cur_month = bw.get_cur_month()

    if args.unit == 'g':
        conv_func = lambda x: x
        punit = 'GiB'
    else:
        conv_func = lambda x: x * 1024
        punit = 'MiB'

    if args.mi:
        _print_mi(cur_month, conv_func, args.summary)
    else:
        _print_human(cur_month, conv_func, punit, args.summary)


def run():
    args = _parse_args()

    try:
        _do_eboxbw(args)
    except KeyboardInterrupt:
        sys.exit(1)
