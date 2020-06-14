from vector import Vector
from matrix import Matrix
from math import sin, cos, pi, sqrt, log10
import struct


def clamp(val, minima, maxima):
    assert minima < maxima
    return max(min(val, maxima), minima)


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

    R = rz * ry * rx
    result = R * vec
    return result


def euler_rot(vector, euler_vector):
    thetax, thetay, thetaz = euler_vector.getval()
    result_matrix = orth_rot(vector, thetax, thetay, thetaz)
    x, y, z = result_matrix.mat[0][0], result_matrix.mat[1][0], result_matrix.mat[2][0]
    return Vector(x, y, z)


def asciiplt(vector, return_string=True, horz=30, vert=9):

    xtra = 0
    ytra = 0
    # extra padding.

    z_length = int(vert * 2 / 3)
    center_horz_pos = int(horz * 1 / 3)

    x, y, z = vector.getval()
    length = vector.norm()
    if length == 0:
        scale = 1
    else:
        scale = sqrt(vert ** 2 + (horz / 2) ** 2) / length / 3

    x, y, z = x * scale, y * scale, z * scale

    x_axis_syb = "/"
    x_neg_axis_syb = "."
    y_axis_syb = "\u2310"
    y_neg_axis_syb = "."
    z_axis_syb = "|"
    z_neg_axis_syb = "."

    drawing = []
    for i in range(0, z_length):
        if i == z_length - 1:
            line = (
                y_neg_axis_syb * center_horz_pos
                + y_axis_syb * (horz - center_horz_pos - 1)
                + "Y"
            )
        elif i == 0:
            line = " " * (center_horz_pos - 1) + "Z" + z_axis_syb
            line += " " * (z_length - i - 2) + x_neg_axis_syb
        else:
            line = " " * center_horz_pos + z_axis_syb
            line += " " * (z_length - i - 2) + x_neg_axis_syb
        # pad out xtra spaces to the right..
        drawing.append("{0:<{1}}".format(line, horz + xtra))
    for i in range(0, vert - z_length):
        if i == vert - z_length - 1:
            line = (
                " " * (center_horz_pos - i - 2)
                + "X"
                + x_axis_syb
                + " " * i
                + z_neg_axis_syb
            )
        else:
            line = (
                " " * (center_horz_pos - i - 1) + x_axis_syb + " " * i + z_neg_axis_syb
            )
        drawing.append("{0:<{1}}".format(line, horz + xtra))

    # pad out xtra lines down.
    for i in range(0, ytra):
        drawing.append("{0:^{1}}".format(" ", horz + xtra))

    def mark_pos(x, y, z, val):
        # map x,y,z to the axis.
        y_ascii = z_length - int(z) + int(x * sqrt(2) / 2) - 1
        x_ascii = center_horz_pos + int(y * 2) - int(x * sqrt(2) / 2)

        # limit the x axis to be greater than 0
        x_ascii = int(clamp(x_ascii, 0, horz - 1))
        y_ascii = int(clamp(y_ascii, 0, vert - 1))

        line = drawing[y_ascii]

        if len(line) < x_ascii:
            diff = x_ascii - len(line)
            drawing[y_ascii] = line + " " * diff + val
        else:
            drawing[y_ascii] = (
                drawing[y_ascii][:x_ascii] + val + drawing[y_ascii][x_ascii + 1 :]
            )

        return x_ascii, y_ascii

    def edit_pos(x, y, val):
        x = clamp(x, 0, horz - 1)
        y = clamp(y, 0, vert - 1)
        line = drawing[y]
        if len(line) < x:
            diff = x - len(line)
            drawing[y] = line + " " * diff + val
        else:
            drawing[y] = drawing[y][:x] + val + drawing[y][(x + len(val)) :]

    # draw a line.
    def draw_line(vec0, vec1):
        x0, y0, z0 = vec0.getval()
        x1, y1, z1 = vec1.getval()

        delta = vec1 - vec0

        # breakdown of difference vector.
        dx, dy, dz = delta.getval()
        sigma = delta.norm()
        # get the step size!
        if sigma == 0:
            x_r, y_r, z_r = 0, 0, 0
        else:
            x_r, y_r, z_r = dx / sigma, dy / sigma, dz / sigma

        # we should fill one point every distance = 1 (or distance = scale as displayed)
        # so as to be as dense as possible.

        if abs(dz) == max(abs(n) for n in delta.getval()):
            line = ":"
        else:
            line = "."

        for i in range(1, int(sigma)):
            xi = x0 + x_r * i
            yi = y0 + y_r * i
            zi = z0 + z_r * i
            mark_pos(xi, yi, zi, line)

    # horizontal plane indicator
    mark_pos(x, y, 0, "*")
    indicator = Vector(x, y, 0)
    # places the marker
    xo, yo = mark_pos(x, y, z, "o")
    draw_line(vector * scale, indicator)

    capx = str("x {:>5.1e}".format(x / scale))
    capy = str("y {:>5.1e}".format(y / scale))
    capz = str("z {:>5.1e}".format(z / scale))

    # make sure the caption does not exceed the drawing space.
    start = clamp(yo - 1, 0, vert - 3)
    edit_pos(xo + 2, start, capx)
    edit_pos(xo + 2, start + 1, capy)
    edit_pos(xo + 2, start + 2, capz)

    line_str = ""
    for line in drawing:
        line_str += line + "\n"

    # return the string version
    if return_string:
        return line_str
    # return the list (line by line) version
    else:
        return drawing


