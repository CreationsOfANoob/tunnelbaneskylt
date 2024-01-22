import os
import argparse
import threading
import time
import skylt
import texttypsnitt
import sl_api


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    RED = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    YELLOW = '\033[93m'

class Natverksstatus:
    def __init__(self):
        self.status = ""
        self._lock = threading.Lock()

    def hamtar(self):
        with self._lock:
            self.status = "Hämtar avgångar..."

    def klar_hamtad(self):
        with self._lock:
            self.status = ""

_running = True

def script_running():
    return _running

def avsluta_script():
    global _running
    _running = False


def hamta_avgangar(station, skylt_lock, on_update, on_finish, skylt_nu, skylt_tid, skylt_kommande):
    while script_running():
        anrop = station.get_avgangar(5, args.o, call_on_update = on_update, call_on_finished = on_finish)
        avgangar = anrop[0]
        deviations = anrop[1]

        with skylt_lock:
            if avgangar == []:
                skylt_uppe_v.uppdatera_text("----")
                skylt_uppe_h.uppdatera_text("")
                skylt_nere.uppdatera_text("Hittar inga avgångar just nu")
            else:
                next = avgangar[0]
                skylt_uppe_v.uppdatera_text(f"{next.linje}  {next.destination}")
                skylt_uppe_h.uppdatera_text(next.ankomsttid)
                if len(avgangar) > 1:
                    skylt_nere.uppdatera_text("      ".join([avgang.to_str() for avgang in avgangar[1:args.a]]) + "   " + "    ".join([deviation.to_str() for deviation in deviations]))
                else:
                    skylt_nere.uppdatera_text("" + "    ".join([deviation.to_str() for deviation in deviations]))

if __name__=="__main__":
    #Kommandotolksargument
    parser = argparse.ArgumentParser(description="Hämtar och visar avgångar från kollektivtrafikstationer i Stockholm.")
    parser.add_argument("-f", help="Uppdateringsfrekvens för skärm", type=int, default=24)
    parser.add_argument("-s", help="Hastighet", type=int, default=2)
    parser.add_argument("-t", help="Filsökväg för typsnitt (json)", type=str, default="data/typsnitt_a.json")
    parser.add_argument("-d", help="Debug-läge", action="store_true")
    parser.add_argument("-n", help="Stationsnamn", type=str, default="Alvik (Stockholm)")
    parser.add_argument("-p", help="Stationsläge", type=int, default=0)
    parser.add_argument("-o", help="Ha med alla trafikslag", action="store_true")
    parser.add_argument("-a", help="Antal avgångar som visas", type=int, default=4)
    args = parser.parse_args()

    typsnitt = texttypsnitt.ASCIITypsnitt.new_from_file(args.t)
    skylt_uppe_v = skylt.SkyltText.new(typsnitt)
    skylt_uppe_h = skylt.SkyltText.new(typsnitt)
    skylt_nere = skylt.SkyltText.new(typsnitt, rullbar = True)
    plattformsskylt = skylt.Skylt.kombinera_vertikalt(skylt.Skylt.kombinera_horisontellt(skylt_uppe_v, skylt_uppe_h, 0), skylt_nere, 0, 2)

    stationsnamn = args.n
    station = sl_api.Station.new_from_name(stationsnamn, args.p, uppdateringsfrekvens = 15)

    natverksstatus = Natverksstatus()
    skylt_lock = threading.RLock()
    api_anrop_thread = threading.Thread(target = hamta_avgangar, args = (station, skylt_lock, natverksstatus.hamtar, natverksstatus.klar_hamtad, skylt_uppe_v, skylt_uppe_h, skylt_nere))
    api_anrop_thread.start()

    print('\033[?25l', end="") #Göm pekare
    os.system('clear')
    while True:
        try:
            time.sleep(1/args.f)
            terminalbredd = os.get_terminal_size().columns

            with skylt_lock:
                plattformsskylt.uppdatera_bredd(terminalbredd)
                print("\033[2J\033[5;0H" + f"{bcolors.YELLOW}{plattformsskylt.rendera()}{bcolors.ENDC}{station.namn}\n\nLäge {station.bevakad_hallplats()}\n\n\n{bcolors.OKCYAN}{natverksstatus.status}{bcolors.ENDC}")#{"\n\n".join(sl_api.get_log())}")
                skylt_nere.rulla(args.s)

        except KeyboardInterrupt:
            avsluta_script()
            print("\n\n Avslutad\n\n")
            print('\033[?25h', end="") #Visa pekare
            break
