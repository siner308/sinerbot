# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib import admin
from .models import KakaoUser, Post
# Register your models here.


class KakaoUserAdmin(admin.ModelAdmin):
    list_display = ('user_key', 'agent_name', 'view_count', 'get_team_display', 'is_friend', 'updated', 'created')
    ordering = ['-updated']

class PostAdmin(admin.ModelAdmin):
    list_display = ('post', 'agent_name', 'created')
    ordering = ['-created']


admin.site.register(Post, PostAdmin)
admin.site.register(KakaoUser, KakaoUserAdmin)