from os import system
from time import sleep
from msvcrt import getch

# reverse operations of string.splitline()
def combinelines(list_of_string, eol="\n"):
    len_org = len(list_of_string[0])
    result = ""
    for i in list_of_string:
        result += i[0:len_org] + eol
    return result


# window class. meant to handle general calls.
class window(object):
    # default window:80*10, no title.
    def __init__(self, title="", width=80, height=10):
        self.title = title
        self.width = width
        self.height = height
        self.elements = []
        self.occupancy = [[0 for i in range(width)] for i in range(height)]
        self.content = str(" " * self.width + "\n") * self.height

    # checking for occupancy.
    def chkokpc(self, row, col, h, w):
        chopped_row_okpc = self.occupancy[row : row + h]
        chopped_okpc = [row[col : col + w] for row in chopped_row_okpc]
        flat_okpc = []
        for o in chopped_okpc:
            flat_okpc.extend(o)
        if all(x == 0 for x in flat_okpc):
            return False
        else:
            return True

    def setokpc(self, row, col, h, w):
        for x in range(row, row + h):
            for y in range(col, col + w):
                self.occupancy[x][y] = 1

    # behavior: if no height passed, h = height
    #           if no width passed, w = full width
    def addelement(self, align, h=None, w=None, b=True, t="", type="default", mk="box"):
        if h is None:
            h = self.height
        elif h < 1:
            h = int(self.height * h)
        if w is None:
            w = self.width
        elif w < 1:
            w = int(self.width * w)

        # choose the appropriate place for placing the starting point (m,n)
        def find_starting_point():
            if "u" in align:
                vert_start = 0
                vert_end = self.height - h + 1
                vert_step = 1
            elif "d" in align:
                vert_start = self.height - h
                vert_end = -1
                vert_step = -1
            if "l" in align:
                horz_start = 0
                horz_end = self.width - w + 1
                horz_step = 1
            elif "r" in align:
                horz_start = self.width - w
                horz_end = -1
                horz_step = -1

            for m in range(vert_start, vert_end, vert_step):
                for n in range(horz_start, horz_end, horz_step):
                    if self.chkokpc(m, n, h, w) is False:
                        self.setokpc(m, n, h, w)
                        return m, n

        m, n = find_starting_point()
        args = (h, w, (m, n), b, "(" + str(len(self.elements)) + ")" + t, mk)
        if type == "default":
            new_element = element(*args)
        elif type == "option":
            new_element = options(*args)
        elif type == "value":
            new_element = val(*args)
        self.elements.append(new_element)

        return new_element

    def render(self):
        screen = self.content.splitlines()
        deflen = len(screen[0])
        for e in self.elements:
            m, n = e.lu
            i = m
            for line in e.content.splitlines():
                screen[i] = screen[i][:n] + line + screen[i][n + len(line) :]
                screen[i] = screen[i][:deflen]
                i += 1

        self.content = combinelines(screen)

        print(self.content)


# element class for handling positions, and pre-defined buubbles,etc
class element(object):
    # default element: a text window.
    # lu: the position of element's upper left corner.
    def __init__(self, h, w, lu, border=True, title="", mk="box"):
        self.h = h
        self.w = w
        self.lu = lu
        self.content = str(" " * w + "\n") * h
        self.title = title
        self.b = border
        self.mk = mk
        if self.b:
            self.border(self.mk)

    # make border. marker dictionary for horizontal border, vertical border and vertex
    # batch editing is more efficient than using addr.
    # can accept a string, or a dictionary describing the border used.
    def border(self, marker="box"):
        empty_border = {"hb": " ", "vb": " ", "vtx": " "}
        boxart = {"hb": "-", "vb": "|", "vtx": "+"}
        if marker == "empty":
            markers = empty_border
        elif marker == "box":
            markers = boxart
        else:
            markers = marker
        lines = self.content.splitlines()
        i = 0
        # modify line by line to comply.
        for line in lines:
            if i == 0:
                lines[i] = (
                    markers["vtx"]
                    + self.title
                    + markers["hb"] * (self.w - 2 - len(self.title))
                    + markers["vtx"]
                )
            elif i == len(lines) - 1:
                lines[i] = (
                    markers["vtx"] + markers["hb"] * (self.w - 2) + markers["vtx"]
                )
            else:
                lines[i] = markers["vb"] + lines[i][1 : len(line) - 1] + markers["vb"]
            i += 1

        self.content = combinelines(lines)

    # method for direct addressing of value. use as sparingly as possible.
    def addr(self, row, col, val):
        assert isinstance(row, int)
        assert isinstance(col, int)
        assert isinstance(val, str)
        lines = self.content.splitlines()
        i = 0
        for line in lines:
            if i == row:
                lines[i] = line[:col] + val + line[col + len(val) :]
            i += 1

        self.content = combinelines(lines)

    # accepts as input a text string, automatically arrange.
    # respects border. should not contain contorl characters
    def text(self, texts):
        assert isinstance(texts, str)
        # text width, excluding the borders.
        tw = self.w - 2

        lines = self.content.splitlines()

        i = 0
        e = 0
        for line in lines:
            if (i != 0 and i != len(lines) - 1) or self.b is False:
                texthere = texts[tw * e : tw * (e + 1)]
                lines[i] = (
                    lines[i][0]
                    + texts[tw * e : tw * (e + 1)]
                    + lines[i][len(texthere) + 1 :]
                )
                e += 1
            i += 1

        self.content = combinelines(lines)

    # graphing mode, respecting the line change characters of give string.
    def graph(self, graph):
        assert isinstance(graph, str)
        # text width, excluding the borders.
        tw = self.w - 2

        lines = self.content.splitlines()
        log = graph.splitlines()

        i = 0
        e = 0
        for line in lines:
            if (i != 0 and i != len(lines) - 1) or self.b is False:
                texthere = log[e][:tw]
                lines[i] = lines[i][0] + texthere + lines[i][len(texthere) + 1 :]
                e += 1
            if e == len(log):
                break
            i += 1

        self.content = combinelines(lines)

    def clear(self):
        h, w = self.h, self.w
        self.content = str(" " * w + "\n") * h
        if self.b:
            self.border(self.mk)


