import logging
import time
from datetime import datetime, timezone
from typing import List
from urllib.parse import urlparse

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
    
def get_weather_darksky(dt):
    logger.info('Retrieving weather')
    
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
    w['curr_summary'] = 'Light rain and windy with high temperature'
    
    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w


def get_tasks() -> List[str]:
    return ['Contacts Tomorrow', 'Put out Garbage']
