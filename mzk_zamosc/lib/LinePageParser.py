import os
import sys
import bs4
import requests
from typing import List
from typing import Dict
from bs4 import BeautifulSoup

PROJECT_DIR = os.path.abspath(__file__).rsplit(os.path.sep, 3)[0]
sys.path.insert(0, PROJECT_DIR)

from mzk_zamosc.lib.dtos import LineData


def parse_td(td: bs4.element.Tag) -> LineData:
    trs = td.table.find_all('tr', recursive=False)
    font = trs[0].td.font
    direction = next(font.br.next_siblings).strip()
    stops = get_stops_from_the_list(trs[1].td.ul.li)
    return LineData(direction, stops)


def get_stops_from_the_list(element: bs4.element.Tag, found: List[str] = None):
    if found is None:
        found = []
    text = element.find(text=True, recursive=False)
    if text:
        found.append(text.strip())
    sub_elements = element.find_all(recursive=False)
    if sub_elements:
        for sub_element in sub_elements:
            get_stops_from_the_list(sub_element, found)
    return found


if __name__ == '__main__':
    t = 'http://www.mzk.zamosc.pl/pliki/rozklad/0000/w.htm'
    req = requests.get(t)
    soup = BeautifulSoup(req.content, 'html.parser')
    tds = soup.body.table.find_all('tr', recursive=False)[1].find_all('td', recursive=False)
    stops_from_0_line = parse_td(tds[-1])
    print(stops_from_0_line)