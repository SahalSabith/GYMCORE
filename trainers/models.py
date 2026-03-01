from django.db import models
from django.conf import settings


class TrainerProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_profile',
        limit_choices_to={'role': 'TRAINER'},
    )
    experience_years = models.PositiveIntegerField(default=0)
    specialization = models.CharField(max_length=200, blank=True)
    bio = models.TextField(blank=True)
    certifications = models.TextField(blank=True, help_text='Comma-separated list')

    def __str__(self):
        return f'Profile: {self.user.get_full_name()}'


class TrainerAssignment(models.Model):
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_assignments',
        limit_choices_to={'role': 'TRAINER'},
    )
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='member_assignments',
        limit_choices_to={'role': 'MEMBER'},
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('trainer', 'member')
        ordering = ['-assigned_at']

    def __str__(self):
        return f'{self.trainer.get_full_name()} → {self.member.get_full_name()}'
