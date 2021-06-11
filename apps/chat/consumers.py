import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404

from .models import *


class GuildConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.guild_id = self.scope['url_route']['kwargs']['guild_id']
        self.guild_room_name = f'guild_{self.guild_id}'

        if self.scope['user'].is_anonymous:
            return

        await self.channel_layer.group_add(
            self.guild_room_name,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, code):
        await self.channel_layer.group_discard(
            self.guild_room_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        text_data_json = json.loads(text_data)
        message = text_data_json.get('message')

        created_at, modified_at = await self.create_message(message=message)

        if self.scope['user'].get_full_name():
            author = self.scope['user'].get_full_name()
        else:
            author = self.scope['user'].username

        # Send message to room group
        await self.channel_layer.group_send(
            self.guild_room_name,
            {
                'type': 'chat_message',
                'message': message,
                'author': author,
                'created_at': created_at,
                'modified_at': modified_at
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        author = event['author']
        created_at = event['created_at']
        modified_at = event['modified_at']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'author': author,
            'created_at': created_at,
            'modified_at': modified_at
        }))

    @database_sync_to_async
    def create_message(self, message):
        guild = get_object_or_404(Guild, id=self.guild_id)
        author = get_object_or_404(Member, user=self.scope['user'], guild=guild)

        newMessage = Message.objects.create(author=author, text=message, guild=guild)

        return newMessage.created_at.strftime('%Y.%m.%d %H:%M'), newMessage.modified_at.strftime('%Y.%m.%d %H:%M')
