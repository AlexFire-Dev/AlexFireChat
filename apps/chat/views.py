import json

import channels.layers
from asgiref.sync import async_to_sync
from django.conf import settings
from django.core.paginator import Paginator
from django.http import HttpResponseRedirect
from django.shortcuts import render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import TemplateView, CreateView, UpdateView, RedirectView

from .models import *
from .forms import *


class IndexView(TemplateView):
    template_name = 'chat/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        membership = Member.objects.filter(user=self.request.user, active=True, banned=False)

        context.update({
            'membership': membership,
        })
        return context


class GuildView(TemplateView):
    template_name = 'chat/guild.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, user=self.request.user, guild=guild, active=True, banned=False)
        messages = Message.objects.filter(guild=guild).order_by('id')
        paginator = Paginator(messages, settings.MESSAGES_PER_LOAD)
        messages = paginator.get_page(paginator.num_pages)

        context.update({
            'guild': guild,
            'member': member,
            'messages': messages,
            'paginator': paginator,
        })
        return context


class GuildCreateView(CreateView):
    form_class = CreateGuildForm
    template_name = 'chat/guild_create.html'

    def form_valid(self, form):
        name = form.cleaned_data.get('name', f'Сервер {self.request.user.username}')

        args = {
            'name': name,
            'creator': self.request.user,
            'poster': self.request.FILES.get('poster'),
        }
        guild = Guild.objects.create(**args)
        Member.objects.create(guild=guild, user=self.request.user, admin=True)
        return HttpResponseRedirect(reverse_lazy('guild-chat', args=[guild.id]))


class GuildJoinView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('index')

    def get(self, request, *args, **kwargs):
        link = get_object_or_404(InviteLink, key=self.request.GET.get('join-input'))
        guild = link.guild
        Member.objects.get_or_create(user=self.request.user, guild=guild)
        member = Member.objects.get(user=self.request.user, guild=guild)
        if member.banned:
            return HttpResponseRedirect(reverse('index'))
        member.active = True
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

        return super(GuildJoinView, self).get(self, request, *args, **kwargs)


class GuildLeaveView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('index')

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=self.kwargs.get('guild'))
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        me.active = False
        me.admin = False
        me.save()

        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'guild_{guild.id}',
            {
                'type': 'chat_member_left',
                'member': {
                    'id': me.id,
                }
            }
        )

        return super(GuildLeaveView, self).get(self, request, *args, **kwargs)


class GuildDeleteView(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('index')

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=self.kwargs.get('guild'), creator=self.request.user)
        channel_layer = channels.layers.get_channel_layer()
        members = Member.objects.filter(guild=guild).order_by('-id')

        for member in members:
            member.admin = False
            member.active = False
            member.save()
            async_to_sync(channel_layer.group_send)(
                f'guild_{guild.id}',
                {
                    'type': 'chat_member_left',
                    'member': {
                        'id': member.id,
                    }
                }
            )
            member.delete()

        guild.delete()

        return super(GuildDeleteView, self).get(self, request, *args, **kwargs)


class GuildMemberKick(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('guild-change-members', args=[self.kwargs.get('guild')])

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), active=True, banned=False)
        if not me.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        elif guild.creator == member.user:
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        elif not member.is_admin():
            if self.request.user != guild.creator:
                return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
            else:
                return super(GuildMemberKick, self).dispatch(request, *args, **kwargs)
        else:
            return super(GuildMemberKick, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), banned=False)
        member.active = False
        member.admin = False
        member.save()

        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'guild_{guild.id}',
            {
                'type': 'chat_member_left',
                'member': {
                    'id': member.id,
                }
            }
        )

        return super(GuildMemberKick, self).get(self, request, *args, **kwargs)


class GuildMemberBan(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('guild-change-members', args=[self.kwargs.get('guild')])

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), active=True, banned=False)
        if not me.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        elif guild.creator == member.user:
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        elif not member.is_admin():
            if self.request.user != guild.creator:
                return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
            else:
                return super(GuildMemberBan, self).dispatch(request, *args, **kwargs)
        else:
            return super(GuildMemberBan, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), banned=False)
        member.banned = True
        member.active = False
        member.admin = False
        member.save()

        channel_layer = channels.layers.get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f'guild_{guild.id}',
            {
                'type': 'chat_member_left',
                'member': {
                    'id': member.id,
                }
            }
        )

        return super(GuildMemberBan, self).get(self, request, *args, **kwargs)


class GuildChangeMainView(UpdateView):
    form_class = CreateGuildForm
    template_name = 'chat/guild_change_main.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Guild, id=self.kwargs.get('guild'))

    def get_success_url(self):
        url = reverse('guild-change-main', args=[self.kwargs.get('guild')])
        return url

    def dispatch(self, request, *args, **kwargs):
        guild = self.get_object()
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeMainView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = self.get_object()
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)

        context.update({
            'guild': guild,
            'member': member,
        })
        return context


class GuildChangeMembersView(TemplateView):
    template_name = 'chat/guild_change_members.html'

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeMembersView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        members = Member.objects.filter(guild=guild, active=True, banned=False)
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)

        context.update({
            'guild': guild,
            'me': me,
            'members': members,
        })
        return context


class GuildChangeBansView(TemplateView):
    template_name = 'chat/guild_change_bans.html'

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeBansView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        members = Member.objects.filter(guild=guild, banned=True)
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)

        context.update({
            'guild': guild,
            'me': me,
            'members': members,
        })
        return context


class GuildChangeLinksView(TemplateView):
    template_name = 'chat/guild_change_links.html'

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeLinksView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        links = InviteLink.objects.filter(guild=guild)

        context.update({
            'guild': guild,
            'member': member,
            'links': links,
        })
        return context


class GenerateInvitationLink(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('guild-change-links', args=[self.kwargs.get('guild')])

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GenerateInvitationLink, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        guild.GenerateKey()
        return super(GenerateInvitationLink, self).get(self, request, *args, **kwargs)


class DeleteInvitationLink(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('guild-change-links', args=[self.kwargs.get('guild')])

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(DeleteInvitationLink, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        link = get_object_or_404(InviteLink, guild=guild, id=kwargs.get('key'))
        link.delete()
        return super(DeleteInvitationLink, self).get(self, request, *args, **kwargs)


class GuildMemberUnban(RedirectView):
    def get_redirect_url(self, *args, **kwargs):
        return reverse('guild-change-bans', args=[self.kwargs.get('guild')])

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        me = get_object_or_404(Member, guild=guild, user=self.request.user, active=True, banned=False)
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), active=False, banned=True)
        if not me.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildMemberUnban, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, id=kwargs.get('member'), banned=True)
        member.banned = False
        member.save()
        return super(GuildMemberUnban, self).get(self, request, *args, **kwargs)
