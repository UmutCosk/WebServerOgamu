import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import render
from schedule import Scheduler
import schedule
import time
from . import main
from . import settings
from . import var_defs
from . import ogamu
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.shortcuts import render,redirect
from django.contrib import messages
import apscheduler.schedulers.blocking

bot_is_on = False
scheduler = BackgroundScheduler()
job_autosave = None
job_expo = None
job_farm = None
text_id = 0
output_msg = ""
farming_an = False
def output_text(text):
    global output_msg
    global text_id
    output_msg = "Msg ID: "+str(text_id)+" > "+text
    text_id = text_id+1

def autosave_tick():
    if bot_is_on:
        print("Running autosave...")
        main.autoSave()




def expo_tick():
    if(settings.expo_an and bot_is_on):
        main.startExpo()
        print("Running expo...")

def farm_tick():
    if(farming_an and bot_is_on):
        print("Running farm...")
        if(not var_defs.already_attacking):
            gal = var_defs.all_farm_planis[var_defs.cur_farm_nr].gal
            sys = var_defs.all_farm_planis[var_defs.cur_farm_nr].sys
            pos = var_defs.all_farm_planis[var_defs.cur_farm_nr].pos
            rad = var_defs.all_farm_planis[var_defs.cur_farm_nr].rad
            moon= var_defs.all_farm_planis[var_defs.cur_farm_nr].moon
            main.setup_atk_session(gal,sys,pos,rad,moon)
            var_defs.already_attacking = True
        elif var_defs.my_attack_session.is_running:
            main.run_spy_session()



def start_job():
    print("START!")
    global job_autosave
    global job_expo
    global job_farm
    job_autosave = scheduler.add_job(autosave_tick, 'interval', seconds=10 , id='autosave')
    job_expo = scheduler.add_job(expo_tick, 'interval', seconds=60, id='expo')
    job_farm = scheduler.add_job(farm_tick,'interval',seconds=3,id='farm')
    try:
        scheduler.start()
    except:
        pass

def stop_job():
    print("STOP!")
    scheduler.remove_job('autosave')
    scheduler.remove_job('expo')
    scheduler.remove_job('farm')

def home(request):
    global farming_an
    ogamu.log_out()
    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an})


#



def toggle_bot(request):
    global bot_is_on
    global farming_an
    if request.POST['bot_status'] == "bot_an":
        if not bot_is_on:
            bot_is_on = True
            ogamu.log_in()
            start_job()
            output_text("Bot ist an!")
        else:
            output_text("Bot ist bereits an!")
    else:
        if bot_is_on:
            bot_is_on = False
            ogamu.log_out()
            stop_job()
            output_text("Bot ist aus!")
        else:
            output_text("Bot ist bereits aus!")
    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an})


def collect(request):
    global bot_is_on
    global farming_an
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

                        celest = ogamu.get_celest_by_pos(gal, sys,pos,moon)
                        if (not celest is None):
                            output_text("Sammeln auf P:" + str(gal) + ":" + str(sys) + ":" + str(pos))
                            main.gather_all_res(gal, sys, pos, moon)
                        else:
                            output_text("Diese Koords gibt es nicht!")
                    else:
                        output_text("Error: Planizahl ist außerhalb des Wertebereichs")
                else:
                    output_text("Error: Syszahl ist außerhalb des Wertebereichs")
            else:
                output_text("Error: Galazahl ist außerhalb des Wertebereichs")
        else:
            output_text("Error: Zahlenfeld vergessen?")
    else:
        output_text("Bot ist aus!")

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an})

def set_expo(request):
    global bot_is_on
    global farming_an
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

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an})

