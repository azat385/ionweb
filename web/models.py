# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.utils.encoding import python_2_unicode_compatible

from django.db import models

@python_2_unicode_compatible
class Tag(models.Model):
    name = models.CharField(max_length=50, null=False)
    description_short = models.CharField(max_length=50, null=True, blank=True)
    description_long = models.CharField(max_length=200, null=True, blank=True)
    comment = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.name

    divider = models.FloatField(default=1)
    multiplier = models.FloatField(default=1)
    koef = models.FloatField(default=1)

    group = models.IntegerField(default=0)
    show = models.BooleanField(default=False)

# @python_2_unicode_compatible
class Data(models.Model):
    tag_id = models.ForeignKey(Tag)
    value = models.FloatField()
    stime = models.CharField(max_length=30)



