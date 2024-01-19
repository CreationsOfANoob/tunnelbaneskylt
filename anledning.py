import random
import json


def parse_anledning(anledning_dict):
    match anledning_dict:
        case list():
            possible = [val for val in anledning_dict]
            vikter = []
            for val in anledning_dict:
                match val:
                    case dict():
                        vikter.append(val.get("vikt", 1))
                    case _:
                        vikter.append(1)
            valt = random.choices(possible, weights=vikter)[0]
            deltext = parse_anledning(valt)
        case str():
            deltext = anledning_dict
        case dict():
            deltext = ""
            if "text" in anledning_dict:
                deltext += anledning_dict["text"]
            if "alternativ" in anledning_dict:
                deltext += random.choice(anledning_dict["alternativ"])
            if "val" in anledning_dict:
                deltext += parse_anledning(anledning_dict["val"])
    return deltext


def slumpad_anledning(filnamn):
    with open(filnamn, "r") as f:
        json_contents = json.loads(f.read())
        anledningstext = ""
        anledningstext += parse_anledning(json_contents)
        return anledningstext


if __name__=="__main__":
    print()
    for i in range(10):
        print(slumpad_anledning("anledningsträd.json"))
    print()
