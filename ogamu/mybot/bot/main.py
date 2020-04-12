import operator
import requests
import time
import schedule
from random import randrange, uniform
from threading import Timer
from . import var_defs
from . import settings
from . import ogamu

def startExpo():
    if settings.expo_an:
        for planet in ogamu.get_planets():
            if(ogamu.checkSlots()[0] == True and ogamu.checkSlots()[1] == True):
                ogamu.setExpo(planet)
        for moon in ogamu.get_moons():
            if(ogamu.checkSlots()[0] == True and ogamu.checkSlots()[1] == True):
                ogamu.setExpo(moon)


def saveAllFleet(attacked_planet):
    id_planet = ogamu.get_celest_ID2(attacked_planet)
    (gal, sys, pos) = ogamu.get_coords2(attacked_planet)
    (metal, crystal, deut) = ogamu.get_celest_ressis2(attacked_planet)
    # Schiffe
    ships = ogamu.get_all_ships2(id_planet)
    fleet = var_defs.Fleet(0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,ships=ships)
    data = fleet.fill_fleet_data(
        5, 249, 9, var_defs.Missions.Park.value, 1, metal, crystal, deut)
    data = fleet.send_fleet(id_planet, data)
    print(data)
    if(not data["Status"] == 'error'):
        var_defs.call_back_ids.append(data["Result"]["ID"])
        print("SEND FOR SAVE")
    else:
        print("YOU DON'T HAVE ANY SHIPS!")


def autoSave():
    attacks = ogamu.get_all_attacks()
    if attacks is not None:
        if(len(attacks) > 0):
            for attack in attacks:
                arrival_time = attack["ArriveIn"]
                print("arrival time: "+str(arrival_time))
                # Zurück spionieren bei unter 1234 Sekunden
                if (attack["ID"] not in var_defs.already_spied_ids and arrival_time < 2345):
                    if(not ogamu.onlySpy(attack) or settings.test_on):
                        var_defs.already_spied_ids.append(attack["ID"])
                        ogamu.spyEnemy2(attack["Origin"],
                                       attack["Destination"])
                        ogamu.isUnderAttack()
                        time.sleep(3)
                # Saven bei unter 123 Sekunden
                if(arrival_time < 240 and attack["ID"] not in var_defs.already_saved_ids):
                    if(not ogamu.onlySpy(attack) or settings.test_on):
                        var_defs.already_saved_ids.append(attack["ID"])
                        saveAllFleet(attack["Destination"])
                        ogamu.isUnderAttack()
                        time.sleep(3)
        else:
            ogamu.callBackFleet(var_defs.call_back_ids)
            var_defs.already_saved_ids.clear()
            var_defs.already_spied_ids.clear()
            var_defs.call_back_ids.clear()

def add_to_database(all_spy_reports, my_celest):
    (gal,sys,pos) = ogamu.get_coords(my_celest)
    if(not var_defs.farm_database.is_already_farming_planet(gal,sys,pos)):
        temp_farm_plani = var_defs.FarmPlanets(gal,sys,pos,0)
        temp_farm_plani.spy_report_collection = var_defs.all_spy_reports.copy()
        var_defs.farm_database.add_farming_plani(temp_farm_plani)



