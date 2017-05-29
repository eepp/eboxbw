# The MIT License (MIT)
#
# Copyright (c) 2014-2015 Philippe Proulx <eepp.ca>
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

from termcolor import cprint, colored
import argparse
import eboxbw
import sys


def _parse_args():
    desc = \
"""Output format is always, for each line:
date, download, upload and combined bandwidth usage."""

    ap = argparse.ArgumentParser(description=desc)

    ap.add_argument('-d', '--details', action='store_true',
                    help='display more bandwidth usage details')
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


def _print_warning(msg):
    cprint('warning: {}'.format(msg), 'yellow', attrs=['bold'], file=sys.stderr)


def _bold(t):
    return colored(t, attrs=['bold'])


def _prop(t):
    return colored(t, 'blue', attrs=['bold'])


def _yes_no(v):
    return {
        True: colored('yes', 'green', attrs=['bold']),
        False: colored('no', 'red', attrs=['bold']),
    }[v]


def _effective(t):
    return colored(t, 'yellow')


def _print_human(usage_info, conv_func, punit, details):
    def gb_txt(gb):
        return '{:.2f} {}'.format(conv_func(gb), punit)

    def print_table_border():
        print('+------------+------------------+------------------+------------------+')

    def print_row(date, dl, ul, cb, date_cb):
        date_txt = date_cb(date)
        fmt_row1 = '| {:10s} | {:>16s} | {:>16s} | {:>16s} |'
        fmt_row2 = '|            | {} | {} | {} |'

        print(fmt_row1.format(date_txt, gb_txt(dl.real_gb), gb_txt(ul.real_gb),
                              gb_txt(cb.real_gb)))

        if dl.effective_gb is not None:
            dl_txt = '{:>16s}'.format(gb_txt(dl.effective_gb))
            ul_txt = '{:>16s}'.format(gb_txt(ul.effective_gb))
            cb_txt = '{:>16s}'.format(gb_txt(cb.effective_gb))

            print(fmt_row2.format(_effective(dl_txt), _effective(ul_txt),
                                  _bold(_effective(cb_txt))))

    def print_table_header():
        print_table_border()
        fmt = '|    {}    |     {}     |      {}      |     {}     |'
        print(fmt.format(_bold('date'), _bold('download'), _bold('upload'),
                         _bold('combined')))
        print_table_border()

    if details:
        print('{}:            {}'.format(_prop('Plan'), usage_info.plan))
        print('{}: {}'.format(_prop('Super off peak?'),
                                         _yes_no(usage_info.has_super_off_peak)))
        print('{}:    {} x 75 GiB'.format(_prop('Extra blocks'),
                                          usage_info.extra_blocks))
        print('{}:   {}'.format(_prop('Plan capacity'),
                                   gb_txt(usage_info.plan_cap.real_gb)))
        print('{}: {}'.format(_prop('Available usage'),
                                   gb_txt(usage_info.available_usage.real_gb)))
        print()

    more = ''

    cur_month_usage = usage_info.cur_month_usage
    date = cur_month_usage.date

    if date is None:
        _print_warning('no usage data available yet for current month')
        return

    if usage_info.has_super_off_peak:
        more = ' (effective usage on second row)'

    print('{}{}:'.format(_prop('Usage summary'), more))
    print_table_header()
    tdl = cur_month_usage.dl_usage
    tul = cur_month_usage.ul_usage
    tcb = cur_month_usage.combined_usage
    print_row(date, tdl, tul, tcb, lambda d: d.strftime('%Y-%m'))
    print_table_border()

    if details:
        print()
        print('{}:'.format(_prop('Usage details')))
        print_table_header()

        for du in cur_month_usage.days_usage:
            print_row(du.date, du.dl_usage, du.ul_usage, du.combined_usage,
                      lambda d: d.strftime('%Y-%m-%d'))

        print_table_border()


def _main(args):
    try:
        usage_info = eboxbw.get_usage_info(args.id)
    except eboxbw.WrongIdError:
        _print_error('cannot read bandwidth usage: wrong ID')
    except eboxbw.TooManyConnectionsError:
        _print_error('cannot read bandwidth usage: too many connection attempts')
    except eboxbw.DownloadError:
        _print_error('cannot read bandwidth usage: cannot download info')
    except eboxbw.DownForMaintenanceError:
        _print_error('cannot read bandwidth usage: site is down for maintenance')
    except eboxbw.HtmlLayoutChangedError:
        _print_error('cannot read bandwidth usage: HTML layout changed')
    except eboxbw.InvalidPageError:
        _print_error('cannot read bandwidth usage: invalid HTML page')
    except Exception as e:
        _print_error('cannot read bandwidth usage: {}'.format(e))
        raise e


    if args.unit == 'g':
        conv_func = lambda x: x
        punit = 'GiB'
    else:
        conv_func = lambda x: x * 1024
        punit = 'MiB'

    _print_human(usage_info, conv_func, punit, args.details)


def run():
    args = _parse_args()

    try:
        _main(args)
    except KeyboardInterrupt:
        sys.exit(1)
