from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TrainingSession

User = get_user_model()


class SessionRequestForm(forms.ModelForm):
    def __init__(self, member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Show only trainers who are assigned to this member (or all if none assigned)
        from trainers.models import TrainerAssignment
        assigned = TrainerAssignment.objects.filter(member=member).values_list('trainer_id', flat=True)
        qs = User.objects.filter(role='TRAINER', pk__in=assigned) if assigned else User.objects.filter(role='TRAINER')
        self.fields['trainer'].queryset = qs
        self.fields['trainer'].label_from_instance = lambda u: u.get_full_name() or u.email

    def clean_date(self):
        date = self.cleaned_data.get('date')
        if date and date < timezone.now().date():
            raise forms.ValidationError('Session date cannot be in the past.')
        return date

    class Meta:
        model = TrainingSession
        fields = ['trainer', 'date', 'time', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }


class SessionResponseForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ['status', 'trainer_response']
        widgets = {'trainer_response': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Trainers can only approve, reject, or mark completed
        self.fields['status'].choices = [
            ('APPROVED', 'Approve'),
            ('REJECTED', 'Reject'),
            ('COMPLETED', 'Mark as Completed'),
        ]
