#!/usr/bin/python3
import calendar
import locale
import logging
import os
import random
import sys
import time
from datetime import datetime
import math

import schedule
from PIL import Image, ImageDraw, ImageFont, ImageOps
from PIL.Image import Image as TImage
from PIL.ImageDraw import ImageDraw as TImageDraw

import lib.epd7in5b_V2 as eInk
from dataHelper import get_events, get_birthdays, get_weather_darksky, \
    get_run_summary, split_text, get_tasks, get_current_books
from displayHelpers import *
from settings import LOCALE, ROTATE_IMAGE

logging.basicConfig(level=os.environ.get("LOGLEVEL", "INFO"),
                    handlers=[logging.FileHandler(filename="info.log", mode='w'),
                    logging.StreamHandler()])
logger = logging.getLogger('app')

CURRENT_DICT = os.path.dirname(os.path.realpath(__file__))
PICTURE_DICT = os.path.join(CURRENT_DICT, 'pictures')
FONT_DICT = os.path.join(CURRENT_DICT, 'fonts')

DEBUG = False

FONT_ROBOTO_DATE = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 175)
FONT_ROBOTO_TEMPERATURE = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 100)
FONT_ROBOTO_H1 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 40)
FONT_ROBOTO_H2 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 30)
FONT_ROBOTO_H3 = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 25)
FONT_ROBOTO_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Roboto-Black.ttf'), 20)
FONT_POPPINS_BOLT_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Poppins-Bold.ttf'), 22)
FONT_POPPINS_P = ImageFont.truetype(
    os.path.join(FONT_DICT, 'Poppins-Regular.ttf'), 20)
LINE_WIDTH = 3


def main():
    logger.info(datetime.now())
    try:
        epd = eInk.EPD()

        if DEBUG:
            logger.info("DEBUG-Mode activated...")

        image_blk = Image.open(os.path.join(
            PICTURE_DICT, "blank-hk.bmp"))
        image_red = Image.open(os.path.join(
            PICTURE_DICT, "blank-hk.bmp"))

        draw_blk = ImageDraw.Draw(image_blk)
        draw_red = ImageDraw.Draw(image_red)

        render_content(draw_blk, image_blk, draw_red,
                       image_red, epd.width, epd.height)
        show_content(epd, image_blk, image_red)
        # clear_content(epd)

    except Exception as e:
        logger.warning(e)
        if not DEBUG:
            logger.info("Trying to module_exit()")
            eInk.epdconfig.module_exit()
        raise e


