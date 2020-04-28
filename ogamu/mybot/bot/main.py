import operator
import requests
import time
import schedule
from random import randrange, uniform
from threading import Timer
from . import var_defs
from . import settings
from . import ogamu
from . import views
import math

def startExpo():
    if settings.expo_an:
        for planet in ogamu.get_planets():
            if(ogamu.checkSlots()[1] == True):
                ogamu.setExpo(planet)
        for moon in ogamu.get_moons():
            if(ogamu.checkSlots()[1] == True):
                ogamu.setExpo(moon)


def get_galaxy_info(gal, sys):
    r = requests.get(
        url="http://"+settings.adress+"/bot/galaxy-infos/"+str(gal)+"/"+str(sys))
    data = r.json()
    return data

def get_coords_of_another_planet(mygal,mysys,mypos):
    for planet in var_defs.all_planets:
        print(planet)
        if(not(planet["Coordinate"]["Galaxy"] == mygal and planet["Coordinate"]["System"] == mysys and planet["Coordinate"]["Position"] == mypos)):
            return (planet["Coordinate"]["Galaxy"],planet["Coordinate"]["System"] ,planet["Coordinate"]["Position"])
    return (0,0,0)


def saveAllFleet(attacked_planet):
    id_planet = ogamu.get_celest_ID2(attacked_planet)
    (gal, sys, pos) = ogamu.get_coords2(attacked_planet)
    (metal, crystal, deut) = ogamu.get_celest_ressis2(attacked_planet)
    # Schiffe
    ships = ogamu.get_all_ships2(id_planet)
    fleet = var_defs.Fleet(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,ships=ships)
    data = fleet.fill_fleet_data(
        gal, sys, 16, var_defs.Missions.Spy.value, 1, metal, crystal, deut)
    print("ID: "+str(id_planet))
    data = fleet.send_fleet(id_planet, data)
    print(data)
    if(not data["Status"] == 'error'):
        var_defs.call_back_ids.append(data["Result"]["ID"])
        print("SEND FOR SAVE")
    else:
        print("YOU DON'T HAVE ANY SHIPS!")


def already_scanned(gal,sys,pos):
    for already_spied_id in var_defs.already_spied_ids:
        if(already_spied_id.gal == gal and already_spied_id.sys == sys and already_spied_id.pos == pos ):
            return True
    return False

def autoSave():
    attacks = ogamu.get_all_attacks()
    if attacks is not None:
        if(len(attacks) > 0):
            for attack in attacks:
                arrival_time = attack["ArriveIn"]
                print("arrival time: "+str(arrival_time))
                # Zurück spionieren bei unter 1234 Sekunden
                check_coords = var_defs.Coords(attack["Origin"]["Galaxy"],attack["Origin"]["System"],attack["Origin"]["Position"])
                if (not already_scanned(check_coords.gal,check_coords.sys,check_coords.pos) and arrival_time < 2345):
                    if(not ogamu.onlySpy(attack) or settings.test_on):
                        var_defs.already_spied_ids.append(check_coords)
                        ogamu.spyEnemy2(attack["Origin"], ogamu.get_celest_ID2(attack["Destination"]))
                        ogamu.isUnderAttack()
                        print("ENEMY ZURÜCK GESCANNT!")
                # Saven bei unter 123 Sekunden
                if(arrival_time < 240 and attack["ID"] not in var_defs.already_saved_ids):
                    if(not ogamu.onlySpy(attack) or settings.test_on):
                        var_defs.already_saved_ids.append(attack["ID"])
                        saveAllFleet(attack["Destination"])
                        ogamu.isUnderAttack()
        else:
            ogamu.callBackFleet(var_defs.call_back_ids)
            var_defs.already_saved_ids.clear()
            var_defs.already_spied_ids.clear()
            var_defs.call_back_ids.clear()



def is_good_spy_report(spy_report):
    result = spy_report["Result"]
    if(result["HasFleetInformation"] == True and result["HasDefensesInformation"] == True):
        if(result["RocketLauncher"] == None and result["LightLaser"] == None and result["HeavyLaser"] == None and
           result["GaussCannon"] == None and result["IonCannon"] == None and result["PlasmaTurret"] == None and
           result["SmallShieldDome"] == None and result["LargeShieldDome"] == None and result["LightFighter"] == None and
           result["HeavyFighter"] == None and result["Cruiser"] == None and result["Battleship"] == None and
           result["Battlecruiser"] == None and result["Bomber"] == None and result["Destroyer"] == None and
           result["SmallCargo"] == None and result["LargeCargo"] == None and result["ColonyShip"] == None and
           result["Recycler"] == None and result["Reaper"] == None and result["Pathfinder"] == None):
            return True
    return False


