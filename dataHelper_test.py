import logging
import time
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse
import json

import requests
import vobject
from dateutil import tz
from icalevents.icalevents import events
from icalevents.icalparser import Event
from lxml import etree
from requests.auth import HTTPBasicAuth

from settings import *

logger = logging.getLogger('app')


def sort_by_date(e: Event):
    return e.start.astimezone()
    
def get_weather(dt):
    logger.info('TEST DATA: Retrieving weather')
    
    baseURL = WEATHER_BASE_URL
    token = WEATHER_KEY
    lat = LATITUDE
    lon = LONGITUDE
    loc = str(lat) + ',' + str(lon)

    # darkSkyUrl = baseURL + '/' + token + '/' + str(lat) + ',' + str(lon) + ',' + dt.strftime('%Y-%m-%dT%H:%M:%S')

    w = {}
    
    w['maxTemp'] = float(100)
    w['minTemp'] = float(-33)
    # 1 row
    # w['day_summary'] = 'Overcast and very windy.'
    # multiple rows
    w['day_summary'] = 'Overcast and very windy throughout the day. Rain expected in the evening possibly hail and tornadoes.'
    
    w['sunrise'] = 1671630900 # Should be 7:55
    w['sunset'] = 1671684960 # Should be 22:56
    w['moonPhase'] = 'Quarter Moon'
    
    w['temperature'] = float(88)
    w['curr_feels_like'] = float(100)
    w['curr_summary'] = 'Light rain and windy with high temperature'
    
    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w


def get_tasks() -> List[str]:
    logger.info('TEST DATA: get tasks')
    return ['Contacts Tomorrow', 'Put out Garbage']

def get_run_summary() -> List[str]:
    logger.info('TEST DATA: run summary')

    data_str = '{"Current Month": {"duration_str": "14h 36m 39s", "nbr": "16", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2022-12-01T17:31:36Z", "rng": "Current Month", "tot_dist": "107.87", "tot_sec": "52599", "type": "Running", "user_id": 1}, "Current Week": {"duration_str": "2h 35m 42s", "nbr": "3", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2022-12-19T12:25:02Z", "rng": "Current Week", "tot_dist": "19.18", "tot_sec": "9342", "type": "Running", "user_id": 1}, "Current Year": {"duration_str": "293h 27m 03s", "nbr": "303", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2022-01-01T07:39:07Z", "rng": "Current Year", "tot_dist": "8888.88", "tot_sec": "1056423", "type": "Running", "user_id": 1}, "Past 30 days": {"duration_str": "18h 30m 34s", "nbr": "21", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2022-11-24T05:58:12Z", "rng": "Past 30 days", "tot_dist": "135.39", "tot_sec": "66634", "type": "Running", "user_id": 1}, "Past 365 days": {"duration_str": "300h 47m 54s", "nbr": "312", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2021-12-23T09:06:07Z", "rng": "Past 365 days", "tot_dist": "2188.10", "tot_sec": "1082874", "type": "Running", "user_id": 1}, "Past 7 days": {"duration_str": "4h 55m 32s", "nbr": "5", "newest_workout": "2022-12-21T10:39:35Z", "oldest_workout": "2022-12-16T10:48:24Z", "rng": "Past 7 days", "tot_dist": "36.32", "tot_sec": "17732", "type": "Running", "user_id": 1}}'
    data = json.loads(data_str)

    return data
