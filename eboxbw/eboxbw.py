import re
import requests
from bs4 import BeautifulSoup


class Error(RuntimeError):
    pass


class DownloadError(Error):
    pass


class InvalidPageError(Error):
    pass


class WrongIdError(Error):
    def __init__(self):
        super().__init__('Wrong ID')


class MonthBwInfo:
    def __init__(self, total_dl_gb, total_ul_gb):
        self._total_dl_gb = total_dl_gb
        self._total_ul_gb = total_ul_gb

    def get_total_dl(self):
        return self._total_dl_gb

    def get_total_ul(self):
        return self._total_ul_gb

    def get_total_combined(self):
        return self._total_dl_gb + self._total_ul_gb


class BwInfo:
    def __init__(self, months_bw_info):
        self._months_bw_info = months_bw_info

    def get_cur_month(self):
        return self._months_bw_info[0]

    def get_month(self, index):
        return self._months_bw_info[index]

    def get_months_count(self):
        return len(self._months_bw_info)


def _get_page(id):
    fmt = 'http://consocable.electronicbox.net/index.php?actions=list&codeVL={}'
    url = fmt.format(id)

    try:
        resp = requests.get(url)
    except Exception as e:
        raise DownloadError('Cannot get information: ' + str(e))

    if resp.status_code != 200:
        raise DownloadError('Wrong HTTP status code: ' + str(resp.status_code))

    return resp.text


def _is_error(page):
    return bool(re.search('error', page, flags=re.I))


def _get_months_tables(soup):
    all_tables = soup.select('#divListAll table > tr.table_white')

    months_tables = []

    # current month
    if len(all_tables) >= 5:
        months_tables.append(all_tables[4])

    # previous month
    if len(all_tables) >= 11:
        months_tables.append(all_tables[10])

    # penultimate month
    if len(all_tables) >= 17:
        months_tables.append(all_tables[16])

    return months_tables


def _get_dlul_gb(td_tag):
    txtdata = td_tag.select('.txtdata')[0]

    for item in txtdata.contents:
        item = str(item).strip()
        item = item.replace(',', '.')

        m = re.search('^([0-9.]+)\\s+([gm])', item, flags=re.I)

        if m:
            number = float(m.group(1))

            if m.group(2).lower() == 'm':
                number /= 1024

            return number


def _get_bw_info_from_table(table_tag):
    cells = table_tag.select('table.table_block td.td_block')

    total_dl = _get_dlul_gb(cells[0])
    total_ul = _get_dlul_gb(cells[1])

    return total_dl, total_ul


def _get_bw_info(page):
    try:
        soup = BeautifulSoup(page)
    except:
        raise InvalidPageError()

    months_tables = _get_months_tables(soup)
    months_bw_info = []

    for month_table in months_tables:
        total_dl, total_ul = _get_bw_info_from_table(month_table)
        months_bw_info.append(MonthBwInfo(total_dl, total_ul))

    return BwInfo(months_bw_info)


def get_bw(id):
    page = _get_page(id)

    if _is_error(page):
        raise WrongIdError()

    return _get_bw_info(page)

