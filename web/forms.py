# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime, date
from django import forms

from django_bootstrap3_daterangepicker.fields import DateRangeField
from django_bootstrap3_daterangepicker.widgets import DateRangeWidget, common_dates


class SelectorForm(forms.Form):
    your_name = forms.CharField(label=u'Ваше имя',
                                max_length=100,
                                required=False,
                                initial=u'User'
                                )
    time_type = forms.ChoiceField(choices=((1, u'Часовой'), (2, u'Суточный')),
                                  label=u"Тип",
                                  widget=forms.RadioSelect,
                                  required=True,
                                  initial= 2,
                                  )
    int_value = forms.IntegerField(label=u'Число', required=False)

    graph_bar = forms.BooleanField(label=u'Графики в столбец',
                                   initial=True,
                                   required=False,
                                   )

    tag_value = forms.MultipleChoiceField(label=u'Данные',
                                          choices=(
                                              (1, u'Активная энергия'),
                                              (2, u'Реактивная энергия'),
                                              (3, u'Энергия по фазно'),
                                            ),
                                          required=True,
                                          widget=forms.CheckboxSelectMultiple,
                                          initial=(1,)
                                          )

    name = forms.CharField(required=False, initial=u'Hello world')

    day_begin = forms.DateField(label=u'Начальная дата',
                                required=True,
                                # widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                widget=forms.DateInput(attrs={'type': 'date'}),
                                initial=date.today().isoformat(),
                                )

    day_end = forms.DateField(label=u'Конечная дата',
                                required=True,
                                # widget=forms.widgets.DateInput(attrs={'type': 'date'}),
                                widget=forms.DateInput(attrs={'type': 'date'}),
                                initial=date.today().isoformat(),
                                )

    # def clean_name(self):
    #     if not self['name'].html_name in self.data:
    #         return self.fields['name'].initial
    #     return self.cleaned_data['name']

    # def clean_name(self):
    #     name = self.cleaned_data['name']
    #     if name is None:
    #         return self.fields['name'].initial
    #     return name

class PeriodFilter(forms.Form):
    range = DateRangeField(widget=DateRangeWidget(picker_options={
        'ranges': common_dates()
    }))