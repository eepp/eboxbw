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

import re
import requests
from datetime import datetime, date
from bs4 import BeautifulSoup


class Error(RuntimeError):
    pass


class DownloadError(Error):
    pass


class InvalidPageError(Error):
    pass


class TooManyConnectionsError(Error):
    def __init__(self):
        super().__init__('Too many connections in a given time')


class WrongIdError(Error):
    def __init__(self):
        super().__init__('Wrong ID')


class DayBwInfo:
    def __init__(self, date, dl_gb, ul_gb):
        self._date = date
        self._dl_gb = dl_gb
        self._ul_gb = ul_gb

    def get_date(self):
        return self._date

    def get_dl(self):
        return self._dl_gb

    def get_ul(self):
        return self._ul_gb

    def get_combined(self):
        return self._dl_gb + self._ul_gb


class MonthBwInfo:
    def __init__(self, date, days_bw_info):
        self._date = date
        self._days_bw_info = days_bw_info

    def get_date(self):
        return self._date

    def get_days(self):
        return self._days_bw_info

    def get_total_dl(self):
        return sum([d.get_dl() for d in self._days_bw_info.values()])

    def get_total_ul(self):
        return sum([d.get_ul() for d in self._days_bw_info.values()])

    def get_total_combined(self):
        return sum([d.get_combined() for d in self._days_bw_info.values()])


class BwInfo:
    def __init__(self, months_bw_info):
        self._months_bw_info = months_bw_info

    def get_cur_month(self):
        return self._months_bw_info[0]


def _download_page(id):
    fmt = 'http://consocable.electronicbox.net/index.php?actions=list&lng=en&codeVL={}'
    url = fmt.format(id)

    try:
        resp = requests.get(url)
    except Exception as e:
        raise DownloadError('Cannot get information: ' + str(e))

    if resp.status_code != 200:
        raise DownloadError('Wrong HTTP status code: ' + str(resp.status_code))

    return resp.text


def _get_dlul_gb(raw_text):
    m = re.search('^([0-9.,]+)\\s+([gm])', raw_text, flags=re.I)

    if m:
        number = float(m.group(1).replace(',', '.'))

        if m.group(2).lower() == 'm':
            number /= 1024

        return number

    return None


def _check_error(page):
    if re.search('error', page, flags=re.I):
        raise WrongIdError()

    if re.search('maximum of request', page, flags=re.I):
        raise TooManyConnectionsError()


def _get_bw_info(page):
    _check_error(page)

    try:
        soup = BeautifulSoup(page)
    except:
        raise InvalidPageError()

    tables = soup.select('table')

    if len(tables) < 5:
        raise InvalidPageError()

    cm_table = tables[4]
    cm_table_trs = cm_table.select('> tr')

    if not cm_table_trs:
        raise InvalidPageError()

    days_bw_info = {}

    for tr in cm_table_trs:
        tds = tr.select('> td')

        if len(tds) < 3:
            continue

        first_td_text = tds[0].text.strip()

        m = re.search('^(\d{4}-\d{2}-\d{2})', first_td_text)

        if not m:
            continue

        date = datetime.strptime(m.group(1), '%Y-%m-%d').date()

        dl_gb_raw = tds[1].text.strip()
        ul_gb_raw = tds[2].text.strip()

        dl_gb = _get_dlul_gb(dl_gb_raw)
        ul_gb = _get_dlul_gb(ul_gb_raw)

        if dl_gb is None or ul_gb is None:
            raise InvalidPageError()

        days_bw_info[date] = DayBwInfo(date, dl_gb, ul_gb)

    if not days_bw_info:
        raise InvalidPageError()

    month_date = list(days_bw_info.keys())[0].replace(day=1)
    cur_month_bw_info = MonthBwInfo(month_date, days_bw_info)

    return BwInfo([cur_month_bw_info])


def get_bw(id):
    page = _download_page(id)

    return _get_bw_info(page)


def get_bw_from_page(page):
    return _get_bw_info(page)
