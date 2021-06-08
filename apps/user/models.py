from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _
from django.db import models
from rest_framework.authtoken.models import Token


class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    avatar = models.ImageField(upload_to='images/user/avatars', null=True, blank=True)
    bot = models.BooleanField(default=False)

    def GenerateBotToken(self):
        if self.bot:
            Token.objects.get_or_create(user_id=self.id)
