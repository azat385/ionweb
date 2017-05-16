# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import Tag, Tag_group, Hourly

from django.contrib import admin


# http://stackoverflow.com/questions/10543032/how-to-show-all-fields-of-model-in-admin-page
class PageAdminName(admin.ModelAdmin):
    def __init__(self, model, admin_site):
        #just to modify the looking
        # self.list_display = [field.name for field in model._meta.fields if field.name != "id"]
        self.list_display = [field.name for field in model._meta.fields]
        editable = list(self.list_display)
        for r in self.list_display_links:
            editable.remove(r)
        self.list_editable = editable

        #run usual init method
        super(PageAdminName, self).__init__(model, admin_site)

    list_display_links = ('name',)
    # list_display = ('name', 'description_short', 'description_long', 'comment', 'device_type')
    # list_editable = ('description_short', 'description_long', 'comment', 'device_type')
    # search_fields = ('device_type',)
    list_per_page = 50
    ordering = ('id', )

class PageAdmin(admin.ModelAdmin):
    list_display = ('id', 'tag', 'value', 'ts', 'start_data', 'end_data')
    list_display_links = ('id', )
    # search_fields = ('title', 'content')
    list_per_page = 50
    ordering = ('id',)

admin.site.register(Tag, PageAdminName)
admin.site.register(Tag_group, PageAdminName)
admin.site.register(Hourly, PageAdmin)

# Register your models here.
