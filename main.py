from math import pi, sqrt, log10

# standard atmospheric pressure,1bar,1E5pa
sap = 1e5

# brents method for numerical solving.
def brents(f, x0, x1, max_iter=150, tolerance=1e-5):
    fx0 = f(x0)
    fx1 = f(x1)

    assert (fx0 * fx1) <= 0, "Root not bracketed"

    if abs(fx0) < abs(fx1):
        x0, x1 = x1, x0
        fx0, fx1 = fx1, fx0

    x2, fx2 = x0, fx0

    mflag = True
    steps_taken = 0

    while steps_taken < max_iter and abs(x1 - x0) > tolerance:
        fx0 = f(x0)
        fx1 = f(x1)
        fx2 = f(x2)

        if fx0 != fx2 and fx1 != fx2:
            L0 = (x0 * fx1 * fx2) / ((fx0 - fx1) * (fx0 - fx2))
            L1 = (x1 * fx0 * fx2) / ((fx1 - fx0) * (fx1 - fx2))
            L2 = (x2 * fx1 * fx0) / ((fx2 - fx0) * (fx2 - fx1))
            new = L0 + L1 + L2

        else:
            new = x1 - ((fx1 * (x1 - x0)) / (fx1 - fx0))

        if (
            (new < ((3 * x0 + x1) / 4) or new > x1)
            or (mflag == True and (abs(new - x1)) >= (abs(x1 - x2) / 2))
            or (mflag == False and (abs(new - x1)) >= (abs(x2 - d) / 2))
            or (mflag == True and (abs(x1 - x2)) < tolerance)
            or (mflag == False and (abs(x2 - d)) < tolerance)
        ):
            new = (x0 + x1) / 2
            mflag = True

        else:
            mflag = False

        fnew = f(new)
        d, x2 = x2, x1

        if (fx0 * fnew) < 0:
            x1 = new
        else:
            x0 = new

        if abs(fx0) < abs(fx1):
            x0, x1 = x1, x0

        steps_taken += 1

    return x1


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
                    i = 0
                    for material in value:
                        print("{} part".format(self.ratio[i]))
                        material.print()
                        i += 1
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
        i = 0
        for propellant in self.composition:
            sum_mass += propellant.molar * float(self.ratio[i])
            sum_vol += sum_mass / propellant.lqdensity
            i += 1

        self.density = sum_mass / sum_vol


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


class Ship(object):
    def __init__(self):
        self.module = []
        self.engines = []
        self.mass = 0
        # structural acceleration limit
        self.str_acc_lim = 0

    def addmod(self, module):
        self.module.append(module)
        if isinstance(module, Engine):
            self.engines.append(Engine)

    def addcluster(self, cluster_list):
        self.module.append(cluster_list)
        for module in cluster_list:
            if isinstance(module, Engine):
                self.engines.append(Engine)

    def tally(self):
        queue = []
        for module in self.module:
            if isinstance(module, list):
                queue.extend(module)
            else:
                queue.append(module)
        for module in queue:
            if module.mass is not None:
                self.mass += module.mass
            if isinstance(module, Tank):
                self.mass += module.pmass

    def buildup_tank(self):
        acc_lim = self.str_acc_lim
        for pos in self.module:
            if isinstance(pos, list):
                for mod in pos:
                    if isinstance(mod, Tank):
                        mod.buildup(acc_lim)
            else:
                if isinstance(pos, Tank):
                    pos.buildup(acc_lim)

    def print(self):
        print("ship diagram:")
        for pos in self.module:
            if not isinstance(pos, list):
                print("|  {:^6}  |".format(pos.__class__.__name__), end="")
                print("")
        print("mass:{:.2f} kg".format(self.mass))


# return a list of the .name attribute of a list of instances, in order.
def index_name(stuffs):
    stuff_index = []
    for stuff in stuffs:
        stuff_index.append(stuff.name)
    return stuff_index


# try to return the parent_clas instance having the .name attr of input string.
# will attempt splicing if possible.
def bind_str_to_inst(input_string, parent_ls):
    # bypass string when no parent_clas given
    if parent_ls == []:
        return input_string

    string_list = input_string.split("|")
    parent_index = index_name(parent_ls)
    return_list = []
    for string in string_list:
        if string not in parent_index:
            # falls back to string mode
            return input_string
        s_pos = parent_index.index(string)
        return_list.append(parent_ls[s_pos])
    return return_list


def return_instance_from_list(input_string, list_of_stuff):
    index_of_stuff = index_name(list_of_stuff)
    place = index_of_stuff.index(input_string)
    return list_of_stuff[place]


# reads txt file, creates and return list of objects of the given class
# with attributes set according to the csv header and value
# txt header must have same name as class attributes
# if value matches that of parent_insance, return that instead.
# call additional calls at the end. string list.
def readtxt(filename, clas, parent_ls=[], additional_calls=None):
    def sanitize_str(myString):
        removal_list = ["\t", "\n"]
        for s in removal_list:
            myString = myString.replace(s, "")
        return myString

    with open(filename) as f:
        is_first_row = True
        headers = []
        stuffs = []
        for line in f:
            line_ls_str = line.split(",")
            if is_first_row:
                for head in line_ls_str:
                    headers.append(sanitize_str(head))
                is_first_row = False
            else:
                new_stuff = clas()
                values = line_ls_str
                i = 0
                for attr in headers:
                    try:
                        setattr(new_stuff, attr, float(values[i]))
                    except ValueError:
                        setattr(
                            new_stuff,
                            attr,
                            bind_str_to_inst(sanitize_str(values[i]), parent_ls),
                        )
                    i += 1
                stuffs.append(new_stuff)

        for stuff in stuffs:
            if additional_calls is not None:
                for call in additional_calls:
                    getattr(stuff, call)()
        return stuffs


# import instances of material classes, defined by material_file_name
# and indexing the materials. ( with name only )

material_file_name = "Material.txt"
materials = readtxt(material_file_name, Material)

# import instances of propellant mixtures, defined by propellant_file_name

mixture_file_name = "Propulsion.txt"
mixtures = readtxt(mixture_file_name, Mixture, materials, Mixture.cleanup_calls)


hydrogen = return_instance_from_list("Hydrogen", materials)
oxygen = return_instance_from_list("Oxygen", materials)
aluminum = return_instance_from_list("Aluminum", materials)

hydtank = Tank()
hydtank.filltank(hydrogen, 2500, aluminum)
hydtank.resize(2)

oxytank = Tank()
oxytank.filltank(oxygen, 10000, aluminum)
oxytank.resize(2)

testship = Ship()
testship.str_acc_lim = 10
testship.addmod(oxytank)
testship.addmod(hydtank)
testship.buildup_tank()
testship.tally()


testship.print()
