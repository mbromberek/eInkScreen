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


def get_events(max_number: int) -> List[Event]:
    logger.info("Retrieving calendar infos")
    utc_timezone = tz.tzutc()
    current_timezone = tz.tzlocal()

    try:
        event_list = events(WEBDAV_CALENDAR_URL, fix_apple=WEBDAV_IS_APPLE)
        logger.info(event_list)
        #logger.info(WEBDAV_CALENDAR_URL_1)
        #event_list_2 = events(WEBDAV_CALENDAR_URL_1, fix_apple=WEBDAV_IS_APPLE)
        #logger.info(event_list_2)
        #event_list.extend(event_list_2)
        event_list.sort(key=sort_by_date)

        start_count = 0
        for event in event_list:
            event.start.replace(tzinfo=utc_timezone)
            event.start = event.start.astimezone(current_timezone)

            # remove events from previous day (problem based on time-zones)
            day_number = time.localtime().tm_mday
            event_date = event.start.date()
            if (day_number == 1 and event_date.month < time.localtime().tm_mon):
                start_count += 1
                max_number += 1
            elif (event_date.day < day_number):
                start_count += 1
                max_number += 1

        logger.info("Got {} calendar-entries (capped to {})".format(
            len(event_list), max_number-start_count))
        return event_list[start_count:max_number]

    except Exception as e:
        logger.critical(e)
        return []


def get_birthdays() -> List[str]:
    logger.info("Retrieving contact (birthday) infos")
    try:
        auth = HTTPBasicAuth(CALDAV_CONTACT_USER, CALDAV_CONTACT_PWD)
        baseurl = urlparse(CALDAV_CONTACT_URL).scheme + \
            '://' + urlparse(CALDAV_CONTACT_URL).netloc

        r = requests.request('PROPFIND', CALDAV_CONTACT_URL, auth=auth, headers={
            'content-type': 'text/xml', 'Depth': '1'})
        if r.status_code != 207:
            raise RuntimeError('error in response from %s: %r' %
                               (CALDAV_CONTACT_URL, r))

        vcardUrlList = []
        root = etree.XML(r.text.encode())
        for link in root.xpath('./d:response/d:propstat/d:prop/d:getcontenttype[starts-with(.,"text/vcard")]/../../../d:href', namespaces={"d": "DAV:"}):
            vcardUrlList.append(baseurl + link.text)

        today = datetime.today()
        birthday_names: List[str] = []
        for vurl in vcardUrlList:
            r = requests.request("GET", vurl, auth=auth)
            vcard = vobject.readOne(r.text)
            if 'bday' in vcard.contents.keys():
                birthday = vcard.contents['bday'][0]
                try:
                    birthday_date = datetime.strptime(
                        birthday.value, "%Y-%m-%d")
                except ValueError:
                    # necessary, because multipe formats are used...
                    birthday_date = datetime.strptime(birthday.value, "%Y%m%d")

                if (birthday_date.day == today.day) and (birthday_date.month == today.month):
                    name = vcard.contents['fn'][0].value
                    birthday_names.append(name)
        return birthday_names
    except Exception as e:
        logger.critical(e)
        return []

def get_weather(dt) -> List[str]:
    logger.info('Retrieving weather')
    
    baseURL = WEATHER_BASE_URL
    token = WEATHER_KEY
    lat = LATITUDE
    lon = LONGITUDE
    loc = str(lat) + ',' + str(lon)

    # url = baseURL + '/history.json' + '?q=' + loc + '&dt=' + dttm.strftime('%Y-%m-%d') + '&hour=' + dttm.strftime('%H')
    url = baseURL + '/history.json' + '?q=' + loc + '&dt=' + dt.strftime('%Y-%m-%d')

    w = {}
    r = requests.get(url, headers={'key':token}, verify=True)
    weatherData = r.json()
    
    logger.info(weatherData)
    weatherDay = weatherData['forecast']['forecastday'][0]['day']
    w['maxTemp'] = weatherDay['maxtemp_f']
    w['minTemp'] = weatherDay['mintemp_f']
    w['avgTemp'] = weatherDay['avgtemp_f']
    w['summary'] = weatherDay['condition']['text']
    w['totalPrecip'] = weatherDay['totalprecip_in']
    
    astronomyDay = weatherData['forecast']['forecastday'][0]['astro']
    w['sunrise'] = astronomyDay['sunrise']
    w['sunset'] = astronomyDay['sunset']
    w['moonPhase'] = astronomyDay['moon_phase']

    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w
    
    
def get_weather_darksky(dt):
    logger.info('Retrieving weather')
    
    baseURL = WEATHER_BASE_URL
    token = WEATHER_KEY
    lat = LATITUDE
    lon = LONGITUDE
    loc = str(lat) + ',' + str(lon)

    darkSkyUrl = baseURL + '/' + token + '/' + str(lat) + ',' + str(lon) + ',' + dt.strftime('%Y-%m-%dT%H:%M:%S')

    w = {}
    r = requests.get(darkSkyUrl)
    weatherData = r.json()
    
    weatherDay = weatherData['daily']['data'][0]
    
    w['maxTemp'] = weatherDay['temperatureMax']
    w['minTemp'] = weatherDay['temperatureMin']
    # w['avgTemp'] = weatherDay['avgtemp_f']
    w['summary'] = weatherDay['summary']
    # w['totalPrecip'] = weatherDay['totalprecip_in']
    
    w['sunrise'] = weatherDay['sunriseTime']
    w['sunset'] = weatherDay['sunsetTime']
    w['moonPhase'] = weatherDay['moonPhase']
    
    w['temperature'] = weatherData['currently']['temperature']
    
    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w

def split_text(s, max_width, new_line_start='') -> List[str]:
    # logger.info('split_text to width: ' + str(max_width))
    str_split_lst = []
    s_tmp = s
    while True:
        if len(s_tmp) <= max_width:
            str_split_index = -1 #Use all of the remaining string
        else:
            str_split_index = s_tmp[0:max_width].rfind(' ')
        if str_split_index == -1: #this logic does not work if there is a word with over max_width in length
            str_split_lst.append(s_tmp)
            return str_split_lst
        str_split_lst.append(s_tmp[0:str_split_index])
        s_tmp = new_line_start + s_tmp[str_split_index+1:]
    
def get_run_summary() -> List[str]:
    logger.info('run summary')
    
    baseURL = WRKT_URL
    token = WRKT_KEY
    
    r = requests.get(baseURL + '/api/run_summary/', headers={'Authorization':'Bearer ' + token}, verify=True)
    if r.status_code == 200:
        data = r.json()
        # logger.info(data)
        return data
    else:
        return None

def get_tasks() -> List[str]:
    return ['Contacts Tomorrow', 'Put out Garbage']

def get_current_books() -> List[str]:
    logger.info('current books')
    baseURL = WRKT_URL
    token = WRKT_KEY
    
    r = requests.get(baseURL + '/api/books/?status=reading', \
        headers={'Authorization':'Bearer ' + token}, verify=True)
    if r.status_code == 200:
        data = r.json()
        # logger.info(data)
        return data
    else:
        return None

    
