from django import forms
from django.contrib.auth import get_user_model
from .models import WorkoutPlan, WorkoutDay, Exercise

User = get_user_model()


class WorkoutPlanForm(forms.ModelForm):
    class Meta:
        model = WorkoutPlan
        fields = ['member', 'title', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'General notes for this plan...'}),
            'title': forms.TextInput(attrs={'placeholder': 'e.g. 4-Week Strength Builder'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = User.objects.filter(role='MEMBER')
        self.fields['member'].label_from_instance = lambda u: u.get_full_name() or u.email


class WorkoutDayForm(forms.ModelForm):
    class Meta:
        model = WorkoutDay
        fields = ['day_of_week', 'notes']
        widgets = {
            'notes': forms.TextInput(attrs={'placeholder': 'e.g. Chest & Triceps'}),
        }


class ExerciseForm(forms.ModelForm):
    class Meta:
        model = Exercise
        fields = ['name', 'sets', 'reps', 'instructions', 'order']
        widgets = {
            'instructions': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Form cues or technique notes...'}),
            'reps': forms.TextInput(attrs={'placeholder': 'e.g. 10 or 8-12'}),
        }


ExerciseFormSet = forms.inlineformset_factory(
    WorkoutDay,
    Exercise,
    form=ExerciseForm,
    extra=3,
    can_delete=True,
)
