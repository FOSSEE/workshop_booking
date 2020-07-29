from django.contrib import admin

from cms.models import *


# Register your models here.

class NavAdmin(admin.ModelAdmin):
    list_display = ['name', 'link', 'position', 'active']
    ordering = ['position']


class SubNavAdmin(admin.ModelAdmin):
    list_display = ['name', 'nav', 'link', 'position', 'active']
    ordering = ['nav', 'position']
    list_filter = ['nav']


class PageAdmin(admin.ModelAdmin):
    list_display = ['title', 'permalink', 'pub_date', 'active']


class StaticFileAdmin(admin.ModelAdmin):
    list_display = ['filename', 'file']


admin.site.register(Nav, NavAdmin)
admin.site.register(SubNav, SubNavAdmin)
admin.site.register(Page, PageAdmin)
admin.site.register(StaticFile, StaticFileAdmin)
