# debugging console for monitoring ship conditions.
# perhaps could be adapted for other use at later date.
from gui import window, mainloop
from utils import get_terminal_size_win


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

    sd = monitor.addelement("lu", w=0.25, h=0.75, t="ship")
    ss = monitor.addelement("lu", w=0.25, h=0.25, type="menu")

    ss.menu("ship:", ship_name)

    def loop_function():
        ship = ls_of_ships[ss.getval()]
        sd.graph(ship.diagram())

    mainloop(monitor, loop_function)
