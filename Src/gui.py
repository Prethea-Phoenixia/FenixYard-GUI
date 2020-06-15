from os import system
from time import sleep
from msvcrt import getch
from utils import combinelines, clamp


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

    def setokpc(self, row, col, h, w, val=1):
        for x in range(row, row + h):
            for y in range(col, col + w):
                self.occupancy[x][y] = val

    def addelement(self, align, h=None, w=None, b=True, t="", type="default", mk="box"):
        """behavior: if no height passed, h = height if no width passed, w = full width
        mk accepts "empty" or "box" or a dictionary with keys "vtx","vb" and "hb", type accepts 
        "option","button","menu",etc., as inputs"""
        if h is None:
            h = self.height
        elif h < 1:
            h = int(round(self.height * h, 0))
        if w is None:
            w = self.width
        elif w < 1:
            w = int(round(self.width * w, 0))

        # choose the appropriate place for placing the starting point (m,n)
        def find_starting_point(w, h):
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

            if align[0] == "u" or align[0] == "d":
                for m in range(vert_start, vert_end, vert_step):
                    for n in range(horz_start, horz_end, horz_step):
                        if self.chkokpc(m, n, h, w) is False:
                            self.setokpc(m, n, h, w)
                            return m, n

            else:
                for n in range(horz_start, horz_end, horz_step):
                    for m in range(vert_start, vert_end, vert_step):
                        if self.chkokpc(m, n, h, w) is False:
                            self.setokpc(m, n, h, w)
                            return m, n

        """

        def spiral_descend(w, h):
            try:
                m, n = find_starting_point(w, h)
                return m, n
            except TypeError:
                try:
                    w -= 1
                    m, n = find_starting_point(w, h)
                    return m, n
                except TypeError:
                    try:
                        w += 1
                        h -= 1
                        m, n = find_starting_point(w, h)
                        return m, n
                    except TypeError:
                        m, n = spiral_descend(w - 1, h - 1)

        """

        try:
            # m, n = spiral_descend(w, h)
            m, n = find_starting_point(w, h)
        except TypeError:
            raise Exception("unable to assign position")

        args = (h, w, (m, n), b, "(" + str(len(self.elements)) + ")" + t, mk)
        if type == "default":
            new_element = element(*args)
        elif type == "option":
            new_element = options(*args)
        elif type == "value":
            new_element = val(*args)
        elif type == "menu":
            new_element = menu(*args)
        elif type == "button":
            new_element = button(*args)
        else:
            raise NotImplementedError
        self.elements.append(new_element)

        return new_element

    def delete_element(self, *args):
        for element in args:
            self.setokpc(element.lu[0], element.lu[1], element.h, element.w, 0)
            self.elements.pop(self.elements.index(element))

    def render(self):
        self.content = str(" " * self.width + "\n") * self.height
        screen = self.content.splitlines()
        deflen = len(screen[0])
        for e in self.elements:
            m, n = e.lu
            i = m
            for line in e.content.splitlines():
                screen[i] = screen[i][:n] + line + screen[i][n + len(line) :]
                screen[i] = screen[i][:deflen]
                i += 1

        print(combinelines(screen))


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
        self.kb = []

    def bind(self, *args):
        for kb in args:
            self.kb.append(kb)

        kbs = ""
        for kb in args:
            kbs += str(kb) + ","
        self.title = "({}/".format(kbs[:-1]) + self.title[1:]
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
        self.clear()
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
        self.clear()
        if self.choice is None:
            self.choice = default
        else:
            self.choice = choice
        self.prompt = pt
        h, w = self.h, self.w
        question_line = "{:_<{width}}{}".format(
            self.prompt, str(self.choice), width=w - 3 - len(str(self.choice)),
        )
        self.graph(question_line)

    # dummy variable kp for compatiability reasons
    def interact(self, kp=None):
        self.choice = not self.choice
        self.update()

    def update(self):
        self.binary(self.prompt, self.choice)

    def getval(self):
        return self.choice

    def setval(self, val):
        self.choice = val
        self.update()


