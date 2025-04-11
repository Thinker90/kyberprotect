from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm

from .models import CustomUser  # Импортируем нашу кастомную модель


# Форма для регистрации
class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser  # Используем CustomUser, а не стандартный User
        fields = ['username', 'email', 'password1', 'password2']


# Форма для входа
class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)
