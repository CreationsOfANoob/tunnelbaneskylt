import os
import argparse
import time
import skylt
import texttypsnitt
import sl_api


class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    EGEN = '\033[93m'


if __name__=="__main__":
    #Kommandotolksargument
    parser = argparse.ArgumentParser(description="Hämtar och visar avgångar från kollektivtrafikstationer i Stockholm.")
    parser.add_argument("-f", help="Uppdateringsfrekvens för skärm", type=int, default=24)
    parser.add_argument("-s", help="Hastighet", type=int, default=2)
    parser.add_argument("-t", help="Filsökväg för typsnitt (json)", type=str, default="data/typsnitt_a.json")
    parser.add_argument("-d", help="Debug-läge", action="store_true")
    parser.add_argument("-n", help="Stationsnamn", type=str, default="Alvik (Stockholm)")
    parser.add_argument("-p", help="Stationsläge", type=int, default=0)
    args = parser.parse_args()

    typsnitt = texttypsnitt.ASCIITypsnitt.new_from_file(args.t)
    skylt_uppe_v = skylt.SkyltText.new(typsnitt)
    skylt_uppe_h = skylt.SkyltText.new(typsnitt)
    skylt_nere = skylt.SkyltText.new(typsnitt, rullbar = True)
    plattformsskylt = skylt.Skylt.kombinera_vertikalt(skylt.Skylt.kombinera_horisontellt(skylt_uppe_v, skylt_uppe_h, 0), skylt_nere, 0, 2)

    stationsnamn = args.n
    station = sl_api.Station.new_from_name(stationsnamn, args.p)

    print('\033[?25l', end="") #Göm pekare
    while True:
        try:
            time.sleep(1/args.f)


            avgangar = station.get_avgangar(5)

            if avgangar == []:
                skylt_uppe_v.uppdatera_text("----")
                skylt_uppe_h.uppdatera_text("")
                skylt_nere.uppdatera_text("Hittar inga avgångar just nu")
            else:
                next = avgangar[0]
                skylt_uppe_v.uppdatera_text(f"{next.linje}  {next.destination}")
                skylt_uppe_h.uppdatera_text(next.ankomsttid)
                if len(avgangar) > 1:
                    skylt_nere.uppdatera_text("      ".join([avgang.to_str() for avgang in avgangar[1:3]]))
                else:
                    skylt_nere.uppdatera_text("")

            skylt_nere.rulla(args.s)

            os.system('clear')
            terminalbredd = os.get_terminal_size().columns
            plattformsskylt.uppdatera_bredd(terminalbredd)
            print("\n" * 2 + f"{bcolors.EGEN}{plattformsskylt.rendera()}{bcolors.ENDC}{station.namn}\n\nLäge {station.bevakad_hallplats()}\n\n{station.hallplatser_str()}")

        except KeyboardInterrupt:
            print("\n\n Avslutad\n\n")
            print('\033[?25h', end="") #Visa pekare
            break
