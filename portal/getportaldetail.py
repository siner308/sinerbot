import requests
import json
from .models import Cookie

def post_portal_guid(guid):
    account = Cookie.objects.get(pk=1)
    url = 'https://intel.ingress.com/r/getPortalDetails'
    headers = {
        'origin': 'https://intel.ingress.com',
        'accept-encoding': 'gzip, deflate, br',
        'accept-language': 'it,en;q=0.8,it-IT;q=0.6,en-US;q=0.4',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36',
        'x-csrftoken': account.csrftoken,
        'content-type': 'application/json; charset=UTF-8',
        'accept': '*/*',
        'referer': 'https://intel.ingress.com/intel',
        'authority': 'intel.ingress.com',
    }
    cookie = {
        'csrftoken': account.csrftoken,
        'SACSID': account.sacsid
    }
    data = {
        'guid': guid,
        'v': account.v
    }

    response = requests.post(url, data=json.dumps(data), headers=headers, cookies=cookie)
    json_data = response.json()

    return json_data['result']


def get_portal_details(guid):
    data = post_portal_guid(guid)
    # portal name
    name = data[8]
    if data[1] == 'R':
        team = '레지'
    elif data[1] == 'N':
        team = '중립'
    else:
        team = '인라'

    # portal mod
    mod = ''
    for i in range(0,4):
        if data[14][i] is not None:
            slot = '%s %s : %s\n' % (data[14][i][2], data[14][i][1], data[14][i][0])
            mod += slot

    # portal image
    img_url = data[7]

    # portal resonator
    resonator = ''
    resonator_levels = 0
    resonator_hp = 0

    for slot in data[15]:
        if slot[1] == 8:
            resonator_hp = 6000
        if slot[1] == 7:
            resonator_hp = 5000
        if slot[1] == 6:
            resonator_hp = 4000
        if slot[1] == 5:
            resonator_hp = 3000
        if slot[1] == 4:
            resonator_hp = 2500
        if slot[1] == 3:
            resonator_hp = 2000
        if slot[1] == 2:
            resonator_hp = 1500
        if slot[1] == 1:
            resonator_hp = 1000

        slot[2] = '(%s/%s) %d%%' % (slot[2], resonator_hp, slot[2]/resonator_hp * 100)

        resonator += '%s: L%s %s\n' % (slot[0], slot[1], slot[2])
        resonator_levels += int(slot[1])

    portal_level = float(resonator_levels)/8.0

    owner = data[16]
    if owner == '':
        owner = 'None'

    lat = str(data[2])
    lat = lat[:2] + '.' + lat[2:]
    lng = str(data[3])
    lng = lng[:3] + '.' + lng[3:]

    google_url = 'https://maps.googleapis.com/maps/api/geocode/json?latlng=%s,%s&key=AIzaSyCUHEZ8AfodCDa8EHpB1q71a8zTkWQ0yPE' % (lat, lng)
    headers = {"Accept-Language": "ko-kr,ko;q=0.8"}
    response = requests.get(google_url, headers=headers)
    content = response.content.decode('utf-8')
    json_data = json.loads(content)
    address_1 = json_data['results'][0]['formatted_address']
    address_2 = json_data['results'][1]['formatted_address']

    text = '포탈명 : %s\n' \
           '소유자 : %s (%s)\n' \
           '레벨 : %s\n\n' \
           '모드 : \n%s\n' \
           '레조 : \n%s\n' \
           '좌표 : (%s, %s)\n\n' \
           '주소(1) : %s\n\n' \
           '주소(2) : %s\n\n' \
           '링크 : https://www.ingress.com/intel?ll=%s,%s&z=17&pll=%s,%s' % (name, owner, team, portal_level, mod, resonator, lat, lng, address_1, address_2, lat, lng, lat, lng)

    return text, img_url