def gather_all_res(target_gal, target_sys, target_pos, selected_planis,moon=False):
    my_target_celest = ogamu.get_celest_by_pos(
        target_gal, target_sys, target_pos)
    target_id = ogamu.get_celest_ID(my_target_celest)
    for planet_name in selected_planis:
        # Get Coords
        planet = ogamu.get_plani_by_name(planet_name)
        from_planet_id = planet["ID"]
        # Alle KT und GT
        ships = ogamu.get_all_ships(planet)
        all_kt = ships["Result"]["SmallCargo"]
        all_gt = ships["Result"]["LargeCargo"]
        # Alle Ressis auf Plani
        (met, cris, deut) = ogamu.get_celest_ressis(planet)
        sum_res = int(met)+int(cris)+int(deut)
        # Calc Kapa KT:
        (kapa_kt, kapa_gt, one_kt, one_gt) = ogamu.calc_cargo_kapa(
            all_kt, all_gt)
        if(kapa_kt > sum_res):
            kt_needed = int(round(sum_res/one_kt))
            my_fleet = var_defs.Fleet(
                0, 0, 0, 0, 0, 0, 0, 0, kt_needed, 0, 0, 0, 0, 0, 0, 0, 0)
            data = my_fleet.fill_fleet_data(
                target_gal, target_sys, target_pos, var_defs.Missions.Transport.value, 10, met, cris, deut, moon=moon)
            my_fleet.send_fleet(from_planet_id, data)
            print("GATHER nur mit KT!")
        else:
            sum_res = sum_res - kapa_kt
            gt_needed = 0
            if(not all_gt is 0):
                gt_needed = int(round(sum_res/one_gt))
            if(gt_needed < all_gt):
                my_fleet = var_defs.Fleet(
                    0, 0, 0, 0, 0, 0, 0, 0, all_kt, gt_needed, 0, 0, 0, 0, 0, 0, 0)
                data = my_fleet.fill_fleet_data(
                    target_gal, target_sys, target_pos, var_defs.Missions.Transport.value, 10, met, cris, deut, moon=moon)
                my_fleet.send_fleet(from_planet_id, data)
                print("GATHER mit allen KT's und paar GT!")
            else:
                my_fleet = var_defs.Fleet(
                    0, 0, 0, 0, 0, 0, 0, 0, all_kt, all_gt, 0, 0, 0, 0, 0, 0, 0)
                data = my_fleet.fill_fleet_data(
                    target_gal, target_sys, target_pos, var_defs.Missions.Transport.value, 10, met, cris, deut, moon=moon)
                my_fleet.send_fleet(from_planet_id, data)
                print("GATHER mit allen KT's und allen GT!")

sys_data = None
switch_sys = True

def scan_modus():
    global sys_data
    global  switch_sys

    current_farm_plani = views.all_farm_planets.get_current_farm_planet()
    if(switch_sys):
        sys_data = ogamu.get_galaxy_info(current_farm_plani.current_scan_gal, current_farm_plani.current_scan_sys)
        switch_sys = False
    enemy_planet = sys_data["Result"]["Planets"][current_farm_plani.current_scan_pos]
    if (not enemy_planet == None and enemy_planet["Inactive"] == True and enemy_planet["Vacation"] == False and
                 enemy_planet["Banned"] == False and enemy_planet["Player"]["Rank"] < settings.min_rank and
                     enemy_planet["Player"]["Rank"] > settings.max_rank):
        (gal,sys,pos) = ogamu.get_coords(enemy_planet)
        current_farm_plani.add_spy_report(gal,sys,pos)
        print("Found good inactive!")
    current_farm_plani.current_scan_pos = current_farm_plani.current_scan_pos + 1
    print("Sys: " + str(current_farm_plani.current_scan_sys) + "Pos: " + str(current_farm_plani.current_scan_pos))
    if(current_farm_plani.current_scan_pos == 15):
        current_farm_plani.current_scan_pos = 0
        current_farm_plani.current_scan_sys = current_farm_plani.current_scan_sys + 1
        switch_sys = True

        if current_farm_plani.current_scan_sys == 500:
            current_farm_plani.current_scan_sys = 1
        if(current_farm_plani.current_scan_sys == current_farm_plani.max_scan_sys):
            print("Scan done for: !"+str(current_farm_plani.name))
            current_farm_plani.already_scanned = True
            current_farm_plani.last_spy_index = len(current_farm_plani.spy_reports)
            current_farm_plani.current_spy_index = 0
            current_farm_plani.current_scan_sys = current_farm_plani.min_sys


