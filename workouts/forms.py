import re
from django import forms
from django.contrib.auth import get_user_model
from .models import WorkoutPlan, WorkoutDay, Exercise

User = get_user_model()


# ── helpers ───────────────────────────────────────────────────────────────────

def _text_field(value, label, min_len=3, max_len=200, allow_numbers=False):
    value = value.strip()
    if not value:
        raise forms.ValidationError(f"{label} is required.")
    if not allow_numbers and re.match(r"^[\d\W]+$", value):
        raise forms.ValidationError(
            f"{label} must contain descriptive text, not just numbers or symbols."
        )
    if len(value) < min_len:
        raise forms.ValidationError(
            f"{label} must be at least {min_len} characters."
        )
    if len(value) > max_len:
        raise forms.ValidationError(
            f"{label} must not exceed {max_len} characters."
        )
    return value


# ── WorkoutPlanForm ───────────────────────────────────────────────────────────

class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ["member", "title", "description"]
        widgets = {
            "description": forms.Textarea(
                attrs={"rows": 3, "placeholder": "General notes for this plan..."}
            ),
            "title": forms.TextInput(
                attrs={"placeholder": "e.g. 4-Week Strength Builder"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["member"].queryset = User.objects.filter(role="MEMBER")
        self.fields["member"].label_from_instance = (
            lambda u: u.get_full_name() or u.email
        )

    def clean_title(self):
        return _text_field(
            self.cleaned_data.get("title", ""), "Title", min_len=3, max_len=200
        )

    def clean_description(self):
        desc = self.cleaned_data.get("description", "").strip()
        if desc:
            if len(desc) < 10:
                raise forms.ValidationError(
                    "Description must be at least 10 characters if provided."
                )
            if len(desc) > 2000:
                raise forms.ValidationError("Description must not exceed 2000 characters.")
        return desc


# ── WorkoutDayForm ────────────────────────────────────────────────────────────

class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = WorkoutDay
        fields = ["day_of_week", "notes"]
        widgets = {
            "notes": forms.TextInput(attrs={"placeholder": "e.g. Chest & Triceps"}),
        }

    def clean_day_of_week(self):
        value = self.cleaned_data.get("day_of_week")
        # Assuming day_of_week is an IntegerField (0=Mon … 6=Sun) or a ChoiceField
        # Validate it is within range if it's an integer
        if value is not None:
            try:
                value = int(value)
            except (TypeError, ValueError):
                raise forms.ValidationError("Select a valid day of the week.")
            if value < 0 or value > 6:
                raise forms.ValidationError(
                    "Day of the week must be between 0 (Monday) and 6 (Sunday)."
                )
        return value

    def clean_notes(self):
        notes = self.cleaned_data.get("notes", "").strip()
        if notes:
            if re.match(r"^\d+$", notes):
                raise forms.ValidationError(
                    "Notes must be descriptive text, not just a number."
                )
            if len(notes) > 200:
                raise forms.ValidationError("Notes must not exceed 200 characters.")
        return notes


# ── ExerciseForm ──────────────────────────────────────────────────────────────

# Accepted reps formats: "10", "8-12", "10-15", "AMRAP", "30s", etc.
_REPS_PATTERN = re.compile(
    r"^(\d{1,3}(-\d{1,3})?|[A-Za-z]{2,10}(\s*\d{0,3}[A-Za-z]*)?)$"
)


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ["name", "sets", "reps", "instructions", "order"]
        widgets = {
            "instructions": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Form cues or technique notes..."}
            ),
            "reps": forms.TextInput(attrs={"placeholder": "e.g. 10 or 8-12"}),
        }

    def clean_name(self):
        return _text_field(
            self.cleaned_data.get("name", ""), "Exercise name",
            min_len=2, max_len=100
        )

    def clean_sets(self):
        sets = self.cleaned_data.get("sets")
        if sets is None:
            raise forms.ValidationError("Sets is required.")
        try:
            sets = int(sets)
        except (TypeError, ValueError):
            raise forms.ValidationError("Sets must be a whole number.")
        if sets < 1:
            raise forms.ValidationError("Sets must be at least 1.")
        if sets > 100:
            raise forms.ValidationError("Sets must not exceed 100.")
        return sets

    def clean_reps(self):
        reps = self.cleaned_data.get("reps", "").strip()
        if not reps:
            raise forms.ValidationError("Reps is required.")
        if not _REPS_PATTERN.match(reps):
            raise forms.ValidationError(
                'Enter reps as a number (e.g. "10"), a range (e.g. "8-12"), '
                'or a label (e.g. "AMRAP", "30s").'
            )
        return reps

    def clean_order(self):
        order = self.cleaned_data.get("order")
        if order is None:
            return order
        try:
            order = int(order)
        except (TypeError, ValueError):
            raise forms.ValidationError("Order must be a whole number.")
        if order < 0:
            raise forms.ValidationError("Order must be 0 or greater.")
        if order > 9999:
            raise forms.ValidationError("Order must not exceed 9999.")
        return order

    def clean_instructions(self):
        instr = self.cleaned_data.get("instructions", "").strip()
        if instr:
            if len(instr) < 5:
                raise forms.ValidationError(
                    "Instructions must be at least 5 characters if provided."
                )
            if len(instr) > 1000:
                raise forms.ValidationError("Instructions must not exceed 1000 characters.")
            if not re.search(r"[A-Za-z]{2,}", instr):
                raise forms.ValidationError("Instructions must contain descriptive text.")
        return instr


ExerciseFormSet = forms.inlineformset_factory(
    WorkoutDay,
    Exercise,
    form=ExerciseForm,
    extra=3,
    can_delete=True,
)