from django.contrib import admin
from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['member', 'trainer', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['member__email', 'trainer__email', 'member__first_name']
    raw_id_fields = ['member', 'trainer']
    list_editable = ['status']
    readonly_fields = ['created_at', 'updated_at']
