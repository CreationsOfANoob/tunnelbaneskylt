import json


class ASCIITypsnitt:
    def __init__(self, letterdict):
        self.letterdict = letterdict

    def render_char(self, char = ""):
        if char not in self.letterdict or len(char) != 1:
            char = "saknad"
        try:
            char_rendered = self.letterdict[char]
        except KeyError:
            char_rendered = "?"

        return char_rendered

    @classmethod
    def pad_string(cls, rader, height, margin = 0):
        radlängd = max([len(rad) for rad in rader]) + margin
        nya_rader = [f"{x: <{radlängd}}" for x in rader]
        for i in range(max(height - len(rader), 0)):
            nya_rader.append(" " * radlängd)
        return nya_rader

    @classmethod
    def add_strings(cls, a, b, margin = 0):
        #Dela upp a, b i rader, sätt ihop rad för rad och kombinera till en sträng
        if b != "":
            if a != "":
                a_rader = a.split("\n")
                b_rader = b.split("\n")
                b_rader = ASCIITypsnitt.pad_string(b_rader, max(len(a_rader), len(b_rader)))
                a_rader = ASCIITypsnitt.pad_string(a_rader, max(len(a_rader), len(b_rader)), margin)
                c = "\n".join([x[0] + x[1] for x in zip(a_rader, b_rader)])
                return c
            return b
        return a

    @classmethod
    def new_from_file(cls, file_path):
        #{"characters":{"A":str, "a":str , "B":str, ... }}
        with open(file_path, "r") as file:
            json_dict = json.loads(file.read())
            #Byt ut punkter mot mellanslag, | mot radbrytningar
            json_dict["characters"] = {k:v.replace("|", "\n").replace(".", " ").replace("#", "●") for k, v in json_dict["characters"].items()}
            return ASCIITypsnitt(json_dict["characters"])


if __name__=="__main__":
    typsnitt = ASCIITypsnitt.new_from_file("typsnitt_a.json")

    a = typsnitt.render_char("A")
    print(a)
