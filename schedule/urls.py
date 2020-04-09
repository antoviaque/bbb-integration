from django.urls import path

from . import views

urlpatterns = [
    path('calendly/webhook', views.calendly_webhook, name='calendly_webhook'),
]
