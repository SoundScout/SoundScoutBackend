from django.db import models
from music.models import Artist


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=20, unique=True)
    max_upload_rate = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.name} Plan (${self.price})"


class Subscription(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
    ]

    artist = models.OneToOneField(Artist, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    end_subscription = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='active')
    is_active = models.BooleanField(default=True)

    # Cached values (optional – copied from plan at creation)
    max_upload_rate = models.IntegerField(default=4)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        # Update cached values if plan is set
        if self.plan:
            self.max_upload_rate = self.plan.max_upload_rate
            self.price = self.plan.price

        # Sync is_active with status
        self.is_active = self.status == 'active'

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.artist.user.username} - {self.plan.name if self.plan else 'No Plan'} Subscription"