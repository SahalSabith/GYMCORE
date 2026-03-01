from django import forms
from django.contrib.auth import get_user_model
from .models import DietPlan, Meal

User = get_user_model()


class DietPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.filter(role='MEMBER')
        self.fields['member'].label_from_instance = lambda u: u.get_full_name() or u.email

    class Meta:
        model = DietPlan
        fields = ['member', 'title', 'calories', 'protein', 'carbs', 'fats', 'notes']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3})}


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ['meal_type', 'food_items', 'calories', 'notes']
        widgets = {
            'food_items': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Enter each food item on a new line'}),
            'notes': forms.Textarea(attrs={'rows': 2}),
        }
