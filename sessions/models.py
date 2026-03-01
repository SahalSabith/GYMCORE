from django.db import models
from django.conf import settings
from django.utils import timezone


class TrainingSession(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='booked_sessions', limit_choices_to={'role': 'MEMBER'},
    )
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='training_sessions', limit_choices_to={'role': 'TRAINER'},
    )
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, help_text='What you want to work on')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    trainer_response = models.TextField(blank=True, help_text='Trainer note on approval/rejection')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f'{self.member.get_full_name()} with {self.trainer.get_full_name()} on {self.date}'

    @property
    def is_upcoming(self):
        from datetime import datetime
        session_dt = timezone.make_aware(datetime.combine(self.date, self.time))
        return session_dt > timezone.now() and self.status == self.Status.APPROVED
