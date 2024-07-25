from django.contrib import admin

from . import models


@admin.register(models.ReservedTime)
class ReservedTimeAdmin(admin.ModelAdmin):
    list_display = ("date_time", "user")
    list_display_links = ("date_time", "user")
    search_fields = ("date_time", "user")
