from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    avatar = models.URLField(blank=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class OTPVerification(models.Model):
    PURPOSE_CHOICES = (
        ("signup", "Signup"),
        ("forgot_password", "Forgot Password"),
    )

    email = models.EmailField()
    code = models.CharField(max_length=5)
    purpose = models.CharField(max_length=30, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.code}"
