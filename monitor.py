# debugging console for monitoring ship conditions.
# perhaps could be adapted for other use at later date.
from gui import window, mainloop
from utils import get_terminal_size_win, SI
from math import pi
from materials import Material, Mixture
from vector import Vector


def watch(world):
    size = get_terminal_size_win()
    if size is None:
        w, h = 100, 50
    else:
        w, h = size
        h -= 2

    monitor = window("", w, h)
    ls_of_ships = [state.ship for state in world.states]
    ship_name = [i for i in range(len(ls_of_ships))]

    def runturn(n):
        world.runturn(n)

    sd = monitor.addelement("lu", w=0.15, h=0.75, t="ship")
    ss = monitor.addelement("lu", w=0.15, h=0.15, type="menu", t="ships")
    ml = monitor.addelement("lu", w=0.25, h=0.20, type="menu", t="modules")
    clss = monitor.addelement("lu", w=0.25, h=0.20, type="menu", t="cluster")
    info = monitor.addelement("lu", w=0.25, h=0.60, t="info")
    run = monitor.addelement("lu", w=0.15, h=0.1, type="menu", t="runturn")
    ss.menu("ship:", ship_name)
    run.menu("run:", ["1", "5"], triggers=[runturn, runturn],trigargs = [1,5], mode="trig")
    run.bind("q", "a", "s")

    def loop_function():
        ship = ls_of_ships[ss.getval()]
        sd.graph(ship.diagram())

        mod_names = []
        for pos in ship.module:
            if isinstance(pos, list):
                posname = "{}x {}".format(len(pos), pos[0].name)
            else:
                posname = pos.name
            mod_names.append(posname)

        ml.menu("pos:", mod_names)

        pos = ship.module[ml.getval()]
        if isinstance(pos, list):
            cluster = pos
        else:
            cluster = [pos]

        cluster_name = []
        for m in cluster:
            if hasattr(m, "ort"):
                r, inc, az = m.ort.cart_to_spher().getval()
                cluster_name.append(
                    str(
                        "i {:> 3} az {:> 3}".format(
                            int(inc / pi * 180), int(az / pi * 180)
                        )
                    )
                )
            else:
                x, y, z = m.pos.getval()
                cluster_name.append(
                    "x {:> 3.1f} y {:> 3.1f} z {:> 3.1f}".format(x, y, z)
                )

        clss.menu("module:", cluster_name)

        mod = cluster[clss.getval()]

        graph = ""
        for x, y in mod.__dict__.items():
            try:
                yfloat = float(y)
                ysi, sifx = SI(yfloat)
                ystr = "{:.3f}{}".format(ysi, sifx)
            except ValueError:
                ystr = str(y)
            except TypeError:
                ystr = str(y)
            if isinstance(y, Material) or isinstance(y, Mixture):
                ystr = str(y.name)
            elif isinstance(y, Vector):
                o, p, q = y.getval()
                ystr = str("({:.1f} , {:.1f} , {:.1f})".format(o, p, q))

            graph += str(
                "{:^{w1}},{:^{w2}}\n".format(
                    str(x), ystr, w1=int(0.25 * w / 3), w2=int(0.25 * w * 2 / 3)
                )
            )
        info.graph(graph)

    mainloop(monitor, loop_function)
