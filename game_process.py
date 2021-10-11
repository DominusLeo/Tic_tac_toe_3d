import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from tqdm import trange

from constants import Configs, DIMENSION, dict_of_shapes_wins
from funcs import init_field, input_coords, render_turn, gravity_correction, win_check, line_render, win_check_from_db

Configs.debug_mod = False  # random turns by pc without players decisions - input()

Configs.GRAVITY = True  # auto turns by PC for debug
Configs.SHAPE = 4  # must be less then 10 (WA)
Configs.stack = {'blue': [], "green": []}  # set color and name for every player, used by matplotlib
Configs.play_vs_bot = 2  # 0, 1, 2 - the presence and number of the bot's move


if __name__ == "__main__":
    fig, ax = init_field()
    stack = Configs.stack

    for i in trange(Configs.SHAPE ** DIMENSION):
        color = list(stack.keys())[i % 2]

        turn = input_coords(i=i, stack=stack, ax=ax, color=color)
        if not turn: break

        turn = gravity_correction(coords=turn, stack=stack)
        stack[color].append(turn)

        render_turn(ax=ax, fig=fig, turn=turn, color=color)

        is_win = win_check_from_db(stack=stack, coords=turn, color=color)
        # is_win = False
        if is_win:
            print(f"{color} player win")
            line_render(stack_render={color: is_win})
            break

    input('end\n')
