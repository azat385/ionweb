# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Tag

from django.contrib import admin


# http://stackoverflow.com/questions/10543032/how-to-show-all-fields-of-model-in-admin-page
class PageAdminTag(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        #just to modify the looking
        # self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        self.list_display = [field.name for field in model._meta.fields]
        editable = list(self.list_display)
        for r in self.list_display_links:
            editable.remove(r)
        self.list_editable = editable

        #run usual init method
        super(PageAdminTag, self).__init__(model, admin_site)

    list_display_links = ('name',)
    # list_display = ('name', 'description_short', 'description_long', 'comment', 'device_type')
    # list_editable = ('description_short', 'description_long', 'comment', 'device_type')
    # search_fields = ('device_type',)
    list_per_page = 25

admin.site.register(Tag, PageAdminTag)
# Register your models here.
