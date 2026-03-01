from django import forms
from .models import Subscription


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ['start_date']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
        }
