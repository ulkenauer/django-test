import enum
from django.contrib.auth.models import User
from django.db import models


class SubscriptionStatus(enum.Enum):
    new = "new"
    viewed = "viewed"


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscriber"
    )
    subscribed = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="subscribed"
    )
    status = models.CharField(max_length=255)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["subscriber", "subscribed"], name="unique_subscription"
            )
        ]

    def __str__(self):
        return self.headline
