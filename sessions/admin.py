from django.contrib import admin
from .models import TrainingSession


@admin.register(TrainingSession)
class TrainingSessionAdmin(admin.ModelAdmin):
    list_display = ['member', 'trainer', 'date', 'time', 'status', 'created_at']
    list_filter = ['status', 'date']
    search_fields = ['member__email', 'trainer__email']
    list_editable = ['status']
    date_hierarchy = 'date'
