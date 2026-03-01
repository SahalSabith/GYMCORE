from django import forms
from django.utils import timezone
from .models import Subscription


class SubscribeForm(forms.ModelForm):
    class Meta:
        model = Subscription
        fields = ["start_date"]
        widgets = {
            "start_date": forms.DateInput(attrs={"type": "date"}),
        }

    def clean_start_date(self):
        date = self.cleaned_data.get("start_date")
        if not date:
            raise forms.ValidationError("Start date is required.")
        today = timezone.now().date()
        if date < today:
            raise forms.ValidationError("Start date cannot be in the past.")
        # Reasonable upper bound – prevent typos like year 9999
        max_future_days = 365
        if (date - today).days > max_future_days:
            raise forms.ValidationError(
                f"Start date must be within the next {max_future_days} days."
            )
        return date