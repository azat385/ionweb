# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.shortcuts import render
from django.http import HttpResponse, Http404
from django.shortcuts import render, get_object_or_404
from django.template.loader import render_to_string
from django.contrib.auth.decorators import login_required

from .models import Data, Tag, Tag_group, Hourly, Daily, Config

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


def date_range_check(date_value, days_diff_min=1, days_diff_max=40):
    date_value = [dateutil.parser.parse(d) for d in date_value]
    #min
    if (date_value[1] - date_value[0]) < timedelta(days=days_diff_min):
        date_value[0] = date_value[1] - timedelta(days=days_diff_min)
    #max
    if (date_value[1] - date_value[0]) > timedelta(days=days_diff_max):
        date_value[0] = date_value[1] - timedelta(days=days_diff_max)

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
    # date_value = date_range_check(date_value)
    return checked, date_value


from django_tables2 import RequestConfig
from .tables import DataTable


def test_view(request):
    data = Data.objects.filter(tag__show=True).order_by('tag', '-ts').distinct('tag')
    table_data = DataTable(data)
    RequestConfig(request).configure(table_data)
    return render(request, 'web/test.html', {'last_data': table_data})


def index(request):
    # tags = Tag.objects.filter(show=True).order_by('id')
    # data = []
    # for t in tags:
    #     data.append(Data.objects.filter(tag=t).last())
    latest_id = Data.objects.latest('id').id
    data = Data.objects.filter(tag__show=True, id__gt=latest_id-100).order_by('tag_id', '-ts').distinct('tag_id')

    labels = [
        "Ts_phaseA",
        "Ts_phaseB",
        "Ts_phaseC",
    ]

    fig = {
        "data": [
            {
                "values": [16, 15, 12, ],
                "labels": labels,
                "domain": {"y": [0, .48]},
                "name": "кВт",
                "hoverinfo": "label+name",
                "hole": .4,
                "type": "pie"
            },
            {
                "values": [27, 11, 25, ],
                "labels": labels,
                "domain": {"y": [.52, 1]},
                "name": "кВт",
                "hoverinfo": "label+name",
                "hole": .4,
                "type": "pie"
            }],
        "layout": {
            "title": "Потребление энергии",
            "annotations": [
                {
                    "font": {
                        "size": 14
                    },
                    "showarrow": False,
                    "text": "Вчера",
                    "x": 0.5,
                    "y": 0.2
                },
                {
                    "font": {
                        "size": 14
                    },
                    "showarrow": False,
                    "text": "Сегодня",
                    "x": 0.5,
                    "y": 0.8
                }
            ]
        }
    }
    pie_plot = plot(fig, output_type='div', auto_open=False,
                        show_link=False, include_plotlyjs=True)

    return render(request, 'web/intro.html', {'last_data': data, 'pie_plot': pie_plot})


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


def get_data_records(checked, date_value_str_list, tag_list, lookup_table, minus_minutes=0):
    records = lookup_table.objects.filter(tag__in=tag_list, ts__range=date_value_str_list).order_by('ts').all()
    l = list(records.values())
    if len(l) < 1:
        return None
    else:
        # print 'checked: koef:', checked['koef']
        if checked['koef']:
            t = tag_list[0]
            gr = t.group
            k = gr.koef
        else:
            k = 1
        # print "k =",k
        df = pd.DataFrame(l)
        # df.loc[:, 'value'] = df['value'] * k
        if k != 1:
            df.loc[:, 'value'] *= k
        if minus_minutes > 0:
            df.loc[:, 'ts'] -= timedelta(minutes=minus_minutes)
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


@login_required()
def table(request):
    checked, date_value = selector_handler(request.GET)
    tag_list = get_tag_list(checked)
    if checked['time_type'].index(is_ch) == 1:
        lookup_table = Daily
        date_value = date_range_check(date_value, 2, 99)
        ts_offset_hour = Config.objects.filter(name='ts_offset_hour')
        if ts_offset_hour.exists():
            ts_offset = ts_offset_hour.get().actual_value()
        else:
            ts_offset = 0
    else:
        lookup_table = Hourly
        date_value = date_range_check(date_value, 1, 7)
        ts_offset = 0
    df = get_data_records(checked=checked, date_value_str_list=date_value,
                          tag_list=tag_list, lookup_table=lookup_table,
                          minus_minutes=ts_offset,
                          )

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
        html_content = df_pivot.to_html(border=1, justify='center')
        html_content = html_content.replace('dataframe', 'table table-hover')

    return render(request, 'web/table.html', {
        'checked': checked,
        'date_value': date_value,
        'html_content': html_content,
        'show_well': [1, 1, 1, 0, 1],
    })


@login_required()
def bar_graph(request):
    checked, date_value = selector_handler(request.GET)
    tag_list = get_tag_list(checked)
    if checked['time_type'].index(is_ch) == 1:
        lookup_table = Daily
        date_value = date_range_check(date_value, 2, 99)
        ts_offset_hour = Config.objects.filter(name='ts_offset_hour')
        if ts_offset_hour.exists():
            ts_offset = ts_offset_hour.get().actual_value()
        else:
            ts_offset = 0
    else:
        lookup_table = Hourly
        date_value = date_range_check(date_value, 1, 7)
        ts_offset = 0
    df = get_data_records(checked=checked, date_value_str_list=date_value,
                          tag_list=tag_list, lookup_table=lookup_table,
                          minus_minutes=ts_offset,
                          )
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
        'show_well': [1, 1, 1, 1, 1],
    })


@login_required()
def inst_graph(request):
    checked, date_value = selector_handler(request.GET)
    date_value = date_range_check(date_value, 1, 3)
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
        'show_well': [1, 1, 0, 0, 1],
    })


from forms import SelectorForm, PeriodFilter

def form_test_view(request):
    # form = PeriodFilter(initial={'range': (date.today(), date.today())})
    # (from_date, to_date) = form.cleaned_data['range']
    return render(request, 'web/base_form_test.html')

def form_view(request):
    # the_initails = {'your_name': u'Ваше Имя', 'time_type': 2, 'int_value': 66}
    if len(request.GET):
        selector_form = SelectorForm(data=request.GET)
    else:
        # selector_form = SelectorForm(initial=the_initails)
        selector_form = SelectorForm()
    selector_form.is_valid()
    return render(request, 'web/base_form.html', {'form': selector_form})




# from django.contrib.auth import logout
#
#
# def logout_view(request):
#     logout(request)