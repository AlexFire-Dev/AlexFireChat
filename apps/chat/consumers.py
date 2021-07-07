import json

from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
from django.conf import settings
from django.core.paginator import Paginator
from rest_framework.authtoken.models import Token

from .models import *


# Consumer чата
class GuildConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.guild_id = self.scope['url_route']['kwargs']['guild_id']
        self.guild_room_name = f'guild_{self.guild_id}'

        await self.setup()
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
        try:
            text_data_json = json.loads(text_data)
            action = text_data_json.get('action')
        except:
            return

        if action == 'send':
            message = text_data_json.get('message')
            message, member, result = await self.create_message(message=message)

            if result:
                nickname = self.scope['user'].username
                if self.scope['user'].get_full_name():
                    nickname = self.scope['user'].get_full_name()

                # Send message to room group
                await self.channel_layer.group_send(
                    self.guild_room_name,
                    {
                        'type': 'chat_message_send',
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
                        'message_id': message_id,
                    }
                )

        elif action == 'clear':
            limit = int(text_data_json.get('limit'))
            ids = await self.delete_messages(limit)
            for one_id in ids:
                await self.channel_layer.group_send(
                    self.guild_room_name,
                    {
                        'type': 'chat_message_delete',
                        'message_id': one_id,
                    }
                )

        elif action == 'load':
            page = int(text_data_json.get('page_id'))
            messages = await self.get_page(page)
            await self.send(text_data=json.dumps({
                'action': 'load',
                'guild': {
                    'id': self.guild_id,
                },
                'messages': messages,
            }))

    # Receive message from room group
    async def chat_message_send(self, event):
        author = event['author']
        message = event['message']

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
                'id': self.guild_id,
            },
        }))

    async def chat_message_delete(self, event):
        message_id = event['message_id']

        await self.send(text_data=json.dumps({
            'action': 'delete',
            'message': {
                'id': message_id,
            },
            'guild': {
                'id': self.guild_id,
            },
        }))

    async def chat_member_joined(self, event):
        await self.send(text_data=json.dumps({
            'action': 'joined',
            'member': {
                'id': event['member']['id'],
                'user': event['member']['user'],
                'username': event['member']['username'],
                'admin': event['member']['admin'],
                'bot': event['member']['bot'],
            },
            'guild': {
                'id': self.guild_id,
            },
        }))

    async def chat_member_kicked(self, event):
        member = event['member']['id']

        await self.send(text_data=json.dumps({
            'action': 'kicked',
            'member': {
                'id': member,
            },
            'guild': {
                'id': self.guild_id,
            },
        }))

        if member == self.scope['member'].id:
            await self.close()

    async def chat_member_banned(self, event):
        member = event['member']['id']

        await self.send(text_data=json.dumps({
            'action': 'banned',
            'member': {
                'id': member,
            },
            'guild': {
                'id': self.guild_id,
            },
        }))

        if member == self.scope['member'].id:
            await self.close()

    @database_sync_to_async
    def get_member(self, member_id):
        try:
            member = Member.objects.get(guild=self.scope['guild'], id=member_id)
            return member, member.user
        except:
            return None

    @database_sync_to_async
    def create_message(self, message):
        try:
            guild = Guild.objects.get(id=self.guild_id)
            author = self.scope['member']

            newMessage = Message.objects.create(author=author, text=message, guild=guild)
            return newMessage, author, True
        except:
            return None, None, False

    @database_sync_to_async
    def delete_message(self, message_id):
        try:
            message = Message.objects.get(id=message_id)
            member = self.scope['member']
        except:
            return False

        if message.author.user == self.scope['user'] or member.is_admin():
            message.delete()
            return True
        return False

    @database_sync_to_async
    def delete_messages(self, limit: int):
        ids = []
        messages = Message.objects.filter(guild_id=self.guild_id).order_by('-id')
        for counter in range(limit):
            try:
                message = messages.latest('id')
                ids.append(message.id)
                message.delete()
            except:
                break
        return ids

    @database_sync_to_async
    def guild_creator(self):
        try:
            return self.scope['guild'].user
        except:
            return None

    @database_sync_to_async
    def get_page(self, page: int):
        try:
            page = self.scope['paginator'].get_page(page)
        except:
            return
        messages = []
        for message in page:
            nickname = message.author.user.username
            if message.author.user.get_full_name():
                nickname = message.author.user.get_full_name()
            messages.append({
                'author': {
                    'id': message.author.id,
                    'nickname': nickname,
                },
                'message': {
                    'id': message.id,
                    'text': message.text,
                    'created_at': message.created_at.strftime('%Y.%m.%d %H:%M'),
                    'modified_at': message.modified_at.strftime('%Y.%m.%d %H:%M'),
                },
            })
        return messages

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
        if self.scope.get('user'):
            try:
                self.scope['member'] = Member.objects.get(user=self.scope['user'], guild_id=self.guild_id)
            except:
                pass
        try:
            self.scope['guild'] = Guild.objects.get(id=self.guild_id)
        except:
            pass
        try:
            messages = Message.objects.filter(guild_id=self.guild_id).order_by('id')
            self.scope['paginator'] = Paginator(messages, settings.MESSAGES_PER_LOAD)
        except:
            pass
