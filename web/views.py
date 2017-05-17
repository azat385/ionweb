# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from .models import Data, Tag, Tag_group, Hourly, Daily

import dateutil.parser
from datetime import date, timedelta
import pandas as pd

# from plotly.offline import plot
# from plotly.graph_objs import Bar, Scatter


is_ch = u'checked'
not_ch = ''


def make_ch_list(list_ch, list_pos):
    l_ch = list(list_ch)
    for p in list_pos:
        l_ch[int(p)-1]=is_ch
    return l_ch


def make_ch(list_ch, pos):
    pos -= 1
    pos = 0 if (pos < 0 or len(list_ch) <= pos) else pos
    result = list(list_ch)
    result[pos] = is_ch
    return result


def date_range_check(date_value, days_diff=1):
    date_value = [dateutil.parser.parse(d) for d in date_value]
    if date_value[0] >= date_value[1]:
        date_value[0] = date_value[1] - timedelta(days=days_diff)
    return [t.date().isoformat() for t in date_value]


def selector_handler(params):
    print params
    t_t = int(params.get('time_type', 1))
    checked = {
        # 'tag_value': make_ch([not_ch] * 3, d_t),
        'time_type': make_ch([not_ch] * 2, t_t),
        'graph_bar': is_ch if params.get('graph_bar', not_ch) else not_ch,
        'koef': is_ch if params.get('koef', not_ch) else not_ch,

    }
    d_t = params.getlist('tag_value', [u'1'])
    # if isinstance(d_t, (list, tuple)):
    if len(d_t)>1:
        checked['tag_value'] = make_ch_list([not_ch] * 3, d_t)
    else:
        checked['tag_value'] = make_ch([not_ch] * 3, int(d_t[0]))

    date_value = [params.get('day_begin', date.today().isoformat()),
                  params.get('day_end', (date.today() + timedelta(days=1)).isoformat()),
                  ]
    date_value = date_range_check(date_value)
    return checked, date_value


def index(request):
    return render(request, 'web/base.html', {})


def get_data_records(checked, date_value_str_list):
    # date_value = [dateutil.parser.parse(d) for d in date_value_str_list]
    tag_name_list = []
    indices = [i for i, x in enumerate(checked['tag_value']) if x == is_ch]
    if 0 in indices:
        tag_name_list.append('Ts_active')
    if 1 in indices:
        tag_name_list.append('Ts_reactive')
    if 2 in indices:
        tag_name_list.append('Ts_phaseA')
        tag_name_list.append('Ts_phaseB')
        tag_name_list.append('Ts_phaseC')
    # print tag_name_list
    tag_list = Tag.objects.filter(name__in=tag_name_list).all()
    # print tag_list
    if checked['time_type'].index(is_ch)==1:
        lookup_table = Daily
    else:
        lookup_table = Hourly
    return lookup_table.objects.filter(tag__in=tag_list, ts__range=date_value_str_list).all()

def table(request):
    checked, date_value = selector_handler(request.GET)
    records = get_data_records(checked=checked, date_value_str_list=date_value)
    df = pd.DataFrame(list(records.values()))
    df_pivot = df.pivot_table(index="ts", columns="tag_id", values="value",
                              aggfunc='sum', margins=True, margins_name='Sum')
    col_names = df_pivot.columns.tolist()[:-1]
    print col_names
    df_pivot.columns = [Tag.objects.filter(id=int(c)).all()[0].name for c in col_names]+['Сумма']
    print df_pivot.columns

    return render(request, 'web/table.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': df_pivot.to_html()
    })


def bar_graph(request):
    checked, date_value = selector_handler(request.GET)
    return render(request, 'web/table.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': None,
    })


def inst_graph(request):
    checked, date_value = selector_handler(request.GET)
    return render(request, 'web/inst.html', {
        'checked': checked,
        'date_value': date_value,
    })