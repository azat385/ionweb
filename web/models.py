# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models


@python_2_unicode_compatible
class Tag_group(models.Model):
    name = models.CharField(max_length=50, null=False)
    description_short = models.CharField(max_length=50, null=True, blank=True)
    description_long = models.CharField(max_length=200, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    divider = models.FloatField(default=1)
    multiplier = models.FloatField(default=1)
    koef = models.FloatField(default=1)
    unit = models.CharField(max_length=10, null=True, blank=True)
    unit_koef = models.CharField(max_length=10, null=True, blank=True)


@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=50, null=False)
    description_short = models.CharField(max_length=50, null=True, blank=True)
    description_long = models.CharField(max_length=200, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name
    group = models.ForeignKey(Tag_group)
    # default=lambda: Tag_group.objects.get(id=1))
    show = models.BooleanField(default=False)
    increasing = models.BooleanField(default=False)
    variable = models.BooleanField(default=False)


# @python_2_unicode_compatible
class Data(models.Model):
    tag = models.ForeignKey(Tag)
    value = models.FloatField()
    ts = models.DateTimeField()

    def __str__(self):
        return "Data: id={} tag={} value={} ts={}".format(
            self.id, self.tag, self.value, self.ts)


@python_2_unicode_compatible
class Hourly(models.Model):
    tag = models.ForeignKey(Tag)
    start_data = models.ForeignKey(Data, null=True, related_name='Hourly.start_data+')
    end_data = models.ForeignKey(Data, null=True, related_name='Hourly.end_data+')
    value = models.FloatField()
    ts = models.DateTimeField()

    def __str__(self):
        return "Hourly: id={} tag={} value={} ts={} start_d={} end_d={}".format(
            self.id, self.tag, self.value, self.ts, self.start_data, self.end_data)


@python_2_unicode_compatible
class Daily(models.Model):
    tag = models.ForeignKey(Tag)
    start_data = models.ForeignKey(Data, null=True, related_name='Daily.start_data+')
    end_data = models.ForeignKey(Data, null=True, related_name='Daily.end_data+')
    value = models.FloatField()
    ts = models.DateTimeField()

    def __str__(self):
        return "Daily: id={} tag={} value={} ts={} start_d={} end_d={}".format(
            self.id, self.tag, self.value, self.ts, self.start_data, self.end_data)


# from django.contrib.contenttypes.models import ContentType
# from django.contrib.contenttypes.fields import GenericForeignKey


@python_2_unicode_compatible
class Config(models.Model):
    name = models.CharField(max_length=100)
    value = models.CharField(max_length=500)
    value_type = models.CharField(max_length=1, choices=(('s','string'),('i','integer'),('b','boolean')))

    # content_type = models.ForeignKey(ContentType)
    # object_id = models.PositiveIntegerField()
    # content_object = GenericForeignKey()

    def actual_value(self):
        types = {
            's': str,
            'i': int,
            'b': (lambda v: v.lower().startswith('t') or v.startswith('1'))
        }
        return types[self.value_type](self.value)

    def __str__(self):
        return "Setting: id={} name={} value={} act_value={}".format(
            self.id, self.name, self.value, self.actual_value())