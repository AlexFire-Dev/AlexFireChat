from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('me/', MeApiView.as_view(), name='api-me'),
    path('me/membership/', MyMembershipApiView.as_view(), name='api-me-membership'),
    path('guild/<int:guild>/', GuildApiView.as_view(), name='api-guild'),
    path('member/<int:member>/', MemberApiView.as_view(), name='api-member')
]
