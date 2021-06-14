from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import re_path, path

from . import consumers


websocket_urlpatterns = [
    # re_path(r'ws/chat/(?P<guild_id>\w+)/$', consumers.GuildConsumer.as_asgi()),
    # url(r'^ws/chat/(?P<guild_id>[^/]+)/$', consumers.GuildConsumer.as_asgi()),
    path('ws/chat/<int:guild_id>/', consumers.GuildConsumer.as_asgi()),
]
