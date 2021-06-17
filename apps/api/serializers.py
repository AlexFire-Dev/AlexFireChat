from rest_framework import serializers


class UserSerializer(serializers.Serializer):
    id = serializers.CharField()
    username = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    email = serializers.EmailField()
    bot = serializers.BooleanField()
    is_staff = serializers.BooleanField()


class GuildSerializer(serializers.Serializer):
    id = serializers.CharField()
    name = serializers.CharField()
    created_at = serializers.DateTimeField()
    creator = serializers.CharField()


class MembershipSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    guild = GuildSerializer()
    user = UserSerializer()
    admin = serializers.BooleanField()
    active = serializers.BooleanField()
    banned = serializers.BooleanField()
    joined = serializers.DateTimeField()
