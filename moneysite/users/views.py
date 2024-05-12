from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import LoginView, PasswordChangeView
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.urls import reverse_lazy
from django.views.generic import UpdateView, CreateView
from datetime import datetime

from .forms import *

current_month = datetime.now().month # для того, чтобы изначально выводилась статистика по текущему месяцу
current_year = datetime.now().year
menu = [
    {'title': 'Расходы', 'url_name': 'index', 'slug': 'spending'},
    {'title': 'Доходы', 'url_name': 'index', 'slug': 'profit'},
    {'title': 'Статистика', 'url_name': 'statistic', 'operation': 'spending', 'year': current_year, 'month': current_month},
    {'title': 'Профиль', 'url_name': 'users:profile'},
    {'title': 'Выйти', 'url_name': 'users:logout'},

]
# Create your views here.
# class LoginUser(LoginView):
#     form_class = LoginUserForm
#     template_name = "users/login.html"
#     extra_context = {'title': 'Авторизация'}

# def login_user(request):
#     if request.user.is_authenticated:
#         redirect_url = reverse('index', kwargs={'operation': 'spending'})
#         return redirect(redirect_url)
#     if request.method == 'POST':
#         form = LoginUserForm(request.POST)
#         context = {
#             'form': form,
#         }
#         if form.is_valid():
#             cd = form.cleaned_data
#             user = authenticate(request, username=cd['login'],
#                                 password=cd['password'])
#             if user and user.is_active:
#                 login(request,user)
#                 redirect_url = reverse('index', kwargs={'operation': 'spending'})
#                 return redirect(redirect_url)
#             else:
#                 context['not_valid'] = 'Неверное имя пользователя или пароль!'
#     else:
#         form = LoginUserForm()
#         context = {
#             'form': form,
#         }
#
#     return render(request, 'users/login.html', context=context)

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

# def register_user(request):
#     if request.method == "POST":
#         form = RegisterUserForm(request.POST)
#         context = {
#             'form': form,
#         }
#         if form.is_valid():
#             user = form.save(commit=False)
#             cd = form.cleaned_data
#             user.set_password(cd['password'])
#             if get_user_model().objects.filter(email=cd['email']).exists():
#                 raise forms.ValidationError('Такая электронная почта уже была зарегистрирована!')
#                 redirect_url = reverse('users:register')
#                 return  redirect(redirect_url)
#             else:
#                 user.save()
#                 redirect_url = reverse('users:login')
#                 return redirect(redirect_url)
#     else:
#         form = RegisterUserForm()
#
#     return render(request, 'users/register.html', {'form': form})


def profileuser(request):
    title = 'Профиль'
    user = request.user
    context = {
        'title': title,
        'user': user,
        'menu': menu,
    }
    return render(request, 'users/profile.html', context=context)

class UserPasswordChange(PasswordChangeView):
    form_class = UserPasswordChangeForm
    success_url = reverse_lazy("users:password_change_done")
    template_name = "users/password-change.html"
    extra_context = {'title': 'Смена пароля'}