def render_content(draw_blk: TImageDraw, image_blk: TImage,  draw_red: TImageDraw, image_red: TImage, height: int, width: int):
    locale.setlocale(locale.LC_ALL, LOCALE)

    # PADDING_L = int(width/10)
    print("Width: " + str(width) + " Height: " + str(height))
    PADDING_L = int(10)
    PADDING_TOP = int(height/100)
    # PADDING_TOP = int(height/100)
    now = time.localtime()
    max_days_in_month = calendar.monthrange(now.tm_year, now.tm_mon)[1]
    day_str = time.strftime("%A")
    day_number = now.tm_mday
    month_str = time.strftime("%B")

    # draw_text_centered(str(day_number), (width/2, 0), draw_blk, FONT_ROBOTO_H1)

    # Heading
    '''
    current_height = height/20
    draw_blk.line((int(0), current_height, width, current_height),
                  fill=1, width=LINE_WIDTH)
    '''
    current_height = PADDING_TOP
    draw_blk.text((PADDING_L, current_height), day_str.upper(),
                  font=FONT_ROBOTO_H3, fill=1)
    current_height += get_font_height(FONT_ROBOTO_H3)
    draw_blk.text((PADDING_L, current_height), month_str.upper(),
                  font=FONT_ROBOTO_H3, fill=1)
    '''
    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_H3, day_str.upper()) - PADDING_L/4
    draw_blk.text((tmp_right_aligned, current_height), day_str.upper(),
                  font=FONT_ROBOTO_H3, fill=1)
    '''
    current_height += get_font_height(FONT_ROBOTO_H3)

    # Date
    current_font_height = get_font_height(FONT_ROBOTO_DATE)
    draw_blk.text((PADDING_L, current_height - current_font_height/10),
                  str(day_number), font=FONT_ROBOTO_DATE, fill=1)
    current_height += current_font_height

    # Month-Overview (with day-string)
    '''
    current_height += PADDING_TOP
    day_of_month = str(day_number) + "/" + str(max_days_in_month)
    draw_blk.text((PADDING_L, current_height), day_of_month,
                  font=FONT_ROBOTO_P, fill=1)

    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_P, day_str.upper()) - PADDING_L/4
    draw_blk.text((tmp_right_aligned, current_height), day_str.upper(),
                  font=FONT_ROBOTO_P, fill=1)

    current_height += get_font_height(FONT_ROBOTO_P) + PADDING_TOP
    '''
    # current_height += get_font_height(FONT_ROBOTO_P) *2
    draw_blk.line((int(0), current_height, width, current_height),
                  fill=1, width=LINE_WIDTH)
    current_height += PADDING_TOP
    current_height_top_third = current_height




    # Weather
    # current_height = height/20 + 10
    current_height = PADDING_TOP + 5

    dttm = datetime.now()
    degree_sign = u'\N{DEGREE SIGN}'
    curr_weather = get_weather_darksky(dttm)
    
    curr_temp = str(round(curr_weather['temperature'])) + degree_sign
    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_TEMPERATURE, curr_temp) - PADDING_L
    draw_red.text((tmp_right_aligned, current_height), curr_temp,
                      font=FONT_ROBOTO_TEMPERATURE, fill=1)
    current_height += get_font_height(FONT_ROBOTO_TEMPERATURE)
    
    curr_font = FONT_ROBOTO_P

    sunrise_tm = 'Rise: ' + datetime.fromtimestamp(curr_weather['sunrise']).strftime('%H:%M')
    sunset_tm = 'Set: ' + datetime.fromtimestamp(curr_weather['sunset']).strftime('%H:%M')

    weather_temp = str(round(curr_weather['maxTemp'])) + degree_sign + ' / ' + str(round(curr_weather['minTemp'])) + degree_sign
    tmp_right_aligned = width - \
        get_font_width(curr_font, weather_temp) - PADDING_L
    draw_blk.text((tmp_right_aligned, current_height), weather_temp,
                      font=curr_font, fill=1)

    current_height += get_font_height(curr_font)
    max_char = 30
    max_sum_rows = 3
    
    weather_sum_lst = split_text(curr_weather['summary'], max_char)
    for index, weather_sum in enumerate(weather_sum_lst):
        if index >= max_sum_rows:
            weather_sum = '...' #If hit max rows then display a row with just ... and exit loop
        tmp_right_aligned = width - \
            get_font_width(FONT_ROBOTO_P, weather_sum ) - PADDING_L
        draw_blk.text((tmp_right_aligned, current_height), weather_sum,
                      font=curr_font, fill=1)
        current_height += get_font_height(curr_font)
        if index >= max_sum_rows:
            break


    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_P, sunrise_tm + ' / ' + sunset_tm) - PADDING_L
    draw_blk.text((tmp_right_aligned, current_height), 
                  sunrise_tm + ' / ' + sunset_tm,
                  font=curr_font, fill=1)
    current_height += get_font_height(curr_font)

    tmp_right_aligned = (width - PADDING_L/4) /2
    current_height += PADDING_TOP
    '''
    draw_blk.line((PADDING_L+width/2, current_height, width - PADDING_L/2, current_height),
                  fill=1, width=LINE_WIDTH)
    '''

    '''
    tmp_right_aligned = width - \
        get_font_width(FONT_ROBOTO_P, sunset_tm) - PADDING_L/4
    draw_blk.text((tmp_right_aligned, current_height), sunset_tm,
                  font=FONT_ROBOTO_P, fill=1)
    '''

    # Month-Tally-Overview
    '''
    current_height += PADDING_TOP
    tally_height = height/40
    tally_width = LINE_WIDTH + width/120  # width + padding
    available_width = width - PADDING_L
    tally_number = int(available_width / tally_width *
                       (day_number / max_days_in_month))
    x_position = PADDING_L + LINE_WIDTH/2
    for i in range(0, tally_number):
        draw_blk.line((x_position, current_height, x_position,
                      current_height + tally_height), fill=1, width=LINE_WIDTH)
        x_position += tally_width
    current_height += tally_height
    '''
    
    # current_height += height/40
    current_height = current_height_top_third
    
    # Tasks
    curr_font = FONT_ROBOTO_P
    tasks_lst = get_tasks()
    current_height = display_rows(tasks_lst, curr_font, draw_blk, PADDING_L, current_height, 4)
    if len(tasks_lst) >0:
        current_height += PADDING_TOP

    
    # Calendar    
    event_list = get_events(6)

    last_event_day = datetime.now().date()
    for event in event_list:
        # Draw new day
        if last_event_day != event.start.date():
            # current_height += height/40
            last_event_day = event.start.date()
            # day_string = "{} {}".format(last_event_day.day,
            #                               last_event_day.strftime("%a"))
            day_string = last_event_day.strftime("%a %d")
            draw_blk.text((PADDING_L, current_height), day_string,
                          font=FONT_ROBOTO_P, fill=1)
            current_height += get_font_height(FONT_ROBOTO_P)

        # Draw event
        event_text = ""
        if event.all_day:
            draw_blk.text((PADDING_L, current_height), "- : -",
                          font=FONT_POPPINS_P, fill=1)
        else:
            draw_blk.text((PADDING_L, current_height), event.start.strftime("%H:%M"),
                          font=FONT_POPPINS_P, fill=1)

        summmary_padding = 60
        draw_blk.text((PADDING_L + summmary_padding, current_height), event.summary,
                      font=FONT_POPPINS_P, fill=1)
        current_height += get_font_height(FONT_POPPINS_P) * 1.1

    # Bottom third
    
    # Run Summary
    #current_height = int(height*0.73)
    current_height = int(height*0.66)
    draw_blk.line((int(0), current_height, width, current_height),
                  fill=1, width=LINE_WIDTH)
    current_height += PADDING_TOP
    
    draw_blk.text((PADDING_L, current_height), 'Running Mileage:',
                  font=FONT_ROBOTO_H3, fill=1)
    current_height += get_font_height(FONT_ROBOTO_H3)
    run_sum = get_run_summary()
    run_sum_font = FONT_ROBOTO_P
    # curr_week_dist = str(round(float(run_sum['Current Week']['tot_dist']))) + 'mi'
    curr_week_dur = run_sum['Current Week']['duration_str']
    # curr_month_dist = str(run_sum['Current Month']['tot_dist']) + 'mi'
    draw_blk.text((PADDING_L, current_height), 'Week:',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+100, current_height), 
                  str(round(float(run_sum['Current Week']['tot_dist']))) + 'mi',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+250, current_height), 
                  run_sum['Current Week']['duration_str'],
                  font=run_sum_font, fill=1)
    # logger.info(str(get_font_width(run_sum_font, 'Past 365: ' ) ))
    current_height += get_font_height(run_sum_font)
    draw_blk.text((PADDING_L, current_height), 'Month:',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+100, current_height), 
                  str(round(float(run_sum['Current Month']['tot_dist']))) + 'mi',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+250, current_height), 
                  run_sum['Current Month']['duration_str'],
                  font=run_sum_font, fill=1)
    current_height += get_font_height(run_sum_font)

    draw_blk.text((PADDING_L, current_height), 'Year:',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+100, current_height), 
                  str(round(float(run_sum['Current Year']['tot_dist']))) + 'mi',
                  font=run_sum_font, fill=1)
    draw_blk.text((PADDING_L+250, current_height), 
                  run_sum['Current Year']['duration_str'],
                  font=run_sum_font, fill=1)
    current_height += get_font_height(run_sum_font) *2
    
    # Current Book
    draw_blk.text((PADDING_L, current_height), 'Current Books:',
                  font=FONT_ROBOTO_H3, fill=1)
    current_height += get_font_height(FONT_ROBOTO_H3)
    curr_book_lst = get_current_books()
    book_font = FONT_ROBOTO_P
    max_char = 50
    max_sum_rows = 2
    for book in curr_book_lst:
        book_author =  '   by ' + book['author']
        book_title_lst = split_text(book['title'], max_char, new_line_start='     ')
        current_height = display_rows(book_title_lst, book_font, draw_blk, PADDING_L, current_height, 2)
        book_author_lst = split_text(book_author, max_char, new_line_start='       ')
        current_height = display_rows(book_author_lst, book_font, draw_blk, PADDING_L, current_height, 2)

    '''
    # Portal-Icons
    y = PADDING_L
    # bithday_persons = get_birthdays()
    bithday_persons =[]
    draw_cake = (len(bithday_persons) > 0)
    max_image_height = 0
    for image in get_portal_images(draw_cake, bool(random.getrandbits(1)), bool(random.getrandbits(1)), bool(random.getrandbits(1))):
        image_blk.paste(image, (y, current_height))
        image_width, image_height = image.size
        y += image_width + PADDING_TOP
        max_image_height = image_height if (
            image_height > max_image_height) else max_image_height
    current_height += max_image_height + PADDING_TOP
    '''
    
    # Draw name of birthday-person
    '''
    if draw_cake:
        bithday_person_string = ", ".join(bithday_persons)
        draw_red.text((PADDING_L, current_height), bithday_person_string,
                      font=FONT_ROBOTO_P, fill=1)
        current_height += get_font_height(FONT_ROBOTO_P)
    '''
    
     
def display_rows(row_lst, font_det, draw_color, padding, strt_height, max_rows=999):
    current_height = strt_height
    for index, row_det in enumerate(row_lst):
        if index >= max_rows:
            row_det = '...' #If hit max rows then display a row with just ... and exit loop
        draw_color.text((padding, current_height), row_det,
            font=font_det, fill=1)
        current_height += get_font_height(font_det)
        if index >= max_rows:
            break
    
    
    return current_height
    
    


def show_content(epd: eInk.EPD, image_blk: TImage, image_red: TImage):
    logger.info("Exporting finial images")
    image_blk.save("EXPORT-black.bmp")
    image_red.save("EXPORT-red.bmp")
    if ROTATE_IMAGE:
        image_blk = image_blk.rotate(180)
        image_red = image_red.rotate(180)
    if not DEBUG:
        init_display(epd)
        logger.info("Writing on display")
        epd.display(epd.getbuffer(image_blk), epd.getbuffer(image_red))
        set_sleep(epd)


def clear_content(epd: eInk.EPD):
    if DEBUG:
        logger.warning("Clear has no effect while debugging")
    else:
        init_display(epd)
        clear_display(epd)
        set_sleep(epd)


if __name__ == '__main__':
    main()
