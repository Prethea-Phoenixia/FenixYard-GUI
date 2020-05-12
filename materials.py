from math import log10

sap = 1e5

class Material(object):
    def __init__(self):
        self.name = None
        self.sdensity = None
        self.lqdensity = None
        self.molar = None

        self.yieldstrength = None

        self.al = None
        self.bl = None
        self.cl = None

        self.ag = None
        self.bg = None
        self.cg = None

        # standard Melting Point
        self.stdMP = None
        # standard Boiling Point
        self.stdBP = None

    # given tempreature solve for vapor pressure, pascal
    def _antoine_p__(self, t):
        if t > self.stdBP:
            # boiling:
            a, b, c = self.ag, self.bg, self.cg
        else:
            # melting or in solid state:
            a, b, c = self.al, self.bl, self.cl
        return 10 ** (a - b / (c + t)) * sap

    # given vapor pressure, calculate kelvin tempreature
    def __antoine_t__(self, p):
        def fa(a, b, c):
            return b / (a - log10(p / sap)) - c

        return min(fa(self.al, self.bl, self.cl), fa(self.ag, self.bg, self.cg))

    # returns adjusted boiling point
    def adjBP(self, p):
        return self.__antoine_t__(p)

    # wrapper to return actual vapor pressure.
    def vap_pres(self, t):
        return self._antoine_p__(t)

    def print(self):
        for key in self.__dict__.keys():
            print(key, self.__dict__[key])


# class representing different propellant mixtures.
class Mixture(object):
    cleanup_calls = ["avgrho"]

    def __init__(self):
        self.name = None
        self.composition = None
        self.ve = None
        self.ratio = None
        self.density = None
        self.twr = None

    def print(self):
        print("REACTION")
        dictattr = self.__dict__
        for key in dictattr.keys():
            value = dictattr[key]
            if isinstance(value, list):
                # also filters out printing mixing ratio.
                if isinstance(value[0], Material):
                    for material in value:
                        print(
                            "{} part".format(
                                self.ratio[self.composition.index(material)]
                            )
                        )
                        material.print()
            else:
                print(key, value)

    def avgrho(self):
        self.ratio = self.ratio.split("|")
        flt_ratio_ls = []
        for str_ratio in self.ratio:
            flt_ratio_ls.append(float(str_ratio))
        self.ratio = flt_ratio_ls
        sum_mass = 0
        sum_vol = 0
        for propellant in self.composition:
            sum_mass += propellant.molar * self.get_ratio(propellant)
            sum_vol += sum_mass / propellant.lqdensity

        self.density = sum_mass / sum_vol

    def get_ratio(self, prop):
        pos = self.composition.index(prop)
        return self.ratio[pos]

    # get prpellant corresponding to ratio given ratio.
    def lookup_ratio(self, ratio):
        pos = self.ratio.index(ratio)
        return self.composition[pos]

    def get_ratio_norm(self, prop):
        sum_r = 0
        for ratio in self.ratio:
            sum_r += ratio
        return self.get_ratio(prop) / sum_r

    # mass ratio.
    def mass_ratio_norm(self, prop):
        sum_m = 0
        for ratio in self.ratio:
            sum_m += ratio * self.lookup_ratio(ratio).molar
        return self.get_ratio(prop) * prop.molar / sum_m
