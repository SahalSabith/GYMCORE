from django.db import models
from django.conf import settings


class DietPlan(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='created_diet_plans', limit_choices_to={'role': 'TRAINER'},
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='diet_plans', limit_choices_to={'role': 'MEMBER'},
    )
    title = models.CharField(max_length=200)
    calories = models.PositiveIntegerField(null=True, blank=True, help_text='Daily target kcal')
    protein = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    carbs = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    fats = models.DecimalField(max_digits=6, decimal_places=1, null=True, blank=True, help_text='grams')
    notes = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.title} → {self.member.get_full_name()}'


class Meal(models.Model):
    class MealType(models.TextChoices):
        BREAKFAST = 'BREAKFAST', 'Breakfast'
        MORNING_SNACK = 'MORNING_SNACK', 'Morning Snack'
        LUNCH = 'LUNCH', 'Lunch'
        AFTERNOON_SNACK = 'AFTERNOON_SNACK', 'Afternoon Snack'
        DINNER = 'DINNER', 'Dinner'
        POST_WORKOUT = 'POST_WORKOUT', 'Post-Workout'

    MEAL_ORDER = {
        'BREAKFAST': 1, 'MORNING_SNACK': 2, 'LUNCH': 3,
        'AFTERNOON_SNACK': 4, 'DINNER': 5, 'POST_WORKOUT': 6,
    }

    diet_plan = models.ForeignKey(DietPlan, on_delete=models.CASCADE, related_name='meals')
    meal_type = models.CharField(max_length=20, choices=MealType.choices)
    food_items = models.TextField(help_text='List each food item on a new line')
    notes = models.TextField(blank=True)
    calories = models.PositiveIntegerField(null=True, blank=True)

    class Meta:
        ordering = ['meal_type']

    def food_list(self):
        return [item.strip() for item in self.food_items.splitlines() if item.strip()]

    def __str__(self):
        return f'{self.get_meal_type_display()} — {self.diet_plan.title}'
