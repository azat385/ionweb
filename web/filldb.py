# -*- coding: utf-8 -*-
import os
# import sys
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ionweb.settings')
django.setup()


def recalc_tag_koef():
    from web.models import Tag_group
    all_tag = Tag_group.objects.all()

    for t in all_tag:
        t.koef = t.multiplier/t.divider
        t.save()

if __name__ == '__main__':
    recalc_tag_koef()

