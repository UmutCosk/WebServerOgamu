import requests
import json
import time
import schedule
from enum import Enum
from random import randrange, uniform
from threading import Timer

# ------------Settings------------ #
# ---General---#
slots_reserviert = 3
telegram = False
test_on = False

# ---Expeditions--- #
expo_an = True
kleine_transporter_exp = 0
große_transporter_exp = 200
spio_sonde_exp = 1
leichte_jaeger_exp = 0
schwere_jaeger_exp = 0
kreuzer_exp = 0
schlachtschiff_exp = 1
reaper_exp = 1
schlachtkreuzer_exp = 1
pathfinder_exp = 1

# ---Variables--- #
already_saved_ids = []
already_spied_ids = []
call_back_ids = []


class Ships(Enum):
    LightFighter = "204"
    HeavyFighter = "205"
    Cruiser = "206"
    Battleship = "207"
    Battlecruiser = "215"
    Bomber = "211"
    Destroyer = "213"
    Deathstar = "214"
    SmallCargo = "202"
    LargeCargo = "203"
    ColonyShip = "208"
    Recycler = "209"
    EspionageProbe = "210"
    SolarSatellite = "212"
    Crawler = "217"
    Reaper = "218"
    Pathfinder = "219"


def telegram_bot_sendtext(bot_message):
    bot_token = '1122280858:AAFzsZSzhNZKEl1LxUc-6BRqPJdMP202FI'
    bot_chat_id = '980798990'
    send_text = 'https://api.telegram.org/bot' + bot_token + \
        '/sendMessage?chat_id=' \
        + bot_chat_id \
        + '&parse_mode=Markdown&text=' \
        + bot_message
    response = requests.get(send_text)
    return response.json()


def isUnderAttack():
    r = requests.get(url="http://127.0.0.1:8080/bot/is-under-attack")
    data = r.json()
    if data["Result"] and telegram:
        telegram_bot_sendtext("Du wirst angegriffen!")
    return data["Result"]


