import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


# ──────────────────────────────────────────────
# Shared validators
# ──────────────────────────────────────────────

def validate_letters_only(value, field_name="This field"):
    """Allow only Unicode letters and spaces (no digits, no special chars)."""
    if not re.match(r"^[^\W\d_]+(?:\s[^\W\d_]+)*$", value.strip(), re.UNICODE):
        raise forms.ValidationError(
            f"{field_name} must contain letters only (no numbers or special characters)."
        )


def validate_phone(value):
    """Digits, spaces, dashes and an optional leading + only."""
    phone = value.strip()
    # Must contain only allowed characters
    if not re.match(r"^\+?[\d\s\-]{7,20}$", phone):
        raise forms.ValidationError(
            "Enter a valid phone number (digits, spaces and dashes only, 7–20 characters)."
        )
    # Must have at least 7 actual digits
    digits_only = re.sub(r"\D", "", phone)
    if len(digits_only) < 7:
        raise forms.ValidationError("Phone number must contain at least 7 digits.")
    if len(digits_only) > 15:
        raise forms.ValidationError("Phone number must not exceed 15 digits.")
    # Reject anything that looks like letters crept in
    if re.search(r"[a-zA-Z]", phone):
        raise forms.ValidationError("Phone number must not contain letters.")


def validate_strong_password(value):
    """Enforce 8+ chars, upper, lower, digit, and special character."""
    errors = []
    if len(value) < 8:
        errors.append("at least 8 characters")
    if not re.search(r"[A-Z]", value):
        errors.append("at least one uppercase letter (A-Z)")
    if not re.search(r"[a-z]", value):
        errors.append("at least one lowercase letter (a-z)")
    if not re.search(r"\d", value):
        errors.append("at least one digit (0-9)")
    if not re.search(r"[!@#$%^&*()_+\-=\[\]{};':\"\\|,.<>\/?`~]", value):
        errors.append("at least one special character (!@#$%^&* etc.)")
    if errors:
        raise forms.ValidationError(
            "Password must contain: " + ", ".join(errors) + "."
        )


def validate_positive_number(value, field_name="Value"):
    """Ensure numeric fields are positive."""
    if value is not None and value < 0:
        raise forms.ValidationError(f"{field_name} must be a positive number.")


