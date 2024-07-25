from django.contrib.auth.models import AbstractUser
from django.db import models


class SubscriptionType(models.TextChoices):
    FREE = "Free"
    LITE = "Lite"
    PRO = "Pro"
    BUSINESS = "Business"


class User(AbstractUser):
    telegram_id = models.CharField(max_length=255, primary_key=True)

    USERNAME_FIELD = "telegram_id"
    REQUIRED_FIELDS = ["username"]

    def __str__(self):
        return f"{self.username} - {self.telegram_id}"
