from django.db import models
from django.conf import settings


DAYS_OF_WEEK = [
    ('MON', 'Monday'),
    ('TUE', 'Tuesday'),
    ('WED', 'Wednesday'),
    ('THU', 'Thursday'),
    ('FRI', 'Friday'),
    ('SAT', 'Saturday'),
    ('SUN', 'Sunday'),
]


class WorkoutPlan(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_workout_plans',
        limit_choices_to={'role': 'TRAINER'},
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_plans',
        limit_choices_to={'role': 'MEMBER'},
    )
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} ({self.member.get_full_name()})'


class WorkoutDay(models.Model):
    workout_plan = models.ForeignKey(WorkoutPlan, on_delete=models.CASCADE, related_name='days')
    day_of_week = models.CharField(max_length=3, choices=DAYS_OF_WEEK)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['day_of_week']
        unique_together = ('workout_plan', 'day_of_week')

    def __str__(self):
        return f'{self.get_day_of_week_display()} – {self.workout_plan.title}'


class Exercise(models.Model):
    workout_day = models.ForeignKey(WorkoutDay, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=200)
    sets = models.PositiveIntegerField(default=3)
    reps = models.CharField(max_length=50, help_text='e.g. 10 or 8-12')
    instructions = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.name} ({self.sets}x{self.reps})'


class WorkoutCompletion(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='workout_completions',
    )
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE, related_name='completions')
    date = models.DateField()
    completed = models.BooleanField(default=True)
    notes = models.CharField(max_length=200, blank=True)

    class Meta:
        unique_together = ('member', 'exercise', 'date')

    def __str__(self):
        return f'{self.member.get_full_name()} – {self.exercise.name} on {self.date}'
