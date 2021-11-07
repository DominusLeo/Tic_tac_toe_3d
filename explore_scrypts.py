import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from tqdm import trange

from constants import Configs, Bot_3_lvl
from game_process import single_game

Configs.GRAVITY = True
Configs.SHAPE = 4  # must be in range(3, 10) (WA)
Configs.stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib

Configs.debug_mod = True  # random turns by pc without players decisions
Configs.second_bot = 3     # 0, 1, 2, 3 - difficult of second bot

Configs.play_vs_bot = 2       # 0, 1, 2, 3 - the presence and number of the bot's move
Configs.bot_difficult = 3


if __name__ == "__main__":
    win_stat = copy.deepcopy(Configs.stack)
    win_stat['nobody'] = []

    if Configs.play_vs_bot == 1:
        print(f"main_{Configs.bot_difficult}_lvl_bot VS debug_{Configs.second_bot}_lvl_bot")
    else:
        print(f"debug_{Configs.second_bot}_lvl_bot VS main_{Configs.bot_difficult}_lvl_bot")

    # set configs for 3rd lvl bot
    bot_1_configs = Bot_3_lvl()
    # bot_1_configs.enemy_weights = {i: bot_1_configs.enemy_weights[i] ** 2 for i in bot_1_configs.enemy_weights}
    # bot_1_configs.own_weights = {i: bot_1_configs.own_weights[i] ** 2 for i in bot_1_configs.own_weights}

    for trying in trange(20):
        color, i, is_win = single_game(rendering=False, bot_2_configs=None, bot_1_configs=bot_1_configs)

        win_stat[color].append(i) if is_win else win_stat['nobody'].append(i)

    # stat analyse
    main_bot_color = list(Configs.stack.keys())[Configs.play_vs_bot - 1]
    debug_bot_color = list(Configs.stack.keys())[Configs.play_vs_bot % 2]

    wins = win_stat[main_bot_color].__len__()
    loses = win_stat[debug_bot_color].__len__()
    nobody = win_stat['nobody'].__len__()

    print(f'wins: {wins} / {trying + 1} = {wins / (trying + 1) * 100}%')
    print(f'loses: {loses} / {trying + 1} = {loses / (trying + 1) * 100}%')
    print(f'nobody: {nobody} / {trying + 1} = {nobody / (trying + 1) * 100}%')
