import re
import datetime
from typing import NamedTuple
from typing import List


class A(NamedTuple):
    href: str
    text: str


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

    @staticmethod
    def hour_and_minute_to_time(hour: str, minutes: List[str]):
        res = []
        for minute in minutes:
            if minute != '-':
                res.append(datetime.time(int(hour), int(re.sub("\D", "", minute))))
        return res

    def __str__(self):
        return f"{self.days} {', '.join([x.strftime('%H:%M') for x in self.time])}"