def attack_inactives():
    add_to_database(var_defs.all_spy_reports,var_defs.my_attack_session.my_celest)
    number_of_attacks = ogamu.get_allowed_slots()

    if(len(var_defs.all_spy_reports) < number_of_attacks):
        number_of_attacks = len(var_defs.all_spy_reports)
    ships = ogamu.get_all_ships(var_defs.my_attack_session.my_celest)
    total_kt = ships['Result']['SmallCargo']
    print(var_defs.my_attack_session.my_celest)
    celest_id = ogamu.get_celest_ID(var_defs.my_attack_session.my_celest)
    if(number_of_attacks == 0):
        print("Keine guten Scans gefunden!")
        ogamu.log_out()
        ogamu.log_in()
    (kt_kapa, gt_kapa) = ogamu.get_cargo_kapa()
    print("Number of Attacks: "+str(number_of_attacks))
    for i in range(number_of_attacks):
        if not var_defs.all_spy_reports[i].res_ges == 0:
            number_kt = round(
                (var_defs.all_spy_reports[i].res_ges / kt_kapa)*0.55)
            if(number_kt < total_kt):
                total_kt = total_kt - number_kt
            elif (number_kt > total_kt):
                number_kt = total_kt
                total_kt = 0
            print("Nr KT: "+str(number_kt))
            my_fleet = var_defs.Fleet(0, 0, 0, 0, 0, 0,
                                      0, 0, number_kt, 0, 0, 0, 0, 0, 0, 0, 0)
            data = my_fleet.fill_fleet_data(var_defs.all_spy_reports[i].gal, var_defs.all_spy_reports[i].sys, var_defs.all_spy_reports[i].pos,
                                            var_defs.Missions.Attack.value, 10, 0, 0, 0)
            my_fleet.send_fleet(celest_id, data)
            print("Farm Sess: Angriff auf Inactiv! an: "+str(var_defs.all_spy_reports[i].gal)+":" +
                  str(var_defs.all_spy_reports[i].sys)+":" +
                  str(var_defs.all_spy_reports[i].pos)+" , mit KT's: "
                  + str(number_kt)+" , mit GesRes:"+str(var_defs.all_spy_reports[i].res_ges))
            if total_kt == 0:
                var_defs.my_attack_session.is_running  = False
                var_defs.all_spy_reports.clear()
                ogamu.delete_all_spy_reports()
                var_defs.cur_farm_nr = var_defs.cur_farm_nr + 1
                if(var_defs.cur_farm_nr == var_defs.max_farm_nr):
                    var_defs.cur_farm_nr = 0
                    var_defs.already_attacking = False
                return

    var_defs.all_spy_reports.clear()
    var_defs.my_attack_session.is_running  = False
    ogamu.delete_all_spy_reports()
    var_defs.cur_farm_nr = var_defs.cur_farm_nr + 1
    if var_defs.cur_farm_nr == var_defs.max_farm_nr:
        var_defs.cur_farm_nr = 0
        var_defs.already_attacking = False


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


def check_all_spy_reports():
    ogamu.log_out()
    ogamu.log_in()
    for spy_report in var_defs.all_spy_reports:
        gal = spy_report.gal
        sys = spy_report.sys
        pos = spy_report.pos
        report = ogamu.get_spy_report(gal, sys, pos)
        if(report["Status"] == 'error'):
            still_error = True
            for i in range(3):
                print("Fehler beim auslesen des Berichtes Try: nr.: "+str(i))
                ogamu.log_out()
                ogamu.log_in()
                report = ogamu.get_spy_report(gal, sys, pos)
                if (not report["Status"] == 'error'):
                    still_error = False
                    break
            if(still_error):
                var_defs.all_spy_reports.remove(spy_report)

        else:
            spy_report.res_ges = int(report["Result"]["Metal"])+int(
                report["Result"]["Crystal"])+int(report["Result"]["Deuterium"])
            if(not is_good_spy_report(report)):
                print(report)
                var_defs.all_spy_reports.remove(spy_report)
    # Sorting by res_ges
    var_defs.all_spy_reports.sort(
        key=operator.attrgetter('res_ges'), reverse=True)
    for i in range(len(var_defs.all_spy_reports)):
        print(var_defs.all_spy_reports[i].res_ges)
    attack_inactives()


