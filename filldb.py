# -*- coding: utf-8 -*-

import logging
from logging.handlers import RotatingFileHandler

# format the log entries
formatter = logging.Formatter('%(asctime)s %(name)s %(levelname)s %(message)s')

handler = RotatingFileHandler('filldb.log',
                              mode='a',
                              maxBytes=20*1024*1024,
                              backupCount=5,
                              encoding=None,
                              delay=0)
handler.setFormatter(formatter)
logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.DEBUG)

import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ionweb.settings')
# os.environ['DJANGO_SETTINGS_MODULE'] = 'ionweb.settings'
django.setup()


from web.models import Tag, Tag_group, Hourly, Daily, Data
from datetime import datetime

def recalc_tag_koef():
    all_tag = Tag_group.objects.all()

    for t in all_tag:
        t.koef = t.multiplier/t.divider
        t.save()


def mer230_base_tags():
    tt_dict = [
        {'pos': 1, 'name': 'Ts_active',},
        {'pos': 2, 'name': 'Ts_reactive',},
        {'pos': 3, 'name': 'T1_active',},
        {'pos': 4, 'name': 'T1_reactive',},
        {'pos': 5, 'name': 'T2_active',},
        {'pos': 6, 'name': 'T2_reactive',},
        {'pos': 7, 'name': 'Ts_phaseA',},
        {'pos': 8, 'name': 'Ts_phaseB',},
        {'pos': 9, 'name': 'Ts_phaseC',},
        {'pos': 10, 'name': 'T1_phaseA',},
        {'pos': 11, 'name': 'T1_phaseB',},
        {'pos': 12, 'name': 'T1_phaseC',},
        {'pos': 13, 'name': 'T2_phaseA',},
        {'pos': 14, 'name': 'T2_phaseB',},
        {'pos': 15, 'name': 'T2_phaseC',},
        {'pos': 16, 'name': 'Ps/100',},
        {'pos': 17, 'name': 'Pa/100',},
        {'pos': 18, 'name': 'Pb/100',},
        {'pos': 19, 'name': 'Pc/100',},
        {'pos': 20, 'name': 'Ua/100',},
        {'pos': 21, 'name': 'Ub/100',},
        {'pos': 22, 'name': 'Uc/100',},
        {'pos': 23, 'name': 'Ia/1000',},
        {'pos': 24, 'name': 'Ib/1000',},
        {'pos': 25, 'name': 'Ic/1000',},
        {'pos': 26, 'name': 'Hz/100',},
    ]

    for t in tt_dict:
        t = Tag(name=t['name'],
                group_id=1)
        t.save()


def data_sorted_records_m_h(current_tag):
    last_record_hourly = Hourly.objects.filter(tag=current_tag).order_by('-id').first()
    if last_record_hourly is None:
        last_record_hourly_stime = datetime(2017, 1, 1, tzinfo=None)
        logger.debug("No last date in hourly table. The default is used")
    else:
        last_record_hourly_stime = last_record_hourly.ts
    data_records = Data.objects.filter(ts__gt=last_record_hourly_stime).filter(
                                       tag=current_tag).filter(ts__minute__lt=2).all()
    prev_hour = 66
    tag_list = []
    for r in data_records:
        hour = r.ts.hour
        if prev_hour != hour:
            tag_list.append(r)
            prev_hour = hour
    return tag_list


def fill_hourly():
    logger.debug('Start adding hourly table....')
    tags = Tag.objects.filter(increasing=True).all()
    added_rows = 0
    for tag in tags:
        data_records = data_sorted_records_m_h(current_tag=tag)
        if data_records is None:
            logger.debug("Tag={} data is empty".format(tag))
            continue
        if len(data_records)<2:
            logger.debug("Tag={} data record less then 2!!! not enough to calc difference".format(tag))
            continue
        for i, d in enumerate(data_records):
            if i == 0:
                d_prev = d
                continue
            new_hourly = Hourly(tag=tag,
                                start_data=d_prev,
                                end_data=d,
                                value=d.value-d_prev.value,
                                ts=d.ts.replace(minute=0, second=0, microsecond=0))
            logger.debug(new_hourly)
            new_hourly.save()
            added_rows += 1
            d_prev = d
    logger.info('Totaly added rows: {}'.format(added_rows))
    logger.debug('End adding hourly table...')


def hourly_sorted_records_m_h(current_tag):
    last_record_daily = Daily.objects.filter(tag=current_tag).order_by('-id').first()
    if last_record_daily is None:
        last_record_hourly_stime = datetime(2017, 1, 1, tzinfo=None)
        logger.debug("No last date in hourly table. The default is used")
    else:
        last_record_hourly_stime = last_record_daily.ts
    hourly_records = Hourly.objects.filter(ts__gte=last_record_hourly_stime).filter(
                                       tag=current_tag).filter(ts__hour=0).all()
    return hourly_records


def fill_daily():
    logger.debug('Start adding daily table....')
    tags = Tag.objects.filter(increasing=True).all()
    added_rows = 0
    for tag in tags:
        data_records = hourly_sorted_records_m_h(current_tag=tag)
        if data_records is None:
            logger.debug("Tag={} hourly is empty".format(tag))
            continue
        if len(data_records)<2:
            logger.debug("Tag={} hourly record less then 2!!! not enough to calc difference".format(tag))
            continue
        for i, d in enumerate(data_records):
            if i == 0:
                d_prev = d
                continue
            new_daily = Daily(tag=tag,
                              start_data=d_prev.start_data,
                              end_data=d.start_data,
                              value=d.start_data.value-d_prev.start_data.value,
                              ts=d.ts.replace(minute=0, second=0, microsecond=0))
            logger.debug(new_daily)
            new_daily.save()
            added_rows += 1
            d_prev = d
    logger.info('Totaly added rows: {}'.format(added_rows))
    logger.debug('End adding daily table...')


if __name__ == '__main__':
    fill_hourly()
    # fill_daily()
    # recalc_tag_koef()
    # mer230_base_tags()
