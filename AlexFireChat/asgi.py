"""
ASGI config for AlexFireChat project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/asgi/
"""

import os
from django.core.asgi import get_asgi_application
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'AlexFireChat.settings')
django.setup()
django_asgi_app = get_asgi_application()

from apps.chat import consumers
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter

import apps.chat.routing
import apps.developer.routing


websocket_urlpatterns = []

for url in apps.chat.routing.websocket_urlpatterns:
    websocket_urlpatterns.append(url)
for url in apps.developer.routing.websocket_urlpatterns:
    websocket_urlpatterns.append(url)


application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        ),
    ),
})
