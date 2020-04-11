from django.test import Client, TestCase

SAMPLE_CALENDLY_WEBHOOK_POST_DATA = b'{"event":"invitee.created","payload":{"event_type":{"uuid":"BHHFEDKAVI6AJAHA","kind":"One-on-One","slug":"30min","name":"30 Minute Meeting","duration":30,"owner":{"type":"users","uuid":"f47dc814f55fc5a19227c01c6b8d2307"}},"event":{"uuid":"FHPWD2PTRYQENSFB","assigned_to":["Xavier Antoviaque"],"extended_assigned_to":[{"name":"Xavier Antoviaque","email":"xavier@opencraft.com","primary":true}],"start_time":"2020-04-30T17:30:00Z","start_time_pretty":"05:30pm - Thursday, April 30, 2020","invitee_start_time":"2020-04-30T13:30:00-04:00","invitee_start_time_pretty":"01:30pm - Thursday, April 30, 2020","end_time":"2020-04-30T18:00:00Z","end_time_pretty":"06:00pm - Thursday, April 30, 2020","invitee_end_time":"2020-04-30T14:00:00-04:00","invitee_end_time_pretty":"02:00pm - Thursday, April 30, 2020","created_at":"2020-04-09T18:51:41Z","location":"https://zoom.us/j/212890698","canceled":false,"canceler_name":null,"cancel_reason":null,"canceled_at":null},"invitee":{"uuid":"FDLQS5YPKWXW4COP","first_name":"Bob","last_name":"Test","name":"Bob Test","email":"xavier+test@antoviaque.org","text_reminder_number":null,"timezone":"America/New_York","created_at":"2020-04-09T18:51:41Z","is_reschedule":false,"payments":[],"canceled":false,"canceler_name":null,"cancel_reason":null,"canceled_at":null},"questions_and_answers":[{"question":"Topic/agenda","answer":"Test"}],"questions_and_responses":{"1_question":"Topic/agenda","1_response":"Test"},"tracking":{"utm_campaign":null,"utm_source":null,"utm_medium":null,"utm_content":null,"utm_term":null,"salesforce_uuid":null},"old_event":null,"old_invitee":null,"new_event":null,"new_invitee":null},"time":"2020-04-09T18:51:43Z"}'

class CalendlyTests(TestCase):

    def test_receive_webhook(self):
        c = Client()
        response = c.generic('POST', '/schedule/calendly/webhook',
                             data=SAMPLE_CALENDLY_WEBHOOK_POST_DATA)
        self.assertEqual(response.status_code, 200)