class val(element):
    def __init__(self, *args):
        super().__init__(*args)
        self.prompt = None
        self.val = None
        self.reversed = False

    def value(self, pt, val, default=0, reversed=False):
        self.clear()
        if self.val is None:
            self.val = default
        else:
            self.val = val
        self.prompt = pt
        h, w = self.h, self.w

        self.reversed = reversed

        if reversed is False:
            value_line = "{:_<{width}}{}".format(
                self.prompt, self.val, width=max(w - 2 - len(str(self.val)), 0)
            )
        else:
            value_line = "{:>{width}}{}".format(
                self.val, self.prompt, width=max(w - 2 - len(str(self.prompt)), 0),
            )
        self.graph(value_line)

    def update(self):
        self.value(self.prompt, self.val, reversed=self.reversed)

    def interact(self, kp=None):
        ip = input("value desired>")
        val_type = None
        try:
            float(self.val)
            val_type = "float"
        except ValueError:
            str(self.val)
            val_type = "string"

        try:
            new_val = float(ip)
            if val_type == "float":
                self.val = new_val
            else:
                print("type mismatch, wants string")
        except ValueError:
            try:
                new_val = str(ip)
                if val_type == "string":
                    self.val = new_val
                else:
                    print("type mismatch: wants float")
            except ValueError:
                print("value not recognized as flt/str.")
        self.update()

    def getval(self):
        return self.val

    def setval(self, val):
        self.val = val
        self.update()


class menu(element):
    def __init__(self, *args):
        super().__init__(*args)
        self.choices = []
        self.prompt = None
        self.selection = None
        self.scroll = None

        self.mode = None
        self.triggers = None
        self.triggered = None
        self.trigargs = None

    def menu(self, pt, choices, default=0, triggers=None, trigargs=None, mode="sel"):
        """sel:selection menu, default behavior
        togg: toggle menu, indicates currently "on"/"selected" state, separate action to confirm.
        (requires one more keybinding. up, down, selection/deselection) keeps state.
        trig: trigger menu, treats the menu as a series of buttons. (up,down,press)
        """
        self.prompt = pt
        self.choices = choices

        self.mode = mode
        self.triggers = triggers
        self.trigargs = trigargs

        self.clear()
        if self.selection is None:
            self.selection = default
        else:
            if self.selection > len(self.choices) - 1:
                self.selection = 0
                self.scroll = 0

        if self.scroll is None:
            self.scroll = 0

        h, w = self.h, self.w

        lines = ""
        if self.choices == []:
            ml = 0
        else:
            ml = max(len(str(choice)) for choice in self.choices)

        if self.mode == "togg":
            ml += 1

        for i in range(len(self.choices)):

            """ handling triggered mode"""
            if self.mode == "sel" or self.mode == "trig":
                choice = self.choices[i]
            elif self.mode == "togg":
                if i == self.triggered:
                    choice = "o" + self.choices[i]
                else:
                    choice = " " + self.choices[i]
            else:
                raise NotImplementedError

            if i != self.selection:
                line = "{:^{w1}}{:<{w2}}".format(
                    " ", choice, w1=max(w - 2 - ml, 1), w2=ml
                )
            else:
                line = "{:_<{w1}}{:<{w2}}".format(
                    self.prompt, choice, w1=max(w - 2 - ml, 1), w2=ml
                )
            lines += line + "\n"
        self.graph(lines[self.scroll * (self.w - 1) :])

    def interact(self, kp=None):
        def flip_up():
            if self.selection < len(self.choices) - 1:
                self.selection += 1
            else:
                self.selection = 0

            start = max(self.selection - (self.h - 2) + 1, 0)

            self.scroll = start

        def flip_down():
            self.selection -= 1
            if self.selection < 0:
                self.selection = len(self.choices) - 1

            self.scroll = min(self.selection, len(self.choices) - self.h + 2)

        if kp is None:
            flip_up()
        elif kp == self.kb[0]:
            flip_up()
        elif kp == self.kb[1]:
            flip_down()
        elif kp == self.kb[2]:
            if self.triggered is None or self.triggered != self.selection:
                self.triggered = self.selection
            else:
                self.triggered = None

        self.update()

    def update(self):
        def op():
            if self.triggered is not None and self.triggers is not None:
                if self.trigargs is None:
                    self.triggers[self.triggered]()
                else:
                    self.triggers[self.triggered](self.trigargs[self.triggered])

        if self.mode == "togg":
            op()
        elif self.mode == "trig":
            op()
            self.triggered = None

        self.menu(
            self.prompt,
            self.choices,
            triggers=self.triggers,
            mode=self.mode,
            trigargs=self.trigargs,
        )

    def getval(self):
        return self.selection

    def setval(self, val):
        self.selection = val
        self.update()

    def getrigg(self):
        return self.triggered

    def setrigg(self, val):
        self.triggered = val
        self.update()


