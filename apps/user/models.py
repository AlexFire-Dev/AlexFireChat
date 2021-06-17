from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='images/user/avatars', null=True, blank=True)
    bot = models.BooleanField(default=False)

    def __str__(self):
        return str(self.id)

    def GenerateBotToken(self):
        if self.bot:
            Token.objects.get_or_create(user_id=self.id)

    def GetBotToken(self):
        if self.bot:
            self.GenerateBotToken()
            return Token.objects.get(user_id=self.id)

    def DeleteBotToken(self):
        if self.bot:
            self.GetBotToken().delete()


class Bot(models.Model):
    account = models.OneToOneField(User, on_delete=models.CASCADE, related_name='this_bot')
    master = models.ForeignKey(User, on_delete=models.PROTECT, related_name='bots')
