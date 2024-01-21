import json

#

class ASCIITypsnitt:
    def __init__(self, letterdict, w, h):
        self.letterdict = letterdict
        self.w = w
        self.h = h

    def render_char(self, char="", space=0):
        if char not in self.letterdict or len(char) != 1:
            char = "saknad"
        char_rendered = self.letterdict[char]

        return ASCIITypsnitt.add_strings(char_rendered, ASCIITypsnitt.render_full_char(space, self.h, " "))

    @classmethod
    def pad_string(cls, rader, height):
        radlängd = max([len(rad) for rad in rader])
        nya_rader = [f"{x: <{radlängd}}" for x in rader]
        for i in range(max(height - len(rader), 0)):
            nya_rader.append(" " * radlängd)
        return nya_rader

    @classmethod
    def add_strings(cls, a, b):
        #Dela upp a, b i rader, sätt ihop rad för rad och kombinera till en sträng
        if b != "":
            if a != "":
                a_rader = a.split("\n")
                b_rader = b.split("\n")
                b_rader = ASCIITypsnitt.pad_string(b_rader, max(len(a_rader), len(b_rader)))
                a_rader = ASCIITypsnitt.pad_string(a_rader, max(len(a_rader), len(b_rader)))
                c = "\n".join([x[0] + x[1] for x in zip(a_rader, b_rader)])
                return c
            return b
        return a

    @classmethod
    def render_full_char(cls, w, h, char):
        return "\n" + (((char * w) + "\n") * h)

    @classmethod
    def new_from_file(cls, file_path):
        #{"w":int, "h":int, "characters":{"a":str, "b":str ... }}
        with open(file_path, "r") as file:
            json_dict = json.loads(file.read())
            #Byt ut punkter mot mellanslag, | mot radbrytningar
            json_dict["characters"] = {k:v.replace("|", "\n").replace(".", " ").replace("#", "*") for k, v in json_dict["characters"].items()}
            print(json_dict["characters"])
            new_typsnitt = ASCIITypsnitt(json_dict["characters"], json_dict["w"], json_dict["h"])
            return new_typsnitt


class SkyltStr:
    def __init__(self, text="", mellanrum=2):
        self.plain_text = text
        self.mellanrum = mellanrum

    def rendera_skylt(self, typsnitt):
        if self.plain_text != "":
            out = ""
            for char in self.plain_text:
                out = ASCIITypsnitt.add_strings(out, typsnitt.render_char(char, self.mellanrum))
            return out
        return ""


if __name__=="__main__":
    typsnitt = ASCIITypsnitt.new_from_file("typsnitt_a.json")

    a = SkyltStr("ABCDEFGHIJKLMNOPQRS")
    print(a.rendera_skylt(typsnitt))
