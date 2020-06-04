from vector import Vector,theta,cross
from utils import euler_rot
from math import pi

class Orders:
    def __init__(self, scene):
        # desired velocity change/desired orientation change.
        self.scene = scene
        self.des_vel_c = Vector(0, 0, 0)
        self.des_ang_vel_c = Vector(0, 0, 0)
        self.ort_tgt = scene.ort
        self.ort_stt = scene.ort
        self.max_ang_acc = 1  # 1 rad/s^2
        self.achievable_tr = 0
        scene.order = self

    # defunct.
    def cancel_angvel(self):
        # order the ship to gradually go to full stop.
        self.des_ang_vel_c = -1 * self.scene.angvel

    def maintain_vel(self):
        self.des_vel_c = Vector(0, 0, 0)

    def burn(self, dv):
        # order ship to burn along current heading.
        self.des_vel_c = Vector(0, 0, dv)

    def translate(self, direction, dv):
        self.cancel_angvel()
        self.des_vel_c = direction * dv

    def rotate(self, direction, rad):
        self.maintain_vel()
        # targeted orientation.
        self.ort_stt = self.scene.ort
        self.ort_tgt = euler_rot(self.scene.ort, (direction.unit()) * rad).unit()
        self.ort_tgt.print()

    def getorder(self):
        return self.des_vel_c, self.des_ang_vel_c

    def update_order(self, accomplished_vel_c, accomplished_ang_vel_c, pulse_time):
        self.des_vel_c -= accomplished_vel_c
        self.des_ang_vel_c -= accomplished_ang_vel_c

        # updates maximum turn rate.
        if self.achievable_tr < accomplished_ang_vel_c.norm() / pulse_time:
            self.achievable_tr = accomplished_ang_vel_c.norm() / pulse_time

        acc = min(self.max_ang_acc, self.achievable_tr)

        # updates des_ang_vel_c according to orientation target.
        # delta:angle to target
        delta = theta(self.ort_tgt, self.scene.ort)
        lastdelta = theta(
            self.ort_tgt,
            euler_rot(self.scene.ort, (accomplished_vel_c * pulse_time * -1)),
        )
        if delta > lastdelta:
            self.ort_stt = self.scene.ort

        if delta > 0:
            if accomplished_ang_vel_c.norm() == 0:
                braking_time = 0
            else:
                braking_time = self.scene.angvel.norm() / acc
            # required angle for full stop
            eta = braking_time ** 2 * acc / 2 + 1 / 180 * pi
            phase = None

            if eta < delta:
                phase = "accelerating"
            else:
                phase = "decelerating"

            if phase == "accelerating":
                self.des_ang_vel_c = (
                    self.max_ang_acc
                    * pulse_time
                    * cross(self.ort_stt, (self.ort_tgt - self.ort_stt)).unit()
                )
            # braking phase
            elif phase == "decelerating":
                if self.scene.angvel.norm() <= (acc * pulse_time):
                    self.des_ang_vel_c = self.scene.angvel * -1
                else:
                    self.des_ang_vel_c = (
                        self.max_ang_acc
                        * pulse_time
                        * cross(self.ort_stt, (self.ort_stt - self.ort_tgt)).unit()
                    )
            else:
                self.des_ang_vel_c = Vector(0, 0, 0)
        else:
            pass

