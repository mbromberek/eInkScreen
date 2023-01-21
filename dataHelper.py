import logging
import time
from datetime import datetime, timezone, timedelta
from zoneinfo import ZoneInfo
from typing import List
from urllib.parse import urlparse

import requests
import vobject
from dateutil import tz
from icalevents.icalevents import events
from icalevents.icalparser import Event
from lxml import etree
from requests.auth import HTTPBasicAuth

import settings

logger = logging.getLogger('app')


def sort_by_date(e: Event):
    return e.start.astimezone()


def get_events(max_number: int) -> List[Event]:
    logger.info("Retrieving calendar infos")
    utc_timezone = tz.tzutc()
    current_timezone = tz.tzlocal()

    try:
        event_list = events(settings.WEBDAV_CALENDAR_URL, fix_apple=settings.WEBDAV_IS_APPLE)
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
        auth = HTTPBasicAuth(settings.CALDAV_CONTACT_USER, settings.CALDAV_CONTACT_PWD)
        baseurl = urlparse(settings.CALDAV_CONTACT_URL).scheme + \
            '://' + urlparse(settings.CALDAV_CONTACT_URL).netloc

        r = requests.request('PROPFIND', settings.CALDAV_CONTACT_URL, auth=auth, headers={
            'content-type': 'text/xml', 'Depth': '1'})
        if r.status_code != 207:
            raise RuntimeError('error in response from %s: %r' %
                               (settings.CALDAV_CONTACT_URL, r))

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
    # return get_weather_darksky(dt)
    return get_weather_weatherkit(dt)


def get_weather_darksky(dt):
    logger.info('Retrieving weather')
    
    baseURL = settings.WEATHER_BASE_URL
    token = settings.WEATHER_KEY
    lat = settings.LATITUDE
    lon = settings.LONGITUDE
    loc = str(lat) + ',' + str(lon)

    darkSkyUrl = baseURL + '/' + token + '/' + str(lat) + ',' + str(lon) + ',' + dt.strftime('%Y-%m-%dT%H:%M:%S')

    w = {}
    r = requests.get(darkSkyUrl)
    weatherData = r.json()
    
    weatherDay = weatherData['daily']['data'][0]
    
    w['maxTemp'] = weatherDay['temperatureMax']
    w['minTemp'] = weatherDay['temperatureMin']
    # w['avgTemp'] = weatherDay['avgtemp_f']
    w['day_summary'] = weatherDay['summary']
    # w['totalPrecip'] = weatherDay['totalprecip_in']
    
    w['sunrise'] = weatherDay['sunriseTime']
    w['sunset'] = weatherDay['sunsetTime']
    w['moonPhase'] = weatherDay['moonPhase']
    
    w['temperature'] = weatherData['currently']['temperature']
    w['curr_feels_like'] = weatherData['currently']['apparentTemperature']
    w['curr_summary'] = weatherData['currently']['summary']
    
    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w

def get_weather_weatherkit(dt) -> List[str]:
    logger.info('Retrieving weather')

    dttm_end = dt + timedelta(seconds=1)
    
    baseURL = settings.WEATHER_BASE_URL
    token = settings.WEATHER_KEY
    lat = settings.LATITUDE
    lon = settings.LONGITUDE
    lang = settings.LANGUAGE
    dataSets = 'currentWeather,forecastDaily'

    url = baseURL + '/' + lang + '/' + lat + '/' + lon + '?dataSets=' + dataSets
    logger.debug(url)

    w = {}
    r = requests.get(url, headers={'Authorization':'Bearer ' + token}, verify=True)
    weatherData = r.json()
    
    logger.debug(weatherData)
    weatherDay = weatherData['forecastDaily']['days'][0]
    w['maxTemp'] = c2F(weatherDay['temperatureMax'])
    w['minTemp'] = c2F(weatherDay['temperatureMin'])
    w['day_summary'] = add_space_in_camelCase(\
        weatherDay['restOfDayForecast']['conditionCode']) 
    
    w['sunrise'] = toLocalTz(\
        datetime.strptime(weatherDay['sunrise'],'%Y-%m-%dT%H:%M:%SZ'))
    w['sunset'] = toLocalTz(\
        datetime.strptime(weatherDay['sunset'],'%Y-%m-%dT%H:%M:%SZ'))
    w['moonPhase'] = add_space_in_camelCase(weatherDay['moonPhase']) 

    weatherCurr = weatherData['currentWeather']
    w['temperature'] = c2F(weatherCurr['temperature'])
    w['curr_feels_like'] = c2F(weatherCurr['temperatureApparent'])
    w['curr_summary'] = add_space_in_camelCase(weatherCurr['conditionCode'])


    w['lat'] = lat
    w['lon'] = lon
    w['date'] = dt

    return w
    
    

def split_text(s, max_width, new_line_start='', max_rows=9999) -> List[str]:
    # logger.info('split_text to width: ' + str(max_width))
    str_split_lst = []
    s_tmp = s
    row_ct = 1
    while True:
        if len(s_tmp) <= max_width:
            str_split_index = -1 #Use all of the remaining string
        else:
            str_split_index = s_tmp[0:max_width].rfind(' ')
        if str_split_index == -1: #this logic does not work if there is a word with over max_width in length
            str_split_lst.append(s_tmp)
            return str_split_lst
        if row_ct == max_rows:
            if str_split_index >=max_width-3:
                str_split_lst.append(s_tmp[0:str_split_index-3]+'...')
            else:
                str_split_lst.append(s_tmp[0:str_split_index]+'...')
            return str_split_lst
        else:
            str_split_lst.append(s_tmp[0:str_split_index])
        s_tmp = new_line_start + s_tmp[str_split_index+1:]
        row_ct +=1

    
def get_run_summary() -> List[str]:
    logger.info('run summary')
    
    baseURL = settings.WRKT_URL
    token = settings.WRKT_KEY
    
    r = requests.get(baseURL + '/api/run_summary/', headers={'Authorization':'Bearer ' + token}, verify=True)
    if r.status_code == 200:
        data = r.json()
        # logger.info(data)
        return data
    else:
        return None

def get_current_books() -> List[str]:
    logger.info('current books')
    baseURL = settings.WRKT_URL
    token = settings.WRKT_KEY
    
    r = requests.get(baseURL + '/api/books/?status=reading', \
        headers={'Authorization':'Bearer ' + token}, verify=True)
    if r.status_code == 200:
        data = r.json()
        # logger.info(data)
        return data
    else:
        return None

def get_tasks() -> List[str]:
    return []

def toUTC(dttm):
    return dttm.astimezone(ZoneInfo(key='UTC'))
def toLocalTz(dttm):
    return dttm.replace(tzinfo=timezone.utc).astimezone(tz=ZoneInfo(key=settings.LOCAL_TZ))


def add_space_in_camelCase(str):
    new_string=""
    for s in str:
        if s.isupper():
            new_string += ' ' + s
        else:
            new_string += s
    return new_string.strip()

def c2F(temp):
    '''
    Convert Celsius to Fahrenheit
    '''
    return (temp * 9/5) +32

def f2C(temp):
    '''
    Convert Fahrenheit to Celsius
    '''
    return (temp -32) * 5/9
