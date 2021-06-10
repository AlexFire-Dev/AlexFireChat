from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView

from .models import *


def passview(request):
    return render(request, 'pass.html')


class IndexView(TemplateView):
    template_name = 'chat/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        membership = Member.objects.filter(user=self.request.user)

        context.update({
            'membership': membership,
        })
        return context


class GuildView(TemplateView):
    template_name = 'chat/guild.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, user=self.request.user, guild=guild)
        messages = Message.objects.filter(guild=guild)

        context.update({
            'guild': guild,
            'messages': messages,
        })
        return context
