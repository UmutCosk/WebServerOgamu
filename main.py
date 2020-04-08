import requests
import time
import schedule
from random import randrange, uniform
from threading import Timer
import var_defs
import settings
import ogamu

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
        call_back_ids.append(data["Result"]["ID"])
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
                        settings.already_spied_ids.append(attack["ID"])
                        ogamu.spyEnemy(attack["Origin"],
                                       attack["Destination"], 1)
                        ogamu.isUnderAttack()
                        time.sleep(3)
                # Saven bei unter 123 Sekunden
                if(arrival_time < 600 and attack["ID"] not in already_saved_ids):
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


def search_attack(gal, enemy_sys, my_celest):
    data = ogamu.get_galaxy_info(gal, enemy_sys)
    if(ogamu.checkSlots()[0] == True):
        for i in range(0, 15):
            if(ogamu.checkSlots()[0] == True):
                enemy_planet = data["Result"]["Planets"][i]
                if not enemy_planet == None:
                    if(enemy_planet["Inactive"] == True):
                        if(enemy_planet["Vacation"] == False):
                            if(enemy_planet["Administrator"] == False):
                                if(enemy_planet["Banned"] == False):
                                    if(enemy_planet["Player"]["Rank"] < settings.min_rank
                                       and enemy_planet["Player"]["Rank"] > settings.max_rank):
                                        pos = i+1
                                        print("FOUND ONE TARGET!")
                                        ogamu.spyEnemy(enemy_planet, my_celest)


def check_all_spy_reports():
    ogamu.log_out()
    ogamu.log_in()
    for i in range(len(var_defs.all_spy_reports)):
        gal = var_defs.all_spy_reports[i].gal
        sys = var_defs.all_spy_reports[i].sys
        pos = var_defs.all_spy_reports[i].pos
        report = ogamu.get_spy_report(gal, sys, pos)
        var_defs.all_spy_reports[i].res_ges = int(report["Result"]["Metal"])+int(
            report["Result"]["Crystal"])+int(report["Result"]["Deuterium"])
        print(var_defs.all_spy_reports[i].res_ges)


def run_spy_session():
    global spySess
    if spySess.is_running:
        if(ogamu.checkSlots()[0] == True):
            print("Sys: "+str(spySess.current_sys) +
                  " , Pos: "+str(spySess.current_pos))
            data = ogamu.get_galaxy_info(spySess.gal, spySess.current_sys)
            enemy_planet = data["Result"]["Planets"][spySess.current_pos-1]
            if not enemy_planet == None:
                if(enemy_planet["Inactive"] == True):
                    if(enemy_planet["Vacation"] == False):
                        if(enemy_planet["Administrator"] == False):
                            if(enemy_planet["Banned"] == False):
                                if(enemy_planet["Player"]["Rank"] < settings.min_rank
                                        and enemy_planet["Player"]["Rank"] > settings.max_rank):
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
                    time.sleep(30)
                    check_all_spy_reports()
                    # Nach 30 Sekunden check alle SpyRepots


def setup_atk_session(gal, sys, pos, radius, moon=False):
    global spySess
    my_celest = ogamu.get_celest_by_pos(gal, sys, pos, moon)
    (min, max) = ogamu.calc_around_gal(sys, radius)
    spySess.current_sys = min
    spySess.last_sys = max
    spySess.gal = gal
    spySess.mon = moon
    spySess.my_celest = my_celest

    # for sys_enemy in range(min, max):
    #     search_attack(gal, sys_enemy, my_celest)
    # return 0


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


# gather_all_res(1, 460, 7, True)
# gather_all_res(1, 460, 7, moon=True)
# ogamu.log_out()
# ogamu.log_in()
# gal = 1
# sys = 457
# pos = 5
# r = requests.get(
#     url="http://127.0.0.1:8080/bot/espionage-report/"+str(gal)+"/"+str(sys)+"/"+str(pos))
# data = r.json()
# print(data)

# setup_atk_session(1, 460, 7, 10, True)
counter = 0
while(True):
    print("Nr: "+str(counter))
    autoSave()
    startExpo()
    startExpo()
    startExpo()
    counter = counter + 1
    time.sleep(240)

# print(ogamu.calc_around_gal(460, 42))
