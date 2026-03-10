from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class MembershipPlan(models.Model):
    DURATION_CHOICES = [
        (30,  'Monthly (30 days)'),
        (90,  'Quarterly (90 days)'),
        (365, 'Yearly (365 days)'),
    ]

    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    duration_days = models.IntegerField(choices=DURATION_CHOICES)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.name} – ₹{self.price}'


class Subscription(models.Model):
    member = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        limit_choices_to={'role': 'MEMBER'},
    )
    plan = models.ForeignKey(MembershipPlan, on_delete=models.PROTECT, related_name='subscriptions')
    start_date = models.DateField(default=timezone.localdate)
    end_date = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_date']

    def save(self, *args, **kwargs):
        if not self.pk:
            self.end_date = self.start_date + timedelta(days=self.plan.duration_days)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.localdate() > self.end_date

    @property
    def days_remaining(self):
        delta = self.end_date - timezone.localdate()
        return max(delta.days, 0)

    def __str__(self):
        return f'{self.member.get_full_name()} -> {self.plan.name}'