# subclass of element, of interactive display portals.
class options(element):
    def __init__(self, *args):
        super().__init__(*args)
        self.choice = None
        self.prompt = None

    def binary(self, pt, choice, default=False):
        if self.choice is None:
            self.choice = default
        else:
            self.choice = choice
        self.prompt = pt
        h, w = self.h, self.w
        question_line = (
            "{:_<{width}}{}".format(
                self.prompt, str(self.choice), width=w - 3 - len(str(self.choice)),
            )
        )
        self.graph(question_line)

    def interact(self):
        self.choice = not self.choice
        self.binary(self.prompt, self.choice)

    def getval(self):
        return self.choice

    def setval(self, val):
        self.choice = val


class val(element):
    def __init__(self, *args):
        super().__init__(*args)
        self.prompt = None
        self.val = None

    def value(self, pt, val, default=0):
        if self.val is None:
            self.val = default
        else:
            self.val = val
        self.prompt = pt
        h, w = self.h, self.w
        value_line = (
            "{:_<{width}}{}".format(
                self.prompt, self.val, width=w - 3 - len(str(self.val))
            )
        )
        self.graph(value_line)

    def interact(self):
        while True:
            ip = input("value desired>")
            try:
                self.val = float(ip)
                break
            except ValueError:
                print("value not recognized. float desired.")
        self.value(self.prompt, self.val)

    def getval(self):
        return self.val

    def setval(self, val):
        self.val = val


def mainloop(window, loopfunction):
    while True:
        system("cls")
        loopfunction()
        window.render()
        ind = getch()
        try:
            ind = int(ind)
            window.elements[ind].interact()
        except ValueError:
            print("{} not understood.Integer please".format(ind))
        except AttributeError:
            print("element {} not interactable".format(ind))
        except IndexError:
            print("index {} out of range:0-{}".format(ind, len(window.elements) - 1))
        sleep(0.1)


if __name__ == "__main__":
    lorem = "Demo of the interactive command-line interface for the project. Use the number preceeding the title to address individual fields. Some fields might prompt you for some input. This simple demo let you control a 3d-cartesian graphing plot."

    from utils import asciiplt
    from vector import Vector

    a = window(width=100, height=20)
    e = a.addelement("lu", w=0.5, t="graph")
    f = a.addelement("ru", h=3, w=50, t="options", type="option")
    g = a.addelement("ru", h=17, w=30, t="help")

    h = a.addelement("ru", h=3, w=20, t="set x", type="value", b=True, mk="empty")
    i = a.addelement("ru", h=3, w=20, t="set y", type="value", b=True, mk="empty")
    j = a.addelement("ru", h=3, w=20, t="set z", type="value", b=True, mk="empty")
    g.text(lorem)
    f.binary("should graph", True)
    x, y, z = 0, 0, 0
    h.value("x", x, 0)
    i.value("y", y, 0)
    j.value("z", z, 0)

    def loopfunction():
        x, y, z = h.getval(), i.getval(), j.getval()
        if f.getval():
            e.graph(asciiplt(Vector(x, y, z), horz=e.w - 2, vert=e.h - 2))
        else:
            e.clear()

    mainloop(a, loopfunction)
