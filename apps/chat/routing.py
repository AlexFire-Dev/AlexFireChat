from django.contrib.auth.decorators import login_required
from django.urls import re_path, path

from . import consumers


websocket_urlpatterns = [
    path('ws/chat/<int:guild_id>/', consumers.GuildConsumer.as_asgi()),
    # re_path(r'ws/chat/(?P<room_name>\w+)/$', consumers.GuildConsumer.as_asgi()),
]
