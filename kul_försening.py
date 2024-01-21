import os
import time
import random
import argparse
import skylt
import anledning
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


def rendera_text(text, typsnitt):
    skylttext = texttypsnitt.Skylt(text)
    return skylttext.rendera_skylt(typsnitt)

def rendera_utsnitt(text_in, position = 0, längd = 10):
    rader = text_in.split("\n")
    rader_utsnitt = []
    for rad in rader:
        förlängd_text = ((" " * (längd + 1)) + rad) * 2
        modulo_pos = position % len(förlängd_text)
        rader_utsnitt.append(förlängd_text[modulo_pos:modulo_pos+längd])
    return "\n".join(rader_utsnitt)


if __name__=="__main__":

    #Kommandotolksargument
    parser = argparse.ArgumentParser(description="Renderar en tunnelbaneskylt med dumma förseningsmeddelanden.")
    parser.add_argument("-f", help="Uppdateringsfrekvens", type=int, default=24)
    parser.add_argument("-s", help="Hastighet", type=int, default=2)
    parser.add_argument("-t", help="Filsökväg för typsnitt (json)", type=str, default="typsnitt_a.json")
    parser.add_argument("-d", help="Debug-läge", action="store_true")
    parser.add_argument("-i", help="Ignorera viktade svar", action="store_true")
    parser.add_argument("-c", help="Censurera grövre skämt", action="store_true")
    parser.add_argument("-m", help="Eget meddelande", type=str, default="")
    args = parser.parse_args()

    typsnitt = texttypsnitt.ASCIITypsnitt.new_from_file(args.t)
    skylt_uppe_v = skylt.SkyltText.new(typsnitt, text = "Hej")
    skylt_uppe_h = skylt.SkyltText.new(typsnitt)
    skylt_nere = skylt.SkyltText.new(typsnitt, rullbar = True)
    plattformsskylt = skylt.Skylt.kombinera_vertikalt(skylt.Skylt.kombinera_horisontellt(skylt_uppe_v, skylt_uppe_h, 0), skylt_nere, 0, 2)

    tid_uppdatera_destination = 0

    print('\033[?25l', end="") #Göm pekare

    while True:
        try:
            time.sleep(1/args.f)
            os.system('clear')
            terminalbredd = os.get_terminal_size().columns
            plattformsskylt.uppdatera_bredd(terminalbredd)

            if time.time() > tid_uppdatera_destination:
                tid_uppdatera_destination = time.time() + random.randint(5, 60)
                destination = anledning.slumpad_anledning("stationer.json")
                ankomsttid = anledning.slumpad_anledning("tider.json", ignorera_vikter = args.i)
                skylt_uppe_v.uppdatera_text(destination)
                skylt_uppe_h.uppdatera_text(ankomsttid)

            if skylt_nere.har_rullat_klart():
                if args.m == "":
                    anledningstext = anledning.slumpad_anledning("anledningsträd.json", ignorera_vikter = args.i)
                    skylt_nere.uppdatera_text(anledningstext)
                else:
                    skylt_nere.uppdatera_text(args.m)
                skylt_nere.rulla_till_kant()

            skylt_nere.rulla(1)
            print("\n" * 2 + f"{bcolors.EGEN}{plattformsskylt.rendera()}{bcolors.ENDC}")

        except KeyboardInterrupt:
            print("\n\n Avslutad")
            print('\033[?25h', end="") #Visa pekare
            break
