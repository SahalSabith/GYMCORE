from django import forms
from django.utils import timezone
from .models import MembershipPlan, Subscription


class MembershipPlanForm(forms.ModelForm):
    class Meta:
        model = MembershipPlan
        fields = ["name", "price", "duration_days", "description", "is_active"]

    def clean_price(self):
        price = self.cleaned_data.get("price")
        if price is not None and price <= 0:
            raise forms.ValidationError("Price must be greater than zero.")
        return price


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
        max_future_days = 365
        if (date - today).days > max_future_days:
            raise forms.ValidationError(
                f"Start date must be within the next {max_future_days} days."
            )
        return date