from matplotlib.widgets import TextBox
from mpl_toolkits.mplot3d import Axes3D
import numpy as np
import matplotlib.pyplot as plt
import itertools
import seaborn as sns


sns.set(style='darkgrid')


def init_field():
    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_xticks(np.arange(1, 5, 1))
    ax.set_yticks(np.arange(1, 5, 1))
    ax.set_zticks(np.arange(1, 5, 1))

    ax.set_xlabel('x axis', fontsize=10, rotation=1)
    ax.set_ylabel('y axis', fontsize=10, rotation=1)
    ax.set_zlabel('z axis', fontsize=10, rotation=1)

    for x in range(1, 5):
        for y in range(1, 5):
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, 4, 100), ys=np.linspace(y, y, 100), c="grey")

    # i dont know how make it
    ax.set_title(f"Tic Tac Toe 3d")
    # ax.set_label(f"Tic Tac Toe 3d")
    ax.legend()

    # WA for good scaling
    ax.scatter3D(0, 0, 1, s=1, c="w")
    ax.scatter3D(5, 5, 4, s=1, c="w")
    fig.show()

    return fig, ax


def input_coords(i, stack: dict, ax, color):
    try:
        # TODO: [06.10.2021 by Lev]
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
            or any(np.array(coords) > 4) \
            or len(coords) != 3:
        print('this turn is impossible\n')
        coords = input_coords(i, stack, ax, color)

    # stack[color].append(coords)

    return coords


def render_turn(i, ax, fig, turn, color):
    ax.scatter(*turn, s=2000, c=color, marker='h', linewidths=2)
    fig.show()
