from math import pi, tan, sin, cos

from modules import Tank, Engine, Rcs

from vector import Vector, dot
from copy import copy

from functools import reduce

from gui import combinelines

from pickle import dump, load


def rsetattr(obj, attr, val):
    pre, _, post = attr.rpartition(".")
    return setattr(rgetattr(obj, pre) if pre else obj, post, val)


# using wonder's beautiful simplification: https://stackoverflow.com/questions/31174295/getattr-and-setattr-on-nested-objects/31174427?noredirect=1#comment86638618_31174427


def rgetattr(obj, attr, *args):
    def _getattr(obj, attr):
        return getattr(obj, attr, *args)

    return reduce(_getattr, [obj] + attr.split("."))


class Ship(object):
    def __init__(self):
        self.module = []
        self.engines = []
        self.mass = 0
        # structural acceleration limit
        self.str_acc_lim = 0
        self.moi = 0, 0
        self.percentage = None
        self.name = "NewShip"

    def add(self, stuff, num=1):
        if num == 1:
            stuff_copy = copy(stuff)
            self.module.append(stuff_copy)
            if isinstance(stuff, Engine):
                # defaults to engine thrusting directly forward.
                self.engines.append([stuff_copy, Vector(0, 0, 1)])
                stuff_copy.ort = Vector(0, 0, 1)

        elif num > 1:
            # add clusters of stuff.
            new_clus = [copy(stuff) for i in range(0, num)]
            self.module.append(new_clus)
            # handling of RCS clusters.
            if isinstance(stuff, Engine):
                for eng in new_clus:
                    spher = Vector(
                        1, pi / 2, 2 * pi * new_clus.index(eng) / len(new_clus)
                    )
                    self.engines.append([eng, spher.spher_to_cart()])
                    eng.ort = spher.spher_to_cart()

        self.tally()

    # try to flatten a non-uniform data structure, e.g.[a,[b,c],d]
    # into [a,b,c,d]
    def get_flat(self, attr):
        queue = []
        for stuff in getattr(self, attr):
            if isinstance(stuff, list):
                queue.extend(stuff)
            else:
                queue.append(stuff)
        return queue

    def tally(self):
        # tally ship mass
        self.mass = 0
        queue = self.get_flat("module")
        for module in queue:
            if module.mass is not None:
                self.mass += module.mass
            if isinstance(module, Tank):
                self.mass += module.pmass

        # starting coordinate system:using starting module's top as
        # reference.
        masses = []
        heights = []
        for mod in self.module:
            # getting maxima of clusters.
            if isinstance(mod, list):
                if all(isinstance(x, Tank) for x in mod):
                    heights.append(max(x.h for x in mod))
                    masses.append(sum(x.mass for x in mod) + sum(x.pmass for x in mod))
                elif all(isinstance(x, Engine) for x in mod):
                    heights.append(max(x.r * 2 for x in mod))
                    masses.append(sum(x.mass for x in mod))
            else:
                if isinstance(mod, Engine):
                    orient = self.engines[[x[0] for x in self.engines].index(mod)][1]
                    heights.append(
                        max(
                            abs(dot(orient, Vector(0, 0, 1)) * mod.h),
                            abs(dot(orient, Vector(1, 0, 0)) * mod.r * 2),
                        )
                    )
                    masses.append(mod.mass)

                else:
                    if isinstance(mod, Tank):
                        heights.append(mod.h)
                        masses.append(mod.mass + mod.pmass)

        # converts to cumulative h
        hcum = []
        curr_h = 0
        for h in heights:
            hcum.append(h / 2 + curr_h)
            curr_h += h

        # center_of_mass as expressed in h
        try:
            h_com = sum(x * y for x, y in zip(hcum, masses)) / sum(masses)
        except ZeroDivisionError:
            h_com = 0

        for mod in self.module:
            p = h_com - hcum[self.module.index(mod)]
            if isinstance(mod, list):
                i = 0
                for m in mod:
                    if len(mod) == 2:
                        rad_sep = m.r
                    else:
                        rad_sep = m.r / tan(pi / len(mod))
                    ang = i / len(mod) * 2 * pi
                    m.pos = p * Vector(0, 0, 1) + Vector(
                        sin(ang) * rad_sep, cos(ang) * rad_sep, 0
                    )
                    i += 1
            else:
                mod.pos = Vector(0, 0, p)

        for mod in self.get_flat("module"):
            if isinstance(mod, Tank):
                mod.percentage()

        sigma_moi_z = 0
        sigma_moi_xy = 0

        for pos in self.module:
            theta_m = 0
            if isinstance(pos, list):
                sum_d_sq_xy = 0
                for i in range(0, len(pos)):
                    ang = i * 2 * pi / len(pos)
                    sum_d_sq_xy += abs(cos(ang)) ** 2

                m = pos[0].mass
                r = pos[0].r
                h = pos[0].h
                d = r / tan(pi / len(pos))
                moi_xy = sum_d_sq_xy * m + (1 / 12 * m * (3 * r ** 2 + h ** 2)) * len(
                    pos
                )
                moi_z = (1 / 2 * m * r ** 2 + m * d ** 2) * len(pos)
                theta_m = sum(x.mass for x in pos)
            else:
                m = pos.mass
                r = pos.r
                h = pos.h

                moi_xy = 1 / 12 * m * (3 * r ** 2 + h ** 2)
                moi_z = 1 / 2 * m * r ** 2

            sigma_moi_xy += moi_xy + theta_m * heights[self.module.index(pos)] ** 2
            sigma_moi_z += moi_z

        # calculates moment of inertia on the x-y plane.
        self.moi = sigma_moi_xy, sigma_moi_z

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
        self.tally()

    # return a dictionary of tank capacity for given tanks.
    # {propellant:mass_remaining,
    #   propellant2:mass_remaining_2}
    def query_tank(self, tanks):
        if tanks is None:
            tanks = self.get_tanks()
        tank_cap = {}
        for tank in tanks:
            content = tank.content
            if content in tank_cap:
                tank_cap[content] = tank_cap[content] + tank.pmass
            else:
                tank_cap.update({content: tank.pmass})
        return tank_cap

    def get_tanks(self):
        modules = self.get_flat("module")
        tanks = []
        for mod in modules:
            if isinstance(mod, Tank):
                tanks.append(mod)
        return tanks

    # calculate the remaining burn time.
    def burntime(self, engine, tanks):
        mix = engine.propellant
        # query tank capacity
        tank_cap = self.query_tank(tanks)
        # calculate burn time possible of engines.
        burntime = {}
        mdot_p_dict = {}
        for propellant in mix.composition:
            mdot_p = engine.mdot * mix.mass_ratio_norm(propellant)
            mdot_p_dict.update({propellant: mdot_p})
            t_p = tank_cap[propellant] / mdot_p
            burntime.update({propellant: t_p})

        # gets the propellant who has the minimal burntime.
        low_prop = min(burntime, key=burntime.get)
        t_min = burntime[low_prop]
        return t_min

    def burn(self, engine, tanks, t):
        t_min = self.burntime(engine, tanks)
        t_actual = min(t_min, t)
        mix = engine.propellant
        for propellant in mix.composition:
            # iterate every tank containing said propellant:
            proposed_drain = (
                t_actual * engine.mdot * engine.propellant.mass_ratio_norm(propellant)
            )
            for tank in tanks:
                content = tank.content
                if content == propellant:
                    if tank.pmass > proposed_drain:
                        tank.pmass -= proposed_drain
                        break
                    else:
                        tank.pmass = 0
                        proposed_drain -= tank.pmass

        self.tally()
        return t_actual

    # return the position of a module. Handles clusters and single modules.
    def get_mod_pos(self, mod):
        return mod.pos

    def get_engine_orient(self, engine):
        for e, o in self.engines:
            if e == engine:
                return o

    def print(self):
        # debugging diagram.
        print("ship diagram:")
        print(self.diagram())

    def diagram(self):
        def makegraph(*args):
            result = []
            for arg in args:
                result.append(arg)
            return result

        # RCS graphics:
        """
         v
        > <
         ^
        """

        rcs = makegraph(">O<")

        # engine graphics
        """
        \\___/
         /   \
        /     \
        """

        eng = makegraph(" \\___/", " /   \\ ", "/     \\")

        # tank graphics
        """
        /¯¯¯\\
        |   |
        |   |
        \\___/
        """

        tank = makegraph("/¯¯¯\\", "|   |", "|   |", "\\___/")
        graph_dict = {Tank: tank, Rcs: rcs, Engine: eng}
        len_dict = {Tank: 5, Rcs: 3, Engine: 7}
        height_dict = {Tank: 4, Rcs: 1, Engine: 3}

        # find the largest length.

        max_length = 0
        height = 0
        for pos in self.module:
            length = 0
            if isinstance(pos, list):
                for mod in pos:
                    length += len_dict[mod.__class__]
                height += height_dict[mod.__class__]
            else:
                length += len_dict[pos.__class__]
                height += height_dict[pos.__class__]
            if length > max_length:
                max_length = length

        # axis of symmetry is between characters:
        centerline = max_length // 2

        graph = str(" " * max_length + "\n") * height

        graph_lines = graph.splitlines()

        height = 0

        for pos in self.module:
            pad_to_left = 0

            if isinstance(pos, list):
                for mod in pos:
                    curr_height = height_dict[mod.__class__]
                    pad_to_left = (len(pos) // 2 - pos.index(mod)) * len_dict[
                        mod.__class__
                    ] + len(pos) % 2 * len_dict[mod.__class__] // 2
                    start = centerline - pad_to_left
                    end = centerline - pad_to_left + len_dict[mod.__class__]
                    graph_index = 0
                    for i in range(height, height + height_dict[mod.__class__]):
                        graph_lines[i] = (
                            graph_lines[i][:start]
                            + graph_dict[mod.__class__][graph_index]
                            + graph_lines[i][end:]
                        )

                        graph_index += 1
            else:
                curr_height = height_dict[pos.__class__]
                pad_to_left = len_dict[pos.__class__] // 2
                start = centerline - pad_to_left
                end = centerline - pad_to_left + len_dict[pos.__class__]
                graph_index = 0
                for i in range(height, height + height_dict[pos.__class__]):
                    graph_lines[i] = (
                        graph_lines[i][:start]
                        + graph_dict[pos.__class__][graph_index]
                        + graph_lines[i][end:]
                    )

                    graph_index += 1

            height += curr_height

            graph = combinelines(graph_lines)

        return graph

    def load(filename):
        savefile = open(filename, "rb")
        myself = load(savefile)
        savefile.close
        return myself

    def save(self, filename):
        savefile = open(filename, "wb")
        dump(self, savefile)
        savefile.close()

    def modnames(self):
        modnames = []
        for mod in self.module:
            if isinstance(mod, list):
                modnames.append("{}x{}".format(len(mod), mod[0].name))
            else:
                modnames.append(mod.name)

        return modnames

    def delmod(self, i):
        deleted_mod = self.module[i]

        if isinstance(deleted_mod, list):
            for i in deleted_mod:
                if isinstance(i, Engine):
                    self.engines.remove([i, self.get_engine_orient(i)])

        elif isinstance(deleted_mod, Engine):
            self.engines.remove([deleted_mod, self.get_engine_orient(deleted_mod)])

        self.module.remove(deleted_mod)

        self.tally()
