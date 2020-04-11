from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

import json
import urllib
from pprint import pprint

def create_bbb_meeting(event_uuid, event_name, event_start_time, event_end_time):
    urllib.urlencode({
        'meetingID': event_uuid,
        'name': event_name,
        #'welcome': 'Welcome!',
        'logoutURL': 'https://opencraft.com/',
        'record': 'true',
        'autoStartRecording': 'true',
        #'logo': 'https://',
        #'bannerText': '',
        #'bannerColor': '',
        #'copyright': '',
        #'allowModsToUnmuteUsers': 'true',
    })

@csrf_exempt
def calendly_webhook(request):
    event_dict = json.loads(request.body)
    event_start_time = event_dict['payload']['event']['start_time']
    event_end_time = event_dict['payload']['event']['end_time']
    event_uuid = event_dict['payload']['event']['uuid']
    event_invitee_name = event_dict['payload']['invitee']['name']
    event_host_name = event_dict['payload']['event']['assigned_to'][0]
    event_name = '%s and %s'.values(event_invitee_name, event_host_name)

    create_bbb_meeting(event_uuid, event_name, event_start_time, event_end_time)
    return HttpResponse("OK")
