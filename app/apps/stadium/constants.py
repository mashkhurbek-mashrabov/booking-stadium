from django.db import models
from django.utils.translation import gettext_lazy as _

class StadiumStatus(models.IntegerChoices):
    AVAILABLE = 1, _('Available')
    IN_USE = 2, _('In Use')
    ARCHIVED = 3, _('Archived')
    DELETED = 4, _('Deleted')