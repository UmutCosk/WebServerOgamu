import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import render
from schedule import Scheduler
import schedule
import time
from . import logic
from django.http import HttpResponse
# Create your views here.
# request.POST.get("title", "")


bot_is_on = False
scheduler = BackgroundScheduler()
job = None

def tick():
    print("test")

def start_job():
    print("START!")
    global job
    job = scheduler.add_job(tick, 'interval', seconds=1 , id='test')
    try:
        scheduler.start()
    except:
        pass

def stop_job():
    print("STOP!")
    scheduler.remove_job('test')


def home(request):
    global bot_is_on
    if bot_is_on:
        return render(request, 'home.html', {'bot_on': 'checked'})
    else:
        return render(request, 'home.html', {'bot_off': 'checked'})
    return render(request, 'home.html')




def toggle_bot(request):
    global bot_is_on
    if request.POST['bot_status'] == "on":
        if not bot_is_on:
            bot_is_on = True
            start_job()
        return render(request,'home.html', {'bot_on': 'checked'})
    else:
        if bot_is_on:
            bot_is_on = False
            stop_job()
        return render(request, 'home.html', {'bot_off': 'checked'})
    return render(request,'home.html')



