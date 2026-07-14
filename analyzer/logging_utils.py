from datetime import datetime
from zoneinfo import ZoneInfo
import logging

class TimezoneFormatter(logging.Formatter):
    def formatTime(self, record, datefmt=None):
        dt = datetime.fromtimestamp(record.created, tz=ZoneInfo('Africa/Cairo'))
        return dt.strftime(datefmt or '%Y-%m-%d %H:%M:%S %z')
