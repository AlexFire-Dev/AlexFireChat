from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import render, get_object_or_404

from apps.chat.models import *
from .serializers import *


class MyMembershipApiView(APIView):
    """
    Информация о активных нахождениях в группах.

    * Нужна аутентификация по токену.
    """

    def get(self, request):
        membership = Member.objects.filter(user=self.request.user, active=True, banned=False)
        serializer = MembershipSerializer(membership, many=True)
        return Response({'membership': serializer.data})


class MeApiView(APIView):
    """
    Информация о конкретном пользователе.

    * Нужна аутентификация по токену.
    """

    def get(self, request):
        me = self.request.user
        serializer = UserSerializer(me)
        return Response(serializer.data)


class GuildApiView(APIView):
    """
    Информация о конкретном сервере.

    * Нужна аутентификация по токену.
    """

    def get(self, request, guild):
        guild_model = get_object_or_404(Guild, id=guild)
        serializer = GuildSerializer(guild_model)
        return Response(serializer.data)


class MemberApiView(APIView):
    """
    Информация о конкретном участнике группы.

    * Нужна аутентификация по токену.
    """

    def get(self, request, member):
        member_model = get_object_or_404(Member, id=member)
        serializer = MembershipSerializer(member_model)
        return Response(serializer.data)
