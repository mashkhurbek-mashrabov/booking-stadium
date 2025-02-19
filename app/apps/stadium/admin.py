from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Stadium, StadiumPhoto


class StadiumPhotoInline(admin.TabularInline):
    model = StadiumPhoto
    extra = 0


@admin.register(Stadium)
class StadiumAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'location_link', 'price_per_hour', 'status', 'created_at', 'updated_at')
    list_filter = ('status', 'created_at', 'updated_at')
    search_fields = ('name', 'contact')
    search_help_text = _("Search by name or contact")
    readonly_fields = ('created_at', 'updated_at')

    fieldsets = (
        (_('Stadium Information'), {
            'fields': ('owner', 'name', 'status', 'price_per_hour', 'address', 'location', 'contact', 'description'),
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
    add_fieldsets = (
        (_('Stadium Information'), {
            'fields': ('owner', 'name', 'status', 'price_per_hour', 'address', 'location', 'contact', 'description'),
        }),
    )
    date_hierarchy = 'created_at'
    inlines = [StadiumPhotoInline]

    def location_link(self, obj):
        if obj.location:
            return f'<a href="https://www.google.com/maps?q={obj.location}" target="_blank">{obj.location}</a>'
        return "-"

    location_link.short_description = _("Location")
