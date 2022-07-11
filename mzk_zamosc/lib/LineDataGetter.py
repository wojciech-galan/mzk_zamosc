import os
import sys
import copy
import pickle
import requests
from typing import Dict
from typing import List
from typing import Tuple
from difflib import SequenceMatcher
from bs4 import BeautifulSoup

PROJECT_DIR = os.path.abspath(__file__).rsplit(os.path.sep, 3)[0]
sys.path.insert(0, PROJECT_DIR)

from mzk_zamosc.lib.dtos import NeighboringStops
from mzk_zamosc.lib.dtos import LineDataWithDepartures
from mzk_zamosc.lib.LinePageParser import parse_td


def guess_missing_stops(line_datas_with_departures: List[LineDataWithDepartures],
                        stops_with_neighbors: Dict[str, NeighboringStops]):
    if len(stops_with_neighbors) > 1:
        stop_names = list(stops_with_neighbors)
    else:
        the_only_stop = list(stops_with_neighbors.values())[0]
        stop_names = [the_only_stop.prev, the_only_stop.this, the_only_stop.next_]
    for line_data_with_departures in line_datas_with_departures:
        complete_stops = [k for k, v in line_data_with_departures.stops_and_departures.items() if v is not None]
        s = SequenceMatcher(None, complete_stops, stop_names)
        matches = s.get_matching_blocks()
        long_matches = [match for match in matches if match.size > 1]
        if long_matches:
            ret = {}
            for match in long_matches:
                ret.update({
                    stop: line_data_with_departures.stops_and_departures[stop] for stop in
                    complete_stops[match.a:match.a + match.size]
                })
            return ret
    return {}


def fill_missing_stops(line_datas_with_departures: List[LineDataWithDepartures],
                       missing_stops: Dict[str, NeighboringStops], rounds: int = 5):
    ret = {}
    current_missing_stops: Dict[str, NeighboringStops] = copy.copy(missing_stops)
    if current_missing_stops:
        while current_missing_stops and rounds:
            missing_stops_data = guess_missing_stops(line_datas_with_departures, current_missing_stops)
            for stop in missing_stops_data:
                try:
                    del current_missing_stops[stop]
                except KeyError:
                    pass  # todo logowanie
            ret.update(missing_stops_data)
            rounds -= 1
    return ret, current_missing_stops


def get_line_data(lines, tds, line_number, repeats: int = 3) -> Tuple[List]:
    missing_line_data = []
    line_number = str(line_number)
    lines_of_interest = {k: v for k, v in lines.items() if k.startswith(f'{line_number} ')}
    line_direction_stops_departures = []
    line_direction_stops_departures_incomplete = []
    datas = [parse_td(td) for td in tds]
    for j, data in enumerate(datas):
        one_line = lines_of_interest[f'{line_number} - > ' + data.direction]
        new_line_with_departures = LineDataWithDepartures(data.direction, data.stops)
        missing_stops = new_line_with_departures.find_stop_data(one_line)
        missing_stops_found, missing_stops_not_found = fill_missing_stops(line_direction_stops_departures,
                                                                          missing_stops)
        new_line_with_departures.update(missing_stops_found)
        missing_stops_found_2, missing_stops_not_found_2 = fill_missing_stops(
            line_direction_stops_departures_incomplete, missing_stops_not_found, repeats)
        new_line_with_departures.update(missing_stops_found_2)
        if missing_stops_not_found_2:
            line_direction_stops_departures_incomplete.append(new_line_with_departures)
        else:
            line_direction_stops_departures.append(new_line_with_departures)

        missing_line_data.extend([(line_number, data.direction, j, stop) for stop in missing_stops_not_found])

    return line_direction_stops_departures + line_direction_stops_departures_incomplete, missing_line_data


if __name__ == '__main__':
    with open(os.path.join(PROJECT_DIR, 'notebooks', 'lines.pickle'), 'rb') as f:
        lines = dict(pickle.load(f))

    line_datas = []
    missing_line_datas = []
    for line_num in (0, 1, 2, 3, 4, 7, 8, 9, 10, 11, 14, 15, 17, 21, 31, 33, 35, 40, 42, 44, 47, 49, 54, 55, 56):
        page = f'http://www.mzk.zamosc.pl/pliki/rozklad/00{line_num:02}/w.htm'
        req = requests.get(page)
        soup = BeautifulSoup(req.content, 'html.parser')
        tds = soup.body.table.find_all('tr', recursive=False)[1].find_all('td', recursive=False)
        line_data, missing_line_data = get_line_data(lines, tds, line_num)
        line_datas.extend(line_data)
        missing_line_datas.extend(missing_line_data)

    for m in missing_line_datas:
        print(m)