def spy_modus():
    if (ogamu.checkSlots()[0] == True):
        current_farm_plani = views.all_farm_planets.get_current_farm_planet()
        if len(current_farm_plani.spy_reports) > 0:
            (gal,sys,pos) = current_farm_plani.get_spy_report_pos(current_farm_plani.current_spy_index)
            ogamu.spyEnemy(gal,sys,pos,current_farm_plani.id)
            current_farm_plani.current_spy_index = current_farm_plani.current_spy_index + 1
            if(current_farm_plani.current_spy_index == current_farm_plani.last_spy_index ):
                print("Spy modus done!")
                current_farm_plani.last_analyse_index = len(current_farm_plani.spy_reports)
                current_farm_plani.current_analyse_index = 0
                current_farm_plani.current_spy_index = 0
                views.current_state = var_defs.FarmState.Analyse
        else:
            print("Keine Spio Berichte gefunden! Radius zu klein? Rang zu streng gewählt?")
            current_farm_plani.last_analyse_index = len(current_farm_plani.spy_reports)
            current_farm_plani.current_analyse_index = 0
            current_farm_plani.current_spy_index = 0
            views.current_state = var_defs.FarmState.Idle
    else:
        print("No Slots currently available")


def analyse_modus():
    current_farm_plani = views.all_farm_planets.get_current_farm_planet()
    (gal,sys,pos) = current_farm_plani.get_spy_report_pos(current_farm_plani.current_analyse_index)
    spy_report = ogamu.get_spy_report(gal,sys,pos)
    if (spy_report["Status"] == 'error'):
        views.farming_an = False
        for i in range(5):
            print("Fehler beim auslesen des Berichtes Try: nr.: " + str(i))
            ogamu.log_out()
            ogamu.log_in()
            spy_report = ogamu.get_spy_report(gal, sys, pos)
            if (not spy_report["Status"] == 'error'):
                break
            print("Könnte Spio Bericht nicht auslesen: "+str(gal)+":"+str(sys)+":"+str(pos))
        views.farming_an = True
    elif (not spy_report["Status"] == 'error'):
        if(is_good_spy_report(spy_report)):
            res_ges = int(spy_report["Result"]["Metal"]) + int(
                spy_report["Result"]["Crystal"]) + int(spy_report["Result"]["Deuterium"])
            current_farm_plani.add_good_spy_report(gal,sys,pos,res_ges)
    current_farm_plani.current_analyse_index = current_farm_plani.current_analyse_index +1
    if(current_farm_plani.current_analyse_index == current_farm_plani.last_analyse_index):
        print("Analyse modus done!")
        current_farm_plani.last_attack_index = len(current_farm_plani.good_spy_reports)
        current_farm_plani.current_analyse_index = 0
        current_farm_plani.current_attack_index = 0
        views.analyse_timer = 0
        current_farm_plani.good_spy_reports.sort(
            key=operator.attrgetter('res'), reverse=True)
        views.current_state = var_defs.FarmState.Attack

def end_attack_modus():
    current_farm_plani = views.all_farm_planets.get_current_farm_planet()
    current_farm_plani.current_analyse_index = 0
    current_farm_plani.last_analyse_index = 0
    current_farm_plani.good_spy_reports.clear()
    current_farm_plani.current_attack_index = 0
    current_farm_plani.last_attack_index = 0
    views.current_state = var_defs.FarmState.Idle
    print("End Attack!")

def roundup(x):
    return int(math.ceil(x / 10.0)) * 10

def attack_modus():
    if (ogamu.checkSlots()[0] == True):
        current_farm_plani = views.all_farm_planets.get_current_farm_planet()
        if len(current_farm_plani.good_spy_reports) > 0 :
            ships = ogamu.get_all_ships2(current_farm_plani.id)
            total_kt = ships['Result']['SmallCargo']
            (kt_kapa, gt_kapa) = ogamu.get_cargo_kapa()
            spy_report =  current_farm_plani.good_spy_reports[current_farm_plani.current_attack_index]
            number_kt = round(
                (spy_report.res / kt_kapa) * settings.kt_ratio)


            if (number_kt < total_kt):
                total_kt = total_kt - number_kt
            elif (number_kt > total_kt):
                number_kt = total_kt
                total_kt = 0
            number_kt = roundup(number_kt)
            my_fleet = var_defs.Fleet(0, 0, 0, 0, 0, 0,
                                      0, 0, number_kt, 0, 0, 0, 0, 0, 0, 0, 0)
            data = my_fleet.fill_fleet_data(spy_report.gal, spy_report.sys,
                                            spy_report.pos,
                                            var_defs.Missions.Attack.value, 10, 0, 0, 0)
            my_fleet.send_fleet(current_farm_plani.id, data)
            print("Attacked plani!")
            current_farm_plani.current_attack_index = current_farm_plani.current_attack_index + 1
            if(current_farm_plani.current_attack_index == current_farm_plani.last_attack_index or total_kt == 0):
                end_attack_modus()
        else:
            print("Nicht genug gute Spyreports zum angreifen gefunden!")
            end_attack_modus()
    else:
        end_attack_modus()

def go_out_of_idle():
    if (ogamu.checkSlots()[0] == True):
        if(views.idle_counter > views.idle_timer*2*60):
            views.idle_counter = 0
            views.all_farm_planets.next_farm_planet()
            views.current_state = var_defs.FarmState.Scan
            print("Cycle done: Scan modus an")
        else:
            views.idle_counter = views.idle_counter + 1






