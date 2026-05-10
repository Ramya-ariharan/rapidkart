from django.contrib.auth.models import AbstractUser
from django.db import models
from .managers import UserManager


import random
from django.utils import timezone
from datetime import timedelta


class User(AbstractUser):

    username = None

    ROLE_CHOICES = (
        ('customer', 'Customer'),
        ('delivery_partner', 'Delivery Partner'),
        ('admin', 'Admin'),
    )

    email = models.EmailField(
        unique=True
    )

    phone = models.CharField(
        max_length=15,
        unique=True,
        null=True,
        blank=True
    )

    role = models.CharField(
        max_length=30,
        choices=ROLE_CHOICES,
        default='customer'
    )

    is_available = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'

    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    


class DeliveryOTP(models.Model):

    phone = models.CharField(max_length=15)

    otp = models.CharField(max_length=6)

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    is_verified = models.BooleanField(
        default=False
    )

    def is_expired(self):

        return timezone.now() > (
            self.created_at + timedelta(minutes=5)
        )

    def __str__(self):

        return f"{self.phone} - {self.otp}"