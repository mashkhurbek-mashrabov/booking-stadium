from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model
from decimal import Decimal

from common.models.base import BaseModel
from account.constants import UserRole
from common.utils import price_formatter
from stadium.constants import StadiumStatus

User = get_user_model()

class Booking(BaseModel):
    stadium = models.ForeignKey(
        'stadium.Stadium',
        on_delete=models.PROTECT,
        related_name='bookings',
        limit_choices_to=models.Q(status=StadiumStatus.AVAILABLE) | models.Q(status=StadiumStatus.IN_USE),
    )
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='bookings',
        limit_choices_to={'role': UserRole.USER}
    )
    start_time = models.DateTimeField(_('Start time'))
    end_time = models.DateTimeField(_('End time'))
    price_per_hour = models.DecimalField(_('Price per hour'), max_digits=10, decimal_places=2, null=True, blank=True)
    total_price = models.DecimalField(_('Total price'), max_digits=10, decimal_places=2, default=0, null=True, blank=True)
    is_cancelled = models.BooleanField(_('Is cancelled'), default=False)

    class Meta:
        verbose_name = _('Booking')
        verbose_name_plural = _('Bookings')
        ordering = ['-start_time']


    def save(self, *args, **kwargs):
        if not self.price_per_hour:
            self.price_per_hour = self.stadium.price_per_hour

        if self.end_time < self.start_time:
            raise ValueError('End time must be greater than start time')

        if self.total_price == 0:
            self.calculate_price()

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.stadium.name} - {self.formatted_start_time}"

    def calculate_price(self):
        time_difference_seconds = (self.end_time - self.start_time).total_seconds()
        time_difference_hours = Decimal(time_difference_seconds) / Decimal(3600)  # Convert to Decimal

        self.total_price = time_difference_hours * self.price_per_hour


    @property
    def formatted_start_time(self):
        return self.start_time.strftime('%H:%M %d-%m-%Y')

    formatted_start_time.fget.short_description = _('Start time')

    @property
    def formatted_end_time(self):
        return self.end_time.strftime('%H:%M %d-%m-%Y')

    formatted_end_time.fget.short_description = _('End time')

    @property
    def formatted_total_price(self):
        return price_formatter(self.total_price)

    formatted_total_price.fget.short_description = _('Total price')
