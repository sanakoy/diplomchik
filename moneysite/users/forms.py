from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm, PasswordChangeForm, UserCreationForm
from django.core.exceptions import ValidationError

app_name = 'users'
class LoginUserForm(AuthenticationForm):
    username = forms.CharField(label="Логин")
    password = forms.CharField(label="Пароль", widget=forms.PasswordInput(render_value=True))


class RegisterUserForm(UserCreationForm):
    password1 = forms.CharField(label="Пароль", widget=forms.PasswordInput(render_value=True))
    password2 = forms.CharField(label="Подтвердите пароль", widget=forms.PasswordInput(render_value=True))

    class Meta:
        model = get_user_model()
        fields = ['username', 'email', 'password1', 'password2']
        labels = {
            'email': 'Эл. почта',
        }

    # def clean_password2(self):
    #     cd = self.cleaned_data
    #     if cd['password2'] != cd['password']:
    #         raise forms.ValidationError('Пароли не совпадают!')
    #     return cd['password']

    def clean_email(self):
        email = self.cleaned_data['email']
        if get_user_model().objects.filter(email=email).exists():
            raise forms.ValidationError('Такая электронная почта уже была зарегистрирована!')
        return email


class ProfileUserForm(forms.ModelForm):
    username = forms.CharField(disabled=True, label="Логин")
    email = forms.CharField(disabled=True, label="Эл. почта")

    class Meta:
        model = get_user_model()
        fields = ['username', 'email']

class UserPasswordChangeForm(PasswordChangeForm):
    old_password = forms.CharField(label="Старый пароль", widget=forms.PasswordInput(render_value=True))
    new_password1 = forms.CharField(label="Новый пароль", widget=forms.PasswordInput(render_value=True))
    new_password2 = forms.CharField(label="Подтвердите новый пароль", widget=forms.PasswordInput(render_value=True))

