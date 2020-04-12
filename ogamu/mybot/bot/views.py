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
init = True
all_farm_planets = var_defs.AllFarmPlanets()
current_state = var_defs.FarmState


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
    global current_state
    if(farming_an):
        print("Running farm...")
        if(not current_state == var_defs.FarmState.Idle):
            current_farm_planet = all_farm_planets.get_current_farm_planet()
            if(not all_farm_planets.skip_if_not_allowed(current_farm_planet)):
                if(current_state == var_defs.FarmState.Scan and not all_farm_planets.all_already_scanned()
                        and not current_farm_planet.already_scanned):
                    print("Scan Modus")
                    main.scan_modus()
                elif (current_state == var_defs.FarmState.Scan and not all_farm_planets.all_already_scanned()
                        and current_farm_planet.already_scanned):
                    all_farm_planets.next_farm_planet()
                elif (current_state == var_defs.FarmState.Scan and all_farm_planets.all_already_scanned()):
                    current_state = var_defs.FarmState.Spy
                if (current_state == var_defs.FarmState.Spy):
                    print("SPY Moduss")
                    all_farm_planets.next_farm_planet()
                    pass
                if (current_state == var_defs.FarmState.Attack):
                    pass





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
    global init
    global current_state
    if(init):
        var_defs.all_planets = ogamu.get_planets()
        for planet in var_defs.all_planets:
            planet['isFarming'] = False
        init = False
        current_state = var_defs.FarmState.Scan


    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets})


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
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets})


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
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets})

def set_expo(request):
    global farming_an
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


    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets})

def farming(request):
    global all_farm_planets
    global farming_an
    if request.POST.get("farm_on", False):
        farming_an = True
    else:
        farming_an = False

    for planet in var_defs.all_planets:
        if request.POST.get(planet["Name"],False) == "on":
            if(not all_farm_planets.already_exits(planet["Name"])):
                moon = True
                if(planet["Moon"]==None):
                    moon = False
                (gal,sys,pos)= ogamu.get_coords(planet)
                planet['isFarming'] = True
                all_farm_planets.add_planet(planet["Name"],gal,sys,pos,moon)
                print("Wurde der Datenbank hinzugefügt: "+planet["Name"])
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                farm_plani.init_scan_vars()
            else:
                print("Ist schon in der Datenbank! Turn On!: "+planet["Name"])
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                farm_plani.turn_on()
        else:
            if(all_farm_planets.already_exits(planet["Name"])):
                planet['isFarming'] = False
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                farm_plani.turn_off()
                print("Ist schon in der Datenkbank! Turn off:!  "+planet["Name"])



    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                        'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                        'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets})


