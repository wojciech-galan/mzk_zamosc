import re
import datetime
from typing import NamedTuple
from typing import List


class A(NamedTuple):
    href: str
    text: str


class Departures(object):

    def __init__(self, days:str, hours:List[str], minutes_and_info:List[str]):
        self.days = days
        assert len(hours) == len(minutes_and_info)
        self._hours = hours
        self._minutes = minutes_and_info
        time = [Departures.hour_and_minute_to_time(self._hours[i], self._minutes[i]) for i in range(len(self._hours))]
        self.time = filter(bool, time)

    @staticmethod
    def hour_and_minute_to_time(hour, minute):
        if minute != '-':
            return datetime.time(int(hour), int(re.sub("\D", "", minute)))
        return None

    def __str__(self):
        return f"{self.days} {', '.join([x.strftime('%H:%M') for x in self.time])}"
