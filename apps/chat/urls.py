from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),

    path('guild/<int:guild>/', login_required(GuildView.as_view()), name='guild-chat'),

    path('guild/<int:guild>/change/main/', login_required(GuildChangeMainView.as_view()), name='guild-change-main'),
    path('guild/<int:guild>/change/members/', login_required(GuildChangeMembersView.as_view()), name='guild-change-members'),
    path('guild/<int:guild>/change/links/', login_required(GuildChangeLinksView.as_view()), name='guild-change-links'),
    path('guild/<int:guild>/change/links/generate/', login_required(GenerateInvitationLink.as_view()), name='generate-invite-link'),

    path('guild/create/', login_required(GuildCreateView.as_view()), name='guild-create')
]
