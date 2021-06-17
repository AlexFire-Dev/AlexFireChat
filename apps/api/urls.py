from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('me/', login_required(MeApiView.as_view()), name='api-me'),
    path('me/membership/', login_required(MyMembershipApiView.as_view()), name='api-me-membership'),
]
