from django.db import models

from apps.user.models import User


class Guild(models.Model):
    name = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)
    creator = models.ForeignKey(User, on_delete=models.PROTECT, related_name='guilds')
    poster = models.ImageField(upload_to='images/guilds/posters', blank=True, null=True)

    def __str__(self):
        return self.name


class Member(models.Model):
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.PROTECT, related_name='membership')
    admin = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.guild}: {self.user}'


class Message(models.Model):
    author = models.ForeignKey(Member, on_delete=models.PROTECT, related_name='messages')
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    guild = models.ForeignKey(Guild, on_delete=models.CASCADE, related_name='messages')

    def __str__(self):
        return f'{self.author}: {self.text}'
