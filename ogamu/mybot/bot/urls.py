from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle_bot', views.toggle_bot, name='toggle_bot')

]
