import os

from materials import Material, Mixture
from gui import window, mainloop
from utils import get_terminal_size_win, all_subclasses
from iohandler import all_file_with_extension, readtxt, index_name

from modules import Mod, Engine, Rcs, Tank

from ship import Ship

from os import system

from math import nan

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
    currentMod = container()

    diagram = editor.addelement("lu", w=0.2, h=0.9, t="Diagram:")

    modselect = editor.addelement("ru", w=0.4, h=0.4, t="Module:", type="menu")

    addmodule = editor.addelement("ru", w=0.1, h=0.1, t="", type="button")

    delmodule = editor.addelement("ru", w=0.1, h=0.1, t="", type="button")

    shipmodlist = editor.addelement("lu", w=0.2, h=0.9, t="Module:", type="menu")
    shipmodlist.bind("w")

    stracclim = editor.addelement("lu", w=0.2, h=0.1, t="", type="value")
    stracclim.value(
        ">>", 9.8,
    )
    stracclim.bind("a")

    shipinfo = editor.addelement("lu", w=0.2, h=0.4, t="info")

    modinfo = editor.addelement("lu", w=0.2, h=0.4, t="info")

    def loop_func():
        modfiles = os.listdir(absolutePath + r"\mods")
        # updates file in the \ships folder.
        files = all_file_with_extension(".ship", absolutePath + r"\ships")
        fileselect.menu("", files, mode="togg")
        modselect.menu("", modfiles, mode="sel")

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
            stracclim.value(">>", 9.8)
            updateDisplayed()

        def delShip():
            try:
                selected_name = files[fileselect.getrigg()]
                savepath = absolutePath + r"\ships\{}".format(selected_name)
                os.remove(savepath)
            except (IndexError, TypeError) as e:
                print("invalid selection. please select ship to delete first.")

        def updateDisplayed():
            """new approach: instead of manually taking note of what must be updated, from now on
            will simply force another render cycle."""
            return True

        def insertModule():
            # which one to get?
            modi = modselect.getval()
            # load our module.
            currentMod.setcontent(
                Mod.load(absolutePath + r"\mods\{}".format(modfiles[modi]))
            )
            # after loading our module, put it in our ship.
            ship = currentShip.getcontent()
            # validate our ship is actually a Ship object
            if ship is not None:
                # by how much?
                while True:
                    try:
                        num = int(input("clusters of>>"))
                        if num >= 1:
                            break
                        else:
                            print("integer >=1 plz")
                    except TypeError:
                        print("numeric please!")

                ship.add(currentMod.getcontent(), num)
                currentShip.setcontent(ship)
                updateDisplayed()
            else:
                print("Create a ship first!")

        def popModule():
            modi = shipmodlist.getval()
            ship = currentShip.getcontent()
            if ship is not None and len(ship.module) > modi:
                ship.delmod(modi)
            else:
                print("not valid deletion")

        addmodule.button("Add Module", insertModule)
        delmodule.button("Del Module", popModule)

        # ship informations displayed.
        if hasattr(ship, "diagram") and ship.diagram() is not None:
            diagram.graph(ship.diagram())
            shipmodlist.menu(">>", ship.modnames())

        ship = currentShip.getcontent()

        save.button("SAVE", saveShip)
        load.button("LOAD", loadShip)
        new.button("NEW", newShip)
        delete.button("DEL", delShip)

        ship = currentShip.getcontent()
        if hasattr(ship, "module") and len(ship.module) > 0:
            if hasattr(ship, "tally"):
                ship.tally()
            if hasattr(ship, "buildup_tank"):
                ship.str_acc_lim = stracclim.getval()
                ship.buildup_tank()

            selmod = ship.module[shipmodlist.getval()]

            if selmod is not None:
                graphics = ""
                if isinstance(selmod, list):
                    for m in selmod:
                        pos = m.pos
                        graphics += "{:.2f},{:.2f},{:.2f}\n".format(pos.x, pos.y, pos.z)
                else:
                    pos = ship.get_mod_pos(selmod)
                    graphics += "{:.2f},{:.2f},{:.2f}\n".format(pos.x, pos.y, pos.z)
                modinfo.graph(graphics)

        else:
            modinfo.clear()

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
    modname = editor.addelement("ul", h=0.1, w=0.35, t="Name:", type="value")
    modname.value("", mod_name, "NewModule")

    modtype = editor.addelement("ul", h=0.1, w=0.15, t="mod:", type="menu")

    delete = editor.addelement("ur", h=0.1, w=0.05, t="", type="button")
    delete.bind("x")

    new = editor.addelement("ur", h=0.1, w=0.05, t="", type="button")
    new.bind("n")

    load = editor.addelement("ur", h=0.1, w=0.05, t="", type="button")
    load.bind("l")

    save = editor.addelement("ur", h=0.1, w=0.05, t="", type="button")
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

            (pC, pS, pM, pLDR, eM, tDG) = tempElem.getcontent()
            content = materials[pC.getval()]

            structure = materials[pS.getval()]
            ldr = pLDR.getval()
            mass = pM.getval()
            warnings = ""
            if ldr > 0 and mass > 0 and structure.yieldstrength > 0:
                tank.set(content, mass * 1000, structure, ldr)
                modname.setval(tank.name)
                currentMod.setcontent(tank)
                warnings = ""
                isValid = True

            if mass <= 0:
                warnings += "!!Tank is empty!!\n"
            if ldr <= 0:
                warnings += "!!length/diameter is not valid!!\n"
            if structure.yieldstrength <= 0:
                warnings += "!!invalid structure!!\n"
            eM.graph(warnings)

            h = nan
            w = nan
            m = nan
            strm = nan

            if tank.h is not None:
                h = tank.h
                w = tank.w

            if tank.mass is not None:
                m = tank.mass

            if tank.strmass is not None:
                strm = tank.strmass

            diagram = "     w = {:.1f}m".format(w) + "\n"
            diagram += "    /-------\\" + "\n"
            diagram += "    |       |" + "\n"
            diagram += "    |       |" + "\n"
            diagram += "    |       |" + "h = {:.1f}m".format(h) + "\n"
            diagram += "    |       |" + "\n"
            diagram += "    |       |" + "\n"
            diagram += "    \\-------/" + "\n"

            diagram += " mass {} t\n".format(m / 1000)

            tDG.graph(diagram)

            return isValid

        def handleEngine():
            isValid = False
            engine = currentMod.getcontent()
            pT, pP, dG, eM = tempElem.getcontent()
            prop = mixtures[pP.getval()]
            thrust = pT.getval()
            if thrust > 0:
                engine.set(prop, thrust * 1000)
                modname.setval(engine.name)
                eM.clear()
                warnings = ""
                currentMod.setcontent(engine)
                isValid = True
            else:
                warnings = "!!Engine is not producing thrust!!"

            rad = engine.r

            if rad is None:
                rad = "!!invalid!!"
            else:
                rad = "r={:.1f}m".format(rad)

            engine_diagram = (
                "      /----\\"
                + "\n"
                + "      |    |  {}".format(rad)
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

            if engine.propellant is not None:
                for prop in engine.propellant.composition:
                    m_r = engine.propellant.mass_ratio_norm(prop) * engine.mdot
                    p_n = prop.name
                    engine_diagram += "{}:{:.2f}kg/s".format(p_n, m_r) + "\n"
            dG.graph(engine_diagram)
            eM.graph(warnings)

            return isValid

        def loadMod():
            filedex = fileselect.getrigg()
            if filedex is not None:
                filepath = absolutePath + r"\mods\\" + str(files[filedex])
                newMod = Ship.load(filepath)
                currentMod.setcontent(newMod)
                handleTemporary(newMod)
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
            handleTemporary(newMod)
            updateDisplayed()

        def delMod():
            try:
                selected_name = files[fileselect.getrigg()]
                savepath = absolutePath + r"\mods\{}".format(selected_name)
                os.remove(savepath)
            except (IndexError, TypeError) as e:
                print("invalid selection. please select ship to delete first.")

        def handleTemporary(newMod):
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
                pC = editor.addelement("lu", h=0.45, w=0.25, type="menu", t="Content")
                pC.menu(">", materialNames, mode="trig")

                pS = editor.addelement("lu", h=0.45, w=0.25, type="menu", t="Structure")
                pS.menu(">", materialNames, mode="trig")

                pM = editor.addelement("lu", h=0.1, w=0.25, type="value", t="mass")
                pM.value("t", pM.val, reversed=True)
                pM.bind("m")
                pLDR = editor.addelement("lu", h=0.1, w=0.25, type="value", t="L/D")
                pLDR.value("", pLDR.val)
                pLDR.bind("r")
                eM = editor.addelement("lu", h=0.2, w=0.25, t="Errors:")
                tDG = editor.addelement("lu", h=0.5, w=0.25, t="Diagram")

                (*tpe,) = (pC, pS, pM, pLDR, eM, tDG)
                tempElem.setcontent(tpe)

        def updateDisplayed():
            return True

        load.button("LOAD", loadMod)
        new.button("NEW", newMod)
        delete.button("DEL", delMod)

        saving_valid = False
        mod = currentMod.getcontent()
        if tempElem.getcontent() is not None:
            if isinstance(mod, Engine):
                saving_valid = handleEngine()
            elif isinstance(mod, Tank):
                saving_valid = handleTank()

        if saving_valid:
            save.button("SAVE", saveMod)
        else:
            save.button("    ", dontsave)

    mainloop(editor, loop_func)

    return True


if __name__ == "__main__":
    while True:
        showModEditor()
        showShipEditor()
