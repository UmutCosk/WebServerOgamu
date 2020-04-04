from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.shortcuts import render

# Create your views here.
def index(request):
    return render(request,'web/base.html')

def register(request):
    register_form = UserCreationForm()
    return render(request, 'web/register.html',{'register_form':register_form})

def login(request):
    login_form = AuthenticationForm()
    return render(request,'web/login.html',{'login_form':login_form})