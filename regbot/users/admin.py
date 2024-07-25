from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from regbot.users.models import User


@admin.register(User)
class ClientAdmin(UserAdmin):
    list_display = ("username", "telegram_id")
    list_display_links = ("username", "telegram_id")
    search_fields = ("telegram_id", "username")
