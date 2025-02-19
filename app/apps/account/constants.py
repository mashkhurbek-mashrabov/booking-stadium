from django.db import models
from django.utils.translation import gettext_lazy as _

class UserRole(models.TextChoices):
    USER = 'user', _('User')
    ADMIN = 'admin', _('Admin')
    OWNER = 'owner', _('Owner')