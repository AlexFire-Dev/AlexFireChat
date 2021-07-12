from django.contrib.auth.decorators import login_required
from django.urls import path, reverse_lazy, include
from django_registration.backends.activation.views import RegistrationView

from .views import *
from .forms import RegisterForm


urlpatterns = [
    path('api-auth/', include('rest_framework.urls')),

    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.authtoken')),

    path('', include('django_registration.backends.activation.urls')),
    path('', include('django.contrib.auth.urls')),
    path('create/', RegistrationView.as_view(form_class=RegisterForm, success_url=reverse_lazy('django_registration_complete')), name='register'),

    path('me/', login_required(AccountView), name='profile'),
    path('change/', login_required(ProfileChangeView.as_view()), name='profile-change'),
]
