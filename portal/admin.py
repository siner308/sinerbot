from django.contrib import admin
from .models import Portal, Cookie


class PortalAdmin(admin.ModelAdmin):
    list_display = ('portal_name', 'guid', 'description', 'created')
    ordering = ['-created']


class CookieAdmin(admin.ModelAdmin):
    list_display = ('sacsid', 'csrftoken', 'v', 'account', 'updated')
    ordering = ['-updated']


admin.site.register(Portal, PortalAdmin)
admin.site.register(Cookie, CookieAdmin)
