from django.contrib import admin
from .models import Screenshot
# Register your models here.


class ScreenshotAdmin(admin.ModelAdmin):
    list_display = ('place_name', 'lat', 'lag', 'zoom_level', 'sha1', 'is_active', 'updated', 'created')
    ordering = ['-created']


admin.site.register(Screenshot, ScreenshotAdmin)