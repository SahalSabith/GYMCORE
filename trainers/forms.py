from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import TrainerProfile, TrainerAssignment

User = get_user_model()


class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = TrainerProfile
        fields = ['experience_years', 'specialization', 'bio', 'certifications']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Tell members about yourself...'}),
            'certifications': forms.TextInput(attrs={'placeholder': 'e.g. ACE, NASM, CrossFit Level 1'}),
        }


class TrainerAssignmentForm(forms.ModelForm):
    class Meta:
        model = TrainerAssignment
        fields = ['trainer', 'member', 'notes']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['trainer'].queryset = User.objects.filter(role='TRAINER')
        self.fields['member'].queryset = User.objects.filter(role='MEMBER')
