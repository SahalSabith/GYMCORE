from django.contrib import admin
from .models import WorkoutPlan, WorkoutDay, Exercise, WorkoutCompletion


class WorkoutDayInline(admin.TabularInline):
    model = WorkoutDay
    extra = 1


class ExerciseInline(admin.TabularInline):
    model = Exercise
    extra = 2


@admin.register(WorkoutPlan)
class WorkoutPlanAdmin(admin.ModelAdmin):
    list_display = ['title', 'trainer', 'member', 'is_active', 'created_at']
    list_filter = ['is_active']
    search_fields = ['title', 'member__email', 'trainer__email']
    inlines = [WorkoutDayInline]


@admin.register(WorkoutDay)
class WorkoutDayAdmin(admin.ModelAdmin):
    list_display = ['workout_plan', 'day_of_week']
    inlines = [ExerciseInline]


@admin.register(Exercise)
class ExerciseAdmin(admin.ModelAdmin):
    list_display = ['name', 'workout_day', 'sets', 'reps']


@admin.register(WorkoutCompletion)
class WorkoutCompletionAdmin(admin.ModelAdmin):
    list_display = ['member', 'exercise', 'date', 'completed']
    list_filter = ['completed', 'date']
