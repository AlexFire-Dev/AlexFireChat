from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True, null=True, blank=True)
    avatar = models.ImageField(upload_to='images/user/avatars', null=True, blank=True)
    system = models.BooleanField(default=False)
    bot = models.BooleanField(default=False)

    username_validator = UnicodeUsernameValidator()
    username = models.CharField(
        _('username'),
        max_length=30,
        unique=True,
        help_text=_('Обязательное поле. Не более 30 символов. Только буквы, цифры и символы @/./+/-/_.'),
        validators=[username_validator],
        error_messages={
            'unique': _('A user with that username already exists.'),
        },
    )

    def __str__(self):
        return self.username

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
