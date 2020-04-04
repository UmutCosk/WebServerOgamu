from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from .forms import RegisterForm,LoginForm

from django.contrib.auth.models import User
# Create your views here.
from django.urls import reverse


def index(request):
    return render(request, 'web/base.html')

def register_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('web:member'))
    register_form = RegisterForm()
    if request.method == "POST":
        register_form = RegisterForm(request.POST)
        if register_form.is_valid():
            username = register_form.cleaned_data['username']
            password = register_form.cleaned_data['password']
            email = register_form.cleaned_data['email']
            User.objects.create_user(username=username,password=password,email=email)
            user = authenticate(request, username=username, password=password)
            if user: #überprüft ob es den user gibt
                login(request, user)
                return redirect(reverse('blog:timeline'))
    return render(request, 'web/register.html', {'register_form': register_form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect(reverse('blog:timeline'))
    login_form = LoginForm()
    if(request.method == 'POST'):
        login_form = LoginForm(request.POST)
        if login_form.is_valid():
            username = login_form.cleaned_data['username']
            password = login_form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request,user)
                return redirect(reverse('blog:timeline'))
    return render(request, 'web/login.html', {'login_form':login_form})

def logout_view(request):
    logout(request)
    return redirect(reverse('web:index'))