# ──────────────────────────────────────────────
# Forms
# ──────────────────────────────────────────────

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput,
        validators=[validate_strong_password],
        help_text=(
            "Must be at least 8 characters and include uppercase, lowercase, "
            "a digit, and a special character."
        ),
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm Password",
    )
    role = forms.ChoiceField(
        choices=[("TRAINER", "Trainer"), ("MEMBER", "Member")],
        help_text="Admins are created via the admin panel only.",
    )

    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "email",
            "phone_number", "role", "password", "password_confirm",
        ]

    # ── field-level validation ──────────────────

    def clean_first_name(self):
        value = self.cleaned_data.get("first_name", "").strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        validate_letters_only(value, "First name")
        if len(value) < 2:
            raise forms.ValidationError("First name must be at least 2 characters.")
        if len(value) > 50:
            raise forms.ValidationError("First name must not exceed 50 characters.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data.get("last_name", "").strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        validate_letters_only(value, "Last name")
        if len(value) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters.")
        if len(value) > 50:
            raise forms.ValidationError("Last name must not exceed 50 characters.")
        return value.title()

    def clean_email(self):
        email = self.cleaned_data.get("email", "").strip().lower()
        if not email:
            raise forms.ValidationError("Email is required.")
        # Basic structural check beyond Django's EmailValidator
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$", email):
            raise forms.ValidationError("Enter a valid email address.")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email already exists.")
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if phone:
            validate_phone(phone)
        return phone

    def clean_role(self):
        role = self.cleaned_data.get("role", "").strip().upper()
        allowed = {"TRAINER", "MEMBER"}
        if role not in allowed:
            raise forms.ValidationError("Select a valid role.")
        return role

    # ── cross-field validation ──────────────────

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get("password")
        pw_confirm = cleaned.get("password_confirm")
        if pw and pw_confirm and pw != pw_confirm:
            self.add_error("password_confirm", "Passwords do not match.")
        return cleaned

    # ── save ────────────────────────────────────

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data["email"].split("@")[0]
        user.set_password(self.cleaned_data["password"])
        user.role = self.cleaned_data["role"]
        if commit:
            base = user.username
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f"{base}{counter}"
                counter += 1
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={"autofocus": True}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["username"].widget.attrs.update({"placeholder": "your@email.com"})
        self.fields["password"].widget.attrs.update({"placeholder": "••••••••"})

    def clean_username(self):
        email = self.cleaned_data.get("username", "").strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]{2,}$", email):
            raise forms.ValidationError("Enter a valid email address.")
        return email


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "first_name", "last_name", "phone_number",
            "profile_photo", "height", "weight", "fitness_goal",
        ]
        widgets = {
            "fitness_goal": forms.Textarea(attrs={"rows": 3}),
        }

    def clean_first_name(self):
        value = self.cleaned_data.get("first_name", "").strip()
        if not value:
            raise forms.ValidationError("First name is required.")
        validate_letters_only(value, "First name")
        if len(value) < 2:
            raise forms.ValidationError("First name must be at least 2 characters.")
        if len(value) > 50:
            raise forms.ValidationError("First name must not exceed 50 characters.")
        return value.title()

    def clean_last_name(self):
        value = self.cleaned_data.get("last_name", "").strip()
        if not value:
            raise forms.ValidationError("Last name is required.")
        validate_letters_only(value, "Last name")
        if len(value) < 2:
            raise forms.ValidationError("Last name must be at least 2 characters.")
        if len(value) > 50:
            raise forms.ValidationError("Last name must not exceed 50 characters.")
        return value.title()

    def clean_phone_number(self):
        phone = self.cleaned_data.get("phone_number", "").strip()
        if phone:
            validate_phone(phone)
        return phone

    def clean_height(self):
        height = self.cleaned_data.get("height")
        if height is not None:
            if not isinstance(height, (int, float)):
                raise forms.ValidationError("Height must be a number.")
            if height <= 0:
                raise forms.ValidationError("Height must be a positive number.")
            if height > 300:
                raise forms.ValidationError("Height must not exceed 300 cm.")
        return height

    def clean_weight(self):
        weight = self.cleaned_data.get("weight")
        if weight is not None:
            if not isinstance(weight, (int, float)):
                raise forms.ValidationError("Weight must be a number.")
            if weight <= 0:
                raise forms.ValidationError("Weight must be a positive number.")
            if weight > 700:
                raise forms.ValidationError("Weight must not exceed 700 kg.")
        return weight

    def clean_fitness_goal(self):
        goal = self.cleaned_data.get("fitness_goal", "").strip()
        if goal and len(goal) > 1000:
            raise forms.ValidationError("Fitness goal must not exceed 1000 characters.")
        return goal
    

class PasswordChangeForm(forms.Form):
    current_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Current Password",
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="New Password",
        validators=[validate_strong_password],
        help_text=(
            "Must be at least 8 characters and include uppercase, lowercase, "
            "a digit, and a special character."
        ),
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput,
        label="Confirm New Password",
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        current = self.cleaned_data.get("current_password")
        if not self.user.check_password(current):
            raise forms.ValidationError("Your current password is incorrect.")
        return current

    def clean_new_password(self):
        new_pw = self.cleaned_data.get("new_password")
        current = self.data.get("current_password")  # raw, pre-clean
        if new_pw and current and new_pw == current:
            raise forms.ValidationError(
                "New password must be different from your current password."
            )
        return new_pw

    def clean(self):
        cleaned = super().clean()
        new_pw = cleaned.get("new_password")
        confirm = cleaned.get("confirm_new_password")
        if new_pw and confirm and new_pw != confirm:
            self.add_error("confirm_new_password", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data["new_password"])
        if commit:
            self.user.save()
        return self.user