def startExpo():
    if expo_an:
        r = requests.get(url="http://127.0.0.1:8080/bot/planets")
        planets = r.json()
        for planet in planets["Result"]:
            r = requests.get(url="http://127.0.0.1:8080/bot/fleets/slots")
            data = r.json()

            if(data["Result"]["InUse"] + slots_reserviert < data["Result"]["Total"]):
                if(data["Result"]["ExpInUse"] < data["Result"]["ExpTotal"]):
                    id_planet = planet["ID"]
                    gal = planet["Coordinate"]["Galaxy"]
                    sys = planet["Coordinate"]["System"]
                    r = requests.get(
                        url="http://127.0.0.1:8080/bot/planets/" +
                        str(id_planet) +
                        "/ships")
                    ships = r.json()
                    if(ships["Result"]["LargeCargo"] >= große_transporter_exp and
                            ships["Result"]["SmallCargo"] >= kleine_transporter_exp and
                            ships["Result"]["LightFighter"] >= leichte_jaeger_exp and
                            ships["Result"]["EspionageProbe"] >= spio_sonde_exp and
                            ships["Result"]["HeavyFighter"] >= schwere_jaeger_exp and
                            ships["Result"]["Cruiser"] >= kreuzer_exp and
                            ships["Result"]["Battleship"] >= schlachtschiff_exp and
                            ships["Result"]["Reaper"] >= reaper_exp and
                            ships["Result"]["Battlecruiser"] >= schlachtkreuzer_exp and
                            ships["Result"]["Pathfinder"] >= pathfinder_exp):
                        data = [
                            ("ships", str(Ships.LargeCargo.value) + ',' +
                             str(große_transporter_exp)),
                            ("ships", str(Ships.SmallCargo.value) + ',' +
                             str(kleine_transporter_exp)),
                            ("ships", str(Ships.Battlecruiser.value) + ',' +
                             str(schlachtkreuzer_exp)),
                            ("ships", str(Ships.Battleship.value) + ',' +
                             str(schlachtschiff_exp)),
                            ("ships", str(Ships.Reaper.value) + ',' +
                             str(reaper_exp)),
                            ("ships", str(Ships.Pathfinder.value) + ',' +
                             str(pathfinder_exp)),
                            ("ships", str(Ships.EspionageProbe.value) + ',' +
                             str(spio_sonde_exp)),
                            ("ships", str(Ships.HeavyFighter.value) + ',' +
                             str(schwere_jaeger_exp)),
                            ("ships", str(Ships.LightFighter.value) + ',' +
                             str(leichte_jaeger_exp)),
                            ("ships", str(Ships.Cruiser.value) + ',' +
                             str(kreuzer_exp)),
                            ("speed", str(10)),
                            ("galaxy", str(gal)),
                            ("system", str(sys)),
                            ("position", str(16)),
                            ("mission", str(15)),
                            ("metal", str(0)),
                            ("crystal", str(0)),
                            ("deuterium", str(0))
                        ]

                        r = requests.post(
                            url="http://127.0.0.1:8080/bot/planets/" +
                            str(id_planet) +
                            "/send-fleet", data=data)
                        data = r.json()
                        print("EXPO GESENDET!")
                        time.sleep(3)
        r = requests.get(url="http://127.0.0.1:8080/bot/moons")
        moons = r.json()
        for moon in moons["Result"]:
            r = requests.get(url="http://127.0.0.1:8080/bot/fleets/slots")
            data = r.json()

            if(data["Result"]["InUse"] + slots_reserviert < data["Result"]["Total"]):
                if(data["Result"]["ExpInUse"] < data["Result"]["ExpTotal"]):
                    id_moon = moon["ID"]
                    gal = moon["Coordinate"]["Galaxy"]
                    sys = moon["Coordinate"]["System"]
                    r = requests.get(
                        url="http://127.0.0.1:8080/bot/planets/" +
                        str(id_moon) +
                        "/ships")
                    ships = r.json()
                    if(ships["Result"]["LargeCargo"] >= große_transporter_exp and
                            ships["Result"]["SmallCargo"] >= kleine_transporter_exp and
                            ships["Result"]["LightFighter"] >= leichte_jaeger_exp and
                            ships["Result"]["EspionageProbe"] >= spio_sonde_exp and
                            ships["Result"]["HeavyFighter"] >= schwere_jaeger_exp and
                            ships["Result"]["Cruiser"] >= kreuzer_exp and
                            ships["Result"]["Battleship"] >= schlachtschiff_exp and
                            ships["Result"]["Reaper"] >= reaper_exp and
                            ships["Result"]["Battlecruiser"] >= schlachtkreuzer_exp and
                            ships["Result"]["Pathfinder"] >= pathfinder_exp):
                        data = [
                            ("ships", str(Ships.LargeCargo.value) + ',' +
                             str(große_transporter_exp)),
                            ("ships", str(Ships.SmallCargo.value) + ',' +
                             str(kleine_transporter_exp)),
                            ("ships", str(Ships.Battlecruiser.value) + ',' +
                             str(schlachtkreuzer_exp)),
                            ("ships", str(Ships.Battleship.value) + ',' +
                             str(schlachtschiff_exp)),
                            ("ships", str(Ships.Reaper.value) + ',' +
                             str(reaper_exp)),
                            ("ships", str(Ships.Pathfinder.value) + ',' +
                             str(pathfinder_exp)),
                            ("ships", str(Ships.EspionageProbe.value) + ',' +
                             str(spio_sonde_exp)),
                            ("ships", str(Ships.HeavyFighter.value) + ',' +
                             str(schwere_jaeger_exp)),
                            ("ships", str(Ships.LightFighter.value) + ',' +
                             str(leichte_jaeger_exp)),
                            ("ships", str(Ships.Cruiser.value) + ',' +
                             str(kreuzer_exp)),
                            ("speed", str(10)),
                            ("galaxy", str(gal)),
                            ("system", str(sys)),
                            ("position", str(16)),
                            ("mission", str(15)),
                            ("metal", str(0)),
                            ("crystal", str(0)),
                            ("deuterium", str(0))
                        ]

                        r = requests.post(
                            url="http://127.0.0.1:8080/bot/planets/" +
                            str(id_moon) +
                            "/send-fleet", data=data)
                        data = r.json()
                        print("EXPO GESENDET!")
                        time.sleep(3)


def getPlanetID(attacked_planet):
    celesttype = attacked_planet["Type"]
    gal = attacked_planet["Galaxy"]
    sys = attacked_planet["System"]
    pos = attacked_planet["Position"]
    r = requests.get(url="http://127.0.0.1:8080/bot/planets")
    planets = r.json()
    for planet in planets["Result"]:
        if(planet["Coordinate"]["Galaxy"] == gal and
                planet["Coordinate"]["System"] == sys and
                planet["Coordinate"]["Position"] == pos):
            if(str(celesttype) == str(3)):
                r = requests.get(
                    url="http://127.0.0.1:8080/bot/planets/"+str(gal)+"/"+str(sys)+"/"+str(pos))
                planet_moon = r.json()
                return planet_moon["Result"]["Moon"]["ID"]
            else:
                return planet["ID"]


def callBackFleet(call_back_ids):
    if len(call_back_ids) > 0:
        for id in call_back_ids:
            requests.post(
                url="http://127.0.0.1:8080/bot/fleets/" +
                str(id) +
                "/cancel")
            print("Fleet zurück gerufen nach SAFE!")
            time.sleep(3)


