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


def mer230_base_tags():
    from web.models import Tag
    tt_dict = [
        {'pos': 1, 'name': 'Ts_active',},
        {'pos': 2, 'name': 'Ts_reactive',},
        {'pos': 3, 'name': 'T1_active',},
        {'pos': 4, 'name': 'T1_reactive',},
        {'pos': 5, 'name': 'T2_active',},
        {'pos': 6, 'name': 'T3_reactive',},
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

if __name__ == '__main__':
    # recalc_tag_koef()
    mer230_base_tags()
