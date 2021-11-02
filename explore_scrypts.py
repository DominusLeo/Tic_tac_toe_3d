import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from tqdm import trange

from constants import Configs
from game_process import single_game

Configs.debug_mod = True  # random turns by pc without players decisions

Configs.GRAVITY = True
Configs.SHAPE = 4  # must be in range(3, 10) (WA)
Configs.stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib
Configs.play_vs_bot = 2  # 0, 1, 2 - the presence and number of the bot's move
Configs.second_bot = False


if __name__ == "__main__":
    win_stat = copy.deepcopy(Configs.stack)

    for trying in trange(25):
        color, i = single_game(rendering=False)
        win_stat[color].append(i)
