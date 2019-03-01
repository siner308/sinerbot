# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models

# Create your models here.
class KakaoUser(models.Model):
    CHOICES = (
        ('U', 'Unknown'),
        ('R', 'Resistance'),
        ('E', 'Enlightened')
    )
    user_key = models.CharField(max_length=50)
    agent_name = models.CharField(max_length=100, blank=True)
    team = models.CharField(max_length=20, choices=CHOICES, default='U')
    view_count = models.IntegerField(default=0)
    is_friend = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True, blank=True)
    updated = models.DateTimeField(auto_now=True, blank=True)

    def __str__(self):
        return self.user_key

class Post(models.Model):
    post = models.CharField(max_length=100000)
    agent_name = models.CharField(max_length=100, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.post