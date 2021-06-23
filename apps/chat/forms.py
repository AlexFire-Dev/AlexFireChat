from django import forms

from .models import Guild


class CreateGuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ('name', 'poster')


class UpdateGuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ('name', 'poster')
