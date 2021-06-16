from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include

from .views import *


urlpatterns = [
    path('', login_required(IndexView.as_view()), name='developer-index'),

    path('bot/create/', login_required(BotCreateView.as_view()), name='bot-create'),
    path('bot/<int:bot>/', login_required(BotView.as_view()), name='bot-detail'),
    path('bot/<int:bot>/edit/', login_required(BotUpdateView.as_view()), name='bot-edit'),
    path('bot/<int:bot>/regenerate/', login_required(BotRegenerateTokenView.as_view()), name='bot-regenerate'),

    path('bot/<int:bot>/join/', login_required(BotJoinView.as_view()), name='bot-join')
]
