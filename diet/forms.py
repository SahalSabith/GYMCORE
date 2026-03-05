# forms.py

from django import forms
from django.contrib.auth import get_user_model
import re
from .models import DietPlan, Meal

User = get_user_model()

_POSITIVE_INT_FIELDS = {
    "calories": (0, 10000, "Calories"),
    "protein":  (0, 1000,  "Protein"),
    "carbs":    (0, 2000,  "Carbs"),
    "fats":     (0, 500,   "Fats"),
}


class DietPlanForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = User.objects.filter(role="MEMBER")
        self.fields["member"].label_from_instance = (
            lambda u: u.get_full_name() or u.email
        )

    class Meta:
        model = DietPlan
        fields = ["member", "title", "calories", "protein", "carbs", "fats", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
            # ← Fix: explicit number inputs so browser + Django agree on format
            "calories": forms.NumberInput(attrs={"min": 0, "max": 10000, "step": 1}),
            "protein":  forms.NumberInput(attrs={"min": 0, "max": 1000,  "step": 1}),
            "carbs":    forms.NumberInput(attrs={"min": 0, "max": 2000,  "step": 1}),
            "fats":     forms.NumberInput(attrs={"min": 0, "max": 500,   "step": 1}),
        }

    def clean_title(self):
        title = self.cleaned_data.get("title", "").strip()
        if not title:
            raise forms.ValidationError("Title is required.")
        if len(title) < 3:
            raise forms.ValidationError("Title must be at least 3 characters.")
        if len(title) > 200:
            raise forms.ValidationError("Title must not exceed 200 characters.")
        if re.match(r"^[\d\W]+$", title):
            raise forms.ValidationError("Title must contain meaningful text, not just numbers or symbols.")
        return title

    def _clean_positive_number(self, field_name):
        min_val, max_val, label = _POSITIVE_INT_FIELDS[field_name]
        value = self.cleaned_data.get(field_name)
        if value is None:
            return value
        # Coerce to int in case it came through as float
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError(f"{label} must be a whole number.")
        if value < min_val:
            raise forms.ValidationError(f"{label} must be 0 or greater.")
        if value > max_val:
            raise forms.ValidationError(f"{label} must not exceed {max_val}.")
        return value

    def clean_calories(self): return self._clean_positive_number("calories")
    def clean_protein(self):  return self._clean_positive_number("protein")
    def clean_carbs(self):    return self._clean_positive_number("carbs")
    def clean_fats(self):     return self._clean_positive_number("fats")

    def clean_notes(self):
        notes = self.cleaned_data.get("notes", "").strip()
        if notes and len(notes) > 2000:
            raise forms.ValidationError("Notes must not exceed 2000 characters.")
        return notes


class MealForm(forms.ModelForm):
    class Meta:
        model = Meal
        fields = ["meal_type", "food_items", "calories", "notes"]
        widgets = {
            "food_items": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Enter each food item on a new line"}
            ),
            "notes":    forms.Textarea(attrs={"rows": 2}),
            "calories": forms.NumberInput(attrs={"min": 0, "max": 10000, "step": 1}),
        }

    def clean_food_items(self):
        items = self.cleaned_data.get("food_items", "").strip()
        if not items:
            raise forms.ValidationError("Food items are required.")
        lines = [l.strip() for l in items.splitlines()]
        non_empty = [l for l in lines if l]
        if not non_empty:
            raise forms.ValidationError("Please enter at least one food item.")
        if len(non_empty) > 50:
            raise forms.ValidationError("You may not enter more than 50 food items.")
        for line in non_empty:
            if re.match(r"^\d+$", line):
                raise forms.ValidationError(
                    f'"{line}" does not look like a food item — please enter a name.'
                )
        return "\n".join(non_empty)

    def clean_calories(self):
        value = self.cleaned_data.get("calories")
        if value is None:
            return value
        try:
            value = int(value)
        except (TypeError, ValueError):
            raise forms.ValidationError("Calories must be a whole number.")
        if value < 0:
            raise forms.ValidationError("Calories must be 0 or greater.")
        if value > 10000:
            raise forms.ValidationError("Calories per meal must not exceed 10,000.")
        return value

    def clean_notes(self):
        notes = self.cleaned_data.get("notes", "").strip()
        if notes and len(notes) > 1000:
            raise forms.ValidationError("Notes must not exceed 1000 characters.")
        return notes