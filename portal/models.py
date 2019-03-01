from django.db import models


class Portal(models.Model):
    portal_name = models.CharField(max_length=100, blank=True)
    guid = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)
    description = models.CharField(max_length=100, blank=True)


class Cookie(models.Model):
    sacsid = models.TextField(blank=True)
    csrftoken = models.TextField(blank=True)
    v = models.TextField(blank=True)
    account = models.CharField(max_length=50, blank=True)
    updated = models.DateTimeField(auto_now_add=True)
