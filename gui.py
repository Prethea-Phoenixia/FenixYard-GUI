from matrix import Matrix


# psuedo_gui class.
class pGUI(object):
    pass


# window class. meant to handle general calls.
class window(pGUI):
    # default window:80*10, no title.
    def __init__(self, title=" ", width=80, height=10):
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
        for i in range(0, h):
            flat_okpc.extend(chopped_okpc[i])
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
    def add_element(self, align, h=None, w=None):
        if h is None:
            h = self.height
        if w is None:
            w = self.width

        # choose the appropriate place for placing the starting point (m,n)
        def find_starting_point():
            if "u" in align:
                vert_start = 0
                vert_end = self.height - h
                vert_step = 1
            elif "d" in align:
                vert_start = self.height - h
                vert_end = 0
                vert_step = -1
            if "l" in align:
                horz_start = 0
                horz_end = self.width - w
                horz_step = 1
            elif "r" in align:
                horz_start = self.width - w
                horz_end = 0
                horz_step = -1

            for m in range(vert_start, vert_end, vert_step):
                for n in range(horz_start, horz_end, horz_step):
                    if self.chkokpc(m, n, h, w) is False:
                        self.setokpc(m, n, h, w)
                        return m, n

        m, n = find_starting_point()

        new_element = element(h, w, (m, n))

        self.elements.append(new_element)

        return new_element

    def render(self):
        print(self.content)


# element class for handling positions, and pre-defined buubbles,etc
class element(window):
    # default element: a text window.
    # lu: the position of element's upper left corner.
    def __init__(self, h, w, lu):
        self.h = h
        self.w = w
        self.lu = lu
        self.content = str(" " * w + "\n") * h

    # make border. marker dictionary for horizontal border, vertical border and vertex
    # batch editing is more efficient than using addr.
    def border(self, markers={"hb": "-", "vb": "|", "vtx": "+"}):
        lines = self.content.splitlines()
        i = 0
        # modify line by line to comply.
        for line in lines:
            if i == 0 or i == len(lines) - 1:
                lines[i] = (
                    markers["vtx"] + markers["hb"] * (self.w - 2) + markers["vtx"]
                )
            else:
                lines[i] = markers["vb"] + lines[i][1 : len(lines) - 1] + markers["vb"]
            i += 1

        self.content = ""
        i = 0
        for line in lines:
            self.content += lines[i] + "\n"
            i += 1

    # method for direct addressing of value. use as sparingly as possible.
    def addr(self, row, col, val):
        lines = self.content.splitlines()
        dft_w = len(lines[0])
        i = 0
        for line in lines:
            if i == row:
                lines[i] = line[:col] + val + line[col + len(val) :]
                lines[i] = lines[i][:dft_w]
            i += 1

        self.content = ""
        i = 0
        for line in lines:
            self.content += lines[i] + "\n"
            i += 1


if __name__ == "__main__":
    a = window()
    e = a.add_element("ul", 5, 5)
    e.border()
    e.addr(2, 2, "test")
    print(e.content)
    a.render()
