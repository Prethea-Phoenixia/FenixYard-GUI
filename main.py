import PySimpleGUI as sg
from math import pi, sqrt


class Material(object):
    def __init__(self):
        self.name = None
        self.density = None
        self.molar = None

    def print(self):
        for key in self.__dict__.keys():
            print(key, self.__dict__[key])


# class representing different propellant mixtures.
class Mixture(object):
    def __init__(self):
        self.name = None
        self.composition = None
        self.ve = None
        self.ratio = None
        self.dw = None
        self.density = None
        self.twr = None

    def print(self):
        for key in self.__dict__.keys():
            print(key, self.__dict__[key])


class Mod(object):
    def __init__(self):
        self.mass = None
        self.volume = None
        self.pos = None


class Engine(Mod):
    def __init__(self):
        self.thrust = None
        self.ve = None
        self.twr = None
        self.effects = None
        self.propellant = None
        self.grid = None
        super().__init__()


class Tank(Mod):
    def __init__(self):
        self.propellant = None
        self.pmass = None


class Ship(object):
    def __init(self):
        self.module = None


# return a list of the .name attribute of a list of instances, in order.
def index_name(stuffs):
    stuff_index = []
    for stuff in stuffs:
        stuff_index.append(stuff.name)
    return stuff_index


# try to return the parent_clas instance having the .name attr of input string.
# will attempt splicing if possible.
def bind_str_to_inst(input_string, parent_clas):
    string_list = input_string.split("|")
    p_index = index_name(parent_clas)
    return_list = []
    for string in string_list:
        s_pos = p_index.index(string)
        return_list.append(parent_clas(s_pos))
    return return_list


# reads txt file, creates and return list of objects of the given class
# with attributes set according to the csv header and value
# txt header must have same name as class attributes
# if value matches that of parent_clas, assign instance of parent_class instead
def readtxt(filename, clas, parent_clas=[]):
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
                            bind_str_to_inst(sanitize_str(values[i]), parent_clas),
                        )
                    i += 1
                stuffs.append(new_stuff)

        return stuffs


def mix_propellant(propellants, material_list, mat_index):
    for propellant in propellants:
        comp_list = propellant.composition.split("|")
        ratio_list = propellant.ratio.split("|")
        sum_mass = 0
        sum_vol = 0
        for i in range(0, len(comp_list)):
            prop_index = mat_index.index(comp_list[i])
            prop_mat = material_list[prop_index]
            sum_mass += prop_mat.molar * float(ratio_list[i])
            sum_vol += sum_mass / prop_mat.density

        propellant.density = sum_mass / sum_vol


#
def scale_engine(propellant, thrust):
    engine = Engine()
    engine.thrust = thrust
    engine.mass = thrust / (propellant.twr * 9.8)
    engine.propellant = propellant
    engine.ve = propellant.ve  # alias for engine.propellant.ve
    # liberal 5MW/m^2,assuming 99% efficient
    r = sqrt((thrust * engine.ve * 0.01) / 5e6 / (4 * pi))
    print(r)
    engine.volume = 4 / 3 * pi * r ** 3 * 3  # arbitary scaling factor of 3
    return engine


""" import instances of material classes, defined by material_file_name
    and indexing the materials. ( with name only )
"""
material_file_name = "Material.txt"
materials = readtxt(material_file_name, Material)

for material in materials:
    material.print()


""" import instances of propellant mixtures, defined by propellant_file_name
"""
mixture_file_name = "Propulsion.txt"
mixtures = readtxt(mixture_file_name, Mixture, materials)

for mix in mixtures:
    mix.print()
