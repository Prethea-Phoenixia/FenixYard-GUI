import pickle
import os

from materials import Material, Mixture
from gui import window, mainloop
from utils import get_terminal_size_win, all_subclasses
from iohandler import all_file_with_extension

from modules import Mod, Engine, Rcs, Tank

from ship import Ship

from os import system


class container:
    def __init__(self):
        self.content = None

    def setcontent(self, val):
        self.content = val

    def getcontent(self):
        return self.content


def showShipEditor():
    w, h = get_terminal_size_win()
    absolutePath = str(os.path.dirname(os.path.realpath(__file__)))
    editor = window("editor", w, h - 1)
    system("title " + "Editor")
    ship_name = "NewShip"
    shipname = editor.addelement("ul", h=0.1, w=0.2, t="Name:", type="value")
    shipname.value("", ship_name, "NewShip")

    fileselect = editor.addelement("ul", h=0.1, w=0.6, t="File:", type="menu")
    fileselect.bind("i", "p", "o")

    save = editor.addelement("ul", h=0.1, w=0.05, t="", type="button")
    save.bind("s")

    load = editor.addelement("ul", h=0.1, w=0.05, t="", type="button")
    load.bind("l")

    new = editor.addelement("ul", h=0.1, w=0.05, t="", type="button")
    new.bind("n")

    delete = editor.addelement("ul", h=0.1, w=0.05, t="", type="button")
    delete.bind("x")

    currentShip = container()

    def loop_func():
        # updates file in the \ships folder.
        files = all_file_with_extension(".ship", absolutePath + r"\ships")
        fileselect.menu("", files, mode="togg")

        ship = currentShip.getcontent()
        if ship is None:
            shipname.setval("NO SHIP LOADED")
        else:
            if shipname.getval() == "NO SHIP LOADED":
                shipname.setval(ship.name)
            elif shipname.getval() != ship.name:  # assigns ship name from input
                ship.name = shipname.getval()

        def loadShip():
            filedex = fileselect.getrigg()
            if filedex is not None:
                filepath = absolutePath + r"\ships\\" + str(files[filedex])
                currentShip.setcontent(Ship.load(filepath))
                updateDisplayed()
            else:
                "no file specified."

        def saveShip():
            if currentShip.getcontent() is not None:
                currentShipName = shipname.getval()
                savepath = absolutePath + r"\ships\{}".format(currentShipName + ".ship")
                (currentShip.getcontent()).save(savepath)
            else:
                print("Ship is empty.")

        def newShip():
            newship = Ship()
            currentShip.setcontent(newship)
            updateDisplayed()

        def delShip():
            try:
                selected_name = files[fileselect.getrigg()]
                savepath = absolutePath + r"\ships\{}".format(selected_name)
                os.remove(savepath)
            except (IndexError, TypeError) as e:
                print("invalid selection. please select ship to delete first.")

        def updateDisplayed():
            """updates when underlying data structure changes due to data load,
            refreshes the ship name display and other stuff. 
            """
            ship = currentShip.getcontent()
            print(ship)
            shipname.setval(ship.name)

        save.button("SAVE", saveShip)
        load.button("LOAD", loadShip)
        new.button("NEW", newShip)
        delete.button("DEL", delShip)

    mainloop(editor, loop_func)


def showModEditor():
    absolutePath = str(os.path.dirname(os.path.realpath(__file__)))
    editor = window("editor", 64, 20)
    system("title " + "Editor")

    mod_name = "NewModule"
    modname = editor.addelement("ul", h=3, w=20, t="Name:", type="value")
    modname.value("", mod_name, "NewModule")

    modtype = editor.addelement("ul", h=3, w=20, t="mod:", type="menu")
    modtype.bind("q", "w")

    save = editor.addelement("ul", h=3, w=6, t="", type="button")
    save.bind("s")

    load = editor.addelement("ul", h=3, w=6, t="", type="button")
    load.bind("l")

    new = editor.addelement("ul", h=3, w=6, t="", type="button")
    new.bind("n")

    delete = editor.addelement("ul", h=3, w=6, t="", type="button")
    delete.bind("x")

    fileselect = editor.addelement("ur", h=17, w=24, t="File:", type="menu")
    fileselect.bind("i", "p", "o")

    currentMod = container()
    tempElem = container()
    tempVal = container()

    def loop_func():
        files = os.listdir(absolutePath + r"\mods")
        modclass = all_subclasses(Mod)
        modclassname = [x.__name__ for x in modclass]
        # updates file in the \mods folder
        fileselect.menu("", files, mode="togg")
        modtype.menu("", modclassname, mode="sel")

        mod = currentMod.getcontent()
        if mod is None:
            modname.setval("NO MODULE LOADED")
        else:
            if modname.getval() == "NO MODULE LOADED":
                modname.setval(mod.name)
            elif modname.getval() != mod.name:  # assigns ship name from input
                mod.name = modname.getval()

        def loadMod():
            filedex = fileselect.getrigg()
            if filedex is not None:
                filepath = absolutePath + r"\mods\\" + str(files[filedex])
                currentMod.setcontent(Ship.load(filepath))
                updateDisplayed()
            else:
                "no file specified."

        def saveMod():
            if currentMod.getcontent() is not None:
                currentShipName = modname.getval()
                savepath = absolutePath + r"\mods\{}".format(currentShipName)
                (currentMod.getcontent()).save(savepath)
            else:
                print("Mod is empty.")

        def newMod():
            newMod = modclass[modtype.getval()]()
            currentMod.setcontent(newMod)
            updateDisplayed()

        def delMod():
            try:
                selected_name = files[fileselect.getrigg()]
                savepath = absolutePath + r"\mods\{}".format(selected_name)
                os.remove(savepath)
            except (IndexError, TypeError) as e:
                print("invalid selection. please select ship to delete first.")

        def updateDisplayed():
            """updates when underlying data structure changes due to data load,
            refreshes the Module name display and other stuff. 
            """
            mod = currentMod.getcontent()
            modname.setval(mod.name)

        save.button("SAVE", saveMod)
        load.button("LOAD", loadMod)
        new.button("NEW", newMod)
        delete.button("DEL", delMod)

        tpe = tempElem.getcontent()
        # delete all temporary element. just in case.
        if tpe is not None:
            editor.delete_element(*tpe)

        mod = currentMod.getcontent()
        tval = tempVal.getcontent()

        if isinstance(mod, Engine):
            propThrust = tval
            pT = editor.addelement("lu", h=3, w=10, type="value")
            pT.value("KN", propThrust,reversed = True)
            (*tpe,) = pT,
            (*tval,) = pT.getval(),

        tempElem.setcontent(tpe)
        tempVal.setcontent(tval)

    mainloop(editor, loop_func)


if __name__ == "__main__":
    showModEditor()
    showShipEditor()
