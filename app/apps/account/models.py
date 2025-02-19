from django.contrib.auth.models import AbstractUser
from django.db import models

from .constants import UserRole

class User(AbstractUser):
    role = models.CharField(max_length=10, choices=UserRole.choices, default=UserRole.USER)