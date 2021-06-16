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
        action = text_data_json.get('action')

        if action == 'send':
            message = text_data_json.get('message')
            message = await self.create_message(message=message)

            author = self.scope['user']

            # Send message to room group
            await self.channel_layer.group_send(
                self.guild_room_name,
                {
                    'type': 'chat_message_send',
                    'author': author,
                    'message': message,
                }
            )

        elif action == 'delete':
            message_id = text_data_json.get('message_id')

            await self.delete_message(message_id=message_id)

            await self.channel_layer.group_send(
                self.guild_room_name,
                {
                    'type': 'chat_message_delete',
                    'message_id': message_id,
                }
            )

    # Receive message from room group
    async def chat_message_send(self, event):
        author = event['author']
        message = event['message']

        nickname = author.username
        if author.get_full_name():
            nickname = author.get_full_name()

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'send',
            'author': {
                'id': author.id,
                'nickname': nickname,
            },
            'message': {
                'id': message.id,
                'text': message.text,
                'created_at': message.created_at.strftime('%Y.%m.%d %H:%M'),
                'modified_at': message.modified_at.strftime('%Y.%m.%d %H:%M'),
            },
        }))

    async def chat_message_delete(self, event):
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message': {
                'id': message_id,
            },
        }))

    @database_sync_to_async
    def create_message(self, message):
        guild = get_object_or_404(Guild, id=self.guild_id)
        author = get_object_or_404(Member, user=self.scope['user'], guild=guild)

        newMessage = Message.objects.create(author=author, text=message, guild=guild)

        return newMessage

    @database_sync_to_async
    def delete_message(self, message_id):
        get_object_or_404(Message, id=message_id).delete()
