"""
ASGI config for altixedu project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from channels.security.websocket import AllowedHostsOriginValidator

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'altixedu.settings')

# Django ASGI application to handle HTTP requests
django_asgi_app = get_asgi_application()

# Import WebSocket consumers and routes
from altixedu.routing import websocket_urlpatterns

# ASGI application that handles both HTTP and WebSocket protocols
application = ProtocolTypeRouter({
    # HTTP protocol - use default Django ASGI app
    'http': django_asgi_app,
    
    # WebSocket protocol - authenticate then route to consumers
    'websocket': AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                websocket_urlpatterns
            )
        )
    ),
})
