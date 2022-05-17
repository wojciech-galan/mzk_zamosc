import re

import bs4.element
import requests
from typing import Generator
from bs4 import BeautifulSoup

from lib.dtos import A


def parse_stops_main_page(url_root:str='http://www.mzk.zamosc.pl/pliki/rozklad/', ending:str='przystan.htm'):
    req = requests.get(f'{url_root}{ending}')
    soup = BeautifulSoup(req.content, 'html.parser')
    table: bs4.element.Tag = soup.findAll('table')[-1]
    for item in table.findAll(find_tr_with_stops):
        for sub in parse_tr(item, url_root):
            print(sub)


def find_tr_with_stops(tr_tag:bs4.element.Tag) -> bool:
    td:bs4.element.Tag = tr_tag.find('td')
    return td and not td.has_attr('class') and not td.has_attr('align')


def parse_tr(tr_tag:bs4.element.Tag, url_root:str) -> Generator[A, None, None]:
    td: bs4.element.Tag = tr_tag.find('td')
    for a in td.findAll('a'):
        yield A(f'{url_root}{a.get("href")}', a.text)


if __name__ == '__main__':
    parse_stops_main_page()
