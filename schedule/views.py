from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import mechanize
import urllib

from bs4 import BeautifulSoup
from pprint import pprint

import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


def bbb_login(br):
    def is_login_form(form):
        return "action" in form.attrs and 'login' in form.attrs['action']

    signin_url = settings.BBB_ROOT_URL + '/b/signin'
    br.open(signin_url)
    br.select_form(predicate=is_login_form)
    br.form['session[email]'] = settings.BBB_USERNAME
    br.form['session[password]'] = settings.BBB_PASSWORD
    response = br.submit()
    assert br.geturl() != signin_url, 'BBB login failed'

def bbb_get_room(br, room_name):
    response = br.response()
    soup = BeautifulSoup(response.read().decode('utf-8'), 'html.parser')
    for tag in soup.find_all(id='room-name-text'):
        if tag.contents[0] == room_name:
            link = tag.find_parents('a')[0]
            return settings.BBB_ROOT_URL + link['href']

def bbb_create_room(br, room_name):
    def is_room_create_form(form):
        try:
            form.find_control("room[name]")
        except mechanize._form_controls.ControlNotFoundError:
            return False
        else:
            return True

    #print(br.response().read().decode('utf-8'))
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

def google_auth():
    scopes = ['https://www.googleapis.com/auth/calendar']
    token_file = 'auth/google_token.pickle'
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('auth/google_credentials.json', scopes)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    return creds

def get_calendar_event(calendar, event_name, event_start_time):
    events_result = calendar.events().list(calendarId='primary', timeMin=event_start_time,
                                           maxResults=10, singleEvents=True,
                                           orderBy='startTime').execute()
    events = events_result.get('items', [])
    for event in events:
        if event['summary'].endswith(event_name):
            return event

def set_calendar_event_location(calendar, calendar_event, location):
    calendar.events().patch(
        calendarId='primary',
        eventId=calendar_event['id'],
        body={'location': location},
    ).execute()

@csrf_exempt
def calendly_webhook(request):
    event_dict = json.loads(request.body)
    pprint(event_dict)

    event_start_time = event_dict['payload']['event']['start_time']
    event_invitee_name = event_dict['payload']['invitee']['name']
    event_invitee_email = event_dict['payload']['invitee']['email']
    event_host_name = event_dict['payload']['event']['assigned_to'][0]
    event_name = '{} and {}'.format(event_invitee_name, event_host_name)
    room_name = '{} ({})'.format(event_invitee_name, event_invitee_email)

    room_url = get_bbb_room_url(room_name)
    pprint(room_url)

    creds = google_auth()
    calendar = build('calendar', 'v3', credentials=creds)
    calendar_event = get_calendar_event(calendar, event_name, event_start_time)
    pprint(calendar_event)
    #set_calendar_event_location(calendar, calendar_event, room_url)

    return HttpResponse("OK")
