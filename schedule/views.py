from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import mechanize
import urllib

from bs4 import BeautifulSoup
from pprint import pprint



def bbb_login(br):
    def is_login_form(form):
        return "action" in form.attrs and 'login' in form.attrs['action']

    br.open(settings.BBB_ROOT_URL + '/b/signin')
    br.select_form(predicate=is_login_form)
    br.form['session[email]'] = settings.BBB_USERNAME
    br.form['session[password]'] = settings.BBB_PASSWORD
    response = br.submit()
    assert 'Sign out' in response.read().decode('utf-8')

def bbb_get_room(br, room_name):
    response = br.response()
    soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
    for tag in soup.find_all(id='room-name-text'):
        if tag.contents[0] == room_name:
            link = tag.find_parents('a')[0]
            return BBB_ROOT_URL + link['href']

def bbb_create_room(br, room_name):
    def is_room_create_form(form):
        try:
            form.find_control("room[name]")
        except mechanize._form_controls.ControlNotFoundError:
            return False
        else:
            return True

    br.select_form(predicate=is_room_create_form)
    br.form['room[name]'] = room_name
    room_anyone_can_start = br.form.find_control('room[anyone_can_start]', nr=0) # Uses duplicate hidden field
    room_anyone_can_start.readonly = False
    room_anyone_can_start.value = '1'
    response = br.submit()
    assert room_name in response.read().decode('utf-8')

    return response.geturl()

def get_bbb_room_url(room_name):
    br = mechanize.Browser()
    br.set_handle_robots(False)

    bbb_login(br)
    room_url = bbb_get_room(br, room_name)
    if not room_url:
        room_url = bbb_create_room(br, room_name)

    return room_url

@csrf_exempt
def calendly_webhook(request):
    event_dict = json.loads(request.body)
    event_start_time = event_dict['payload']['event']['start_time']
    event_end_time = event_dict['payload']['event']['end_time']
    event_uuid = event_dict['payload']['event']['uuid']
    event_invitee_name = event_dict['payload']['invitee']['name']
    event_invitee_email = event_dict['payload']['invitee']['email']
    event_host_name = event_dict['payload']['event']['assigned_to'][0]
    event_name = '{} and {}'.format(event_invitee_name, event_host_name)
    room_name = '{} ({})'.format(event_invitee_name, event_invitee_email)

    print(get_bbb_room_url(room_name))
    return HttpResponse("OK")
