# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2017-05-17 09:13
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('web', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='tag_group',
            name='unit_koef',
            field=models.CharField(blank=True, max_length=10, null=True),
        ),
    ]
