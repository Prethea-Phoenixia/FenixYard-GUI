import PySimpleGUI as sg
import re


class Material(object):
    def __init__(self):
        self.name = None
        self.density = None


class Propellant(object):
    def __init__(self):
        self.name = None
        self.composition = None
        self.ratio = None
        self.ve = None
        self.dw = None
        self.density = None


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
        super().__init__()


# reads txt file, creates and return list of objects of the given class
# with attributes set according to the csv header and value
# txt header must have same name as class attributes
def readtxt(filename, clas):
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
                print(headers)
            else:
                new_stuff = clas()
                values = line_ls_str
                i = 0
                for attr in headers:
                    try:
                        setattr(new_stuff, attr, float(values[i]))
                    except ValueError:
                        setattr(new_stuff, attr, sanitize_str(values[i]))
                    i += 1
                stuffs.append(new_stuff)

        return stuffs


def index(stuffs):
    stuff_index = []
    for stuff in stuffs:
        stuff_index.append(stuff.name)
    return stuff_index


def mix_propellant(propellants, material_list, mat_index):
    for propellant in propellants:
        comp_list = propellant.composition.split("|")
        ratio_list = propellant.ratio.split("|")

        sum_den = 0
        for i in range(0, len(comp_list)):
            prop_index = mat_index.index(comp_list[i])
            prop_mat = material_list[prop_index]
            sum_den += prop_mat.density * float(ratio_list[i])

        propellant.density = sum_den


material_file_name = "Material.txt"
materials = readtxt(material_file_name, Material)
material_index = index(materials)
propellant_file_name = "Propellant.txt"
propellants = readtxt(propellant_file_name, Propellant)

mix_propellant(propellants, materials, material_index)

for mat in materials:
    print(mat.name, mat.density)

for prop in propellants:
    print(prop.name, prop.ve, prop.composition, prop.ratio, prop.density)