def run_spy_session():
    (gal,sys,pos) = ogamu.get_coords(var_defs.my_attack_session.my_celest)
    if(settings.farm_from_database and not settings.reset_farm_database):
        ships = ogamu.get_all_ships(var_defs.my_attack_session.my_celest)
        total_spy = ships["Result"]["EspionageProbe"]
        if (ogamu.checkSlots()[0] == True and total_spy >= settings.spy_for_farming):
            (gal, sys, pos) = ogamu.get_coords(var_defs.my_attack_session.my_celest)
            index = var_defs.my_attack_session.current_sys
            farm_plani = var_defs.farm_database.get_farm_plani_from_database(gal,sys,pos)
            print("farm plani länge: "+str(len(var_defs.farm_database.all_farm_planis)))
            print("spy reports lönge: "+str(len(farm_plani.spy_report_collection)))


            enemy_gal = farm_plani.spy_report_collection[index].gal
            enemy_sys = farm_plani.spy_report_collection[index].sys
            enemy_pos = farm_plani.spy_report_collection[index].pos
            print(enemy_gal,enemy_sys,enemy_pos)
            ogamu.spyEnemy(gal,sys,pos,var_defs.my_attack_session.my_celest)
            var_defs.my_attack_session.current_sys = var_defs.my_attack_session.current_sys + 1
            print("Spy from Database!")
            if(var_defs.my_attack_session.current_sys == var_defs.my_attack_session.last_sys):
                print("Spy Session ist vorbei!")
                time.sleep(60)
                check_all_spy_reports()

    else:
        ships = ogamu.get_all_ships(var_defs.my_attack_session.my_celest)
        total_spy = ships["Result"]["EspionageProbe"]
        if(ogamu.checkSlots()[0] == True and total_spy >= settings.spy_for_farming):
            print("Sys: "+str(var_defs.my_attack_session.current_sys) +
                  " , Pos: "+str(var_defs.my_attack_session.current_pos))
            data = ogamu.get_galaxy_info(var_defs.my_attack_session.gal, var_defs.my_attack_session.current_sys)
            enemy_planet = data["Result"]["Planets"][var_defs.my_attack_session.current_pos-1]
            if (not enemy_planet == None and enemy_planet["Inactive"] == True and enemy_planet["Vacation"] == False and
                enemy_planet["Banned"] == False and enemy_planet["Player"]["Rank"] < settings.min_rank and
                    enemy_planet["Player"]["Rank"] > settings.max_rank):
                print("FOUND ONE TARGET!")
                (gale, syse, pose) = ogamu.get_coords(enemy_planet)
                ogamu.spyEnemy(
                    gale,syse,pose, var_defs.my_attack_session.my_celest)
                spy_report = var_defs.SpyReports(0, gale, syse, pose)
                var_defs.all_spy_reports.append(spy_report)
            var_defs.my_attack_session.current_pos = var_defs.my_attack_session.current_pos + 1

            if(var_defs.my_attack_session.current_pos == 16):
                var_defs.my_attack_session.current_pos = 1
                var_defs.my_attack_session.current_sys = var_defs.my_attack_session.current_sys + 1
                if var_defs.my_attack_session.current_sys == 500:
                    var_defs.my_attack_session.current_sys = 1
                if var_defs.my_attack_session.current_sys == var_defs.my_attack_session.last_sys:
                    print("Spy Session ist vorbei!")
                    time.sleep(60)
                    check_all_spy_reports()
                    # Nach 30 Sekunden check alle SpyRepots
        else:
            print("Attack Session pausiert!: Nicht genug Slots oder Spiosonden")


def setup_atk_session(gals, syss, poss, radiuss, moon=False):
    #Init
    var_defs.all_spy_reports.clear()
    settings.farm_from_database = False
    gal = int(gals)
    sys = int(syss)
    pos = int(poss)
    radius = int(radiuss)
    my_celest = ogamu.get_celest_by_pos(gal, sys, pos, moon)
    var_defs.my_attack_session.my_celest = my_celest
    ships = ogamu.get_all_ships(my_celest)
    total_kt = ships["Result"]["SmallCargo"]
    total_spy = ships["Result"]["EspionageProbe"]
    if (total_kt < settings.check_kt):
        print("Zu wenig Kleine Transis!!")
        var_defs.my_attack_session.is_running  = False
        return
    if (total_spy < settings.check_spy):
        print("Zu wenig Spio Sonden!!")
        var_defs.my_attack_session.is_running  = False
        return
    var_defs.my_attack_session.gal = gal
    var_defs.my_attack_session.moon = moon
    #Farm from Database
    (gal, sys, pos) = ogamu.get_coords(var_defs.my_attack_session.my_celest)
    if (var_defs.farm_database.is_already_farming_planet(gal, sys, pos) and not settings.reset_farm_database):
        settings.farm_from_database = True
        var_defs.my_attack_session.current_sys = 0
        farm_plani = var_defs.farm_database.get_farm_plani_from_database(gal, sys, pos)
        var_defs.my_attack_session.last_sys = len( farm_plani.spy_report_collection)
        var_defs.all_spy_reports = farm_plani.spy_report_collection

        print("Atk From Database!")
    else:
        (min, max) = ogamu.calc_around_gal(sys, radius)
        var_defs.my_attack_session.current_sys = min
        var_defs.my_attack_session.last_sys = max
        print("Atk. Session gestartet von P: "+str(gal)+":"+str(sys)+":"+str(pos))
    var_defs.my_attack_session.is_running  = True


def gather_all_res(target_gal, target_sys, target_pos, moon=False):
    my_target_celest = ogamu.get_celest_by_pos(
        target_gal, target_sys, target_pos)
    target_id = ogamu.get_celest_ID(my_target_celest)
    if(ogamu.checkSlots()[0] == True):
        for planet in ogamu.get_planets():
            if(ogamu.checkSlots()[0] == True):
                    # Get Coords
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

