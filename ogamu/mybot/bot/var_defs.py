from enum import Enum
import json
import requests
from . import settings
from . import views
from . import ogamu

# ---Variables--- #
already_saved_ids = []
already_spied_ids = []
call_back_ids = []
all_planets = []


class SpyReport:
    def __init__(self,gal,sys,pos):
        self.gal = gal
        self.sys = sys
        self.pos = pos
        self.res = 0
        self.allow_attack = False

class FarmPlanet:
    def __init__(self,id,name,gal,sys,pos,moon=False):
        self.id = id
        self.name = name
        self.gal = gal
        self.sys = sys
        self.pos = pos
        self.moon = moon
        self.spy_reports = []
        self.allowed_farming = False
        self.already_scanned = False
    # Scans
        self.current_scan_gal = 0
        self.current_scan_sys = 0
        self.current_scan_pos = 0
        self.max_scan_sys = 0
        self.min_sys = 0
    # Spies
        self.current_spy_index = 0
        self.last_spy_index = 0
    # Analyse
        self.current_analyse_index = 0
        self.last_analyse_index = 0
        self.good_spy_reports = []
    # Attack
        self.current_attack_index = 0
        self.last_attack_index = 0


    def init_scan_vars(self):
        (min, max) = ogamu.calc_around_gal(self.sys, settings.farming_radius)
        self.current_scan_gal = self.gal
        self.current_scan_sys = min
        self.min_sys = min
        self.max_scan_sys = max
        self.turn_on()

        print("Wurde initilaizisiert!")
    def add_good_spy_report(self,spy_report):
        self.good_spy_reports.append(spy_report)

    def get_spy_report_pos(self,index):
        gal = self.spy_reports[index].gal
        sys = self.spy_reports[index].sys
        pos = self.spy_reports[index].pos
        return (gal,sys,pos)
    def add_spy_report(self,gal,sys,pos):
        spy_report = SpyReport(gal,sys,pos)
        self.spy_reports.append(spy_report)
    def add_good_spy_report(self, gal, sys, pos,res_ges):
        spy_report = SpyReport(gal, sys, pos)
        spy_report.res = res_ges
        self.good_spy_reports.append(spy_report)
    def remove_spy_report(self,gal,sys,pos):
        for spy_report in self.spy_reports:
            if(spy_report.gal == gal and spy_report.sys == sys and spy_report.pos == pos):
                self.spy_reports.remove((spy_report))
    def turn_on(self):
        self.allowed_farming = True
    def turn_off(self):
        self.allowed_farming = False


class AllFarmPlanets:
    def __init__(self):
        self.planets =[]
        self.currentIndex = 0
    def get_current_farm_planet(self):
        return self.planets[self.currentIndex]
    def next_farm_planet(self):
        self.currentIndex = self.currentIndex + 1
        print("NEXT FARM PLANET!")
        if(self.currentIndex == len(self.planets)):
            self.currentIndex = 0
        if(not self.planets[self.currentIndex].allowed_farming):
            self.currentIndex = self.currentIndex + 1
    def already_exits(self,name):
        for planet in self.planets:
            if(name == planet.name):
                return True
        return False
    def get_planet_by_name(self,name):
        for planet in self.planets:
            if (name == planet.name):
                return planet

    def add_planet(self,id,name,gal,sys,pos,moon=False):
        farm_planet = FarmPlanet(id,name,gal,sys,pos,moon)
        self.planets.append(farm_planet)


    def skip_if_not_allowed(self,farm_planet):
        if(not farm_planet.allowed_farming):
            self.next_farm_planet()
            print("Skipping to next farm planet")
            return True
        return False
    def all_already_scanned(self):
        for farm_planet in self.planets:
            if(not farm_planet.already_scanned):
                return False
        return True








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

class FarmState(Enum):
    Scan = "scan"
    Spy = "spy"
    Attack = "attack"
    Idle = "idle"
    Analyse = "analyse"
    Init = "idle"


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
