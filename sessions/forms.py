import re
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TrainingSession

User = get_user_model()

# ── shared helpers ────────────────────────────────────────────────────────────

def _validate_notes(value, max_len=1000):
    if value and len(value) > max_len:
        raise forms.ValidationError(f"Notes must not exceed {max_len} characters.")
    # Reject notes that are only numbers / symbols with no words at all
    if value and not re.search(r"[A-Za-z]", value):
        raise forms.ValidationError("Notes must contain at least some descriptive text.")
    return value


def _clean_future_date(date):
    if not date:
        raise forms.ValidationError("Date is required.")
    if date < timezone.now().date():
        raise forms.ValidationError("Session date cannot be in the past.")
    max_future_days = 365
    if (date - timezone.now().date()).days > max_future_days:
        raise forms.ValidationError(
            f"Session date must be within the next {max_future_days} days."
        )
    return date


# ── SessionRequestForm ────────────────────────────────────────────────────────

class SessionRequestForm(forms.ModelForm):
    def __init__(self, member, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from trainers.models import TrainerAssignment
        assigned = TrainerAssignment.objects.filter(member=member).values_list(
            "trainer_id", flat=True
        )
        qs = (
            User.objects.filter(role="TRAINER", pk__in=assigned)
            if assigned
            else User.objects.filter(role="TRAINER")
        )
        self.fields["trainer"].queryset = qs
        self.fields["trainer"].label_from_instance = (
            lambda u: u.get_full_name() or u.email
        )

    class Meta:
        model = TrainingSession
        fields = ["trainer", "date", "time", "notes"]
        widgets = {
            "date":  forms.DateInput(attrs={"type": "date"}),
            "time":  forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_date(self):
        return _clean_future_date(self.cleaned_data.get("date"))

    def clean_time(self):
        time = self.cleaned_data.get("time")
        if not time:
            raise forms.ValidationError("Time is required.")
        # Only accept times between 06:00 and 22:00
        if time.hour < 6 or time.hour >= 22:
            raise forms.ValidationError(
                "Sessions must be scheduled between 06:00 and 22:00."
            )
        return time

    def clean_notes(self):
        return _validate_notes(self.cleaned_data.get("notes", "").strip())


# ── SessionResponseForm ───────────────────────────────────────────────────────

class SessionResponseForm(forms.ModelForm):
    class Meta:
        model = TrainingSession
        fields = ["status", "trainer_response"]
        widgets = {"trainer_response": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            ("APPROVED",   "Approve"),
            ("REJECTED",   "Reject"),
            ("COMPLETED",  "Mark as Completed"),
        ]

    def clean_status(self):
        status = self.cleaned_data.get("status", "").strip().upper()
        allowed = {"APPROVED", "REJECTED", "COMPLETED"}
        if status not in allowed:
            raise forms.ValidationError("Select a valid status.")
        return status

    def clean_trainer_response(self):
        response = self.cleaned_data.get("trainer_response", "").strip()
        status = self.cleaned_data.get("status")
        if status == "REJECTED" and not response:
            raise forms.ValidationError(
                "Please provide a reason when rejecting a session."
            )
        if response:
            _validate_notes(response, max_len=1000)
        return response