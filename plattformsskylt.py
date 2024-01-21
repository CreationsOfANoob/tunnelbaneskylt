import os
import time
import argparse
import skylt
import texttypsnitt


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
    parser = argparse.ArgumentParser(description="Renderar en tunnelbaneskylt med dumma förseningsmeddelanden.")
    parser.add_argument("-f", help="Uppdateringsfrekvens för skärm", type=int, default=24)
    parser.add_argument("-s", help="Hastighet", type=int, default=2)
    parser.add_argument("-t", help="Filsökväg för typsnitt (json)", type=str, default="data/typsnitt_a.json")
    parser.add_argument("-d", help="Debug-läge", action="store_true")
    args = parser.parse_args()

    typsnitt = texttypsnitt.ASCIITypsnitt.new_from_file(args.t)
    skylt_uppe_v = skylt.SkyltText.new(typsnitt)
    skylt_uppe_h = skylt.SkyltText.new(typsnitt)
    skylt_nere = skylt.SkyltText.new(typsnitt, rullbar = True)
    plattformsskylt = skylt.Skylt.kombinera_vertikalt(skylt.Skylt.kombinera_horisontellt(skylt_uppe_v, skylt_uppe_h, 0), skylt_nere, 0, 2)

    print('\033[?25l', end="") #Göm pekare
    while True:
        try:
            time.sleep(1/args.f)
            os.system('clear')
            terminalbredd = os.get_terminal_size().columns
            plattformsskylt.uppdatera_bredd(terminalbredd)

            skylt_nere.rulla(1)
            print("\n" * 2 + f"{bcolors.EGEN}{plattformsskylt.rendera()}{bcolors.ENDC}")

        except KeyboardInterrupt:
            print("\n\n Avslutad")
            print('\033[?25h', end="") #Visa pekare
            break
