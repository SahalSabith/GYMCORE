from django.contrib import admin
from .models import MembershipPlan, Subscription


@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_days', 'is_active', 'created_at']
    list_filter = ['is_active', 'duration_days']
    search_fields = ['name']
    list_editable = ['is_active']


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['member', 'plan', 'start_date', 'end_date', 'is_active']
    list_filter = ['is_active', 'plan']
    search_fields = ['member__email', 'member__first_name']
    readonly_fields = ['end_date', 'created_at']
    raw_id_fields = ['member']