# reverse operations of string.splitline()
def combinelines(list_of_string, eol="\n"):
    len_org = len(list_of_string[0])
    result = ""
    for i in list_of_string:
        result += i[0:len_org] + eol
    return result


def solve_quadra(a, b, c):
    if a == 0:
        return -c / b
    delta = b ** 2 - 4 * a * c
    if delta > 0:
        x1 = (-b + sqrt(delta)) / (2 * a)
        x2 = (-b - sqrt(delta)) / (2 * a)
        return x1, x2
    elif delta == 0:
        return -b / (2 * a)
    else:
        return None


def get_terminal_size_win():
    try:
        from ctypes import windll, create_string_buffer

        # stdin handle is -10
        # stdout handle is -11
        # stderr handle is -12
        h = windll.kernel32.GetStdHandle(-12)
        csbi = create_string_buffer(22)
        res = windll.kernel32.GetConsoleScreenBufferInfo(h, csbi)
        if res:
            (
                bufx,
                bufy,
                curx,
                cury,
                wattr,
                left,
                top,
                right,
                bottom,
                maxx,
                maxy,
            ) = struct.unpack("hhhhHhhhhhh", csbi.raw)
            sizex = right - left + 1
            sizey = bottom - top + 1
            return sizex, sizey
    except Exception:
        pass


def all_subclasses(cls):

    if cls == type:
        raise ValueError("Invalid class - 'type' is not a class")

    subclasses = set()

    stack = []
    try:
        stack.extend(cls.__subclasses__())
    except (TypeError, AttributeError) as ex:
        raise ValueError("Invalid class" + repr(cls)) from ex

    while stack:
        sub = stack.pop()
        subclasses.add(sub)
        try:
            stack.extend(s for s in sub.__subclasses__() if s not in subclasses)
        except (TypeError, AttributeError):
            continue

    return list(subclasses)


if __name__ == "__main__":
    """
    vector = Vector(-2, 3, -40)
    euler_vec = Vector(0, pi / 2, pi / 2)
    result = orth_rot(vector, pi / 2, 0, pi / 2)
    result.print()
    result2 = euler_rot(vector, euler_vec)
    result2.print()
    vector.print()
    print(asciiplt(vector))
    """
    print(get_terminal_size_win())
    print(SI(250))
    print(all_subclasses(object))
