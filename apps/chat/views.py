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

        key = self.request.GET.get('join_input')

        if key:
            try:
                link = InviteLink.objects.get(key=key)
                guild = link.guild
                Member.objects.get_or_create(user=self.request.user, guild=guild)
            except:
                pass

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
            'member': member,
            'messages': messages,
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
        }
        guild = Guild.objects.create(**args)
        Member.objects.create(guild=guild, user=self.request.user, admin=True)
        return HttpResponseRedirect(reverse_lazy('guild-chat', args=[guild.id]))


class GuildChangeMainView(UpdateView):
    form_class = CreateGuildForm
    template_name = 'chat/guild_change_main.html'

    def get_object(self, queryset=None):
        return get_object_or_404(Guild, id=self.kwargs.get('guild'))

    def get_success_url(self):
        url = reverse('guild-change', args=[self.kwargs.get('guild')])
        return url

    def dispatch(self, request, *args, **kwargs):
        guild = self.get_object()
        member = get_object_or_404(Member, guild=guild, user=self.request.user)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeMainView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = self.get_object()
        member = get_object_or_404(Member, guild=guild, user=self.request.user)

        context.update({
            'guild': guild,
            'member': member,
        })
        return context


class GuildChangeMembersView(TemplateView):
    template_name = 'chat/guild_change_members.html'

    def dispatch(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeMembersView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        members = Member.objects.filter(guild=guild)
        me = get_object_or_404(Member, guild=guild, user=self.request.user)

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
        member = get_object_or_404(Member, guild=guild, user=self.request.user)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GuildChangeLinksView, self).dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        member = get_object_or_404(Member, guild=guild, user=self.request.user)
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
        member = get_object_or_404(Member, guild=guild, user=self.request.user)
        if not member.is_admin():
            return HttpResponseRedirect(reverse('guild-chat', args=[self.kwargs.get('guild')]))
        else:
            return super(GenerateInvitationLink, self).dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        guild = get_object_or_404(Guild, id=kwargs.get('guild'))
        guild.GenerateKey()
        return super(GenerateInvitationLink, self).get(self, request, *args, **kwargs)
