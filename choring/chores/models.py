from django.db import models
from django.contrib.auth import get_user_model


class Chore(models.Model):
    RECURRENCE_NONE = 'none'
    RECURRENCE_WEEKLY = 'weekly'
    RECURRENCE_MONTHLY = 'monthly'
    RECURRENCE_CHOICES = [
        (RECURRENCE_NONE, 'None'),
        (RECURRENCE_WEEKLY, 'Weekly'),
        (RECURRENCE_MONTHLY, 'Monthly'),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    assigned_to = models.ForeignKey(get_user_model(), null=True, blank=True, on_delete=models.SET_NULL)
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)
    recurrence = models.CharField(max_length=10, choices=RECURRENCE_CHOICES, default=RECURRENCE_NONE)
    active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def next_occurrence_after(self, date):
        """Return the next occurrence date on or after given date, or None."""
        from datetime import timedelta
        from dateutil.relativedelta import relativedelta

        if not self.active:
            return None

        if self.recurrence == self.RECURRENCE_NONE:
            if self.due_date and self.due_date >= date:
                return self.due_date
            return None

        # recurring
        base = self.start_date or self.due_date
        if not base:
            return None

        current = base
        # if base is before date, advance
        while current < date:
            if self.recurrence == self.RECURRENCE_WEEKLY:
                current = current + timedelta(days=7)
            else:
                current = current + relativedelta(months=1)
        return current


# Create your models here.
