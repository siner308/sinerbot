import json
from django.conf.urls import url
from django.urls import path
from . import views
from screenshot.views import make_screenshot, get_cookie
from api.views import immune_view
from django.conf.urls import url, include
from rest_framework import routers, serializers, viewsets


urlpatterns = [
    path('', views.default),
    path('anomaly/', immune_view, name='immune_view'),
    path('statics/', views.statics, name='statics'),
    path('screenshot/', make_screenshot, name='screenshot'),
    path('cookie/', get_cookie, name='get_cookie'),
    # path('link/', views.link_distanc_calculator, name='link'),
    path('keyboard/', views.keyboard, name='keyboard'),
    path('message/', views.message, name='message'),
    path('friend/', views.add_friend, name='add_friend'),
    path('friend/<user_key>/', views.delete_friend, name='delete_friend')
]
