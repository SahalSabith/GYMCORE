from django.contrib import admin
from .models import TrainerProfile, TrainerAssignment


@admin.register(TrainerProfile)
class TrainerProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'specialization', 'experience_years']
    search_fields = ['user__email', 'user__first_name', 'specialization']
    raw_id_fields = ['user']


@admin.register(TrainerAssignment)
class TrainerAssignmentAdmin(admin.ModelAdmin):
    list_display = ['trainer', 'member', 'assigned_at']
    search_fields = ['trainer__email', 'member__email']
    raw_id_fields = ['trainer', 'member']
    list_filter = ['assigned_at']
