from math import pi, log
from vector import Vector, dot, cross


from materials import Material, Mixture
from modules import Tank, Engine, Rcs
from iohandler import readtxt, return_instance_from_list
from ship import Ship
from matrix import Matrix, lssq, nnls, lsnm, vec_to_pbl_matrix
from utils import euler_rot, asciiplt

# layer for accounting for current ship state.
class State(object):
    # time value used for propulsion integration setting.
    deltaT = 1

    def __init__(self):
        self.ship = None
        # world coordinate.
        self.pos = Vector(0, 0, 0)
        self.ort = Vector(0, 0, 1)
        self.vel = Vector(0, 0, 0)
        self.angvel = Vector(0, 0, 0)
        self.order = None

    def step(self, myOrder, dT=1):
        # initialize variables:
        tanks = self.ship.get_tanks()
        desired_vel_c, desired_ort_c = myOrder.getorder()
        myShip = self.ship

        acc = []
        ang_acc = []

        for engine, orientation in myShip.engines:
            f = orientation * engine.thrust
            r = Vector(0, 0, myShip.get_mod_pos(engine))
            tq = cross(r, f)

            a = f / myShip.mass
            alpha = tq / self.ship.moi

            acc.append(a)
            ang_acc.append(alpha)

        vel_pblm = vec_to_pbl_matrix(desired_vel_c, acc)
        ort_pblm = vec_to_pbl_matrix(desired_ort_c, ang_acc)
        vel_pblm.print()
        print(vel_pblm.row, vel_pblm.column)
        ort_pblm.print()
        print(ort_pblm.row, ort_pblm.column)

        pblmtx = Matrix(len(vel_pblm.mat) + len(ort_pblm.mat), len(myShip.engines) + 1)
        pblmtx.mat = vel_pblm.mat
        pblmtx.mat.extend(ort_pblm.mat)
        l, r = pblmtx.deaug()

        engine_burntimes = nnls(l, r)

        i = 0
        deltav = Vector(0, 0, 0)
        deltaw = Vector(0, 0, 0)
        for engine, ort in myShip.engines:
            this_burn_time = min(engine_burntimes[i], dT)
            myShip.burn(engine, tanks, this_burn_time)
            deltav += this_burn_time * acc[i]
            deltaw += this_burn_time * ang_acc[i]
            i += 1

        self.vel += deltav
        self.angvel += deltaw

        self.pos += self.vel * dT
        euler_vec = self.angvel * dT
        self.ort = euler_rot(self.ort, euler_vec)

        myOrder.report(deltav, deltaw)

    def print(self):
        self.ship.print()
        print(
            "position    {:^6.1f} {:^6.1f} {:^6.1f}".format(
                self.pos.x, self.pos.y, self.pos.z
            )
        )

        pos = asciiplt(self.pos, return_string=False)
        vel = asciiplt(self.vel, return_string=False)
        ort = asciiplt(self.ort, return_string=False)

        for i in range(0, len(pos)):
            print(pos[i] + vel[i] + ort[i])


# order interpretation layer.
# example:
# ship_a_order = Orders(),
# ship_a_order.maintain_hdg()


class Orders:
    def __init__(self, ship):
        # desired velocity change/desired orientation change.
        self.ship = ship
        self.des_vel_c = Vector(0, 0, 0)
        self.des_ort_c = Vector(0, 0, 0)

    def maintain_hdg(self):
        # order ship to maintain heading:
        self.des_ort_c = Vector(0, 0, 0)

    def burn(self, dv):
        # order ship to burn along current heading.
        self.maintain_hdg()
        self.des_vel_c = Vector(0, 0, dv)

    def getorder(self):
        return self.des_vel_c, self.des_ort_c

    def report(self, accomplished_vel_c, accomplished_ort_c):
        self.des_vel_c -= accomplished_vel_c
        self.des_ort_c -= accomplished_ort_c


if __name__ == "__main__":
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
    engine.print()

    ntr = Engine()
    ntr.scale_engine(sntrw, 20000)
    ntr.print()

    rcs = Rcs()
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

    testorder = Orders(testship)
    testorder.burn(500)
    for i in range(50):
        testscene.step(testorder)
    testscene.print()
