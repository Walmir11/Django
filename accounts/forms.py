from django.contrib.auth.forms import UserCreationForm
from django import forms
from .models import User

class BaseUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'first_name', 'last_name', 'email')

class ClienteCreationForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.CLIENTE
        if commit:
            user.save()
        return user

class ProfissionalCreationForm(BaseUserCreationForm):
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = User.UserType.PROFISSIONAL
        if commit:
            user.save()
        return user