def farming(request):
    global farming_an
    var_defs.max_farm_nr = 0
    var_defs.cur_farm_nr = 0
    var_defs.all_farm_planis.clear()
    var_defs.already_attacking = False
    var_defs.farmPlani1.use = False
    var_defs.farmPlani2.use = False
    var_defs.farmPlani3.use = False
    if (not request.POST.get('farm_on', False) == False):
        if(not request.POST['farm_gal_1'] == "" and not request.POST['farm_sys_1'] == "" and not request.POST['farm_pos_1'] == ""
                and not request.POST['farm_rad_1'] == ""):
            if int(request.POST['farm_gal_1']) >= 1 and int(request.POST['farm_gal_1']) <= 6:
                if int(request.POST['farm_sys_1']) >= 1 and int(request.POST['farm_sys_1']) <= 499:
                    if int(request.POST['farm_pos_1']) >= 1 and int(request.POST['farm_pos_1']) <= 15:
                        var_defs.farmPlani1.gal = int(request.POST['farm_gal_1'])
                        var_defs.farmPlani1.sys = int(request.POST['farm_sys_1'])
                        var_defs.farmPlani1.pos = int(request.POST['farm_pos_1'])
                        var_defs.farmPlani1.rad = int(request.POST['farm_rad_1'])
                        var_defs.farmPlani1.use = True
                        var_defs.farmPlani1.moon = False
                        if (request.POST.get('farm_moon_1', False) == "on"):
                            var_defs.farmPlani1.moon = True
                        celest = ogamu.get_celest_by_pos(var_defs.farmPlani1.gal, var_defs.farmPlani1.sys,
                                                         var_defs.farmPlani1.pos, var_defs.farmPlani1.moon)
                        print(celest)
                        if (not celest is None):
                            var_defs.max_farm_nr = var_defs.max_farm_nr + 1
                            var_defs.all_farm_planis.append((var_defs.farmPlani1))
                            farming_an = True
                            print("ICH WAR HIER!")
                        else:
                            output_text("Diese Koords gibt es nicht!")
                            farming_an = False




        var_defs.farmPlani2.use = False
        if (not (request.POST['farm_gal_2'] == "" or request.POST['farm_sys_2'] == "" or request.POST['farm_pos_2'] == ""or
        request.POST['farm_rad_2'] == "")):
            if int(request.POST['farm_gal_2']) >= 1 and int(request.POST['farm_gal_2']) <= 6:
                if int(request.POST['farm_sys_2']) >= 1 and int(request.POST['farm_sys_2']) <= 499:
                    if int(request.POST['farm_pos_2']) >= 1 and int(request.POST['farm_pos_2']) <= 15:
                        var_defs.farmPlani2.gal = int(request.POST['farm_gal_2'])
                        var_defs.farmPlani2.sys = int(request.POST['farm_sys_2'])
                        var_defs.farmPlani2.pos = int(request.POST['farm_pos_2'])
                        var_defs.farmPlani2.rad = int(request.POST['farm_rad_2'])
                        var_defs.farmPlani2.use = True
                        var_defs.farmPlani2.moon = False
                        if (request.POST.get('farm_moon_2', False) == "on"):
                            var_defs.farmPlani2.moon = True
                        celest = ogamu.get_celest_by_pos(var_defs.farmPlani2.gal ,var_defs.farmPlani2.sys,var_defs.farmPlani2.pos,var_defs.farmPlani2.moon)
                        if(not celest is None):
                            var_defs.max_farm_nr = var_defs.max_farm_nr + 1
                            var_defs.all_farm_planis.append((var_defs.farmPlani2))
                            farming_an = True
                        else:
                            farming_an = False
                            output_text("Diese Koords gibt es nicht!")


        var_defs.farmPlani3.use = False
        if (not (request.POST['farm_gal_3'] == "" or request.POST['farm_sys_3'] == "" or request.POST['farm_pos_3'] == ""or
        request.POST['farm_rad_3']== "")):
            if int(request.POST['farm_gal_3']) >= 1 and int(request.POST['farm_gal_3']) <= 6:
                if int(request.POST['farm_sys_3']) >= 1 and int(request.POST['farm_sys_3']) <= 499:
                    if int(request.POST['farm_pos_3']) >= 1 and int(request.POST['farm_pos_3']) <= 15:
                        var_defs.farmPlani3.gal = int(request.POST['farm_gal_3'])
                        var_defs.farmPlani3.sys = int(request.POST['farm_sys_3'])
                        var_defs.farmPlani3.pos = int(request.POST['farm_pos_3'])
                        var_defs.farmPlani3.rad = int(request.POST['farm_rad_3'])
                        var_defs.farmPlani3.use = True
                        var_defs.farmPlani3.moon = False
                        if (request.POST.get('farm_moon_3', False) == "on"):
                            var_defs.farmPlani3.moon = True
                        celest = ogamu.get_celest_by_pos(var_defs.farmPlani3.gal, var_defs.farmPlani3.sys,
                                                         var_defs.farmPlani3.pos, var_defs.farmPlani3.moon)
                        if (not celest is None):
                            var_defs.max_farm_nr = var_defs.max_farm_nr + 1
                            var_defs.all_farm_planis.append((var_defs.farmPlani3))
                            farming_an = True
                        else:
                            farming_an = False
                            output_text("Diese Koords gibt es nicht!")
    else:
        farming_an = False

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg,"farm_on": farming_an})


