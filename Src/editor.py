import pickle
import os

from materials import Material, Mixture
from gui import window, mainloop
from utils import get_terminal_size_win, all_subclasses
from iohandler import all_file_with_extension, readtxt, index_name

from modules import Mod, Engine, Rcs, Tank

from ship import Ship

from os import system

absolutePath = str(os.path.dirname(os.path.realpath(__file__)))

w, h = get_terminal_size_win()


class container:
    def __init__(self):
        self.content = None

    def setcontent(self, val):
        self.content = val

    def getcontent(self):
        return self.content


def showShipEditor():

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
    # import instances of material classes, defined by material_file_name
    # and indexing the materials. ( with name only )

    material_file_name = "Material.txt"
    materials = readtxt(absolutePath + r"\\" + material_file_name, Material)

    # import instances of propellant mixtures, defined by propellant_file_name

    mixture_file_name = "Propulsion.txt"
    mixtures = readtxt(
        absolutePath + r"\\" + mixture_file_name,
        Mixture,
        materials,
        Mixture.cleanup_calls,
    )
    mixtureNames = index_name(mixtures)
    materialNames = index_name(materials)

    editor = window("editor", 2 * (w // 2), 2 * (h // 2) - 4)
    system("title " + "Editor")

    mod_name = "NewModule"
    modname = editor.addelement("ul", h=0.1, w=0.24, t="Name:", type="value")
    modname.value("", mod_name, "NewModule")

    modtype = editor.addelement("ul", h=0.1, w=0.24, t="mod:", type="menu")
    modtype.bind("q", "w")

    delete = editor.addelement("ur", h=0.1, w=0.12, t="", type="button")
    delete.bind("x")

    new = editor.addelement("ur", h=0.1, w=0.12, t="", type="button")
    new.bind("n")

    load = editor.addelement("ur", h=0.1, w=0.12, t="", type="button")
    load.bind("l")

    save = editor.addelement("ur", h=0.1, w=0.12, t="", type="button")
    save.bind("s")

    fileselect = editor.addelement("ur", h=0.9, w=0.48, t="File:", type="menu")
    fileselect.bind("i", "p", "o")

    currentMod = container()
    tempElem = container()

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

        def handleTank():
            isValid = False
            tank = currentMod.getcontent()
            (pC, pS, pM, pLDR, eM) = tempElem.getcontent()
            content = materials[pC.getval()]
            structure = materials[pS.getval()]
            ldr = pLDR.getval()
            mass = pM.getval()
            if ldr > 0 and mass > 0:
                tank.set(content, mass, structure, ldr)
                modname.setval(tank.name)
                currentMod.setcontent(tank)
                isValid = True

            if mass <= 0:
                eM.text("!!length/diameter is not valid!!")
            if ldr <= 0:
                eM.text("!!Tank is empty!!")

            return isValid

        def handleEngine():
            isValid = False
            engine = currentMod.getcontent()
            pT, pP, dG, eM = tempElem.getcontent()
            prop = mixtures[pP.getval()]
            thrust = pT.getval()
            if thrust > 0:
                engine.set(prop, thrust)
                modname.setval(engine.name)
                eM.clear()
                warnings = ""
                currentMod.setcontent(engine)
                isValid = True
            else:
                warnings = "!!Engine is not producing thrust!!"

            engine_diagram = (
                "      /----\\"
                + "\n"
                + "      |    |"
                + "\n"
                + "      \\    /"
                + "\n"
                + "      /    \\"
                + "\n"
                + "     /      \\"
                + "\n"
                + "    /        \\"
                + "\n"
            )
            dG.graph(engine_diagram)

            eM.text(warnings)

            return isValid

        def loadMod():
            filedex = fileselect.getrigg()
            if filedex is not None:
                filepath = absolutePath + r"\mods\\" + str(files[filedex])
                currentMod.setcontent(Ship.load(filepath))
                updateDisplayed()
            else:
                "no file specified."

        def saveMod():
            currentShipName = modname.getval()
            savepath = absolutePath + r"\mods\{}".format(currentShipName)
            (currentMod.getcontent()).save(savepath)

        def dontsave():
            if currentMod.getcontent() is None:
                print("no module to save.")
            else:
                print("Module have errors.cannot save.")

        def newMod():
            newMod = modclass[modtype.getval()]()
            currentMod.setcontent(newMod)
            updateDisplayed()

            tpe = tempElem.getcontent()

            # delete all temporary element. just in case.
            if tpe is not None:
                editor.delete_element(*tpe)
                tempElem.setcontent(None)

            if isinstance(newMod, Engine):
                pT = editor.addelement("lu", h=0.1, w=0.24, type="value")
                pT.value("KN", pT.val, reversed=True)
                pP = editor.addelement("lu", h=0.8, w=0.24, type="menu")
                pP.menu(">", mixtureNames, mode="sel")
                dG = editor.addelement("lu", h=0.45, w=0.24)
                eM = editor.addelement("lu", h=0.45, w=0.24)

                (*tpe,) = (pT, pP, dG, eM)
                tempElem.setcontent(tpe)

            elif isinstance(newMod, Tank):
                pC = editor.addelement("lu", h=0.45, w=0.24, type="menu", t="Content")
                pC.menu(">", materialNames, mode="sel")
                pS = editor.addelement("lu", h=0.45, w=0.24, type="menu", t="Structure")
                pS.menu(">", materialNames, mode="sel")
                pM = editor.addelement("lu", h=0.1, w=0.24, type="value", t="mass")
                pM.value("t", pM.val, reversed=True)
                pM.bind("m")
                pLDR = editor.addelement("lu", h=0.1, w=0.24, type="value", t="L/D")
                pLDR.value("", pLDR.val)
                pLDR.bind("r")
                eM = editor.addelement("lu", h=0.2, w=0.24)

                (*tpe,) = (pC, pS, pM, pLDR, eM)
                tempElem.setcontent(tpe)

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

        load.button("LOAD", loadMod)
        new.button("NEW", newMod)
        delete.button("DEL", delMod)

        saving_valid = False
        mod = currentMod.getcontent()
        if isinstance(mod, Engine):
            saving_valid = handleEngine()
        elif isinstance(mod, Tank):
            saving_valid = handleTank()

        if saving_valid:
            save.button("SAVE", saveMod)
        else:
            save.button("    ", dontsave)

    mainloop(editor, loop_func)


if __name__ == "__main__":
    showModEditor()
    showShipEditor()
