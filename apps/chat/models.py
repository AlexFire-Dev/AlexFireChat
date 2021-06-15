from django.db import models
import random, string

from apps.user.models import User


class Guild(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='guilds')
    poster = models.ImageField(upload_to='images/guilds/posters', blank=True, null=True)

    def __str__(self):
        return self.name

    def GenerateKey(self):
        letters = string.ascii_lowercase
        key = ''.join(random.choice(letters) for i in range(15))
        InviteLink.objects.create(guild=self, key=key)


class Member(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership')
    admin = models.BooleanField(default=False)
    active = models.BooleanField(default=True)
    banned = models.BooleanField(default=False)
    joined = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.guild}: {self.user}'

    def is_admin(self):
        if self.admin:
            return True
        else:
            return


class Message(models.Model):
    author = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return f'{self.author}: {self.text}'


class InviteLink(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='invitation_links')
    key = models.CharField(max_length=15, unique=True, null=True)

    def __str__(self):
        return f'{self.guild}: {self.key}'
