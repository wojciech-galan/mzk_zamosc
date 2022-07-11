import re
import datetime
from typing import NamedTuple
from typing import List
from typing import Dict


class A(NamedTuple):
    href: str
    text: str


class LineData(NamedTuple):
    direction: str
    stops: List[str]


class Departures(object):

    def __init__(self, days: str, hours: List[List[str]], minutes_and_info: List[List[str]]):
        self.days = days
        assert len(hours) == len(minutes_and_info)
        assert all([len(hour) == 1 for hour in hours])
        self._hours = hours
        self._minutes = minutes_and_info
        time = []
        for i in range(len(self._hours)):
            time.extend(Departures.hour_and_minute_to_time(self._hours[i][0], self._minutes[i]))
        self.time = filter(bool, time)
        super().__init__()

    @staticmethod
    def hour_and_minute_to_time(hour: str, minutes: List[str]):
        res = []
        for minute in minutes:
            if minute != '-':
                res.append(datetime.time(int(hour), int(re.sub("\D", "", minute))))
        return res

    def __str__(self):
        return f"{self.days} {', '.join([x.strftime('%H:%M') for x in self.time])}"


class NeighboringStops(NamedTuple):
    prev: str
    this: str
    next_: str


class LineDataWithDepartures(object):
    def __init__(self, direction: str, stops: List[str]):
        self.direction: str = direction
        self.stops_and_departures: Dict[str, List] = {stop: None for stop in stops}  # list of departures
        self.__data_complete = False
        super().__init__()

    def is_complete(self) -> bool:
        self.__data_complete = self.__data_complete or all(self.stops_and_departures.values())
        return bool(self.__data_complete)

    def find_stop_data(self, one_line_stop_data: Dict[str, List[Departures]]) -> Dict[str, NeighboringStops]:
        missing_stops = {}
        stops = list(self.stops_and_departures.keys())
        for i, stop in enumerate(stops[:-1]):
            try:
                self.stops_and_departures[stop] = one_line_stop_data[stop]
            except KeyError:
                try:
                    self.stops_and_departures[stop] = one_line_stop_data[stop.replace('(NŻ)', '').strip()]
                except KeyError:
                    prev = stops[i - 1] if i else None
                    missing_stops[stop] = NeighboringStops(
                        prev,
                        stop,
                        stops[i + 1]
                    )
        return missing_stops

    def update(self, update_data: Dict[str, List]):
        self.stops_and_departures.update(update_data)
