from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import UpdateView

from .models import User
from .forms import ProfileChangeForm


def AccountView(request, userid):

    context = {
        'accountuser': get_object_or_404(User, id=userid),
    }

    return render(request, 'user/profile.html', context=context)


class ProfileChangeView(UpdateView):
    form_class = ProfileChangeForm
    template_name = 'user/profile-change.html'

    def get_object(self, queryset=None):
        return self.request.user

    def get_success_url(self):
        url = reverse('profile', args=[self.request.user.id])
        return url
