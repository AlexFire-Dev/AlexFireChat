from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('', login_required(IndexView.as_view()), name='index'),
    path('guild/<int:guild>/', login_required(GuildView.as_view()), name='guild-chat')
]
