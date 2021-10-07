import time
from matplotlib.widgets import TextBox
import sympy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import seaborn as sns

from constants import Configs, DIMENSION

sns.set(style='darkgrid')


def init_field():
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_xticks(np.arange(1, Configs.SHAPE + 1, 1))
    ax.set_yticks(np.arange(1, Configs.SHAPE + 1, 1))
    ax.set_zticks(np.arange(1, Configs.SHAPE + 1, 1))

    ax.set_xlabel('x axis', fontsize=10, rotation=1)
    ax.set_ylabel('y axis', fontsize=10, rotation=1)
    ax.set_zlabel('z axis', fontsize=10, rotation=1)

    for x in range(1, Configs.SHAPE + 1):
        for y in range(1, Configs.SHAPE + 1):
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, Configs.SHAPE, 100), ys=np.linspace(y, y, 100),
                    c="grey", linewidth=5, alpha=0.8)

    ax.set_title(f"Tic Tac Toe 3d") if Configs.GRAVITY else ax.set_title(f"Levitating Tic Tac Toe 3d")
    # ax.legend()

    # WA for good scaling
    ax.scatter3D(0, 0, 1, s=1, c="w")
    ax.scatter3D(Configs.SHAPE + 1, Configs.SHAPE + 1, Configs.SHAPE, s=1, c="w")
    fig.show()

    return fig, ax


def input_coords(i, stack: dict, ax, color):
    if Configs.debug_mod:
        coords = list(np.random.randint(1, Configs.SHAPE + 1, DIMENSION))
        if coords in itertools.chain(*stack.values()):
            return input_coords(i, stack, ax, color)
        else:
            input()
            return coords

    try:
        # TODO: [06.10.2021 by Lev] replace terminal input into matplotlib box
        # text_box = TextBox(ax, f"{color} player {i % 2 + 1}\nprint your coords: ")
        # print(text_box.text)
        # input_data = text_box.on_submit(print)

        input_data = input(f"{color} player {i % 2 + 1}\nprint your coords: ")
        coords = [int(i) for i in input_data]
        print()
    except:  # TODO: [06.10.2021 by Lev] set right exception
        print("input is wrong\n")
        coords = input_coords(i, stack, ax, color)

    # WA for exit
    if len(coords) == 1:
        return

    if (coords in [*itertools.chain(*stack.values())]) \
            or any(np.array(coords) < 1) \
            or any(np.array(coords) > Configs.SHAPE) \
            or len(coords) != DIMENSION:
        print('this turn is impossible\n')
        coords = input_coords(i, stack, ax, color)

    return coords


def render_turn(ax, fig, turn, color):
    ax.scatter(*turn, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.5, edgecolors='black')
    fig.show()


def gravity_correction(coords, stack):
    line_stack = [*itertools.chain(*stack.values())]

    if Configs.GRAVITY:
        if coords[-1] == 1:
            return coords
        else:
            temp = coords.copy()
            temp[-1] = temp[-1] - 1
            if temp in line_stack:
                return coords
            else:
                return gravity_correction(temp, stack)
    else:
        return coords


def win_check(stack, coords, color):
    for line in itertools.combinations(stack[color], Configs.SHAPE):
        if (coords in line) and sympy.Point.is_collinear(*line):
            return line
    return False


def line_render(line_points, color):
    fig, ax = init_field()

    for i in line_points:
        ax.scatter(*i, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.5, edgecolors='black')
    fig.show()
