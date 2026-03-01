import re
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from .models import TrainingSession

User = get_user_model()


def _validate_notes(value, max_len=1000):
    if value and len(value) > max_len:
        raise forms.ValidationError(f"Notes must not exceed {max_len} characters.")
    if value and not re.search(r"[A-Za-z]", value):
        raise forms.ValidationError("Notes must contain at least some descriptive text.")
    return value


class BookSessionForm(forms.ModelForm):
    """Used by members to request a session."""

    class Meta:
        model = TrainingSession
        fields = ["trainer", "date", "time", "notes"]
        widgets = {
            "date":  forms.DateInput(attrs={"type": "date"}),
            "time":  forms.TimeInput(attrs={"type": "time"}),
            "notes": forms.Textarea(
                attrs={"rows": 3, "placeholder": "What do you want to focus on?"}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainer"].queryset = User.objects.filter(role="TRAINER")
        self.fields["trainer"].label_from_instance = (
            lambda u: u.get_full_name() or u.email
        )

    def clean_date(self):
        date = self.cleaned_data.get("date")
        if not date:
            raise forms.ValidationError("Date is required.")
        if date < timezone.now().date():
            raise forms.ValidationError("Session date cannot be in the past.")
        if (date - timezone.now().date()).days > 365:
            raise forms.ValidationError("Session date must be within the next 365 days.")
        return date

    def clean_time(self):
        time = self.cleaned_data.get("time")
        if not time:
            raise forms.ValidationError("Time is required.")
        if time.hour < 6 or time.hour >= 22:
            raise forms.ValidationError(
                "Sessions must be scheduled between 06:00 and 22:00."
            )
        return time

    def clean_notes(self):
        return _validate_notes(self.cleaned_data.get("notes", "").strip())


class TrainerResponseForm(forms.ModelForm):
    """Used by trainers to approve/reject a session."""

    class Meta:
        model = TrainingSession
        fields = ["status", "trainer_note"]
        widgets = {
            "trainer_note": forms.Textarea(
                attrs={"rows": 2, "placeholder": "Optional note to the member..."}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            ("APPROVED",  "Approve"),
            ("REJECTED",  "Reject"),
            ("COMPLETED", "Mark Completed"),
        ]

    def clean_status(self):
        status = self.cleaned_data.get("status", "").strip().upper()
        if status not in {"APPROVED", "REJECTED", "COMPLETED"}:
            raise forms.ValidationError("Select a valid status.")
        return status

    def clean_trainer_note(self):
        note = self.cleaned_data.get("trainer_note", "").strip()
        status = self.cleaned_data.get("status")
        if status == "REJECTED" and not note:
            raise forms.ValidationError("Please provide a reason for rejection.")
        if note:
            _validate_notes(note, max_len=1000)
        return note