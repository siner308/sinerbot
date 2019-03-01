from django.contrib import admin

# Register your models here.
from .models import Log

class LogAdmin(admin.ModelAdmin):
    list_display = ('log', 'agent_name', 'user_key', 'created')
    ordering = ['-created']

admin.site.register(Log, LogAdmin)