import threading
from apscheduler.schedulers.background import BackgroundScheduler
from django.shortcuts import render
from schedule import Scheduler
import schedule
import time
import random
from . import main
from . import settings
from . import var_defs
from . import ogamu
from django.http import HttpResponse
from django.contrib.auth.models import User, auth
from django.shortcuts import render,redirect
from django.contrib import messages
import apscheduler.schedulers.blocking
import math

bot_is_on = False
scheduler = BackgroundScheduler()
job_autosave = None
job_expo = None
job_farm = None
text_id = 0
output_msg = ""
farming_an = False
init = True
first_farm = True
all_farm_planets = var_defs.AllFarmPlanets()
current_state = var_defs.FarmState
analyse_timer = 0
farm_timer = 0.5
random_timer = 30
idle_timer = 5
idle_counter = 0



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

counter_bot = 0
counter_rand = random.randint(6, 14)
def farm_tick():
    global counter_bot
    global counter_rand
    global current_state
    global analyse_timer
    if(farming_an and bot_is_on):
        print(current_state)
        current_farm_planet = all_farm_planets.get_current_farm_planet()
        print("Running farm on...: "+current_farm_planet.name)
        if(not all_farm_planets.skip_if_not_allowed(current_farm_planet)):
            if(current_state == var_defs.FarmState.Scan and not all_farm_planets.all_already_scanned()
                    and not current_farm_planet.already_scanned):
                print("Scan Modus")
                main.scan_modus()
            elif (current_state == var_defs.FarmState.Scan and not all_farm_planets.all_already_scanned()
                    and current_farm_planet.already_scanned):
                all_farm_planets.next_farm_planet()
                print("SWITCH BACK!")
            elif (current_state == var_defs.FarmState.Scan and all_farm_planets.all_already_scanned()):
                current_state = var_defs.FarmState.Spy
                counter_bot = 0
                counter_rand = random.randint(6, 14)
            if (current_state == var_defs.FarmState.Spy and counter_bot > counter_rand):
                main.spy_modus()
                counter_bot = 0
                counter_rand = random.randint(6, 14)
            elif current_state == var_defs.FarmState.Spy:
                counter_bot = counter_bot + 1
            if (current_state == var_defs.FarmState.Analyse):
                analyse_timer = analyse_timer + 1
                print("Anal.Timer: "+str(analyse_timer))
                if(analyse_timer > 200):
                    print("Anaaaal!")
                    main.analyse_modus()
            if (current_state == var_defs.FarmState.Attack and counter_bot > counter_rand):
                print("Attack modudeska")
                main.attack_modus()
                counter_bot = 0
                counter_rand = random.randint(6, 14)
            elif current_state == var_defs.FarmState.Attack:
                counter_bot = counter_bot + 1
            if (current_state == var_defs.FarmState.Idle):
                print("Idlemode")
                main.go_out_of_idle()



def start_job():
    print("START!")
    global job_autosave
    global job_expo
    global job_farm
    job_autosave = scheduler.add_job(autosave_tick, 'interval', seconds=45 , id='autosave')
    job_expo = scheduler.add_job(expo_tick, 'interval', seconds=60, id='expo')
    job_farm = scheduler.add_job(farm_tick,'interval', seconds=farm_timer, id='farm')
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
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets,
                                               "res_slot": settings.slots_reserviert,
                                               "exp_slot": settings.expo_reserviert})


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
    settings.slots_reserviert = request.POST['reserve_slots']
    settings.expo_reserviert = request.POST['exp_slots']

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets,
                                               "res_slot": settings.slots_reserviert ,"exp_slot": settings.expo_reserviert })


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
                        selected_planis = []
                        allowed_slots = ogamu.get_allowed_slots()
                        for planet in var_defs.all_planets:
                            if request.POST.get(planet["Name"], False) == "on" and not planet["Name"] == celest["Name"]:
                                selected_planis.append(planet["Name"])
                        if(len(selected_planis) <= allowed_slots):
                            if (not celest is None):
                                output_text("Sammeln auf P:" + str(gal) + ":" + str(sys) + ":" + str(pos))
                                main.gather_all_res(gal, sys, pos,selected_planis,moon)
                            else:
                                output_text("Diese Koords gibt es nicht!")
                        else:
                            output_text("Du hast nicht genug freie Slots!")
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
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets,
                                               "res_slot": settings.slots_reserviert,
                                               "exp_slot": settings.expo_reserviert})

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
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets,
                                               "res_slot": settings.slots_reserviert,
                                               "exp_slot": settings.expo_reserviert})

id_celest = 0
def farming(request):
    global id_celest
    global all_farm_planets
    global farming_an
    global current_state
    global first_farm
    if_added = False
    at_least_one = False

    for planet in var_defs.all_planets:
        if request.POST.get(planet["Name"],False) == "on":
            if(not all_farm_planets.already_exits(planet["Name"])):
                moon = True
                id_celest = planet["ID"]
                if(planet["Moon"]==None):
                    moon = False
                else:
                    id_celest = ogamu.get_celest_ID3(planet)
                    print(id_celest)
                (gal,sys,pos)= ogamu.get_coords(planet)
                planet['isFarming'] = True

                all_farm_planets.add_planet(id_celest,planet["Name"],gal,sys,pos,moon)
                print("Wurde der Datenbank hinzugefügt: "+planet["Name"])
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                farm_plani.init_scan_vars()
                if_added = True
                at_least_one = True
            else:
                print("Ist schon in der Datenbank! Turn On!: "+planet["Name"])
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                current_state == var_defs.FarmState.Scan
                planet['isFarming'] = True
                at_least_one = True
                farm_plani.turn_on()
        else:
            if(all_farm_planets.already_exits(planet["Name"])):
                planet['isFarming'] = False
                farm_plani = all_farm_planets.get_planet_by_name(planet["Name"])
                if(all_farm_planets.get_current_farm_planet().name == planet["Name"]):
                    current_state == var_defs.FarmState.Scan
                farm_plani.turn_off()
                print("Ist schon in der Datenkbank! Turn off:!  "+planet["Name"])
    if(if_added == True and first_farm == True):
        current_state = var_defs.FarmState.Scan
        first_farm = False
        print("Scan started for the first time!")
    if request.POST.get("farm_on", False) and at_least_one:
        farming_an = True
    else:
        farming_an = False

    return render(request, 'home_norma.html', {'bot_on': bot_is_on, 'kt_exp': settings.kleine_transporter_exp,
                                               'gt_exp': settings.große_transporter_exp
        , 'lj_exp': settings.leichte_jaeger_exp, 'sj_exp': settings.schwere_jaeger_exp, 'xer_exp': settings.kreuzer_exp
        , 'ss_exp': settings.schlachtschiff_exp, 'sxer_exp': settings.schlachtkreuzer_exp,
                                               'reaper_exp': settings.reaper_exp
        , 'spy_exp': settings.spio_sonde_exp, 'path_exp': settings.pathfinder_exp, 'exp_an_exp': settings.expo_an
        , 'output_text': output_msg, "farm_on": farming_an, "farm_planets": var_defs.all_planets,
                                               "res_slot": settings.slots_reserviert,
                                               "exp_slot": settings.expo_reserviert})