class button(element):
    def __init__(self, *args):
        super().__init__(*args)
        self.prompt = None
        self.trigger = None

    def button(self, prompt, trigger):
        self.graph(prompt)
        self.trigger = trigger

    def interact(self, dummy=None):
        self.trigger()


def mainloop(window, loopfunction):
    while True:
        # OS specific, to be changed.
        system("cls")
        loopfunction()
        window.render()
        ind = getch()
        kbs = {}
        for element in window.elements:
            for kp in element.kb:
                kbs.update({kp: window.elements.index(element)})

        try:
            ind = int(ind)
            window.elements[ind].interact()
        except ValueError:
            try:
                if ind == chr(27).encode():
                    return None
                ind = ind.decode("utf8")
                if hasattr(window.elements[kbs[ind]], "interact"):
                    window.elements[kbs[ind]].interact(ind)
                else:
                    print("element {} is not interactable".format(ind))
            except UnicodeDecodeError:
                # catches the second return in case of a "/xe0" escape sequence.
                getch()
                print(
                    "special characters, for example arrow keys and function keys, cannot be used."
                )
            except KeyError:
                print('element with keybind "{}" not found in {}'.format(ind, kbs))

        except AttributeError:
            print("element {} not interactable".format(ind))
        except IndexError:
            print("index {} out of range:0-{}".format(ind, len(window.elements) - 1))

    return None


if __name__ == "__main__":
    lorem = "Demo of the interactive command-line interface for the project. Use the number preceeding the title to address individual fields. Some fields might prompt you for some input. This simple demo let you control a 3d-cartesian graphing plot."

    sandwich = ["bread", "butter", "beef", "bread"]

    from utils import asciiplt
    from vector import Vector
    from utils import get_terminal_size_win

    size = get_terminal_size_win()
    if size is None:
        w, h = 100, 50
    else:
        w, h = size
        h -= 2

    a = window(width=w, height=h)
    e = a.addelement("lu", w=0.5, t="graph")
    f = a.addelement("ru", h=3, w=0.5, t="options", type="option")
    f.bind(" ")
    g = a.addelement("ru", h=17, w=30, t="help")

    h = a.addelement("ru", h=3, w=20, t="set x", type="value", b=True, mk="empty")
    i = a.addelement("ru", h=3, w=20, t="set y", type="value", b=True, mk="empty")
    j = a.addelement("ru", h=3, w=20, t="set z", type="value", b=True, mk="empty")

    k = a.addelement("ru", h=0.1, w=0.2, t="testing menu", type="menu", b=True)
    k.bind("t", "e")

    g.text(lorem)
    f.binary("should graph", True)
    x, y, z = 0, 0, 0
    h.value("x", x, 0)
    h.bind("x")
    i.value("y", y, 0)
    i.bind("y")
    j.value("z", z, 0)
    j.bind("z")

    k.menu("sandwich", sandwich)

    def loopfunction():
        x, y, z = h.getval(), i.getval(), j.getval()
        if f.getval():
            e.graph(asciiplt(Vector(x, y, z), horz=e.w - 2, vert=e.h - 2))
        else:
            e.clear()

    mainloop(a, loopfunction)
