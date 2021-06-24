from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),

    path('guild/join/', login_required(GuildJoinView.as_view()), name='guild-join'),
    path('guild/<int:guild>/', login_required(GuildView.as_view()), name='guild-chat'),

    path('guild/<int:guild>/change/main/', login_required(GuildChangeMainView.as_view()), name='guild-change-main'),

    path('guild/<int:guild>/change/members/', login_required(GuildChangeMembersView.as_view()), name='guild-change-members'),
    path('guild/<int:guild>/change/members/<int:member>/kick/', login_required(GuildMemberKick.as_view()), name='guild-member-kick'),
    path('guild/<int:guild>/change/members/<int:member>/ban/', login_required(GuildMemberBan.as_view()), name='guild-member-ban'),

    path('guild/<int:guild>/change/bans/', login_required(GuildChangeBansView.as_view()), name='guild-change-bans'),
    path('guild/<int:guild>/change/bans/<int:member>/unban/', login_required(GuildMemberUnban.as_view()), name='guild-member-unban'),

    path('guild/<int:guild>/change/links/', login_required(GuildChangeLinksView.as_view()), name='guild-change-links'),
    path('guild/<int:guild>/change/links/generate/', login_required(GenerateInvitationLink.as_view()), name='generate-invite-link'),
    path('guild/<int:guild>/change/links/delete/<int:key>/', login_required(DeleteInvitationLink.as_view()), name='delete-invite-link'),

    path('guild/create/', login_required(GuildCreateView.as_view()), name='guild-create')
]
