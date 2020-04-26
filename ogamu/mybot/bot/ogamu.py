from . import var_defs
from . import settings
import requests
import json
import time


def log_in():
    r = requests.get(url="http://"+settings.adress+"/bot/login")
    data = r.json()
    print("Logged in...")


def log_out():
    r = requests.get(url="http://"+settings.adress+"/bot/logout")
    data = r.json()
    print("Logged out...")


def telegram_bot_sendtext(bot_message):
    # Semihs:
    # bot_token = '1122280858:AAFzsZSzhNZKEl1LxUc-6BRqPJdMP202FI'
    # bot_chat_id = '980798990'
    # Umuts:
    bot_token = '803752516:AAFuc80sQd3jsOtvBno-lt5HD9_ZcHFA36w'
    bot_chat_id = '1078730557'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' \
        + bot_chat_id \
        + '&parse_mode=Markdown&text=' \
        + bot_message
    response = requests.get(send_text)
    return response.json()


def isUnderAttack():
    r = requests.get(url="http://"+settings.adress+"/bot/is-under-attack")
    data = r.json()
    if data["Result"] and settings.telegram:
        telegram_bot_sendtext("Du wirst angegriffen!")
    return data["Result"]

def is_slots_ready_for_next_attack():
    r = requests.get(url="http://" + settings.adress + "/bot/fleets/slots")
    data = r.json()
    slots_that_should_be_free = int(settings.slots_reserviert) + int(settings.expo_reserviert)
    if(data["Result"]["InUse"] <= int(slots_that_should_be_free)):
        return True
    return False


def get_plani_by_name(name):
    for planet in var_defs.all_planets:
        if(planet["Name"] == name):
            return planet
    return None




def get_allowed_slots():
    r = requests.get(url="http://"+settings.adress+"/bot/fleets/slots")
    data = r.json()
    return data["Result"]["Total"] - data["Result"]["InUse"] - int(settings.slots_reserviert) - int(settings.expo_reserviert)



def checkSlots():
    result_fleet = False
    result_exp = False
    r = requests.get(url="http://"+settings.adress+"/bot/fleets/slots")
    data = r.json()
    if(data["Result"]["InUse"] + int(settings.slots_reserviert) + int(settings.expo_reserviert) - data["Result"]["ExpInUse"]  < data["Result"]["Total"]):
        result_fleet = True
    if(data["Result"]["ExpInUse"] < data["Result"]["ExpTotal"]):
        result_exp = True
    return (result_fleet, result_exp)


def get_planets():
    r = requests.get(url="http://"+settings.adress+"/bot/planets")
    planets = r.json()
    return planets["Result"]


def get_moons():
    r = requests.get(url="http://"+settings.adress+"/bot/moons")
    moons = r.json()
    return moons["Result"]



def get_coords(celest):
    gal = celest["Coordinate"]["Galaxy"]
    sys = celest["Coordinate"]["System"]
    pos = celest["Coordinate"]["Position"]
    return (gal, sys, pos)


