from rest_framework.response import Response
from rest_framework.views import APIView

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
