from django.contrib import admin

from .models import *


@admin.register(Guild)
class GuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'created_at')


@admin.register(Member)
class GuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'guild', 'user', 'admin')


@admin.register(Message)
class GuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'author')


@admin.register(InviteLink)
class GuildAdmin(admin.ModelAdmin):
    list_display = ('id', 'guild', 'key')
