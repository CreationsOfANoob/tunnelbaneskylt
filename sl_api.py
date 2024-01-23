import requests
import json
import time

api_keys = None
_print_log = []

class Avgang:
    def __init__(self, destination, ankomsttid, linje, datetime, hallplats):
        self.destination = destination
        self.ankomsttid = ankomsttid
        self.ankomsttid_datetime = datetime
        self.linje = linje
        self.hallplats = hallplats

    def __lt__(self, other):
        if self.ankomsttid_datetime is None:
            return False
        elif other.ankomsttid_datetime is None:
            return True
        else:
            return self.ankomsttid_datetime < other.ankomsttid_datetime

    def to_str(self):
        return f"{self.linje}  {self.destination}  {self.ankomsttid}"

    @classmethod
    def new_from_dict(cls, dict):
        linje = dict.get("LineNumber", "??")
        destination = dict.get("Destination", "Okänd plats")
        ankomsttid = dict.get("DisplayTime", "-")
        ankomsttid_datetime = dict.get("ExpectedDateTime", None)
        hallplats = dict.get("StopPointNumber", "1")
        return Avgang(destination, ankomsttid, linje, ankomsttid_datetime, hallplats)


class Deviation:
    def __init__(self, meddelande, hallplats):
        self.meddelande = meddelande
        self.hallplats = hallplats

    def to_str(self):
        return self.meddelande

    @classmethod
    def new_from_dict(cls, dict):
        meddelande = dict["Deviation"]["Text"]
        hallplats = dict["StopInfo"]["StopAreaNumber"]
        return Deviation(meddelande, hallplats)


class Station:
    def __init__(self, namn, id, hallplats, uppdateringsfrekvens, tunnelbana, sparvagn, buss, pendeltag):
        self._id = id
        self._uppdateringsfrekvens = uppdateringsfrekvens
        self._avgangar = []
        self._deviations = []
        self._tid_nasta_uppdatering = 0
        self.namn = namn
        self._stop_points = []
        self._bevakad_hallplats_index = hallplats

    def get_avgangar(self, attempts = 1, osorterad = False, call_on_update = None, call_on_finished = None):
        attempt = 0
        while attempt < attempts and len(self._avgangar) == 0 or attempt == 0:
            self.uppdatera_avgangar(call_on_update, call_on_finished)
            attempt += 1
        avgangar = []
        deviations = []

        if osorterad:
            return (self._avgangar, self._deviations)
        for avgang in self._avgangar:
            if avgang.hallplats == self._stop_points[self._bevakad_hallplats_index]:
                avgangar.append(avgang)

        for deviation in self._deviations:
            if deviation.hallplats == self._stop_points[self._bevakad_hallplats_index]:
                deviations.append(deviation)

        return (avgangar, deviations)

    def byt_hallplats(self, ny_hallplats):
        self._bevakad_hallplats_index = ny_hallplats
        self._bevakad_hallplats_index %= len(self._stop_points)

    def bevakad_hallplats(self):
        if not self._stop_points == []:
            return self._stop_points[self._bevakad_hallplats_index]

    def hallplatser_str(self):
        str = ""
        for hallplats in self._stop_points:
            str += f"\n{hallplats}\n"
        return str

    def uppdatera_avgangar(self, call_on_update, call_on_finished):
        if time.time() > self._tid_nasta_uppdatering:
            if not call_on_update is None:
                call_on_update()

            self._tid_nasta_uppdatering = time.time() + self._uppdateringsfrekvens
            api_data = anropa_sl_realtidsinformation(self._id)
            avgangsdata = api_data.get("ResponseData")
            json_file_from_dict(api_data, "data/api/cache/senaste_api_anrop.json")

            if not avgangsdata is None:
                alla_avgangar = avgangsdata.get("Metros", []) + avgangsdata.get("Trains", []) + avgangsdata.get("Trams", []) + avgangsdata.get("Buses", [])
                self._avgangar = []
                self._stop_points = []
                self._deviations = []
                for avgang_data in alla_avgangar:
                    if avgang_data["StopPointNumber"] not in self._stop_points:
                        self._stop_points.append(avgang_data["StopPointNumber"])
                    self._avgangar.append(Avgang.new_from_dict(avgang_data))
                self._stop_points.sort() #<---- kan inte sortera None
                alla_meddelanden = avgangsdata.get("StopPointDeviations")
                for deviation in alla_meddelanden:
                    self._deviations.append(Deviation.new_from_dict(deviation))
            if not call_on_finished is None:
                call_on_finished()

    @classmethod
    def new_from_name(cls, stationsnamn, hallplats = 0, uppdateringsfrekvens = 20, tunnelbana = True, sparvagn = False, buss = False, pendeltag = False):
        id, namn = cls._hitta_stationsinfo(stationsnamn)
        return Station(namn, id, hallplats, uppdateringsfrekvens, tunnelbana, sparvagn, buss, pendeltag)

    @classmethod
    def _hitta_stationsinfo(cls, stationsnamn):
        station_dict = hitta_station(stationsnamn)
        if station_dict == None:
            raise ValueError(f'Stationen "{stationsnamn}" kunde inte hittas.')
        id = station_dict["ID"]
        namn = station_dict["namn"]
        return (id, namn)


