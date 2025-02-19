from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class StadiumConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stadium'
    verbose_name = _('Stadium')
