from django_registration.forms import RegistrationForm
from django import forms

from .models import User


class RegisterForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User


class ProfileChangeForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('avatar', 'username', 'first_name', 'last_name')
