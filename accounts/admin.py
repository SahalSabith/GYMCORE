from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'get_full_name', 'role', 'is_active', 'date_joined')
    list_filter = ('role', 'is_active', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('-date_joined',)

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Gym Profile', {
            'fields': ('role', 'phone_number', 'profile_photo', 'height', 'weight', 'fitness_goal')
        }),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Gym Profile', {
            'fields': ('email', 'first_name', 'last_name', 'role', 'phone_number')
        }),
    )
