from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse

from .forms import LoginUserForm


# Create your views here.
# class LoginUser(LoginView):
#     form_class = LoginUserForm
#     template_name = "users/login.html"
#     extra_context = {'title': 'Авторизация'}

def login_user(request):
    if request.method == 'POST':
        form = LoginUserForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            print(cd)
            user = authenticate(request, username=cd['login'],
                                password=cd['password'])
            if user and user.is_active:
                login(request,user)
                redirect_url = reverse('index', kwargs={'operation': 'spending'})
                return redirect(redirect_url)
    else:
        form = LoginUserForm()

    return render(request, 'users/login.html', {'form': form})


def logout_user(request):
    logout(request)
    return redirect('users:login')