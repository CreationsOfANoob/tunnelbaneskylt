import requests
import json
import time

api_keys = None


class Avgang:
    def __init__(self, destination, ankomsttid, linje, datetime):
        self.destination = destination
        self.ankomsttid = ankomsttid
        self.ankomsttid_datetime = datetime
        self.linje = linje

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
        return Avgang(destination, ankomsttid, linje, ankomsttid_datetime)

class Station:
    def __init__(self, id, uppdateringsfrekvens, tunnelbana, sparvagn, buss, pendeltag):
        self._id = id
        self._uppdateringsfrekvens = uppdateringsfrekvens
        self._avgangar = []
        self._tid_nasta_uppdatering = 0
        self

    def get_avgangar(self):
        self.uppdatera_avgangar()
        return self._avgangar

    def uppdatera_avgangar(self):
        if time.time() > self._tid_nasta_uppdatering:
            self._tid_nasta_uppdatering = time.time() + self._uppdateringsfrekvens
            avgangsdata = anropa_sl_realtidsinformation(self._id).get("ResponseData")
            if not avgangsdata is None:
                alla_avgangar = avgangsdata.get("Metros", [])
                filtrerade_avgangar = alla_avgangar
                self._avgangar = [Avgang.new_from_dict(avgang_data) for avgang_data in filtrerade_avgangar]

    @classmethod
    def new_from_name(cls, stationsnamn, uppdateringsfrekvens = 20, tunnelbana = True, sparvagn = False, buss = False, pendeltag = False):
        id = cls._hitta_stationsid(stationsnamn)
        return Station(id, uppdateringsfrekvens, tunnelbana, sparvagn, buss, pendeltag)

    @classmethod
    def _hitta_stationsid(cls, stationsnamn):
        station_dict = hitta_station(stationsnamn)
        if station_dict == None:
            raise ValueError(f'Stationen "{stationsnamn}" kunde inte hittas.')
        id = station_dict["ID"]
        return id


def dict_from_json_file(filnamn):
    with open(filnamn, "r") as file:
        json_contents = json.loads(file.read())
        return json_contents

def json_file_from_dict(dict, filnamn):
    with open(filnamn, "w") as file:
        file.write(json.dumps(dict, indent = 4))

def hitta_station(station_str):
    hittad_station = None
    sparade_stationer = dict_from_json_file("data/api/stationsid.json").get("stationer", {"stationer":[]})
    try:
        #Börja med att kolla om stationsnamnet matchar en sparad station
        hittad_station = sparade_stationer[station_str]
        return hittad_station
    except KeyError:
        #Sök efter sparade alias till stationer
        for namn, station in sparade_stationer.items():
            if station_str in station.get("alias", []):
                hittad_station = station
                return hittad_station
        #Annars, sök mot SL:s API Platsuppslag
        try:
            hittad_station = anropa_sl_platsuppslag(station_str)["ResponseData"][0]
            print(hittad_station)
            if not hittad_station is None:
                sparad_station = sparade_stationer.get(hittad_station["Name"])
                if sparad_station is None:
                    sparad_station = {"ID":hittad_station["SiteID"], "alias":[station_str]}
                else:
                    sparad_station["ID"] = hittad_station["SiteId"]
                    sparad_station["alias"].append(station_str)

                sparade_stationer[hittad_station["Name"]] = sparad_station
                json_file_from_dict(sparade_stationer, "data/api/stationsid.json")
        except KeyError:
            pass
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
        print("Filen data/api/nycklar.json saknas.\nDu måste skaffa API-nycklar från https://developer.trafiklab.se\noch skapa filen data/api/nycklar.json.\nSe mallfilen data/api/nycklar_mall.json.")
        return
    try:
        return nycklar_dict[nyckelnamn]
    except KeyError:
        print(f"Nyckel {nyckelnamn} saknas i data/api/nycklar.json")

def api_meddelande(request_object):
    print(f"API-anrop med statuskod {request_object.status_code}")

def anropa_sl_platsuppslag(stationsnamn):
    api_key = get_api_key("sl_platsuppslag")
    platsuppslag = requests.get(f"https://journeyplanner.integration.sl.se/v1/typeahead.json?key={api_key}&searchstring={stationsnamn}&type=S")
    api_meddelande(platsuppslag)
    return platsuppslag.json()

def anropa_sl_realtidsinformation(stationsid):
    api_key = get_api_key("sl_realtidsinformation")
    realtidsinformation = requests.get(f"https://api.sl.se/api2/realtimedeparturesV4.json?key={api_key}&siteid={stationsid}&timewindow=20")
    api_meddelande(realtidsinformation)
    return realtidsinformation.json()


if __name__=="__main__":
    print()
    stationsnamn = input("Vilken station vill du kolla?\nStation: ")
    station = Station.new_from_name(stationsnamn)
    avgangar = station.get_avgangar()
    print()
    for avgang in avgangar:
        print(avgang.to_str())
    #
    # stationskoll = requests.get(f"https://journeyplanner.integration.sl.se/v1/typeahead.json?key={sl_platsuppslag_key}&searchstring={stationsnamn}&type=S")
    # print(stationskoll.status_code)
    #
    # print(stationskoll.json()["ResponseData"][0]["Name"])
    # stationsid = stationskoll.json()["ResponseData"][0]["SiteId"]
    #
    # svar = requests.get(f"https://api.sl.se/api2/realtimedeparturesV4.json?key={sl_realtid_key}&siteid={stationsid}&timewindow=20")
    # print(svar.status_code)
    # tunnelbana = svar.json()["ResponseData"]["Metros"]
    # sparvagn = svar.json()["ResponseData"]["Trams"]
    # bussar = svar.json()["ResponseData"]["Buses"]
    #
    # alla = tunnelbana + sparvagn + bussar
    # alla_sorterad = sorted(alla, key=lambda x: str(x.get("ExpectedDateTime", 0)))
    # for avgang in alla:
    #     linje = avgang["LineNumber"]
    #     destination = avgang["Destination"]
    #     tid_kvar = avgang["DisplayTime"]
    #     print(f"{linje}  {destination}  {tid_kvar}")
