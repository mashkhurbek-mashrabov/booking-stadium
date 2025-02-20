import random
import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models
from rest_framework_simplejwt.tokens import RefreshToken
from common.models.base import BaseModel

from .constants import UserRole

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.USER)

    @property
    def full_name(self):
        return f'{self.first_name} {self.last_name}'

    def check_email(self):
        if self.email:
            self.email = self.email.lower()

    def token(self):
        refresh = RefreshToken.for_user(self)
        return {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

    def clean(self):
        self.check_email()

    def save(self, *args, **kwargs):
        if not self.pk or not self.username:
            self.clean()
        super(User, self).save(*args, **kwargs)