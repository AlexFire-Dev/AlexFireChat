import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.shortcuts import get_object_or_404
from rest_framework.authtoken.models import Token

from .models import *


# Consumer чата
class GuildConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.guild_id = self.scope['url_route']['kwargs']['guild_id']
        self.guild_room_name = f'guild_{self.guild_id}'

        await self.get_user()
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
        guild_id = await self.get_guild()

        if action == 'send':
            message = text_data_json.get('message')
            message, member = await self.create_message(message=message)

            nickname = self.scope['user'].username
            if self.scope['user'].get_full_name():
                nickname = self.scope['user'].get_full_name()

            # Send message to room group
            await self.channel_layer.group_send(
                self.guild_room_name,
                {
                    'type': 'chat_message_send',
                    'guild_id': guild_id,
                    'author': {
                        'id': member.id,
                        'nickname': nickname
                    },
                    'message': {
                        'id': message.id,
                        'text': message.text,
                        'created_at': message.created_at.strftime('%Y.%m.%d %H:%M'),
                        'modified_at': message.modified_at.strftime('%Y.%m.%d %H:%M'),
                    },
                }
            )

        elif action == 'delete':
            message_id = text_data_json.get('message_id')
            result = await self.delete_message(message_id=message_id)

            if result:
                await self.channel_layer.group_send(
                    self.guild_room_name,
                    {
                        'type': 'chat_message_delete',
                        'guild_id': guild_id,
                        'message_id': message_id,
                    }
                )

    # Receive message from room group
    async def chat_message_send(self, event):
        author = event['author']
        message = event['message']
        guild_id = event['guild_id']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'action': 'send',
            'author': {
                'id': author['id'],
                'nickname': author['nickname'],
            },
            'message': {
                'id': message['id'],
                'text': message['text'],
                'created_at': message['created_at'],
                'modified_at': message['modified_at'],
            },
            'guild': {
                'id': guild_id,
            },
        }))

    async def chat_message_delete(self, event):
        message_id = event['message_id']
        guild_id = event['guild_id']

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message': {
                'id': message_id,
            },
            'guild': {
                'id': guild_id,
            },
        }))

    @database_sync_to_async
    def create_message(self, message):
        guild = get_object_or_404(Guild, id=self.guild_id)
        author = get_object_or_404(Member, user=self.scope['user'], guild=guild)

        newMessage = Message.objects.create(author=author, text=message, guild=guild)

        return newMessage, author

    @database_sync_to_async
    def delete_message(self, message_id):
        message = get_object_or_404(Message, id=message_id)
        member = get_object_or_404(Member, user=self.scope['user'], guild_id=self.guild_id)

        if message.author.user == self.scope['user'] or member.is_admin():
            message.delete()
            return True
        return False

    @database_sync_to_async
    def get_user(self):
        token = dict(self.scope['headers']).get(b'authorization')
        if token:
            token = token[6:].decode('UTF-8')
            self.scope['user'] = get_object_or_404(Token, key=token).user

    @database_sync_to_async
    def get_guild(self):
        guild = get_object_or_404(Guild, id=self.guild_id)
        return guild.id
