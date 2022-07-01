import os
import sys
import pickle
import bs4.element
import requests
from collections import defaultdict
from collections.abc import Container
from typing import Generator
from bs4 import BeautifulSoup

PROJECT_DIR = os.path.abspath(__file__).rsplit(os.path.sep, 2)[0]
sys.path.insert(0, PROJECT_DIR)

from mzk_zamosc.lib.dtos import A
from mzk_zamosc.lib.StopPageParsers import get_lines_from_given_stop
from mzk_zamosc.lib.StopPageParsers import parse_stop_page
from mzk_zamosc.lib.constants import VALID_DAYS


def parse_stops_main_page(url_root: str = 'http://www.mzk.zamosc.pl/pliki/rozklad/', ending: str = 'przystan.htm') -> \
        Generator[A, None, None]:
    req = requests.get(f'{url_root}{ending}')
    soup = BeautifulSoup(req.content, 'html.parser')
    table: bs4.element.Tag = soup.findAll('table')[-1]
    for item in table.findAll(find_tr_with_stops):
        for sub in parse_tr(item, url_root):
            yield sub


def find_tr_with_stops(tr_tag: bs4.element.Tag) -> bool:
    td: bs4.element.Tag = tr_tag.find('td')
    return td and not td.has_attr('class') and not td.has_attr('align')


def parse_tr(tr_tag: bs4.element.Tag, url_root: str) -> Generator[A, None, None]:
    td: bs4.element.Tag = tr_tag.find('td')
    for a in td.findAll('a'):
        yield A(f'{url_root}{a.get("href")}', a.text.strip())


def get_and_validate_data(out_path_stops: str, out_path_lines: str, valid_days: Container = VALID_DAYS):
    stop_departures_mapping = defaultdict(dict)
    line_departures_mapping = defaultdict(dict)
    for a in parse_stops_main_page():
        stop = a.text
        lines = get_lines_from_given_stop(a.href)
        for line in lines:
            departures = [x for x in parse_stop_page(line.href)]
            stop_departures_mapping[stop][line.text] = departures
            line_departures_mapping[line.text][stop] = departures

    days = set([z.days for x in stop_departures_mapping.values() for y in x.values() for z in y])
    assert all([day in valid_days for day in days])
    with open(out_path_stops, 'wb') as f:
        pickle.dump(dict(stop_departures_mapping), f)
    with open(out_path_lines, 'wb') as f:
        pickle.dump(dict(line_departures_mapping), f)


if __name__ == '__main__':
    get_and_validate_data(
        os.path.join(PROJECT_DIR, 'notebooks', 'stops.pickle'),
        os.path.join(PROJECT_DIR, 'notebooks', 'lines.pickle')
    )

