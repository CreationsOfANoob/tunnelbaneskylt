import os
import time
import random
import argparse
import anledning
import text_till_typsnitt as ttt


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
    skylttext = ttt.SkyltStr(text)
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

    typsnitt = ttt.ASCIITypsnitt.new_from_file(args.t)
    förseningsanledning = anledning.slumpad_anledning("anledningsträd.json", args.i, censur=args.c)
    if args.m != "":
        förseningsanledning = args.m
    renderad_anledning = rendera_text(förseningsanledning, typsnitt)

    tid_uppdatera_destination = 0
    print('\033[?25l', end="") #Göm pekare

    pos = 0
    while True:
        try:
            time.sleep(1/args.f)
            os.system('clear')
            terminalbredd = os.get_terminal_size().columns

            if time.time() > tid_uppdatera_destination:
                destination = rendera_text(anledning.slumpad_anledning("stationer.json", censur=args.c), typsnitt)
                tid = rendera_text(anledning.slumpad_anledning("tider.json"), typsnitt)
                tid_textbredd = max([len(rad) for rad in tid.split("\n")])
                rad_uppe = ttt.ASCIITypsnitt.add_strings(rendera_utsnitt(destination, terminalbredd - tid_textbredd, terminalbredd - tid_textbredd), tid)
                pos = -1
                tid_uppdatera_destination = time.time() + random.randint(5, 90)

            if pos > max([len(rad) for rad in renderad_anledning.split("\n")]) + terminalbredd + 3:
                förseningsanledning = anledning.slumpad_anledning("anledningsträd.json", args.i, censur=args.c)
                renderad_anledning = rendera_text(förseningsanledning, typsnitt)
                pos = 0

            meddelande = rendera_utsnitt(renderad_anledning, pos, terminalbredd)
            print("\n" * 5 + f"{bcolors.EGEN}{rad_uppe + ("\n" * 2) + meddelande}{bcolors.ENDC}")
            if args.d:
                print(förseningsanledning)
                print(args)
            pos += args.s
        except KeyboardInterrupt:
            print()
            print()
            print(rendera_text("Avslutad", typsnitt))
            print()
            print()

            print('\033[?25h', end="")
            break
