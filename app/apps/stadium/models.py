from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MaxLengthValidator
from django.contrib.auth import get_user_model

from .constants import StadiumStatus
from common.models.base import BaseModel
from account.constants import UserRole

User = get_user_model()


class Stadium(BaseModel):
    owner = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='stadiums',
        verbose_name=_('Owner'),
        limit_choices_to={'role': UserRole.OWNER}
    )
    name = models.CharField(_('Name'), max_length=150, unique=True)
    location = models.CharField(
        _('Location'),
        max_length=100,
        help_text=_('Separate latitude and longitude with a comma'),
    )
    address = models.CharField(_('Address'), max_length=200)
    contact = models.CharField(_('Contact'), max_length=100)
    price_per_hour = models.DecimalField(_('Price per hour'), max_digits=10, decimal_places=2, default=0)
    status = models.SmallIntegerField(_('Status'), choices=StadiumStatus.choices, default=StadiumStatus.AVAILABLE)
    description = models.TextField(
        _('Description'),
        blank=True, null=True,
        validators=[MaxLengthValidator(2000)]
    )

    class Meta:
        verbose_name = _('Stadium')
        verbose_name_plural = _('Stadiums')

    def __str__(self):
        return self.name


class StadiumPhoto(BaseModel):
    stadium = models.ForeignKey(Stadium, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(_('Image'), upload_to='stadium/')
    is_main = models.BooleanField(_('Is main photo?'), default=False)

    class Meta:
        verbose_name = _('Stadium Photo')
        verbose_name_plural = _('Stadium Photos')

    def save(self, *args, **kwargs):
        if self.is_main:
            StadiumPhoto.objects.filter(stadium=self.stadium).update(is_main=False)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Photo of {self.stadium.name}"
