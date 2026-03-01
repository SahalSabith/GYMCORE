from django.db import models
from django.conf import settings


class TrainingSession(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='requested_sessions',
        limit_choices_to={'role': 'MEMBER'},
    )
    trainer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='trainer_sessions',
        limit_choices_to={'role': 'TRAINER'},
    )
    date = models.DateField()
    time = models.TimeField()
    notes = models.TextField(blank=True, help_text='Goal or notes for this session')
    status = models.CharField(max_length=15, choices=Status.choices, default=Status.PENDING)
    trainer_note = models.TextField(blank=True, help_text='Trainer can add a note when approving/rejecting')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date', '-time']

    def __str__(self):
        return f'{self.member.get_full_name()} with {self.trainer.get_full_name()} on {self.date}'

    @property
    def status_color(self):
        return {
            'PENDING': 'yellow',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'COMPLETED': 'blue',
            'CANCELLED': 'gray',
        }.get(self.status, 'gray')
