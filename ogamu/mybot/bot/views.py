import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import render
from schedule import Scheduler
import schedule
import time
from . import main
from . import settings
from . import var_defs
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.shortcuts import render,redirect
from django.contrib import messages

bot_is_on = False
scheduler = BackgroundScheduler()
job_autosave = None
job_expo = None
text_id = 0
output_msg = ""



def login(request):
    return render(request, 'login.html')

def output_text(text):
    global output_msg
    global text_id
    output_msg = "Msg ID: "+str(text_id)+" > "+text
    text_id = text_id+1

def autosave_tick():
    print("Running autosave...")
    main.autoSave()

def expo_tick():
    main.startExpo()
    print("Running expo...")

def farm_tick():
    print("Running farm...")


def start_job():
    print("START!")
    global job_autosave
    global job_expo
    job_autosave = scheduler.add_job(autosave_tick, 'interval', seconds=60 , id='autosave')
    job_expo = scheduler.add_job(expo_tick, 'interval', seconds=60, id='expo')
    try:
        scheduler.start()
    except:
        pass

def stop_job():
    print("STOP!")
    scheduler.remove_job('autosave')
    scheduler.remove_job('expo')

def home(request):
    return render(request, 'bot/home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                             'gt_exp': settings.große_transporter_exp
            , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
            , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                             'reaper_exp': settings.reaper_exp
            , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
            , 'output_text': output_msg})


#



def toggle_bot(request):
    global bot_is_on
    if request.POST['bot_status'] == "bot_an":
        if not bot_is_on:
            bot_is_on = True
            #start_job()
            output_text("Bot ist an!")
        else:
            output_text("Bot ist bereits an!")
    else:
        if bot_is_on:
            bot_is_on = False
            #stop_job()
            output_text("Bot ist aus!")
        else:
            output_text("Bot ist bereits aus!")
    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                         'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                         'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg})


def collect(request):
    global bot_is_on
    if bot_is_on:
        if not request.POST['collect1'] == "" and not request.POST['collect2'] == ""  and not request.POST['collect3'] == "" :
            if int(request.POST['collect1']) >= 1 and int(request.POST['collect1']) <= 6:
                if int(request.POST['collect2']) >= 1 and int(request.POST['collect2']) <= 499:
                    if int(request.POST['collect3']) >= 1 and int(request.POST['collect3']) <= 15:
                        gal = request.POST['collect1']
                        sys = request.POST['collect2']
                        pos = request.POST['collect3']
                        moon = False
                        if(request.POST.get('collect4',False) == "on"):
                            moon = True
                            output_text("Sammeln auf M:"+str(gal)+":"+str(sys)+":"+str(pos))
                        else:
                            output_text("Sammeln auf P:"+str(gal)+":"+str(sys)+":"+str(pos))
                        # main.gather_all_res(gal,sys,pos,moon)
                    else:
                        output_text("Error: Planizahl ist außerhalb des Wertebereichs")
                else:
                    output_text("Error: Syszahl ist außerhalb des Wertebereichs")
            else:
                output_text("Error: Galazahl ist außerhalb des Wertebereichs")
        else:
            output_text("Error: Zahlenfeld vergessen?")
    else:
        output_text("Sammeln geht nicht! -> Bot ist aus!")

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                         'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                         'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg})

