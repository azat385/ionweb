# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-30 12:07
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0004_auto_20170530_1419'),
    ]

    operations = [
        migrations.RenameModel("Setting", "Config")
    ]
