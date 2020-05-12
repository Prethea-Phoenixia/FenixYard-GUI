from math import pi, sqrt
from numerical import brents


class Mod(object):
    def __init__(self):
        self.mass = None
        self.volume = None
        self.str = None

        # radius and height respectively.
        self.r = None
        self.h = None


class Tank(Mod):
    def __init__(self):
        super().__init__()
        self.content = None
        self.pmass = None

        # width, equal to h-2r
        self.w = None

    def print(self):
        print("{} tank made of {}".format(self.content.name, self.str.name))
        print(
            "{:.2f} kg empty, currently {:.2f} kg".format(
                self.mass, self.pmass + self.mass
            )
        )
        print("diam of {:.2f} m, height of {:.2f} m".format(self.r * 2, self.h))

    def filltank(self, propellant, pmass, material):
        self.content = propellant
        self.pmass = pmass
        self.volume = pmass / propellant.lqdensity
        # mass of tank left for structural calculation in futures.
        self.str = material

    # bullet shaped tank.
    def resize(self, ldratio):
        v = self.volume
        self.r = (v / (pi * (2 * ldratio - 2 / 3))) ** (1 / 3)
        self.h = 2 * self.r * ldratio
        self.w = 2 * self.r * (ldratio - 1)

    # build up tank
    def buildup(self, acc):
        str_mtr = self.str
        r = self.r
        w = self.w
        pmass = self.pmass
        # iterative finding mass.
        propellant = self.content
        gas_p = propellant.vap_pres(propellant.stdBP)

        def f(mass):
            f = (pmass + mass) * acc
            p = f / (pi * r ** 2) + gas_p
            massTank = (
                2 * pi * r ** 2 * (r + w) * p * str_mtr.sdensity / str_mtr.yieldstrength
            )
            deltamass = massTank - mass
            return deltamass

        self.mass = brents(f, 0, pmass)

    def percentage(self):
        return self.pmass / (self.volume * self.content.lqdensity)


class Engine(Mod):
    def __init__(self):
        super().__init__()
        self.thrust = None
        self.ve = None
        self.twr = None
        self.effects = None
        self.propellant = None
        self.grid = None

    def scale_engine(self, propellant, thrust):
        engine = self
        engine.thrust = thrust
        engine.mass = thrust / (propellant.twr * 9.8)
        engine.propellant = propellant
        engine.ve = propellant.ve  # alias for engine.propellant.ve
        # liberal 5MW/m^2,assuming 99% efficient
        r = sqrt((thrust * engine.ve * 0.01) / 5e6 / (4 * pi))
        engine.volume = 4 / 3 * pi * r ** 3 * 3  # arbitary scaling factor of 3
        engine.r = r
        engine.h = engine.volume / (pi * r ** 2)

    def print(self):
        print(
            "{:.2f}kg thruster using {} producing {:.1f} kgf thrust".format(
                self.mass, self.propellant.name, self.thrust / 9.8
            )
        )