def set_expo(request):
    global bot_is_on
    if bot_is_on:
        kt = request.POST['exp_kt']
        gt = request.POST['exp_gt']
        lj = request.POST['exp_lj']
        sj = request.POST['exp_sj']
        xer = request.POST['exp_xer']
        ss = request.POST['exp_ss']
        sxer = request.POST['exp_sxer']
        reaper = request.POST['exp_reaper']
        spy = request.POST['exp_spy']
        path = request.POST['exp_path']
        exp_an = False
        if (request.POST.get('exp_an',False) == "on"):
            exp_an = True
            output_text("Expo Funktion eingeschaltet!")
        else:
            output_text("Expo Funktion ausgeschaltet!!")
        settings.kleine_transporter_exp = int(kt)
        settings.große_transporter_exp = int(gt)
        settings.leichte_jaeger_exp = int(lj)
        settings.schwere_jaeger_exp = int(sj)
        settings.kreuzer_exp = int(xer)
        settings.schlachtschiff_exp = int(ss)
        settings.schlachtkreuzer_exp = int(sxer)
        settings.reaper_exp = int(reaper)
        settings.spio_sonde_exp = int(spy)
        settings.pathfinder_exp = int(path)
        settings.expo_an = exp_an
        if(request.POST.get('manuel_senden', False)):
            main.startExpo()
            output_text("Expo Settings gespeichert und gestartet!")
        else:
            output_text("Expo gestartet!")
    else:
        output_text("Error: Bot ist aus!")

    return render(request, 'home_norma.html',   {'bot_on': bot_is_on,'kt_exp': settings.kleine_transporter_exp, 'gt_exp':settings.große_transporter_exp
        ,'lj_exp': settings.leichte_jaeger_exp,'sj_exp':settings.schwere_jaeger_exp,'xer_exp':settings.kreuzer_exp
        ,'ss_exp': settings.schlachtschiff_exp ,'sxer_exp': settings.schlachtkreuzer_exp,'reaper_exp':settings.reaper_exp
        ,'spy_exp': settings.spio_sonde_exp,'path_exp':settings.pathfinder_exp,'exp_an_exp': settings.expo_an
        ,'output_text' : output_msg})

def farming(request):
    if(not(request.POST['farm_gal_1'] == "" or request.POST['farm_sys_1'] == "" or request.POST['farm_pos_1'] == "")):
        if int(request.POST['farm_gal_1']) >= 1 and int(request.POST['farm_gal_1']) <= 6:
            if int(request.POST['farm_sys_1']) >= 1 and int(request.POST['farm_sys_1']) <= 499:
                if int(request.POST['farm_pos_1']) >= 1 and int(request.POST['farm_pos_1']) <= 15:
                    var_defs.farmPlani1.gal = request.POST['farm_gal_1']
                    var_defs.farmPlani1.sys = request.POST['farm_sys_1']
                    var_defs.farmPlani1.pos = request.POST['farm_pos_1']
                    var_defs.farmPlani1.use = True
    else:
        var_defs.farmPlani1.use = False

    if (not (request.POST['farm_gal_2'] == "" or request.POST['farm_sys_2'] == "" or request.POST['farm_pos_2'] == "")):
        if int(request.POST['farm_gal_2']) >= 1 and int(request.POST['farm_gal_2']) <= 6:
            if int(request.POST['farm_sys_2']) >= 1 and int(request.POST['farm_sys_2']) <= 499:
                if int(request.POST['farm_pos_2']) >= 1 and int(request.POST['farm_pos_2']) <= 15:
                    var_defs.farmPlani2.gal = request.POST['farm_gal_2']
                    var_defs.farmPlani2.sys = request.POST['farm_sys_2']
                    var_defs.farmPlani2.pos = request.POST['farm_pos_2']
                    var_defs.farmPlani2.use = True
    else:
        var_defs.farmPlani2.use = False

    if (not (request.POST['farm_gal_3'] == "" or request.POST['farm_sys_3'] == "" or request.POST['farm_pos_3'] == "")):
        if int(request.POST['farm_gal_3']) >= 1 and int(request.POST['farm_gal_3']) <= 6:
            if int(request.POST['farm_sys_3']) >= 1 and int(request.POST['farm_sys_3']) <= 499:
                if int(request.POST['farm_pos_3']) >= 1 and int(request.POST['farm_pos_3']) <= 15:
                    var_defs.farmPlani3.gal = request.POST['farm_gal_3']
                    var_defs.farmPlani3.sys = request.POST['farm_sys_3']
                    var_defs.farmPlani3.pos = request.POST['farm_pos_3']
                    var_defs.farmPlani3.use = True
    else:
        var_defs.farmPlani3.use = False


    if (request.POST.get('farm_on', False) == False):
        settings.farming_an = False
    else:
        settings.farming_an = True

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                         'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                         'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg})


