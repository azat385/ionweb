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

from plotly.offline import plot
from plotly.graph_objs import Bar, Scatter


is_ch = u'checked'
not_ch = ''
html_None = 'Нет данных'


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


def get_tag_list(checked):
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
    return Tag.objects.filter(name__in=tag_name_list).all()


def get_inst_tag_list(checked):
    pos_selected = checked['tag_value'].index(is_ch)
    gr_name = 'power'
    if pos_selected == 0:
        gr_name = 'current'
    if pos_selected == 1:
        gr_name = 'voltage'
    if pos_selected == 2:
        gr_name = 'power'
    return Tag.objects.filter(group__name=gr_name).all()


def get_data_records(checked, date_value_str_list, tag_list, lookup_table):
    records = lookup_table.objects.filter(tag__in=tag_list, ts__range=date_value_str_list).order_by('ts').all()
    l = list(records.values())
    if len(l) < 1 :
        return None
    else:
        print 'checked: koef:',checked['koef']
        if checked['koef']:
            t = tag_list[0]
            gr = t.group
            k = gr.koef
        else:
            k = 1
        print "k =",k
        df = pd.DataFrame(l)
        # df.loc[:, 'value'] = df['value'] * k
        df.loc[:, 'value'] *= k
        df.loc[:, 'ts'] = df['ts'].dt.tz_convert('Europe/Moscow')
        df.loc[:, 'ts'] = df['ts'].dt.strftime('%Y-%m-%d %H:%M')
        return df


def table_header(id_list, checked):
    result = []
    id_list = [int(i) for i in id_list]
    tt = Tag.objects.filter(id__in=id_list).all()
    for t in tt:
        if checked['koef']:
            u = t.group.unit_koef
        else:
            u = t.group.unit
        result.append("{}, {}".format(t.name, u))
    return result


def table(request):
    checked, date_value = selector_handler(request.GET)
    tag_list = get_tag_list(checked)
    if checked['time_type'].index(is_ch)==1:
        lookup_table = Daily
    else:
        lookup_table = Hourly
    df = get_data_records(checked=checked, date_value_str_list=date_value,
                          tag_list=tag_list, lookup_table=lookup_table)

    if df is None:
        html_content = html_None
    else:
        df_pivot = df.pivot_table(index="ts", columns="tag_id", values="value",
                                  aggfunc='sum', margins=True, margins_name='Sum')
        col_names = df_pivot.columns.tolist()[:-1]
        # print col_names
        # df_pivot.columns = [Tag.objects.filter(id=int(c)).all()[0].name for c in col_names]+['Сумма']
        # BETTER WAY: send tag list to template!!!!
        df_pivot.columns = table_header(col_names, checked) + ['Сумма']
        print df_pivot.columns
        html_content = df_pivot.to_html()

    return render(request, 'web/table.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': html_content,
    })


def bar_graph(request):
    checked, date_value = selector_handler(request.GET)
    tag_list = get_tag_list(checked)
    if checked['time_type'].index(is_ch)==1:
        lookup_table = Daily
    else:
        lookup_table = Hourly
    df = get_data_records(checked=checked, date_value_str_list=date_value,
                          tag_list=tag_list, lookup_table=lookup_table)
    if df is None:
        html_content = html_None
    else:
        tag_id_list = df.tag_id.unique()
        tag_id_list = tag_id_list.tolist()
        tag_id_list = [int(i) for i in tag_id_list]
        traces = []
        for t_id in tag_id_list:
            ts_value = df[df['tag_id'] == t_id][['ts', 'value']]
            data_XY = ts_value.values.T.tolist()
            t = Tag.objects.filter(id=t_id).all()[0]
            t_name = t.name
            tr = Bar(name=t_name,
                     y=data_XY[1],
                     x=data_XY[0],
                     )
            traces.append(tr)
        data_plot = {
            'data': traces,
            'layout': {
                'barmode': '',
                'xaxis': {'title': 'Время'},
                'yaxis': {'title': 'Энергия [Вт*ч]'},
                'title': 'График потребления',
            }}

        if checked['graph_bar']:
            data_plot['layout']['barmode'] = 'stack'

        if checked['koef']:
            data_plot['layout']['yaxis'] = {'title': 'Энергия [кВт*ч]'}

        html_content = plot(data_plot, output_type='div', auto_open=False,
                            show_link=False, include_plotlyjs=True)
    return render(request, 'web/table.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': html_content,
    })


def inst_graph(request):
    checked, date_value = selector_handler(request.GET)
    tag_list = get_inst_tag_list(checked)
    df = get_data_records(checked=checked, date_value_str_list=date_value,
                          tag_list=tag_list, lookup_table=Data)
    if df is None:
        html_content = html_None
    else:
        tag_id_list = df.tag_id.unique()
        tag_id_list = tag_id_list.tolist()
        tag_id_list = [int(i) for i in tag_id_list]
        traces = []
        for t_id in tag_id_list:
            ts_value = df[df['tag_id'] == t_id][['ts', 'value']]
            data_XY = ts_value.values.T.tolist()
            t = Tag.objects.filter(id=t_id).all()[0]
            t_name = t.name
            tr = Scatter(name=t_name,
                         y=data_XY[1],
                         x=data_XY[0],
                         # mode = 'lines+markers',
                         # connectgaps=False,
                         )
            traces.append(tr)
        data_plot = {
            'data': traces,
            'layout': {
                'barmode': '',
                'xaxis': {'title': 'Время',
                          # 'range': ['2017-05-18', '2017-05-19'],
                          },
                'yaxis': {'title': 'Энергия [Вт*ч]'},
                'title': 'График потребления',
                'height': 720,
            }}

        if checked['graph_bar']:
            data_plot['layout']['barmode'] = 'stack'

        html_content = plot(data_plot, output_type='div', auto_open=False,
                            show_link=False, include_plotlyjs=True)
    return render(request, 'web/inst.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': html_content,
    })