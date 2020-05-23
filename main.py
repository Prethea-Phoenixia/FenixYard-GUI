from math import pi, log
from vector import Vector, dot, cross


from materials import Material, Mixture
from modules import Tank, Engine
from iohandler import readtxt, return_instance_from_list
from ship import Ship
from matrix import Matrix, lssq, nnls, lsnm
from utils import euler_rot, asciiplt


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

    # try to fire main thrusters to move along orientation.
    def fire_main_thrusters(self, time):
        dT = State.deltaT

        tanks = self.ship.get_tanks()
        for i in range(0, time, dT):
            m0 = self.ship.mass
            sig_deltamom = 0
            sig_deltam = 0

            # integrate the entire burn sequence
            for engine, orientation in self.ship.engines:
                if orientation == Vector(0, 0, 1):
                    actual_burntime = self.ship.burn(engine, tanks, dT)
                    sig_deltamom += actual_burntime * engine.thrust
                    sig_deltam += actual_burntime * engine.mdot

                if sig_deltamom == 0:
                    eff_ve = 0
                else:
                    eff_ve = sig_deltamom / sig_deltam

                m1 = self.ship.mass

                self.vel += self.ort.unit() * log(m0 / m1) * eff_ve
                self.pos += self.vel * dT
                if sig_deltamom == 0:
                    continue
                else:
                    self.pos += (
                        self.ort * eff_ve * (dT + (dT - m0 / sig_deltam) * log(m0 / m1))
                    )

    def fire_rotational_thrusters(self, time, rot_desired_acc):

        tanks = self.ship.get_tanks()
        dT = State.deltaT

        for t in range(0, time, dT):
            relevent_enignes = []
            for engine, orientation in self.ship.engines:
                # vector result of vector f
                fvec = orientation * engine.thrust
                rvec = Vector(0, 0, self.ship.get_mod_pos(engine))
                # engine's torque.
                tq = cross(rvec, fvec)
                racc = tq / self.ship.moi
                if dot(tq, rot_desired_acc) != 0:
                    relevent_enignes.append([engine, racc])

            # solve the torque balancing problem.

            pbl_matrix = Matrix(3, 3)
            xl, yl, zl = [], [], []
            for engine, rot_acc in relevent_enignes:
                x, y, z = rot_acc.getval()
                xl.append(x)
                yl.append(y)
                zl.append(z)

            pbl_matrix.mat[0] = xl
            pbl_matrix.mat[1] = yl
            pbl_matrix.mat[2] = zl

            o, p, q = rot_desired_acc.getval()

            res_matrix = Matrix(3, 1)

            res_matrix.mat = [[o], [p], [q]]

            solution = nnls(pbl_matrix, res_matrix)

            # if the desired angular acceleration is not attainable, try very hard
            if max(solution) > 1:
                norm_solution = [i / max(solution) for i in solution]
            else:
                norm_solution = solution

            # burn every RCS engine
            i = 0
            for engine, racc in relevent_enignes:
                self.ship.burn(engine, tanks, dT * norm_solution[i])
                self.angvel += racc * dT * norm_solution[i]
                i += 1

            euler_vec = self.angvel * dT

            self.ort = euler_rot(self.ort, euler_vec)
            """
            print("angular velocity")
            self.angvel.print()
            print("orientation:")
            self.ort.print()
            print()
            """

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
    testscene.fire_main_thrusters(40)
    testscene.print()

    testscene.fire_rotational_thrusters(30, Vector(1, 1, 0))
    testscene.fire_rotational_thrusters(30, Vector(-1, -1, 0))
    testscene.print()
