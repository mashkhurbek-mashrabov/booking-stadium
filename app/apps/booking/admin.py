from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('stadium', 'user', 'formatted_start_time', 'formatted_end_time', 'created_at', 'updated_at')

    add_fieldsets = (
        (_("Booking Details"), {
            'fields': ('stadium', 'user', 'start_time', 'end_time'),
        }),
    )

    fieldsets = (
        (_("Booking Details"), {
            'fields': ('stadium', 'user', 'start_time', 'end_time'),
        }),
        (_("Price"), {
            'fields': ('price_per_hour', 'total_price', 'is_cancelled'),
        }),
        (_("Timestamps"), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at', 'price_per_hour', 'total_price', 'is_cancelled')