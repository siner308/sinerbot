import json, urllib
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView
from django.http import JsonResponse
from django.core import serializers
from django.shortcuts import render
from rest_framework.permissions import AllowAny
from rest_framework.decorators import api_view, permission_classes, authentication_classes
from rest_framework.authentication import TokenAuthentication, SessionAuthentication




@api_view(['GET'])
@authentication_classes((TokenAuthentication, SessionAuthentication))
@permission_classes((AllowAny,))
def immune_view(request):
    url = 'http://ingress-test.sakura.ne.jp/release/plugin/portal_immunity/portalImmunity_default.json'
    with urllib.request.urlopen(url) as url:
        data = json.loads(url.read().decode())
    return Response(data=data)