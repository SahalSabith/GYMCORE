import re
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, min_length=8)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    role = forms.ChoiceField(
        choices=[('TRAINER', 'Trainer'), ('MEMBER', 'Member')],
        help_text='Admins are created via the admin panel only.'
    )

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'phone_number', 'role', 'password', 'password_confirm']

    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError('An account with this email already exists.')
        return email

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not re.match(r'^\+?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError('Enter a valid phone number.')
        return phone

    def clean(self):
        cleaned = super().clean()
        pw = cleaned.get('password')
        pw_confirm = cleaned.get('password_confirm')
        if pw and pw_confirm and pw != pw_confirm:
            self.add_error('password_confirm', 'Passwords do not match.')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)
        # Derive username from email to satisfy AbstractUser requirement
        user.username = self.cleaned_data['email'].split('@')[0]
        user.set_password(self.cleaned_data['password'])
        user.role = self.cleaned_data['role']
        if commit:
            # Ensure username uniqueness
            base = user.username
            counter = 1
            while User.objects.filter(username=user.username).exists():
                user.username = f'{base}{counter}'
                counter += 1
            user.save()
        return user


class LoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email', widget=forms.EmailInput(attrs={'autofocus': True}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'placeholder': 'your@email.com'})
        self.fields['password'].widget.attrs.update({'placeholder': '••••••••'})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'profile_photo', 'height', 'weight', 'fitness_goal']
        widgets = {
            'fitness_goal': forms.Textarea(attrs={'rows': 3}),
        }

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number', '').strip()
        if phone and not re.match(r'^\+?[\d\s\-]{7,15}$', phone):
            raise forms.ValidationError('Enter a valid phone number.')
        return phone
