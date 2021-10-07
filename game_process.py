import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from constants import Configs, DIMENSION
from funcs import init_field, input_coords, render_turn, gravity_correction, win_check, line_render


Configs.GRAVITY = True
Configs.SHAPE = 4  # must be less then 10 (WA)
Configs.stack = {'blue': [], "green": []}  # set color and name for every player, used by matplotlib
Configs.debug_mod = False  # random turns by pc without players decisions - input()


if __name__ == "__main__":
    fig, ax = init_field()
    stack = Configs.stack

    for i in range(Configs.SHAPE ** DIMENSION):
        color = list(stack.keys())[0] if i % 2 else list(stack.keys())[1]

        turn = input_coords(i=i, stack=stack, ax=ax, color=color)
        if not turn: break

        turn = gravity_correction(coords=turn, stack=stack)
        stack[color].append(turn)

        render_turn(ax=ax, fig=fig, turn=turn, color=color)

        is_win = win_check(stack=stack, coords=turn, color=color)
        if is_win:
            print(f"{color} player win")
            line_render(line_points=is_win, color=color)
            break

    input('end\n')
