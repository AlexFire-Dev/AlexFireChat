from django_registration.forms import RegistrationForm
from django import forms

from .models import User


class RegisterForm(RegistrationForm):
    class Meta(RegistrationForm.Meta):
        model = User
