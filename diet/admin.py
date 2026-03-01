from django.contrib import admin
from .models import DietPlan, Meal


class MealInline(admin.TabularInline):
    model = Meal
    extra = 3


@admin.register(DietPlan)
class DietPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'member', 'calories', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'member__email', 'trainer__email']
    inlines = [MealInline]


@admin.register(Meal)
class MealAdmin(admin.ModelAdmin):
    list_display = ['diet_plan', 'meal_type', 'calories']
    list_filter = ['meal_type']
