from django.http import HttpResponse

def calendly_webhook(request):
    return HttpResponse("Hello, world. You're at the calendly webhook")
