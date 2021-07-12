import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework.authtoken.models import Token

from .models import *


# Consumer чата
class BotConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = 'bots'

        await self.setup()
        if self.scope['user'].is_anonymous or not self.scope['user'].bot:
            return

        await self.channel_layer.group_add(
            self.room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.room_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
        except:
            return

    async def bot_joined(self, event):
        if self.scope['user'].id == event['user']:
            await self.send(text_data=json.dumps({
                'action': 'joined',
                'guild_id': event['guild'],
            }))

    @database_sync_to_async
    def setup(self):
        token = dict(self.scope['headers']).get(b'authorization')
        if token:
            token = token[6:].decode('UTF-8')
            try:
                user = Token.objects.get(key=token).user
                self.scope['user'] = user
            except:
                pass
