import requests

sl_realtid_key = "ceb477e0ee44462ea61febb7c5733e49"
sl_platsuppslag_key = "2694e7e1419a4d21866cdf899005c9a9"

if __name__=="__main__":
    stationsnamn = input("Vilken station vill du kolla?\nStation: ")

    stationskoll = requests.get(f"https://journeyplanner.integration.sl.se/v1/typeahead.json?key={sl_platsuppslag_key}&searchstring={stationsnamn}&type=S")
    print(stationskoll.status_code)

    print(stationskoll.json()["ResponseData"][0]["Name"])
    stationsid = stationskoll.json()["ResponseData"][0]["SiteId"]

    svar = requests.get(f"https://api.sl.se/api2/realtimedeparturesV4.json?key={sl_realtid_key}&siteid={stationsid}&timewindow=20")
    print(svar.status_code)
    tunnelbana = svar.json()["ResponseData"]["Metros"]
    sparvagn = svar.json()["ResponseData"]["Trams"]
    bussar = svar.json()["ResponseData"]["Buses"]

    alla = tunnelbana + sparvagn + bussar
    alla_sorterad = sorted(alla, key=lambda x: str(x.get("ExpectedDateTime", 0)))
    for avgang in alla:
        linje = avgang["LineNumber"]
        destination = avgang["Destination"]
        tid_kvar = avgang["DisplayTime"]
        print(f"{linje}  {destination}  {tid_kvar}")
