from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TrainingSession

User = get_user_model()


class BookSessionForm(forms.ModelForm):
    """Used by members to request a session."""

    class Meta:
        model = TrainingSession
        fields = ['trainer', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3, 'placeholder': 'What do you want to focus on?'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = User.objects.filter(role='TRAINER')
        self.fields['trainer'].label_from_instance = lambda u: u.get_full_name() or u.email

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('Session date cannot be in the past.')
        return date


class TrainerResponseForm(forms.ModelForm):
    """Used by trainers to approve/reject a session."""

    class Meta:
        model = TrainingSession
        fields = ['status', 'trainer_note']
        widgets = {
            'trainer_note': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Optional note to the member...'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trainers can only approve, reject, or mark complete
        self.fields['status'].choices = [
            ('APPROVED', 'Approve'),
            ('REJECTED', 'Reject'),
            ('COMPLETED', 'Mark Completed'),
        ]
