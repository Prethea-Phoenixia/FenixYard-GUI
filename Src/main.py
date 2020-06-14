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
    pass