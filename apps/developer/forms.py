from django import forms

from apps.user.models import User


class BotForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('username',)
