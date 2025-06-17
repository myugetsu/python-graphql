import string
import random
from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone
from typing import List, Tuple


def generate_user_id() -> str:
    """
    Generate a custom user ID in the format u_[a-Z0-9]+.

    Returns:
        str: Generated user ID.
    """
    chars = string.ascii_letters + string.digits
    return "u_" + "".join(random.choices(chars, k=10))


def generate_app_id() -> str:
    """
    Generate a custom app ID in the format app_[a-Z0-9]+.

    Returns:
        str: Generated app ID.
    """
    chars = string.ascii_letters + string.digits
    return "app_" + "".join(random.choices(chars, k=10))


class User(models.Model):
    """
    Represents a system user who can own applications.

    Fields:
        id (str): Custom user ID (primary key).
        username (str): Unique username.
        plan (str): Account plan, either 'HOBBY' or 'PRO'.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    PLAN_CHOICES = [
        ("HOBBY", "Hobby"),
        ("PRO", "Pro"),
    ]

    id = models.CharField(primary_key=True, max_length=20, editable=False)
    username = models.CharField(max_length=150, unique=True)
    plan = models.CharField(max_length=10, choices=PLAN_CHOICES)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_user_id()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.username:
            raise ValidationError("Username cannot be empty.")
        if self.plan not in dict(self.PLAN_CHOICES):
            raise ValidationError("Invalid plan.")

    def __str__(self):
        return f"{self.username} ({self.id})"


class DeployedApp(models.Model):
    """
    Represents an application owned by a user.

    Fields:
        id (str): Custom app ID (primary key).
        active (bool): Whether the app is active.
        owner (User): Foreign key to the owning user.
        created_at (datetime): Creation timestamp.
        updated_at (datetime): Last update timestamp.
    """

    id = models.CharField(primary_key=True, max_length=20, editable=False)
    active = models.BooleanField(default=True)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="apps")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.id:
            self.id = generate_app_id()
        super().save(*args, **kwargs)

    def clean(self):
        if not self.owner_id:
            raise ValidationError("App must have an owner.")

    def __str__(self):
        return f"App {self.id} (Owner: {self.owner.username})"
