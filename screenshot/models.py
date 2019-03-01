from django.db import models


class Screenshot(models.Model):
    place_name = models.CharField(max_length=100, blank=True)
    lat = models.DecimalField(decimal_places=6, max_digits=1000)
    lag = models.DecimalField(decimal_places=6, max_digits=1000)
    zoom_level = models.IntegerField(default=17)
    sha1 = models.CharField(max_length=64, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, blank=True)
