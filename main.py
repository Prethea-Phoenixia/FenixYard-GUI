from math import pi, log
from vector import Vector, dot
from copy import copy

from materials import Material, Mixture
from modules import Tank, Engine
from iohandler import readtxt, return_instance_from_list

# standard atmospheric pressure,1bar,1E5pa


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

    def burn(self, engine, tanks, t):
        mix = engine.propellant
        ve = engine.ve
        force = engine.thrust
        mdot = force / ve
        # query tank capability
        tank_cap = {}
        for tank in tanks:
            content = tank.content
            if content in tank_cap:
                tank_cap.update(content=tank_cap[content] + tank.pmass)
            else:
                tank_cap.update({content: tank.pmass})

        # calculate burn time possible of engines.
        burntime = {}
        mdot_p_dict = {}
        for propellant in mix.composition:
            mdot_p = mdot * mix.mass_ratio_norm(propellant)
            mdot_p_dict.update({propellant: mdot_p})
            t_p = tank_cap[propellant] / mdot_p
            burntime.update({propellant: t_p})

        # gets the propellant who has the minimal burntime.
        low_prop = min(burntime, key=burntime.get)

        # actual burntime is min(burntime constrained by propellant/
        # burntime specified)
        t_actual = min(burntime[low_prop], t)

        for propellant in mix.composition:
            # iterate every tank containing said propellant:
            proposed_drain = t_actual * mdot_p_dict[propellant]
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
        return ve

    def get_mod_pos(self, mod):
        if isinstance(mod, list):
            return self.mod_pos[self.module.index(mod)]
        else:
            if mod in self.module:
                return self.mod_pos[self.module.index(mod)]
            else:
                flat_pos = self.get_flat("mod_pos")
                return flat_pos[self.get_flat("mod").index(mod)]

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
                        op = str("\\__{:^10}__/".format(eng.__class__.__name__))
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
                        op = str("  /          \\  ")
                    else:
                        op = str("      {:¯^4}      ".format("/\\"))
                    print(op, end="")
                print("")

        print("mass:{:.2f} kg".format(self.mass))


class State(object):
    def __init__(self):
        self.ship = None
        # world coordinate.
        self.pos = Vector(0, 0, 0)
        self.vel = Vector(0, 0, 0)
        self.ort = Vector(1, 0, 0)

    # fire main thrusters to move along orientation.
    def fire_main_thrusters(self, time):
        modules = self.ship.get_flat("module")
        tanks = []
        for mod in modules:
            if isinstance(mod, Tank):
                tanks.append(mod)

        m0 = self.ship.mass
        sig_mom = 0
        sig_mdot = 0
        for engine, orientation in self.ship.engines:
            if orientation == Vector(0, 0, 1):
                self.ship.burn(engine, tanks, time)
                sig_mom += engine.thrust
                sig_mdot += engine.thrust / engine.ve

        eff_ve = sig_mom / sig_mdot

        m1 = self.ship.mass

        v0 = self.vel
        self.vel += self.ort.unit() * log(m0 / m1) * eff_ve
        v1 = self.vel
        self.pos += (v0 + v1) / 2 * time

    def print(self):
        self.ship.print()
        print(
            "position    {:^6.1f} {:^6.1f} {:^6.1f}".format(
                self.pos.x, self.pos.y, self.pos.z
            )
        )
        print(
            "velocity    {:^6.1f} {:^6.1f} {:^6.1f}".format(
                self.vel.x, self.vel.y, self.vel.z
            )
        )
        print(
            "orientation {:^6.1f} {:^6.1f} {:^6.1f}".format(
                self.ort.x, self.ort.y, self.ort.z
            )
        )


# import instances of material classes, defined by material_file_name
# and indexing the materials. ( with name only )

material_file_name = "Material.txt"
materials = readtxt(material_file_name, Material)

# import instances of propellant mixtures, defined by propellant_file_name

mixture_file_name = "Propulsion.txt"
mixtures = readtxt(mixture_file_name, Mixture, materials, Mixture.cleanup_calls)


hydrogen = return_instance_from_list("Hydrogen", materials)
oxygen = return_instance_from_list("Oxygen", materials)
water = return_instance_from_list("Water", materials)
aluminum = return_instance_from_list("Aluminum", materials)

lh2lox = return_instance_from_list("LH2-LOX", mixtures)

hydtank = Tank()
hydtank.filltank(hydrogen, 2500, aluminum)
hydtank.resize(2)

oxytank = Tank()
oxytank.filltank(oxygen, 10000, aluminum)
oxytank.resize(2)

watertank = Tank()
watertank.filltank(water, 1000, aluminum)
watertank.resize(1)


engine = Engine()
engine.scale_engine(lh2lox, 50000)
engine.print()

rcs = Engine()
rcs.scale_engine(lh2lox, 1000)
rcs.print()

testship = Ship()
testship.str_acc_lim = 30
testship.addmod(watertank)
testship.addcluster([oxytank, hydtank])
testship.addcluster([oxytank, hydtank])
testship.addradialengines(rcs, 3)
testship.addengine(engine, Vector(0, 0, 1))
testship.buildup_tank()
testship.tally()

testscene = State()
testscene.ship = testship
testscene.print()
testscene.fire_main_thrusters(50)
testscene.print()
