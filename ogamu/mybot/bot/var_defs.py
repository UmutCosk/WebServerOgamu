from enum import Enum
import json
import requests
from . import settings

# ---Variables--- #
already_saved_ids = []
already_spied_ids = []
call_back_ids = []
all_spy_reports = []
all_farm_planis = []
max_farm_nr = 0
cur_farm_nr = 0
already_attacking = False


class FarmDatabase:
    def __init__(self):
        self.all_farm_planis = []
    def add_farming_plani(self,farm_planet):
        self.all_farm_planis.append(farm_planet)
    def is_already_farming_planet(self,gal,sys,pos):
        for farm_plani in self.all_farm_planis:
            if(gal == farm_plani.gal and sys == farm_plani.sys and pos == farm_plani.pos):
                return True
        return False
    def get_farm_plani_from_database(self,gal,sys,pos):
        for farm_plani in self.all_farm_planis:
            if (gal == farm_plani.gal and sys == farm_plani.sys and pos == farm_plani.pos):
                return farm_plani



farm_database = FarmDatabase()



class FarmPlanets:
    def __init__(self,gal,sys,pos,rad,moon=False):
        self.gal = gal
        self.sys = sys
        self.pos = pos
        self.moon = moon
        self.use = False
        self.rad = rad
        self.spy_report_collection = []


farmPlani1 = FarmPlanets(1,1,1,1,False)
farmPlani2 = FarmPlanets(1,1,1,1,False)
farmPlani3 = FarmPlanets(1,1,1,1,False)

class AttackSession:
    def __init__(self, sys_min, sys_max, gal, moon, my_celest):
        self.gal = gal
        self.moon = moon
        self.my_celest = my_celest
        self.current_sys = sys_min
        self.last_sys = sys_max
        self.current_pos = 1
        self.is_running = False

my_attack_session = AttackSession(0,0,0,False,None)

class SpyReports:
    def __init__(self, res_ges, gal, sys, pos):
        self.res_ges = res_ges
        self.gal = gal
        self.sys = sys
        self.pos = pos


class Coords:
    def __init__(self, gal, sys, pos):
        self.gal = gal
        self.sys = sys
        self.pos = pos


class Missions(Enum):
    Attack = "1"
    GroupedAttack = "2"
    Transport = "3"
    Park = "4"
    ParkInThatAlly = "5"
    Spy = "6"
    Colonize = "7"
    RecycleDebrisField = "8"
    Destroy = "9"
    MissileAttack = "10"
    Expedition = "15"


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


class Fleet:
    def __init__(self, lj, sj, xer, ss, sxer, bomber, zerri, rip, kt, gt, kolo, recyc, spio, sats, crawler, reaper, path, ships=None):
        self.lj = lj
        self.sj = sj
        self.xer = xer
        self.ss = ss
        self.sxer = sxer
        self.bomber = bomber
        self.zerri = zerri
        self.rip = rip
        self.kt = kt
        self.gt = gt
        self.kolo = kolo
        self.recyc = recyc
        self.spio = spio
        self.sats = sats
        self.crawler = crawler
        self.reaper = reaper
        self.path = path
        print(ships)
        if(not ships == None):
            self.lj = ships["Result"]["LightFighter"]
            self.sj = ships["Result"]["HeavyFighter"]
            self.xer = ships["Result"]["Cruiser"]
            self.ss = ships["Result"]["Battleship"]
            self.sxer = ships["Result"]["Battlecruiser"]
            self.bomber = ships["Result"]["Bomber"]
            self.zerri = ships["Result"]["Destroyer"]
            self.rip = ships["Result"]["Deathstar"]
            self.kt = ships["Result"]["SmallCargo"]
            self.gt = ships["Result"]["LargeCargo"]
            self.kolo = ships["Result"]["ColonyShip"]
            self.recyc = ships["Result"]["Recycler"]
            self.spio = ships["Result"]["EspionageProbe"]
            print("SPIOOOO: "+str(self.spio))
            self.sats = ships["Result"]["SolarSatellite"]
            self.crawler = ships["Result"]["Crawler"]
            self.reaper = ships["Result"]["Reaper"]
            self.path = ships["Result"]["Pathfinder"]

    def fill_fleet_data(self, gal, sys, pos, mission, speed, met, kris, deut, moon=False):
        celest_type = str(1)
        if moon:
            celest_type = str(3)
        data = [
            ("ships", str(Ships.LightFighter.value) + ',' +
                str(self.lj)),
            ("ships", str(Ships.HeavyFighter.value) + ',' +
                str(self.sj)),
            ("ships", str(Ships.Cruiser.value) + ',' +
                str(self.xer)),
            ("ships", str(Ships.Battleship.value) + ',' +
                str(self.ss)),
            ("ships", str(Ships.Battlecruiser.value) + ',' +
                str(self.sxer)),
            ("ships", str(Ships.Bomber.value) + ',' +
                str(self.bomber)),
            ("ships", str(Ships.Destroyer.value) + ',' +
                str(self.zerri)),
            ("ships", str(Ships.Deathstar.value) + ',' +
                str(self.rip)),
            ("ships", str(Ships.LargeCargo.value) + ',' +
                str(self.gt)),
            ("ships", str(Ships.SmallCargo.value) + ',' +
                str(self.kt)),
            ("ships", str(Ships.ColonyShip.value) + ',' +
                str(self.kolo)),
            ("ships", str(Ships.Recycler.value) + ',' +
                str(self.recyc)),
            ("ships", str(Ships.EspionageProbe.value) + ',' +
                str(self.spio)),
            ("ships", str(Ships.Reaper.value) + ',' +
                str(self.reaper)),
            ("ships", str(Ships.Pathfinder.value) + ',' +
                str(self.path)),
            ("ships", str(Ships.SolarSatellite.value) + ',' +
                str(self.sats)),
            ("ships", str(Ships.Crawler.value) + ',' +
                str(self.crawler)),
            ("speed", str(speed)),
            ("galaxy", str(gal)),
            ("system", str(sys)),
            ("position", str(pos)),
            ("type", celest_type),
            ("mission", str(mission)),
            ("metal", str(met)),
            ("crystal", str(kris)),
            ("deuterium", str(deut))]
        return data

    def send_fleet(self, id_planet, data):
        r = requests.post(
            url="http://"+settings.adress+"/bot/planets/" +
            str(id_planet) +
            "/send-fleet", data=data)
        return r.json()