def dict_from_json_file(filnamn):
    with open(filnamn, "r") as file:
        json_contents = json.loads(file.read())
        return json_contents

def json_file_from_dict(dict, filnamn):
    with open(filnamn, "w") as file:
        file.write(json.dumps(dict, indent = 4))

def hitta_station(station_str):
    hittad_station = None
    sparade_stationer = dict_from_json_file("data/api/cache/stationsid.json")
    try:
        #Börja med att kolla om stationsnamnet matchar en sparad station
        hittad_station = sparade_stationer[station_str]
        hittad_station["namn"] = station_str
        return hittad_station
    except KeyError:
        #Sök efter sparade alias till stationer
        for namn, station in sparade_stationer.items():
            if station_str in station.get("alias", []):
                hittad_station = station
                hittad_station["namn"] = namn
                return hittad_station
        #Annars, sök mot SL:s API Platsuppslag
        api_stationer = anropa_sl_platsuppslag(station_str).get("ResponseData")
        if not (api_stationer is None or api_stationer == []):
            best_result = api_stationer[0]
            sparad_station = sparade_stationer.get(best_result["Name"])
            if sparad_station is None:
                sparad_station = {"ID":best_result["SiteId"], "alias":[station_str]}
            else:
                sparad_station["ID"] = best_result["SiteId"]
                sparad_station["alias"].append(station_str)

            sparade_stationer[best_result["Name"]] = sparad_station
            hittad_station = sparad_station
            hittad_station["namn"] = best_result["Name"]
            json_file_from_dict(sparade_stationer, "data/api/cache/stationsid.json")
    return hittad_station


def change_global_api_key_dict(dict):
    global api_keys
    api_keys = dict

def get_api_key(nyckelnamn):
    if not api_keys is None:
        try:
            return api_keys[nyckelnamn]
        except KeyError:
            pass
    try:
        nycklar_dict = dict_from_json_file("data/api/nycklar.json")
    except FileNotFoundError:
        log_print("Filen data/api/nycklar.json saknas.\nDu måste skaffa API-nycklar från https://developer.trafiklab.se\noch skapa filen data/api/nycklar.json.\nSe mallfilen data/api/nycklar_mall.json.")
        return
    try:
        return nycklar_dict[nyckelnamn]
    except KeyError:
        log_print(f"Nyckel {nyckelnamn} saknas i data/api/nycklar.json")

def api_meddelande(request_object):
    log_print(f"API-anrop med statuskod {request_object.status_code}")

def anropa_sl_platsuppslag(stationsnamn):
    api_key = get_api_key("sl_platsuppslag")
    platsuppslag = requests.get(f"https://journeyplanner.integration.sl.se/v1/typeahead.json?key={api_key}&searchstring={stationsnamn}&type=S")
    api_meddelande(platsuppslag)
    return platsuppslag.json()

def anropa_sl_realtidsinformation(stationsid):
    api_key = get_api_key("sl_realtidsinformation")
    realtidsinformation = requests.get(f"https://api.sl.se/api2/realtimedeparturesV4.json?key={api_key}&siteid={stationsid}&timewindow=40")
    api_meddelande(realtidsinformation)
    return realtidsinformation.json()

def log_print(str = ""):
    global _print_log
    if __name__=="__main__":
        print(str)
    else:
        _print_log.append(str)

def get_log():
    return _print_log

if __name__=="__main__":
    log_print()
    stationsnamn = input("Vilken station vill du kolla?\nStation: ")
    station = Station.new_from_name(stationsnamn)
    api_data = station.get_avgangar(5)
    avgangar = api_data[0]
    deviations = api_data[1]
    log_print()
    log_print(station.namn)
    for avgang in avgangar:
        log_print(avgang.to_str())
    for deviation in deviations:
        log_print(deviation.to_str())
