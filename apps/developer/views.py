import channels.layers
from asgiref.sync import async_to_sync
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, RedirectView

from apps.chat.models import *
from apps.user.models import *
from .forms import *


class IndexView(TemplateView):
    template_name = 'developer/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bots = Bot.objects.filter(master=self.request.user)

        context.update({
            'bots': bots,
        })
        return context


class BotCreateView(CreateView):
    form_class = BotForm
    template_name = 'developer/bot-create.html'

    def form_valid(self, form):
        username = form.cleaned_data.get('username')

        user_args = {
            'username': username,
            'bot': True,
        }

        user = User.objects.create(**user_args)
        user.set_unusable_password()
        user.email = f'{user.id}@chat.bot'
        user.GenerateBotToken()
        user.save()
        bot = Bot.objects.create(master=self.request.user, account=user)
        return HttpResponseRedirect(reverse_lazy('developer-index'))


class BotView(TemplateView):
    template_name = 'developer/bot.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'), master=self.request.user)

        context.update({
            'bot': bot,
        })
        return context


class BotRegenerateTokenView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('bot-detail', args=[self.kwargs.get('bot')])

    def get(self, request, *args, **kwargs):
        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'), master=self.request.user)
        bot.account.DeleteBotToken()
        bot.account.GenerateBotToken()

        return super(BotRegenerateTokenView, self).get(self, request, *args, **kwargs)


class BotUpdateView(UpdateView):
    form_class = BotForm
    template_name = 'developer/bot-change.html'

    def get_object(self, queryset=None):
        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'), master=self.request.user)
        return bot.account

    def get_success_url(self):
        return reverse('bot-detail', args=[self.kwargs.get('bot')])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'), master=self.request.user)

        context.update({
            'bot': bot,
        })
        return context


class BotJoinView(TemplateView):
    template_name = 'developer/bot-join.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'))
        admins = Member.objects.filter(user=self.request.user, active=True, banned=False, admin=True)

        context.update({
            'bot': bot,
            'membership': admins,
        })
        return context

    def get(self, request, *args, **kwargs):
        guild_id = int(self.request.GET.get('guild-select', 0))
        if guild_id == 0:
            return super(BotJoinView, self).get(self, request, *args, **kwargs)

        guild = get_object_or_404(Guild, id=guild_id)
        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'))
        Member.objects.get_or_create(user=bot.account, guild=guild)
        member = Member.objects.get(user=bot.account, guild=guild)
        if member.banned:
            return HttpResponseRedirect(reverse('developer-index'))
        if member.active and member.admin:
            return super(BotJoinView, self).get(self, request, *args, **kwargs)
        member.active = True
        member.admin = True
        member.save()

        channel_layer = channels.layers.get_channel_layer()
        username = member.user.username
        if member.user.get_full_name():
            username = member.user.get_full_name()

        async_to_sync(channel_layer.group_send)(
            f'guild_{guild.id}',
            {
                'type': 'chat_member_joined',
                'member': {
                    'id': member.id,
                    'user': member.user.id,
                    'username': username,
                    'admin': member.admin,
                    'bot': member.user.bot,
                }
            }
        )

        async_to_sync(channel_layer.group_send)(
            'bots',
            {
                'type': 'bot_joined',
                'guild': guild.id,
                'member': member.id,
                'user': member.user.id,
            }
        )

        return super(BotJoinView, self).get(self, request, *args, **kwargs)


class BotDeleteView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('developer-index')

    def get(self, request, *args, **kwargs):
        bot = get_object_or_404(Bot, id=self.kwargs.get('bot'), master=self.request.user)
        bot.account.delete()
        bot.delete()

        return super(BotDeleteView, self).get(self, request, *args, **kwargs)
