import operator
import requests
import time
import schedule
from random import randrange, uniform
from threading import Timer
from . import var_defs
from . import settings
from . import ogamu

spySess = var_defs.AttackSession(0, 0, 0, False, None)


def startExpo():
    if settings.expo_an:
        for planet in ogamu.get_planets():
            if(ogamu.checkSlots()[0] == True and ogamu.checkSlots()[1] == True):
                ogamu.setExpo(planet)
        for moon in ogamu.get_moons():
            if(ogamu.checkSlots()[0] == True and ogamu.checkSlots()[1] == True):
                ogamu.setExpo(moon)


def saveAllFleet(attacked_planet):
    id_planet = ogamu.get_celest_ID(attacked_planet)
    (gal, sys, pos) = ogamu.get_coords(attacked_planet)
    (metal, crystal, deut) = ogamu.get_celest_ressis(attacked_planet)
    # Schiffe
    ships = ogamu.get_all_ships(attacked_planet)
    fleet = var_defs.Fleet(ships=ships)
    data = fleet.fill_fleet_data(
        gal, sys, 16, var_defs.Missions.Expedition.value, 1, metal, crystal, deut)
    data = fleet.send_fleet(id_planet, data)
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
                print(attack)
                if (attack["ID"] not in var_defs.already_spied_ids and arrival_time < 2345):
                    if(not ogamu.onlySpy(attack) or settings.test_on):
                        var_defs.already_spied_ids.append(attack["ID"])
                        ogamu.spyEnemy(attack["Origin"],
                                       attack["Destination"], 1)
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


def attack_inactives():
    global atkSess
    number_of_attacks = ogamu.get_allowed_slots()
    print(number_of_attacks)
    if(len(var_defs.all_spy_reports) < number_of_attacks):
        number_of_attacks = len(var_defs.all_spy_reports)
    ships = ogamu.get_all_ships(spySess.my_celest)
    total_kt = ships['Result']['SmallCargo']
    celest_id = ogamu.get_celest_ID(spySess.my_celest)
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
                spySess.is_running = False
                var_defs.all_spy_reports.clear()
                ogamu.delete_all_spy_reports()
                return
    var_defs.all_spy_reports.clear()
    spySess.is_running = False
    ogamu.delete_all_spy_reports()


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
        if(report == None):
            print("Fehler beim auslesen des Berichtes!")
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
    global spySess
    if spySess.is_running:
        ships = ogamu.get_all_ships(spySess.my_celest)
        total_spy = ships["Result"]["EspionageProbe"]
        if(ogamu.checkSlots()[0] == True and total_spy >= settings.spy_for_farming):
            print("Sys: "+str(spySess.current_sys) +
                  " , Pos: "+str(spySess.current_pos))
            data = ogamu.get_galaxy_info(spySess.gal, spySess.current_sys)
            enemy_planet = data["Result"]["Planets"][spySess.current_pos-1]
            if (not enemy_planet == None and enemy_planet["Inactive"] == True and enemy_planet["Vacation"] == False and
                enemy_planet["Banned"] == False and enemy_planet["Player"]["Rank"] < settings.min_rank and
                    enemy_planet["Player"]["Rank"] > settings.max_rank):
                print("FOUND ONE TARGET!")
                ogamu.spyEnemy(
                    enemy_planet, spySess.my_celest)
            spySess.current_pos = spySess.current_pos + 1

            if(spySess.current_pos == 16):
                spySess.current_pos = 1
                spySess.current_sys = spySess.current_sys + 1
                if spySess.current_sys == 500:
                    spySess.current_sys = 1
                if spySess.current_sys == spySess.last_sys:
                    spySess.is_running = False
                    print("Spy Session ist vorbei!")
                    time.sleep(60)
                    check_all_spy_reports()
                    # Nach 30 Sekunden check alle SpyRepots
        else:
            print("Attack Session pausiert!: Nicht genug Slots")


def setup_atk_session(gal, sys, pos, radius, moon=False):
    global spySess
    print(gal, sys, pos)
    my_celest = ogamu.get_celest_by_pos(gal, sys, pos, moon)
    spySess.my_celest = my_celest
    ships = ogamu.get_all_ships(spySess.my_celest)
    total_kt = ships["Result"]["SmallCargo"]
    total_spy = ships["Result"]["EspionageProbe"]
    if(total_kt < settings.check_kt):
        print("Zu wenig Kleine Transis!!")
        spySess.is_running = False
        return
    if(total_spy < settings.check_spy):
        print("Zu wenig Spio Sonden!!")
        spySess.is_running = False
        return
    (min, max) = ogamu.calc_around_gal(sys, radius)
    spySess.current_sys = min
    spySess.last_sys = max
    spySess.gal = gal
    spySess.mon = moon
    spySess.is_running = True
    print("Atk. Session gestartet von P: "+str(gal)+":"+str(sys)+":"+str(pos))


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


# settings.adress = "127.0.0.1:1337"
# counter = 0
# while True:
#     setup_atk_session(1, 159, 8, 15, False)
#     while spySess.is_running:
#         print(str(counter))
#         run_spy_session()
#         counter = counter + 1


# settings.adress = "127.0.0.1:8080"
# counter = 0
# while True:
#     print(str(counter))
#     startExpo()
#     autoSave()
#     counter = counter + 1
#     time.sleep(30)
