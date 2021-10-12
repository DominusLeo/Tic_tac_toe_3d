import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from tqdm import trange

from constants import Configs, DIMENSION, dict_of_shapes_wins
from funcs import init_field, input_coords, render_turn, gravity_correction, win_check, line_render, win_check_from_db

Configs.debug_mod = False  # random turns by pc without players decisions - input()

Configs.GRAVITY = True
Configs.SHAPE = 4  # must be in range(3, 10) (WA)
Configs.stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib
Configs.play_vs_bot = 2  # 0, 1, 2 - the presence and number of the bot's move


# win_stat = copy.deepcopy(Configs.stack)
# for trying in trange(15):
if __name__ == "__main__":
    fig, ax = init_field()
    stack = copy.deepcopy(Configs.stack)

    for i in trange(Configs.SHAPE ** DIMENSION):
        color = list(stack.keys())[i % 2]

        turn = input_coords(i=i, stack=stack, color=color)
        if not turn: break  # WA for exit

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
        # win_stat[color].append(i)
