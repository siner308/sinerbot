from django.conf.urls import url, include
from django.urls import path
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('kakao.urls')),
    url(r'^api-auth/', include('rest_framework.urls'))
]

SOCIAL_AUTH_URL_NAMESPACE = 'social'
LOGIN_REDIRECT_URL='/'