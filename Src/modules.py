from math import pi, sqrt
from numerical import brents
from pickle import dump, load


class Mod(object):
    def __init__(self):
        self.mass = None
        self.volume = None
        self.str = None

        # radius and height respectively.
        self.r = None
        self.h = None

        # position in ships.
        self.pos = None

        # name will be referred to.
        self.name = "NewModule"

    def save(self, filename):
        savefile = open(filename, "wb")
        dump(self, savefile)
        savefile.close()

    def load(filename):
        savefile = open(filename, "rb")
        myself = load(savefile)
        savefile.close
        return myself


class Tank(Mod):
    def __init__(self):
        super().__init__()
        self.content = None
        self.pmass = None

        # width, equal to h-2r
        self.w = None

        self.fillratio = None

        self.strmass = None

    def filltank(self, propellant, pmass, material):
        self.content = propellant
        self.pmass = pmass
        self.volume = pmass / propellant.lqdensity
        # mass of tank left for structural calculation in futures.
        self.str = material
        # name it!
        self.name = "{:.1f}t {} tank of {}".format(
            self.pmass / 1000, self.str.name, self.content.name
        )
        self.mass = self.pmass

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

        self.strmass = brents(f, 0, pmass)
        self.mass = self.strmass + self.pmass

    def percentage(self):
        self.fillratio = self.pmass / (self.volume * self.content.lqdensity)
        return self.fillratio

    def set(self, propellant, pmass, material, ldratio):
        """material, float, material,float"""
        self.filltank(propellant, pmass, material)
        self.resize(ldratio)


class Engine(Mod):
    def __init__(self):
        super().__init__()
        self.thrust = None
        self.ve = None
        self.twr = None
        self.effects = None
        self.propellant = None
        self.grid = None
        self.mdot = None

        self.ort = None

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
        self.mdot = self.thrust / self.ve

        if self.thrust > 9800:
            self.name = "{:.1f}tf {} thruster".format(
                self.thrust / 9800, self.propellant.name
            )
        else:
            self.name = "{:.1f}kgf {} RCS".format(
                self.thrust / 9.8, self.propellant.name
            )

    def set(self, propellant, thrust):
        """material,float"""
        self.scale_engine(propellant, thrust)


class Rcs(Engine):
    def __init__(self):
        super().__init__()
