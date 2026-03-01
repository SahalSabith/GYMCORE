import re
from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import TrainerProfile, TrainerAssignment

User = get_user_model()


class TrainerProfileForm(forms.ModelForm):
    class Meta:
        model = TrainerProfile
        fields = ["experience_years", "specialization", "bio", "certifications"]
        widgets = {
            "bio": forms.Textarea(
                attrs={"rows": 4, "placeholder": "Tell members about yourself..."}
            ),
            "certifications": forms.TextInput(
                attrs={"placeholder": "e.g. ACE, NASM, CrossFit Level 1"}
            ),
        }

    def clean_experience_years(self):
        years = self.cleaned_data.get("experience_years")
        if years is None:
            return years
        # Must be a whole number
        if not isinstance(years, int):
            raise forms.ValidationError("Experience years must be a whole number.")
        if years < 0:
            raise forms.ValidationError("Experience years cannot be negative.")
        if years > 60:
            raise forms.ValidationError("Experience years must not exceed 60.")
        return years

    def clean_specialization(self):
        value = self.cleaned_data.get("specialization", "").strip()
        if not value:
            raise forms.ValidationError("Specialization is required.")
        # Must not be purely numeric
        if re.match(r"^\d+$", value):
            raise forms.ValidationError("Specialization must be descriptive text, not a number.")
        if len(value) < 3:
            raise forms.ValidationError("Specialization must be at least 3 characters.")
        if len(value) > 200:
            raise forms.ValidationError("Specialization must not exceed 200 characters.")
        return value

    def clean_bio(self):
        bio = self.cleaned_data.get("bio", "").strip()
        if bio:
            if len(bio) < 20:
                raise forms.ValidationError("Bio must be at least 20 characters if provided.")
            if len(bio) > 2000:
                raise forms.ValidationError("Bio must not exceed 2000 characters.")
            # Must contain actual words
            if not re.search(r"[A-Za-z]{2,}", bio):
                raise forms.ValidationError("Bio must contain descriptive text.")
        return bio

    def clean_certifications(self):
        certs = self.cleaned_data.get("certifications", "").strip()
        if certs:
            if len(certs) > 500:
                raise forms.ValidationError("Certifications must not exceed 500 characters.")
            # Reject entries that are purely numeric
            if re.match(r"^\d+$", certs):
                raise forms.ValidationError(
                    "Certifications must be text (e.g. ACE, NASM), not a number."
                )
        return certs


class TrainerAssignmentForm(forms.ModelForm):
    class Meta:
        model = TrainerAssignment
        fields = ["trainer", "member", "notes"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 2}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["trainer"].queryset = User.objects.filter(role="TRAINER")
        self.fields["member"].queryset  = User.objects.filter(role="MEMBER")

    def clean(self):
        cleaned = super().clean()
        trainer = cleaned.get("trainer")
        member  = cleaned.get("member")
        # Prevent duplicate assignments
        if trainer and member:
            if TrainerAssignment.objects.filter(
                trainer=trainer, member=member
            ).exclude(pk=self.instance.pk).exists():
                raise forms.ValidationError(
                    "This trainer is already assigned to this member."
                )
        return cleaned

    def clean_notes(self):
        notes = self.cleaned_data.get("notes", "").strip()
        if notes and len(notes) > 500:
            raise forms.ValidationError("Notes must not exceed 500 characters.")
        return notes