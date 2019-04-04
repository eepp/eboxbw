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

import re
import requests
import datetime
from bs4 import BeautifulSoup


class Error(RuntimeError):
    pass


class DownloadError(Error):
    pass


class InvalidPageError(Error):
    pass


class HtmlLayoutChangedError(InvalidPageError):
    pass


class TooManyConnectionsError(Error):
    def __init__(self):
        super().__init__('Too many connections in a given time')


class WrongIdError(Error):
    def __init__(self):
        super().__init__('Wrong ID')


class DownForMaintenanceError(Error):
    def __init__(self):
        super().__init__('Site is down for maintenance')


class Quantity:
    def __init__(self, real_gb, effective_gb=None):
        self._real_gb = real_gb
        self._effective_gb = effective_gb

    @property
    def real_gb(self):
        return self._real_gb

    @property
    def effective_gb(self):
        return self._effective_gb

    @property
    def real_mb(self):
        return self._real_gb * 1024

    @property
    def effective_mb(self):
        return self._effective_gb * 1024

    @property
    def real_kb(self):
        return self.real_mb * 1024

    @property
    def effective_kb(self):
        return self.effective_mb * 1024

    def __repr__(self):
        fmt = 'Quantity(real_gb={}, effective_gb={})'

        return fmt.format(self._real_gb, self._effective_gb)


class DayUsage:
    def __init__(self, date, dl_usage, ul_usage, combined_usage):
        self._date = date
        self._dl_usage = dl_usage
        self._ul_usage = ul_usage
        self._combined_usage = combined_usage

    @property
    def date(self):
        return self._date

    @property
    def dl_usage(self):
        return self._dl_usage

    @property
    def ul_usage(self):
        return self._ul_usage

    @property
    def combined_usage(self):
        return self._combined_usage


class MonthUsage:
    def __init__(self, date, days_usage, dl_usage, ul_usage, combined_usage):
        self._date = date
        self._days_usage = days_usage
        self._dl_usage = dl_usage
        self._ul_usage = ul_usage
        self._combined_usage = combined_usage

    @property
    def date(self):
        return self._date

    @property
    def dl_usage(self):
        return self._dl_usage

    @property
    def ul_usage(self):
        return self._ul_usage

    @property
    def combined_usage(self):
        return self._combined_usage

    @property
    def days_usage(self):
        return self._days_usage


class UsageInfo:
    def __init__(self, plan, extra_blocks, plan_cap, available_usage,
                 has_super_off_peak, months_usage):
        self._plan = plan
        self._extra_blocks = extra_blocks
        self._plan_cap = plan_cap
        self._available_usage = available_usage
        self._has_super_off_peak = has_super_off_peak
        self._months_usage = months_usage

    @property
    def plan(self):
        return self._plan

    @property
    def extra_blocks(self):
        return self._extra_blocks

    @property
    def plan_cap(self):
        return self._plan_cap

    @property
    def available_usage(self):
        return self._available_usage

    @property
    def has_super_off_peak(self):
        return self._has_super_off_peak

    @property
    def cur_month_usage(self):
        return self._months_usage[0]


def _download_page(id):
    url = 'http://conso.ebox.ca/index.php'
    payload = {
        'actions': 'list',
        'lng': 'en',
        'code': id,
    }

    try:
        resp = requests.post(url, timeout=15, data=payload)
    except requests.exceptions.Timeout:
        raise DownloadError('Timeout')
    except Exception as e:
        raise DownloadError('Cannot get information: ' + str(e))

    if resp.status_code != 200:
        raise DownloadError('Wrong HTTP status code: ' + str(resp.status_code))

    return resp.text


def _text_to_gb_value(raw_text):
    m = re.search('^([0-9.,]+)\\s+([gm])', raw_text, flags=re.I)

    if m:
        number = float(m.group(1).replace(',', '.'))

        if m.group(2).lower() == 'm':
            number /= 1024

        return number

    raise HtmlLayoutChangedError('Cannot decode value: {}'.format(raw_text))


def _check_error(page):
    if re.search(r'error', page, flags=re.I):
        raise WrongIdError()

    if re.search(r'maximum of request', page, flags=re.I):
        raise TooManyConnectionsError()

    if re.search(r'for maintenance', page, flags=re.I):
        raise DownForMaintenanceError()


