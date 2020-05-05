import PySimpleGUI as sg

import csv


class Material(object):
    def __init__(self):
        self.name = None
        self.density = None


class Propellant(object):
    def __init__(self, name, composition, mixing_ratio):
        self.name = name
        self.composition = composition
        self.mixing_ratio = mixing_ratio


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


# reads csv file, creates and return list of objects of the given class
# with attributes set according to the csv header and value
# csv header must have same name as class attributes
def readcsv(csvfilename, clas):
    with open(csvfilename, newline="") as csvfile:
        reader = csv.reader(csvfile, dialect="excel")
        is_first_row = True
        headers = []
        stuffs = []
        for row in reader:
            row_ls_str = row[0].split("\t")
            if is_first_row:
                headers = row_ls_str
                is_first_row = False
            else:
                new_stuff = clas()
                values = row_ls_str
                i = 0
                for attr in headers:
                    setattr(new_stuff, attr, values[i])
                    i += 1
                stuffs.append(new_stuff)

        return stuffs


material_file_name = "Material.csv"
materials = readcsv(material_file_name, Material)