def get_celest_ID(celestial):
    celest = None
    celesttype = celestial["Coordinate"]["Type"]
    (gal, sys, pos) = get_coords(celestial)
    if(str(celesttype) == str(3)):
        r = requests.get(
            url="http://"+settings.adress+"/bot/moons/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
    else:
        r = requests.get(
            url="http://"+settings.adress+"/bot/planets/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
    return celest["Result"]["ID"]

def get_celest_ID3(celestial):
    (gal, sys, pos) = get_coords(celestial)
    r = requests.get(
            url="http://"+settings.adress+"/bot/moons/"+str(gal)+"/"+str(sys)+"/"+str(pos))
    celest = r.json()
    return celest["Result"]["ID"]

def get_coords2(celest):
    gal = celest["Galaxy"]
    sys = celest["System"]
    pos = celest["Position"]
    return (gal, sys, pos)


def get_celest_ID2(celestial):
    celest = None
    celesttype = celestial["Type"]
    (gal, sys, pos) = get_coords2(celestial)
    if(str(celesttype) == str(3)):
        r = requests.get(
            url="http://"+settings.adress+"/bot/moons/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
    else:
        r = requests.get(
            url="http://"+settings.adress+"/bot/planets/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
    return celest["Result"]["ID"]




def get_celest_by_pos(gal, sys, pos, moon=False):
    if moon == False:
        r = requests.get(
            url="http://"+settings.adress+"/bot/planets/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
        return celest["Result"]
    else:
        r = requests.get(
            url="http://"+settings.adress+"/bot/moons/"+str(gal)+"/"+str(sys)+"/"+str(pos))
        celest = r.json()
        return celest["Result"]


def setExpo(celest):
    id_celest = celest["ID"]
    (gal, sys, pos) = get_coords(celest)
    r = requests.get(
        url="http://"+settings.adress+"/bot/planets/" +
        str(id_celest) +
        "/ships")
    ships = r.json()
    if(ships["Result"]["LargeCargo"] >= settings.große_transporter_exp and
            ships["Result"]["SmallCargo"] >= settings.kleine_transporter_exp and
            ships["Result"]["LightFighter"] >= settings.leichte_jaeger_exp and
            ships["Result"]["EspionageProbe"] >= settings.spio_sonde_exp and
            ships["Result"]["HeavyFighter"] >= settings.schwere_jaeger_exp and
            ships["Result"]["Cruiser"] >= settings.kreuzer_exp and
            ships["Result"]["Battleship"] >= settings.schlachtschiff_exp and
            ships["Result"]["Reaper"] >= settings.reaper_exp and
            ships["Result"]["Battlecruiser"] >= settings.schlachtkreuzer_exp and
            ships["Result"]["Pathfinder"] >= settings.pathfinder_exp):
        fleet = var_defs.Fleet(settings.leichte_jaeger_exp, settings.schwere_jaeger_exp, settings.kreuzer_exp,
                               settings.schlachtschiff_exp, settings.schlachtkreuzer_exp, 0, 0, 0,
                               settings.kleine_transporter_exp, settings.große_transporter_exp, 0, 0,
                               settings.spio_sonde_exp, 0, 0, settings.reaper_exp, settings.pathfinder_exp)
        data = fleet.fill_fleet_data(
            gal, sys, 16, var_defs.Missions.Expedition.value, 10, 0, 0, 0)
        r = requests.post(
            url="http://"+settings.adress+"/bot/planets/" +
            str(id_celest) +
            "/send-fleet", data=data)
        print("EXPO GESENDET!")
        time.sleep(3)


def delete_all_spy_reports():
    requests.post(url="http://"+settings.adress +
                  "/bot/delete-all-espionage-reports")


def callBackFleet(call_back_ids):
    if len(call_back_ids) > 0:
        for id in call_back_ids:
            requests.post(
                url="http://"+settings.adress+"/bot/fleets/" +
                str(id) +
                "/cancel")
            print("Fleet zurück gerufen nach SAFE!")


def onlySpy(attack):
    if(attack["Ships"]["LightFighter"] == 0 and
       attack["Ships"]["HeavyFighter"] == 0 and
       attack["Ships"]["Cruiser"] == 0 and
       attack["Ships"]["Battleship"] == 0 and
       attack["Ships"]["Battlecruiser"] == 0 and
       attack["Ships"]["Bomber"] == 0 and
       attack["Ships"]["Destroyer"] == 0 and
       attack["Ships"]["Deathstar"] == 0 and
       attack["Ships"]["SmallCargo"] == 0 and
       attack["Ships"]["LargeCargo"] == 0 and
       attack["Ships"]["ColonyShip"] == 0 and
       attack["Ships"]["Recycler"] == 0 and
       abs(attack["Ships"]["EspionageProbe"]) > 0 and
       attack["Ships"]["Reaper"] == 0 and
       attack["Ships"]["Pathfinder"] == 0):
        return True

    return False


def get_galaxy_info(gal, sys):
    r = requests.get(
        url="http://"+settings.adress+"/bot/galaxy-infos/"+str(gal)+"/"+str(sys))
    data = r.json()
    return data


def get_all_ships(celest):
    id_celest = celest["ID"]
    r = requests.get(
        url="http://"+settings.adress+"/bot/planets/" +
        str(id_celest) +
        "/ships")
    ships = r.json()
    return ships

def get_all_ships2(celest_id):
    id_celest = celest_id
    r = requests.get(
        url="http://"+settings.adress+"/bot/planets/" +
        str(id_celest) +
        "/ships")
    ships = r.json()
    return ships



def get_all_attacks():
    r = requests.get(url="http://"+settings.adress+"/bot/attacks")
    data = r.json()
    attacks = data["Result"]
    return attacks

# def get_id_by_coords(g):
#     for planet in get_planets():


def get_celest_ressis(celest):
    id_celest = get_celest_ID(celest)
    r = requests.get(
        url="http://"+settings.adress+"/bot/planets/"+str(id_celest)+"/resources")
    celest = r.json()
    met = celest["Result"]["Metal"]
    crys = celest["Result"]["Crystal"]
    deut = celest["Result"]["Deuterium"]
    return (met, crys, deut)

def get_celest_ressis2(celest):
    id_celest = get_celest_ID2(celest)
    r = requests.get(
        url="http://"+settings.adress+"/bot/planets/"+str(id_celest)+"/resources")
    celest = r.json()
    met = celest["Result"]["Metal"]
    crys = celest["Result"]["Crystal"]
    deut = celest["Result"]["Deuterium"]
    return (met, crys, deut)


def spyEnemy(gal,sys,pos, my_celest_id):
    fleet = var_defs.Fleet(0, 0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0, settings.spy_for_farming, 0, 0, 0, 0)
    data = fleet.fill_fleet_data(
        gal, sys, pos, var_defs.Missions.Spy.value, 10, 0, 0, 0)
    data = fleet.send_fleet(my_celest_id, data)
    print("Enemy spied!")

def spyEnemy2(enemy_planet, my_celest_id):

    (gal, sys, pos) = get_coords2(enemy_planet)
    fleet = var_defs.Fleet(0, 0, 0, 0, 0, 0, 0, 0, 0,
                           0, 0, 0,5,0,0,0,0)
    data = fleet.fill_fleet_data(
        gal, sys, pos, var_defs.Missions.Spy.value,9, 0, 0, 0)
    data = fleet.send_fleet(my_celest_id, data)
    print("Enemy spied!")

def calc_around_gal(sys, radius):
    min = sys-radius
    max = sys+radius
    min_temp = 0
    max_temp = 0
    if(max > 499):
        max_result = max - 499
    else:
        max_result = max
    if(min < 1):
        min_result = 499 + min
    else:
        min_result = min
    return (min_result, max_result)


def get_research():
    r = requests.get(
        url="http://"+settings.adress+"/bot/get-research")
    research = r.json()
    return research["Result"]


def calc_cargo_kapa(kt, gt):
    research = get_research()
    hyper = research["HyperspaceTechnology"]
    kapa_kt = 0.05*int(hyper)*5000 + 5000
    kapa_gt = 0.05*int(hyper)*25000+25000
    return (kapa_kt*kt, kapa_gt*gt, kapa_kt, kapa_gt)


def get_cargo_kapa():
    research = get_research()
    hyper = research["HyperspaceTechnology"]
    kapa_kt = 0.05*int(hyper)*5000 + 5000
    kapa_gt = 0.05*int(hyper)*25000+25000
    return (kapa_kt, kapa_gt)


def get_spy_report(gal, sys, pos):
    r = requests.get(
        url="http://"+settings.adress+"/bot/espionage-report/"+str(gal)+"/"+str(sys)+"/"+str(pos))
    return r.json()