def _has_super_off_peak(soup):
    return not bool(soup.select('.order_offpeak'))


def _get_usage_infos(soup):
    info_table = soup.select('table table')[0]
    trs = info_table.select('tr')
    plan = trs[0].select('div')[0].text.replace('Plan:', '').strip()
    extra_blocks = trs[1].select('div')[0].text
    m = re.search(r'(\d+) [xX]', extra_blocks)
    extra_blocks = int(m.group(1))
    plan_cap = trs[2].select('div')[0].text.replace('Plan total:', '').strip()
    plan_cap = _text_to_gb_value(plan_cap)
    plan_cap = Quantity(plan_cap, plan_cap)
    available_usage = trs[3].select('div')[0].text.replace('Available:', '')
    available_usage = available_usage.strip()
    available_usage = _text_to_gb_value(available_usage)
    available_usage = Quantity(available_usage, available_usage)
    has_super_off_peak = _has_super_off_peak(soup)

    return plan, extra_blocks, plan_cap, available_usage, has_super_off_peak


def _cur_month_qty_from_td(td):
    span = td.select('span.txtdata')[0]
    items = re.findall('\d+(?:[.,]\d+?)?\s*[GgMm]', str(span))

    if len(items) == 1:
        # non-super off peak
        gb = _text_to_gb_value(items[0])

        return Quantity(gb, gb)
    elif len(items) == 3:
        # super off peak
        real_gb = _text_to_gb_value(items[0])
        effective_gb = _text_to_gb_value(items[2])

        return Quantity(real_gb, effective_gb)
    else:
        raise HtmlLayoutChangedError('Current usage summary layout changed (box)')


def _day_usage_from_tr(tr):
    tds = tr.select('tr > td')

    if len(tds) != 4:
        return None

    raw_date = tds[0].text.strip()
    m = re.match(r'(\d{4})-(\d{2})-(\d{2})', raw_date)

    if not m:
        return None

    date = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
    dl_qty = Quantity(_text_to_gb_value(tds[1].text))
    ul_qty = Quantity(_text_to_gb_value(tds[2].text))
    cb_qty = Quantity(_text_to_gb_value(tds[3].text))

    return DayUsage(date, dl_qty, ul_qty, cb_qty)


def _get_cur_month_usage(soup):
    try:
        table = soup.select('tr.table_white table tr.table_white table')[0]
        tr = table.select('tr')[1]
        tds = tr.select('tr > td')
    except:
        raise HtmlLayoutChangedError('Current usage summary layout changed (table)')

    if len(tds) != 3:
        raise HtmlLayoutChangedError('Current usage summary layout changed (boxes)')

    dl_qty = _cur_month_qty_from_td(tds[0])
    ul_qty = _cur_month_qty_from_td(tds[1])
    cb_qty = _cur_month_qty_from_td(tds[2])
    trs = soup.select('#div1 > center > table > tr')

    if not trs:
        raise HtmlLayoutChangedError('Day usage details table layout changed')

    day_usages = []

    for tr in trs:
        day_usage = _day_usage_from_tr(tr)

        if day_usage is not None:
            day_usages.append(day_usage)

    try:
        date = day_usages[0].date.replace(day=1)
    except IndexError:
        date = None

    return MonthUsage(date, day_usages, dl_qty, ul_qty, cb_qty)


def _get_usage_info_from_page(page):
    _check_error(page)

    try:
        soup = BeautifulSoup(page, "html.parser")
    except:
        raise InvalidPageError()

    try:
        plan, extra_b, plan_cap, avail_usage, has_sop = _get_usage_infos(soup)
    except:
        raise HtmlLayoutChangedError('General informations layout changed')

    cur_month_usage = _get_cur_month_usage(soup)
    usage_info = UsageInfo(plan, extra_b, plan_cap, avail_usage, has_sop,
                           [cur_month_usage])

    return usage_info


def get_usage_info(id):
    return _get_usage_info_from_page(_download_page(id))


def get_usage_info_from_page(page):
    return _get_usage_info_from_page(page)
