from django import forms
from django.contrib.auth.forms import AuthenticationForm

app_name = 'users'
class LoginUserForm(forms.Form):
    login = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль")