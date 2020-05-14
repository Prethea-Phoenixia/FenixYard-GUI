from math import pi

from modules import Tank, Engine

from vector import Vector, dot
from copy import copy


class Ship(object):
    def __init__(self):
        self.module = []
        self.engines = []
        self.mass = 0
        # structural acceleration limit
        self.str_acc_lim = 0
        self.mod_pos = []
        self.moi = 0

    # use the module passed as a protoype and copy it.
    def addmod(self, module):
        module = copy(module)
        self.module.append(module)

    def addcluster(self, cluster_list):
        new_clus = []
        for tank in cluster_list:
            new_clus.append(copy(tank))
        self.module.append(new_clus)

    # separates adding of engine system.
    def addengine(self, engine, orientation):
        engine_itself = copy(engine)
        self.module.append(engine_itself)
        self.engines.append([engine_itself, orientation])

    # intended for adding reaction control thrusters (RCS).
    def addradialengines(self, engine, num):
        radials = [copy(engine) for i in range(0, num)]

        self.module.append(radials)
        for eng in radials:
            spher = Vector(1, pi / 2, 2 * pi * radials.index(eng) / len(radials))
            self.engines.append([eng, spher.spher_to_cart()])

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
        self.mod_pos = []
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
        h_com = sum(x * y for x, y in zip(hcum, masses)) / sum(masses)

        for mod in self.module:
            self.mod_pos.append(h_com - hcum[self.module.index(mod)])

        # calculates moment of inertia on the x-y plane.
        self.moi = sum(m * r ** 2 for r, m in zip(self.mod_pos, masses)) + sum(
            1 / 12 * m * l ** 2 for l, m in zip(heights, masses)
        )

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
        if isinstance(mod, list):
            return self.mod_pos[self.module.index(mod)]
        else:
            if mod in self.module:
                return self.mod_pos[self.module.index(mod)]
            else:
                for cluster in self.module:
                    if isinstance(cluster, list):
                        if mod in cluster:
                            return self.mod_pos[self.module.index(cluster)]

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

    def get_engine_orient(self, engine):
        for e, o in self.engines:
            if e == engine:
                return o

    def print(self):
        print("ship diagram:")
        max_clustering = 0
        for po in self.module:
            if isinstance(po, list):
                max_clustering = max(max_clustering, len(po))

        def get_padding(curr_clustering):
            return (max_clustering / 2 * 16) - (8 + 8 * (curr_clustering - 1))

        def pad(clustering):
            i = 0
            while i < get_padding(clustering):
                print(" ", end="")
                i += 1

        # convert everything into nested list
        display_queue = []
        for pos in self.module:
            if isinstance(pos, list):
                display_queue.append(pos)
            else:
                display_queue.append([pos])

        for pos in display_queue:
            if all(isinstance(x, Tank) for x in pos):
                pad(len(pos))
                for mod in pos:
                    print("/¯¯¯¯¯¯¯¯¯¯¯¯¯¯\\", end="")
                print("")
                pad(len(pos))
                for mod in pos:
                    op = str("|  {:^10}  |".format(mod.content.name))
                    print(op, end="")
                print("")
                pad(len(pos))
                for mod in pos:
                    op = str("|  {:^10.2f}  |".format(mod.percentage()))
                    print(op, end="")
                print("")
                pad(len(pos))
                for mod in pos:
                    print("\\______________/", end="")
                print("")

            elif all(isinstance(x, Engine) for x in pos):
                pad(len(pos))
                for eng in pos:
                    if self.get_engine_orient(eng) == Vector(0, 0, 1):
                        op = str("\\__{:^10}__/".format("Engine"))
                    else:
                        op = str("      {:_^4}      ".format("\\/"))
                    print(op, end="")
                print("")
                pad(len(pos))
                for eng in pos:
                    if self.get_engine_orient(eng) == Vector(0, 0, 1):
                        # main thruster, firing toward the back:
                        op = str("   /        \\   ")
                    else:
                        op = str("     >{:^4}<     ".format("RCS"))
                    print(op, end="")
                print("")
                pad(len(pos))
                for eng in pos:
                    if self.get_engine_orient(eng) == Vector(0, 0, 1):
                        op = str("  / {:^8} \\  ".format(eng.propellant.name))
                    else:
                        op = str("      {:¯^4}      ".format("/\\"))
                    print(op, end="")
                print("")

        print("mass:{:.2f} kg".format(self.mass))
