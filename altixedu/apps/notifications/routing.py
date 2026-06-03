from django.urls import path
from apps.notifications.consumers import MessageConsumer

websocket_urlpatterns = [
    path('ws/messages/', MessageConsumer.as_asgi()),
]
