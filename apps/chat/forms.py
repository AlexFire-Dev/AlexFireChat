from django import forms

from .models import Guild, Member


class CreateGuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ('name', 'poster')


class UpdateGuildForm(forms.ModelForm):
    class Meta:
        model = Guild
        fields = ('name', 'poster')


class UpdateMemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ('admin',)
