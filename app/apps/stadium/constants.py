from django.db import models
from django.utils.translation import gettext_lazy as _

class StadiumStatus(models.IntegerChoices):
    AVAILABLE = 1, _('Available')
    UNAVAILABLE = 2, _('Unavailable')
    IN_USE = 3, _('In Use')
    ARCHIVED = 4, _('Archived')