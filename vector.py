# vector library.
from math import sqrt, sin, cos, acos, atan
from math import pi


class Vector:
    def setval(self, x, y, z):
        self.x, self.y, self.z = x, y, z

    def __init__(self, x, y, z):
        self.setval(x, y, z)

    def getval(self):
        return self.x, self.y, self.z

    def norm(self):
        return sqrt(self.x ** 2 + self.y ** 2 + self.z ** 2)

    def unit(self):
        norm = self.norm()
        unit_vec = self / norm
        return unit_vec

    def __add__(self, o):
        x0, y0, z0 = self.getval()
        x1, y1, z1 = o.getval()
        ans = Vector(x0 + x1, y0 + y1, z0 + z1)
        return ans

    def __mul__(self, num):
        x, y, z = self.getval()
        return Vector(x * num, y * num, z * num)

    def __rmul__(self, num):
        return self.__mul__(num)

    def __truediv__(self, m):
        x, y, z = self.getval()
        ans = Vector(x / m, y / m, z / m)
        return ans

    def __eq__(self, o):
        if self.getval() == o.getval():
            return True
        else:
            return False

    def spher_to_cart(self):
        # r: radius, theta:inclination phi:azimuth
        r, theta, phi = self.getval()
        x = r * sin(theta) * cos(phi)
        y = r * sin(theta) * sin(phi)
        z = r * cos(theta)

        return Vector(x, y, z)

    def cart_to_spher(self):
        # r: radius, theta:inclination phi:azimuth
        x, y, z = self.getval()
        r = sqrt(x ** 2 + y ** 2 + z ** 2)
        phi = atan(y / x)
        theta = acos(z / r)

        return Vector(r, theta, phi)

    def print(self):
        print(self.x, self.y, self.z)


def dot(a, b):
    x0, y0, z0 = a.getval()
    x1, y1, z1 = b.getval()

    return x0 * x1 + y0 * y1 + z0 * z1


def cross(a, b):
    a1, a2, a3 = a.getval()
    b1, b2, b3 = b.getval()
    x = a2 * b3 - a3 * b2
    y = a3 * b1 - a1 * b3
    z = a1 * b2 - a2 * b1
    return Vector(x, y, z)


def theta(a, b):
    return acos(dot(a, b) / (a.norm() * b.norm()))


if __name__ == "__main__":
    a = Vector(2, 3, 4)
    b = Vector(4, 5, 6)
    print((a + b).unit().norm())
    print(a == b)
    print(a == a)
