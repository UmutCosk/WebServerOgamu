from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('toggle_bot', views.toggle_bot, name='toggle_bot'),
    path('collect',views.collect,name='collect'),
    path('set_expo',views.set_expo,name='set_exp'),
    path('farming',views.farming,name='farming')

]
