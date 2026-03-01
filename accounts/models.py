from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Admin'
        TRAINER = 'TRAINER', 'Trainer'
        MEMBER = 'MEMBER', 'Member'

    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_photo = models.ImageField(upload_to='profile_photos/', blank=True, null=True)
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.MEMBER)

    # Fitness-specific fields
    height = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Height in cm')
    weight = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Weight in kg')
    fitness_goal = models.TextField(blank=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip() or self.email

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_trainer(self):
        return self.role == self.Role.TRAINER

    def is_member(self):
        return self.role == self.Role.MEMBER

    def __str__(self):
        return f'{self.get_full_name()} ({self.role})'
