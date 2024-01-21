import texttypsnitt


class SkyltText:
    def __init__(self, typsnitt, text, mellanrum, bredd, rullbar):
        self._typsnitt = typsnitt
        self._plain_text = text
        self._mellanrum = mellanrum
        self._bredd = bredd
        self._rullbar = rullbar

        self._pekare = 0
        self._renderad_text = ""
        self._renderad_textbredd = 0
        self._renderad_text_uppdaterad = False

    def _rendera_text(self):
        if self._plain_text == "":
            self._renderad_text = ""
        else:
            out = ""
            for char in self._plain_text:
                out = texttypsnitt.ASCIITypsnitt.add_strings(out, self._typsnitt.render_char(char), self._mellanrum)
            self._renderad_text = out
        self._renderad_textbredd = len(self._renderad_text.split("\n")[0])
        self._renderad_text_uppdaterad = True

    def _uppdatera_renderad_text(self):
        if not self._renderad_text_uppdaterad:
            self._rendera_text()

    def uppdatera_text(self, text):
        if text != self._plain_text:
            self._plain_text = text
            self._renderad_text_uppdaterad = False
            self.rulla_till_kant()

    def uppdatera_bredd(self, ny_bredd = 0):
        self._bredd = ny_bredd

    def bredd(self):
        self._uppdatera_renderad_text()
        return self._renderad_textbredd

    def rulla(self, pixlar):
        if self._bredd > 0 and self._rullbar:
            if self._pekare + pixlar < 0:
                self._pekare = self._bredd + pixlar
            else:
                self._pekare += pixlar

    def rulla_till_kant(self):
        self._pekare = 0

    def har_rullat_klart(self):
        return self._pekare > self._bredd + self._renderad_textbredd and self._bredd != 0 or self._plain_text == ""

    def rendera(self):
        self._uppdatera_renderad_text()
        pekare = self._pekare
        if self._bredd == 0:
            utsnitt = self._renderad_textbredd
            pekare = utsnitt
        else:
            utsnitt = self._bredd

        rader = self._renderad_text.split("\n")
        rader_ut = []
        modulo_pos = pekare % (utsnitt + self._renderad_textbredd)
        for rad in rader:
            if self._rullbar:
                hel_rad = rad.rjust(utsnitt + self._renderad_textbredd) * 2
            else:
                hel_rad = rad.ljust(utsnitt + self._renderad_textbredd) * 2
            rader_ut.append(hel_rad[modulo_pos:modulo_pos+utsnitt])
        return "\n".join(rader_ut)

    @classmethod
    def new(cls, typsnitt, text = "", mellanrum = 2, bredd = 0, rullbar = False):
        return SkyltText(typsnitt, text, mellanrum, bredd, rullbar)


class _skylttyp:
    VERTIKAL = "vertikal"
    HORISONTELL = "horisontell"

class Skylt:
    def __init__(self, text_a, text_b, bredd, marginal, typ):
        self._text_a = text_a
        self._text_b = text_b
        self._bredd = bredd
        self._marginal = marginal
        self._typ = typ
        self.uppdatera_bredd(bredd)

    def rendera(self):
        text_ut = ""
        match self._typ:
            case _skylttyp.VERTIKAL:
                text_ut = self._text_a.rendera() + ("\n" * (self._marginal + 1)) + self._text_b.rendera()
            case _skylttyp.HORISONTELL:
                text_ut = texttypsnitt.ASCIITypsnitt.add_strings(self._text_a.rendera(), self._text_b.rendera(), margin = self._marginal)
        return text_ut

    def uppdatera_bredd(self, ny_bredd):
        self._bredd = ny_bredd
        match self._typ:
            case _skylttyp.VERTIKAL:
                self._text_a.uppdatera_bredd(ny_bredd)
                self._text_b.uppdatera_bredd(ny_bredd)
            case _skylttyp.HORISONTELL:
                self._text_a.uppdatera_bredd(ny_bredd - self._text_b.bredd() - self._marginal)
                self._text_b.uppdatera_bredd(self._text_b.bredd())

    def bredd(self):
        return self._bredd

    @classmethod
    def kombinera_horisontellt(cls, element_a, element_b, bredd, marginal = 2):
        return Skylt(element_a, element_b, bredd, marginal, _skylttyp.HORISONTELL)

    @classmethod
    def kombinera_vertikalt(cls, element_a, element_b, bredd, marginal = 2):
        return Skylt(element_a, element_b, bredd, marginal, _skylttyp.VERTIKAL)


if __name__=="__main__":
    t = texttypsnitt.ASCIITypsnitt.new_from_file("typsnitt_a.json")
    v = SkyltText.new(t, "Vänster")
    h = SkyltText.new(t, "Höger")
    n = SkyltText.new(t, "Nere")

    s = Skylt.kombinera_vertikalt(Skylt.kombinera_horisontellt(v, h, 60), n, 60)
    print(s.rendera())