def saveAllFleet(attacked_planet):
    id_planet = getPlanetID(attacked_planet)
    r = requests.get(
        url="http://127.0.0.1:8080/bot/planets/"+str(id_planet)+"/resources")
    planet = r.json()

    # Ressis
    metal = planet["Result"]["Metal"]
    crystal = planet["Result"]["Crystal"]
    deut = planet["Result"]["Deuterium"]
    # Schiffe
    r = requests.get(
        url="http://127.0.0.1:8080/bot/planets/" +
        str(id_planet) +
        "/ships")
    ships = r.json()
    data = [
        ("ships", str(Ships.LargeCargo.value) + ',' +
         str(ships["Result"]["LargeCargo"])),
        ("ships", str(Ships.SmallCargo.value) + ',' +
         str(ships["Result"]["SmallCargo"])),
        ("ships", str(Ships.Battlecruiser.value) + ',' +
         str(ships["Result"]["Battlecruiser"])),
        ("ships", str(Ships.Battleship.value) + ',' +
         str(ships["Result"]["Battleship"])),
        ("ships", str(Ships.Reaper.value) + ',' +
         str(ships["Result"]["Reaper"])),
        ("ships", str(Ships.Pathfinder.value) + ',' +
         str(ships["Result"]["Pathfinder"])),
        ("ships", str(Ships.EspionageProbe.value) + ',' +
         str(ships["Result"]["EspionageProbe"])),
        ("ships", str(Ships.HeavyFighter.value) + ',' +
         str(ships["Result"]["HeavyFighter"])),
        ("ships", str(Ships.LightFighter.value) + ',' +
         str(ships["Result"]["LightFighter"])),
        ("ships", str(Ships.Cruiser.value) + ',' +
         str(ships["Result"]["Cruiser"])),
        ("ships", str(Ships.Recycler.value) + ',' +
         str(ships["Result"]["Recycler"])),
        ("ships", str(Ships.ColonyShip.value) + ',' +
         str(ships["Result"]["ColonyShip"])),
        ("ships", str(Ships.Destroyer.value) + ',' +
         str(ships["Result"]["Destroyer"])),
        ("ships", str(Ships.Deathstar.value) + ',' +
         str(ships["Result"]["Deathstar"])),
        ("ships", str(Ships.Bomber.value) + ',' +
         str(ships["Result"]["Bomber"])),
        ("speed", str(1)),
        ("galaxy", str(1)),
        ("system", str(461)),
        ("position", str(7)),
        ("mission", str(5)),
        ("metal", str(metal)),
        ("crystal", str(crystal)),
        ("deuterium", str(deut))
    ]

    r = requests.post(
        url="http://127.0.0.1:8080/bot/planets/" +
        str(id_planet) +
        "/send-fleet", data=data)
    data = r.json()
    if(not data["Status"] == 'error'):
        call_back_ids.append(data["Result"]["ID"])
        print("SEND FOR SAVE")
    else:
        print("YOU DON'T HAVE ANY SHIPS!")


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


def spyEnemy(enemy_planet, planet):
    id_planet = getPlanetID(planet)
    gal = enemy_planet["Galaxy"]
    sys = enemy_planet["System"]
    pos = enemy_planet["Position"]
    data = [
        ("ships", str(Ships.EspionageProbe.value) + ',' +
         str(1)),
        ("speed", str(10)),
        ("galaxy", str(gal)),
        ("system", str(sys)),
        ("position", str(pos)),
        ("mission", str(6)),
        ("metal", str(0)),
        ("crystal", str(0)),
        ("deuterium", str(0))
    ]

    r = requests.post(
        url="http://127.0.0.1:8080/bot/planets/" +
        str(id_planet) +
        "/send-fleet", data=data)
    data = r.json()
    print("ENEMY SPIED BACK")


def autoSave():
    r = requests.get(url="http://127.0.0.1:8080/bot/attacks")
    data = r.json()
    attacks = data["Result"]
    if attacks is not None:
        if(len(attacks) > 0):
            for attack in attacks:
                arrival_time = attack["ArriveIn"]
                print("arrival time: "+str(arrival_time))
                # Zurück spionieren bei unter 1234 Sekunden
                print(attack)
                if (attack["ID"] not in already_spied_ids and arrival_time < 2345):
                    if(not onlySpy(attack) or test_on):
                        already_spied_ids.append(attack["ID"])
                        spyEnemy(attack["Origin"], attack["Destination"])
                        isUnderAttack()
                        time.sleep(3)
                # Saven bei unter 123 Sekunden
                if(arrival_time < 160 and attack["ID"] not in already_saved_ids):
                    if(not onlySpy(attack) or test_on):
                        already_saved_ids.append(attack["ID"])
                        saveAllFleet(attack["Destination"])
                        isUnderAttack()
                        time.sleep(3)
        else:
            callBackFleet(call_back_ids)
            already_saved_ids.clear()
            already_spied_ids.clear()
            call_back_ids.clear()


counter = 1
while True:
    autoSave()
    startExpo()
    print("Durchgang Nr.: "+str(counter))
    counter = counter + 1
    if(counter == 9999999):
        counter = 0
    time.sleep(30)
