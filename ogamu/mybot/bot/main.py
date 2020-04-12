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


   # if (not enemy_planet == None and enemy_planet["Inactive"] == True and enemy_planet["Vacation"] == False and
   #              enemy_planet["Banned"] == False and enemy_planet["Player"]["Rank"] < settings.min_rank and
   #                  enemy_planet["Player"]["Rank"] > settings.max_rank):
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



def scan_modus():
    current_farm_plani = views.all_farm_planets.get_current_farm_planet()
    data = ogamu.get_galaxy_info(current_farm_plani.current_scan_gal, current_farm_plani.current_scan_sys)
    current_farm_plani.current_scan_sys = current_farm_plani.current_scan_sys + 1
    if(current_farm_plani.current_scan_sys == current_farm_plani.max_scan_sys):
        print("Scan done for: !"+str(current_farm_plani.name))
        current_farm_plani.already_scanned = True