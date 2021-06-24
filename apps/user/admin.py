from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, Bot


@admin.register(User)
class UserAdmin(DefaultUserAdmin):
    list_display = (
        'username', 'first_name', 'last_name', 'is_superuser', 'is_staff', 'is_active', 'bot'
    )
    fieldsets = (
        (None, {'fields': ('avatar', 'username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email')}),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'bot', 'system', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )


@admin.register(Bot)
class BotAdmin(admin.ModelAdmin):
    list_display = ('master', 'account')
