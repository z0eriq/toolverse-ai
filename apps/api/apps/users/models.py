from __future__ import annotations

from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.users.managers import UserManager


class User(AbstractBaseUser, PermissionsMixin, TimeStampedModel):
    class Role(models.TextChoices):
        USER = "user", "User"
        ADMIN = "admin", "Admin"

    email = models.EmailField(unique=True, db_index=True)
    name = models.CharField(max_length=150, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = UserManager()

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS: list[str] = []

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.email

    @property
    def is_admin(self) -> bool:
        return self.role == self.Role.ADMIN or self.is_superuser


class Profile(TimeStampedModel):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    bio = models.TextField(blank=True)
    avatar_url = models.URLField(blank=True)
    locale = models.CharField(max_length=10, default="en")
    theme = models.CharField(max_length=20, default="system")
    public_username = models.SlugField(max_length=64, unique=True, null=True, blank=True)
    is_public = models.BooleanField(default=False, db_index=True)
    headline = models.CharField(max_length=200, blank=True, default="")

    def __str__(self) -> str:
        return f"Profile<{self.user.email}>"
