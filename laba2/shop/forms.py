from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import CustomUser


class RegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    phone = forms.CharField(required=False, label='Телефон')

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'phone', 'password1', 'password2')


class LoginForm(AuthenticationForm):
    username = forms.CharField(label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
