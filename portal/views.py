from django.shortcuts import render
from .models import Portal, Cookie
from .getportaldetail import post_portal_guid


def add_portal(guid):
    data = post_portal_guid(guid)

    try:
        Portal.objects.get(portal_name=data[8])
        message = {'text': '이미 등록된 포탈입니다.'}
    except:
        Portal.objects.create(portal_name=data[8], guid=guid)
        message = {'text': '%s 이(가) 등록되었습니다.' % data[8]}
    return message

def create_or_update_account(sacsid, account=None):
    cookie = Cookie.objects.get(pk=1)
    cookie.sacsid = sacsid
    if account:
        cookie.account = account
    cookie.save()
