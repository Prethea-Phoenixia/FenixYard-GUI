from vector import Vector
from matrix import Matrix
from math import sin, cos, pi


def orth_rot(vector, thetax, thetay, thetaz):
    rx = Matrix(3, 3)
    ry = Matrix(3, 3)
    rz = Matrix(3, 3)

    x, y, z = vector.getval()
    vec = Matrix(3, 1)
    vec.mat = [[x], [y], [z]]

    rx.mat = [[1, 0, 0], [0, cos(thetax), -sin(thetax)], [0, sin(thetax), cos(thetax)]]
    ry.mat = [[cos(thetay), 0, sin(thetay)], [0, 1, 0], [-sin(thetay), 0, cos(thetay)]]
    rz.mat = [[cos(thetaz), -sin(thetaz), 0], [sin(thetaz), cos(thetaz), 0], [0, 0, 1]]

    R = rx * ry * rz
    result = R * vec
    return result


def euler_rot(vector, euler_vector):
    thetax, thetay, thetaz = euler_vector.getval()
    result_matrix = orth_rot(vector, thetax, thetay, thetaz)
    x, y, z = result_matrix.mat[0][0], result_matrix.mat[1][0], result_matrix.mat[2][0]
    return Vector(x, y, z)


if __name__ == "__main__":
    vector = Vector(0, 0, 1)
    euler_vec = Vector(0,pi/2,pi/2)
    result = orth_rot(vector, pi / 2, 0, pi / 2)
    result.print()
    result2 = euler_rot(vector,euler_vec)
    result2.print()