import os
import sys
import lxml
import bs4.element
import requests
from functools import partial
from lxml import etree
from bs4 import BeautifulSoup
from typing import List

PROJECT_DIR = os.path.abspath(__file__).rsplit(os.path.sep, 3)[0]
sys.path.insert(0, PROJECT_DIR)

from mzk_zamosc.lib.dtos import A
from mzk_zamosc.lib.dtos import Departures
from mzk_zamosc.lib.functions import tag_has_attribute
from mzk_zamosc.lib.functions import is_aligned
from mzk_zamosc.lib.functions import has_only_child_with_attribute


def get_lines_from_given_stop(line_url: str, url_root: str = 'http://www.mzk.zamosc.pl/pliki/rozklad/') -> List[A]:
    req = requests.get(line_url)
    soup = BeautifulSoup(req.content, 'html.parser')
    table: bs4.element.Tag = soup.body.table
    hrefs: bs4.element.ResultSet = table.findAll('a')
    return [A(f'{url_root}{x["href"].lstrip(".")}', x.text.strip()) for x in hrefs[:-1]]


def parse_stop_page(stop_url: str):
    req = requests.get(stop_url)
    soup = BeautifulSoup(req.content, 'html.parser')
    tr: bs4.element.Tag = soup.body.table.tr
    found: bs4.element.ResultSet[bs4.element.Tag] = tr.findAll(tag_has_bgcolor)
    assert len(found) == 1
    timetable = found[0]
    departures = []
    for tr in timetable.findAll(align=is_center_aligned):
        if has_one_td_with_class(tr):
            departure = td_has_class_is_followed_by_td_without_class(tr)
            if departure:
                departures.append(departure)
    return departures


def td_has_class_is_followed_by_td_without_class(tr: bs4.element.Tag) -> Departures:
    if has_one_td_with_class(tr) and not has_one_td_with_class(tr.next_sibling) and not has_one_td_with_class(
            tr.next_sibling.next_sibling):
        return Departures(parse_departure_days(tr),
                          parse_departure_hours(etree.fromstring(tr.next_sibling.prettify())),
                          parse_departure_hours(
                              etree.fromstring(tr.next_sibling.next_sibling.prettify()))
                          )


def parse_departure_days(tr: bs4.element.Tag) -> str:
    return tr.td.b.text


def parse_departure_hours(element: lxml.etree._Element, found: List[str] = None) -> List[List[str]]:
    if found is None:
        found = []
    text = element.text.strip() if element.text else None
    if text: found.append([text])
    if element.tag == 'br':
        br_text = element.tail.strip()
        if br_text:
            found[-1].append(br_text)
    else:
        sub_element: lxml.etree._Element
        for sub_element in element:
            parse_departure_hours(sub_element, found)
    return found


tag_has_bgcolor = partial(tag_has_attribute, attribute_name='bgcolor')
is_center_aligned = partial(is_aligned, alignment="CENTER")
has_one_td_with_class = partial(has_only_child_with_attribute, child_name='td', attribute_name='class')

if __name__ == '__main__':
    for element in parse_stop_page('http://www.mzk.zamosc.pl/pliki/rozklad/0056/0056t030.htm'):
        print(element)
    for element in parse_stop_page('http://www.mzk.zamosc.pl/pliki/rozklad//0000/0000t008.htm'):
        print(element)
