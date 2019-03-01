import json
import datetime
import re

from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt

from intelbot.settings.base import get_secret
from selenium import webdriver

from logs.models import Log

# Create your views here.
from screenshot.models import Screenshot
from .models import KakaoUser, Post
from portal.getportaldetail import get_portal_details
from portal.views import add_portal, create_or_update_account
from portal.models import Portal


function_buttons = [
    '지도',
    '포탈',
    '링크거리',
    '명령어입력',
    '개발자에게 한마디'
]

def default(request):
    return render(request, 'kakao/homepage.html', )

def statics(request):
    return render(request, 'kakao/statics.html', )

@csrf_exempt
def keyboard(request):
    return JsonResponse({"type": "buttons",
                         "buttons": function_buttons})

@csrf_exempt
def message(request):
    user_key_1 = get_secret("KAKAO_USER_KEY", "1")
    user_key_2 = get_secret("KAKAO_USER_KEY", "2")
    # get content_name
    json_str = request.body.decode('utf-8')
    received_json_data = json.loads(json_str)
    content_name = '%s' % received_json_data['content']
    user_key = received_json_data['user_key']

    # get or create
    try:
        user = KakaoUser.objects.get(user_key=user_key)
    except:
        user = KakaoUser.objects.create(user_key=user_key)

    if not user.is_friend:
        message = {'text': '친구로 등록되어있지 않습니다.\n'\
                          '만약 친구추가가 되어있는 상태라면, 차단했다가 다시 추가해주세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))

    # !승인 커맨드를 입력하여 유저를 승인할때.
    if content_name.startswith('!승인 '):
        # 개발자의 유저키와 일치한다면. (sinerbot, sinertest)
        if user_key == user_key_1 or user_key == user_key_2:
            agent_name = content_name[4:]
            try:
                unverified_user = KakaoUser.objects.get(agent_name=agent_name)
            except:
                message = {'text': '그런 유저는 없습니다.'}
                keyboard = {"type": "buttons",
                            "buttons": function_buttons}
                return JsonResponse(make_message(message, keyboard))

            unverified_user.team = 'R'
            unverified_user.save()
            message = {'text': unverified_user.agent_name + '님이 승인되었습니다.'}
            keyboard = {"type": "buttons", "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))
        else:
            message = {'text': '당신은 관리자가 아닙니다.'}
            keyboard = {"type": "buttons",
                        "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))

    # !agent 커맨드를 입력하여 등록/수정을 요청할때
    if content_name.startswith('!agent '):
         new_agent_name = content_name[7:]
         if new_agent_name.isalnum():
             try:
                 KakaoUser.objects.get(agent_name=new_agent_name)
             except:
                 if not user.agent_name:
                     log = new_agent_name + '님의 에이전트명이 등록되었습니다.'
                 else:
                     log = user.agent_name + '님의 에이전트명이 ' + new_agent_name + '로\n변경되었습니다.'
                 Log.objects.create(log=log, agent_name=new_agent_name, user_key=user_key)
                 user.agent_name = new_agent_name
                 user.save()
                 message = {'text': log}
                 keyboard = {"type": "buttons", "buttons": function_buttons}
                 return JsonResponse(make_message(message, keyboard))

             message = {'text': '이미 같은 이름을 가진 에이전트가 존재합니다.\n다시 입력하세요.\n\n'
                               '버튼모드로 돌아가려면 아무거나 입력하세요.'}
             keyboard = {'type': 'text'}
             return JsonResponse(make_message(message, keyboard))
         else:
             message = {'text': '에이전트명은 영문과 숫자로만 이루어져 있습니다.\n'
                                '예) !agent SinerDJ\n\n'
                                '버튼모드로 돌아가려면 아무거나 입력하세요.'}
             keyboard = {'type': 'text'}
             return JsonResponse(make_message(message, keyboard))

    # agent_name check
    if not user.agent_name:
        message = {'text': '등록된 에이전트가 아닙니다.\n'
                '명령어와 에이전트명을 조합하여 등록해주세요.\n'
                '만약 에이전트명이 foobar라면, 다음과 같습니다.\n'
                '예시 => !agent SinerDJ\n\n'
                '버튼모드로 돌아가려면 아무거나 입력하세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))


    # 미승인 유저
    if user.team == 'U':
        message = {'text': '승인되지 않은 유저입니다.\n'\
                           '개발자에게 문의하세요.'}
        keyboard = {"type": "text"}
        return JsonResponse(make_message(message, keyboard))

    if user.team == 'E':
        message = {'text': '당신은 인라이튼드로 추정됩니다.\n'\
                   '잘못된 정보라면, 개발자나 지역담당 및 요원에게 문의해주세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))

    # !링크거리
    if content_name.startswith('!링크거리 '):
        option = content_name[6:]
        link_distance = link_distanc_calculator(option)
        message = {'text': link_distance}
        keyboard = {'type': 'buttons', 'buttons': function_buttons}
        return JsonResponse(make_message(message, keyboard))

    # 링크거리 도움말
    if content_name == '링크거리':
        message = {'text': 'Usage : (디플된레저의레벨) (모드종류) (例. !링크거리 87665544 rr) 모드 종류는 r s v\n'
                           'V : Very Rare Link Amp\n'
                           'S : Softbank Link Amp\n'
                           'R : Rare Link Amp\n\n'
                           '버튼모드로 돌아가려면 아무거나 입력하세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))

    # 명령어 도움말
    if content_name == '명령어입력':
        message = {'text': '!agent (에이전트명)\n'
                           '!승인 (에이전트명)\n'
                           '!전달 (하고싶은말)\n'
                           '!링크거리 (디플된레저의레벨) (모드종류)\n'
                           '!포탈등록 (포탈 guid)\n'
                           '!포탈 (등록된파밍장 or 포탈 guid)\n'
                           '!등록\n'
                           '!활성화\n'
                           '!비활성화\n'
                           '!토큰 (SACSID) (email)\n'
                           '찍어라 사이너봇\n\n'
                           '버튼모드로 돌아가려면 아무거나 입력하세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))

    # 지도 선택모드
    if content_name == '지도':
        user.view_count += 1
        user.save()

        places = Screenshot.objects.filter(is_active=True)
        map_buttons = []

        map_buttons.append('← 메뉴로 돌아가기')
        for place in places:
            map_buttons.append(place.place_name)

        map_buttons = sorted(map_buttons)

        message = {'text': '보고싶은 지역을 선택하세요.'}
        keyboard = {'type': 'buttons','buttons': map_buttons}
        return JsonResponse(make_message(message, keyboard))

    if content_name == '포탈':
        user.view_count += 1
        user.save()

        places = Portal.objects.all()
        map_buttons = []
        map_buttons.append('← 메뉴로 돌아가기')

        for place in places:
            map_buttons.append('포탈 : %s' % place.portal_name)

        map_buttons = sorted(map_buttons)
        message = {'text': '보고싶은 포탈을 선택하세요.\n(테스트중인 기능입니다.)'}
        keyboard = {'type': 'buttons','buttons': map_buttons}
        return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('포탈 : '):
        portal_name = content_name[5:]
        portal = Portal.objects.get(portal_name=portal_name)
        data, img_url = get_portal_details(portal.guid)
        message = {'text': data,
                   "photo": {'url': img_url, 'width': 720, 'height': 630},
                   'message_button': {"label": "크게보기", "url": img_url}}
        keyboard = {'type': 'buttons', 'buttons': function_buttons}
        return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('!토큰 '):
        # 개발자의 유저키와 일지한다면. (sinerbot, sinertest)
        if user_key == user_key_1 or user_key == user_key_2:
            str = content_name[4:]
            list = str.split(' ')
            if len(list) == 1:
                create_or_update_account(list[0])
            else:
                create_or_update_account(list[0], list[1])
            message = {'text': '토큰이 등록되었습니다.'}
            keyboard = {"type": "buttons",
                        "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))
        else:
            message = {'text': '당신은 관리자가 아닙니다.'}
            keyboard = {"type": "buttons",
                        "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('!등록 '):
        # 개발자의 유저키와 일지한다면. (sinerbot, sinertest)
        if user_key == user_key_1 or user_key == user_key_2:
            option = content_name[4:]
            parts = option.strip().split(' ')
            print(parts)
            place_name = parts[0]
            lat = parts[1]
            lag = parts[2]
            zoom_level = parts[3]
            sha1 = hash(place_name)
            print(sha1)

            try:
                place = Screenshot.objects.get(sha1=sha1)
            except:
                place = None

            if place:
               message = {'text': '이미 존재하는 장소입니다.'}
            else:
                Screenshot.objects.create(place_name=place_name, lat=lat, lag=lag, zoom_level=zoom_level, sha1=sha1)
                message = {'text': place_name + '이(가) 등록되었습니다.'}
            keyboard = {'type': 'buttons', 'buttons': function_buttons}
            return JsonResponse(make_message(message, keyboard))
        else:
            message = {'text': '당신은 관리자가 아닙니다.'}
            keyboard = {"type": "buttons",
                        "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))

    # start screenshot
    if content_name == '찍어라 사이너봇':
        if user_key == user_key_1 or user_key == user_key_2:
            print('start screenshot!!')
            return redirect('screenshot')
        else:
            message = {'text': '막 찍으면 큰일나요!'}
            keyboard = {"type": "buttons",
                        "buttons": function_buttons}
            return JsonResponse(make_message(message, keyboard))

    # 지도 선택했으면 이미지 주소를 가져옴
    place = content_to_obj(content_name)

    # 이미지 주소를 받아왔을때
    if place:
        year = place.updated.year
        month = place.updated.month
        day = place.updated.day
        hour = place.updated.hour
        minute = place.updated.minute
        second = place.updated.second

        unix_time = datetime.datetime(year, month, day, hour, minute, second).strftime('%s')
        print('%s[%s]' % (place.sha1, unix_time))
        host = 'http://sinersound.com/static/img/'
        # img_url = host + place.sha1 + '[%s]' % unix_time
        img_url = host + place.sha1 + '_%s%s%s%s%s%s' % (year, month, day, hour, minute, second)
        old_format = '%Y-%m-%d %H:%M:%S.%f'
        new_format = '%y/%m/%d %H:%M:%S'
        place_updated = datetime.datetime.strptime('%s' % place.updated, old_format).strftime(new_format)
        message = {'text': '%s' % place.place_name + '\n\n' + \
                           '%s' % place_updated,
                   "photo": {'url': img_url + '_cropped.png', 'width': 720, 'height': 630},
                   'message_button': {"label": "크게보기", "url": img_url + '_origin.png'}}

        keyboard = {"type": "buttons", "buttons": function_buttons}
        return JsonResponse(make_message(message, keyboard))

    # !전달 명령어를 사용해서 개발자에게 한마디
    if content_name == '개발자에게 한마디':
        message = {'text': '!전달 명령어를 사용하여 개발자에게 한마디를 남겨주세요.\n\n'
                           '예) !전달 빨리 개발해주세요!!!!\n\n'
                           '버튼모드로 돌아가려면 아무거나 입력하세요.'}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))

    # !전달 명령어가 들어왔을때
    if content_name.startswith('!전달 '):
        post = content_name[4:]
        Post.objects.create(post=post, agent_name=user.agent_name)
        log = post
        Log.objects.create(log=log, agent_name=user.agent_name, user_key=user.user_key)
        message = {'text': '메시지가 전달되었습니다.'}
        keyboard = {'type': 'buttons', 'buttons': function_buttons}
        return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('!비활성화 '):
        if user_key == user_key_1 or user_key == user_key_2:
            str = content_name[6:]
            places = Screenshot.objects.filter(place_name__icontains=str)
            print(places)
            target = ''
            for place in places:
                place.is_active = False
                place.save()
                target = target.join(place.place_name + '\n')
            message = {'text': target + '\n가 비활성화 되었습니다.'}
            keyboard = {'type': 'text'}
            return JsonResponse(make_message(message, keyboard))
        else:
            message = {'text': '당신은 관리자가 아닙니다.'}
            keyboard = {'type': 'buttons', 'buttons': function_buttons}
            return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('!활성화 '):
        if user_key == user_key_1 or user_key == user_key_2:
            str = content_name[5:]
            places = Screenshot.objects.filter(place_name__icontains=str)
            target = ''
            for place in places:
                place.is_active = True
                place.save()
                target = target.join(place.place_name + '\n')
            message = {'text': target + '\n가 활성화 되었습니다.'}
            keyboard = {'type': 'text'}
            return JsonResponse(make_message(message, keyboard))
        else:
            message = {'text': '당신은 관리자가 아닙니다.'}
            keyboard = {'type': 'buttons', 'buttons': function_buttons}
            return JsonResponse(make_message(message, keyboard))

    if content_name.startswith('!포탈등록 '):
        guid = content_name[6:]
        message = add_portal(guid)
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))


    if content_name.startswith('!포탈 '):
        portal_name = content_name[4:]
        try:
            portal = Portal.objects.get(portal_name=portal_name)
            portal_name = portal.guid
        except:
            pass

        if portal_name == '가락시장':
            data = ''
            guids = ['fc79068c8438438ea4e9519271024040.16',
                    'ade258e7016444a6885b10a2dcbf835d.16',
                    'c793be863abc4a2cb5e9ef476d935954.16']
            for guid in guids:
                portal_detail, img_url = get_portal_details(guid)
                data += portal_detail + '\n\n'
        elif portal_name == '봉산':
            data = ''
            guids = ['a73b748ac8784f46b0250ddc1af03c68.16',
                    'fff822acd3fd484faec8799ee569af38.16',
                    'afe200b00cde4e9081c192356e8669ef.16',
                     'd63c3280460b4e1fa52948235014183f.16']
            for guid in guids:
                portal_detail, img_url = get_portal_details(guid)
                data += portal_detail + '\n\n'
        else:
            data, img_url = get_portal_details(portal_name)

        message = {'text': data,
                   "photo": {'url': img_url, 'width': 720, 'height': 630},
                   'message_button': {"label": "크게보기", "url": img_url}}
        keyboard = {'type': 'text'}
        return JsonResponse(make_message(message, keyboard))


    # 예외처리 (text입력창에서 조건에 없는 텍스트 입력시)
    message = {'text': '버튼모드로 돌아갑니다.'}
    keyboard = {'type': 'buttons', 'buttons': function_buttons}
    return JsonResponse(make_message(message, keyboard))

@csrf_exempt
def add_friend(request):
    json_str = request.body.decode('utf-8')
    received_json_data = json.loads(json_str)
    user_key = received_json_data['user_key']

    if request.method == 'POST':
        try:
            old_user = KakaoUser.objects.get(user_key=user_key)
        except KakaoUser.DoesNotExist:
            old_user = None

        if old_user is None:
            KakaoUser.objects.create(user_key=user_key, is_friend=True)
        else:
            old_user.is_friend = True
            old_user.save()
        return HttpResponse(status=200)
    return HttpResponse(status=400)

@csrf_exempt
def delete_friend(request, user_key):
    if request.method == 'DELETE':
        try:
            user = KakaoUser.objects.get(user_key=user_key)
            user.is_friend = False
            user.save()
            return HttpResponse(status=200)
        except:
            return HttpResponse(status=404)
    return HttpResponse(status=400)

def make_message(message_message, message_keyboard):
    message = {
        'message': message_message,
        'keyboard': message_keyboard
    }
    return message

def content_to_obj(content_name):
    try:
        place = Screenshot.objects.get(place_name=content_name)
        return place
    except:
        return None

def create_or_modify_agent_name(user, agent_name):
    try:
        KakaoUser.objects.get(agent_name=agent_name)
    except:
        user.agent_name = agent_name
        user.save(force_update=True)
        message = {'text': '에이전트명이 등록되었습니다.'}
        keyboard = {"type": "buttons", "buttons": function_buttons}
        return JsonResponse(make_message(message, keyboard))

    message = {'text': '이미 같은 이름을 가진 에이전트가 존재합니다.\n다시 입력하세요.'}
    keyboard = {'type': 'text'}
    return JsonResponse(make_message(message, keyboard))

def link_distanc_calculator(argv):
    table = {
        '': 1.000,
        'R': 2.000,
        'RR': 2.500,
        'RRR': 2.750,
        'RRRR': 3.000,
        'S': 5.000,
        'SR': 5.500,
        'SRR': 5.750,
        'SRRR': 6.000,
        'SS': 6.250,
        'SSR': 6.500,
        'SSRR': 6.750,
        'SSS': 6.825,
        'SSSR': 7.125,
        'SSSS': 7.500,
        'V': 7.000,
        'VR': 7.500,
        'VRR': 7.750,
        'VRRR': 8.000,
        'VS': 8.250,
        'VSR': 8.500,
        'VSRR': 8.750,
        'VSS': 8.875,
        'VSSR': 9.125,
        'VSSS': 9.500,
        'VV': 8.750,
        'VVR': 9.000,
        'VVRR': 9.250,
        'VVS': 9.375,
        'VVSR': 9.625,
        'VVSS': 10.000,
        'VVV': 9.625,
        'VVVR': 9.875,
        'VVVS': 10.250,
        'VVVV': 10.500,
    }
    parts = argv.strip().split(' ')
    resonators = parts[0]
    mods = ''
    try:
        mods = ''.join(sorted(parts[1].upper(), key=lambda m: {'V': 1, 'S': 2, 'R': 3}[m]))
    except:
        pass

    return '%s km' % round(160 * ((sum(map(int, resonators)) / 8.0) ** 4) / 1000.0 * table[mods], 3)
