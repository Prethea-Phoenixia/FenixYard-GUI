from vector import Vector, cross


from materials import Material, Mixture
from modules import Tank, Engine, Rcs
from iohandler import readtxt, return_instance_from_list
from ship import Ship
from matrix import Matrix, nnls, vec_to_pbl_matrix
from utils import euler_rot

from orders import Orders

import os

absolutePath = str(os.path.dirname(os.path.realpath(__file__)))

# layer for accounting for current ship state.
class State(object):
    # time value used for propulsion integration setting.

    def __init__(self):
        self.ship = None
        # world coordinate.
        self.pos = Vector(0, 0, 0)
        # orientation. in cartesian.
        self.ort = Vector(0, 0, 1)
        self.vel = Vector(0, 0, 0)
        self.angvel = Vector(0, 0, 0)
        self.order = None

    # 10 milliseconds
    def step(self, myOrder, dT=0.01):
        # initialize variables:
        tanks = self.ship.get_tanks()
        desired_vel_c, desired_ang_vel_c = myOrder.getorder()
        myShip = self.ship

        acc = []
        ang_acc = []

        for engine, orientation in myShip.engines:
            f = orientation * engine.thrust
            r = Vector(0, 0, myShip.get_mod_pos(engine))
            tq = cross(r, f)

            a = f / myShip.mass
            tqx, tqy, tqz = tq.getval()
            moixy, moiz = self.moi
            alpha = Vector(tqx / moixy, tqy / moixy, tqz / moiz)

            acc.append(a)
            ang_acc.append(alpha)

        vel_pblm = vec_to_pbl_matrix(desired_vel_c, acc)
        ang_pblm = vec_to_pbl_matrix(desired_ang_vel_c, ang_acc)

        pblmtx = Matrix(len(vel_pblm.mat) + len(ang_pblm.mat), len(myShip.engines) + 1)
        pblmtx.mat = vel_pblm.mat
        pblmtx.mat.extend(ang_pblm.mat)
        l, r = pblmtx.deaug()

        engine_burntimes = nnls(l, r)

        i = 0

        deltav = Vector(0, 0, 0)
        deltaw = Vector(0, 0, 0)
        for engine, ort in myShip.engines:
            if max(engine_burntimes) == 0:
                this_burn_time = 0
            else:
                this_burn_time = dT * engine_burntimes[i] / max(engine_burntimes)
            myShip.burn(engine, tanks, this_burn_time)
            deltav += this_burn_time * acc[i]
            deltaw += this_burn_time * ang_acc[i]
            i += 1

        # assuming mostly constant-acceleration.(reasonable assumption under small enough dt)
        euler_vec = self.angvel * dT + 1 / 2 * deltaw * dT ** 2
        self.ort = euler_rot(self.ort, euler_vec).unit()

        self.pos += self.vel * dT + 1 / 2 * deltav.norm() * dT ** 2 * self.ort

        # translate deltav (in ship coordinate space) into world coordinate space.
        self.vel += deltav.norm() * self.ort
        self.angvel += deltaw

        myOrder.update_order(deltav, deltaw, dT)

    def print(self):
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
            "orientation {:^6.4f} {:^6.4f} {:^6.4f}".format(
                self.ort.x, self.ort.y, self.ort.z
            )
        )
        print(
            "angvel      {:^6.4f} {:^6.4f} {:^6.4f}".format(
                self.angvel.x, self.angvel.y, self.angvel.z
            )
        )
        print()


class World:
    def __init__(self):
        self.time = 0
        self.states = []
        self.pulse = 0.01  # pulse time(dt) = 0.01s

    def runturn(self, time):
        for i in range(int(time / self.pulse)):
            for state in self.states:
                state.step(state.order, self.pulse)
            self.time += self.pulse


if __name__ == "__main__":
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

    hydrogen = return_instance_from_list("Hydrogen", materials)
    oxygen = return_instance_from_list("Oxygen", materials)
    water = return_instance_from_list("Water", materials)
    aluminum = return_instance_from_list("Aluminum", materials)

    lh2lox = return_instance_from_list("LH2-LOX", mixtures)
    sntrw = return_instance_from_list("SNTR-H2O", mixtures)

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
    engine.scale_engine(lh2lox, 500000)

    ntr = Engine()
    ntr.scale_engine(sntrw, 20000)

    rcs = Rcs()
    rcs.scale_engine(lh2lox, 500)

    testship = Ship()
    testship.str_acc_lim = 30

    testship.addmod(watertank)
    testship.addradialengines(rcs, 4)
    testship.addcluster(oxytank, 2)
    testship.addcluster(hydtank, 2)
    testship.addradialengines(rcs, 4)
    testship.addengine(engine, Vector(0, 0, 1))

    testship.buildup_tank()
    testship.tally()

    testship.remove_mod(0)

    testscene = State()
    testscene.ship = testship

    testorder = Orders(testscene)
    testscene.order = testorder

    world = World()
    world.states.append(testscene)

    from monitor import watch

    watch(world)
