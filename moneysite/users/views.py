from django.contrib.auth import logout
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.generic import CreateView
from datetime import datetime

from .forms import *

current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
current_year = datetime.now().year
menu_dict = {
        'spending': {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
        'profit': {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
        'statistic': {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
        'profile': {'title': 'Профиль', 'url_name': 'users:profile'},
        'logout': {'title': 'Выйти', 'url_name': 'users:logout'},
}

class LoginUser(LoginView):
    form_class = LoginUserForm
    template_name = 'users/login.html'
    extra_context = {'title': 'Авторизация'}

    def get_success_url(self):
        return reverse_lazy('spending')


def logout_user(request):
    logout(request)
    return redirect('users:login')

class RegisterUser(CreateView):
    form_class = RegisterUserForm
    template_name = 'users/register.html'
    extra_context = {'title': 'Регистрация'}
    success_url = reverse_lazy('users:login')


def profileuser(request):
    title = 'Профиль'
    user = request.user
    context = {
        'title': title,
        'user': user,
        'menu': menu_dict,
    }
    return render(request, 'users/profile.html', context=context)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password-change.html"
    extra_context = {'title': 'Смена пароля', 'menu': menu_dict}