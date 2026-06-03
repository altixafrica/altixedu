"""
WebSocket routing configuration for Django Channels.
Maps WebSocket URLs to their corresponding consumers.
"""

from django.urls import path
from apps.notifications.consumers import MessageConsumer

websocket_urlpatterns = [
    # Real-time messaging WebSocket
    path('ws/messages/', MessageConsumer.as_asgi(), name='websocket_messages'),
]
