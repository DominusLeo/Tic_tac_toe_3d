import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import copy
from tqdm import trange

from constants import Configs, Bot_3_lvl
from game_process import single_game

hz = Configs()

render = False

hz.GRAVITY = True
hz.SHAPE = 4  # must be in range(3, 10) (WA)

fst_color = 'white'
snd_color = 'black'

hz.stack = {fst_color: [], snd_color: []}  # set color and name for every player, used by matplotlib
hz.field_data = {fst_color: hz.field_data['fst_player'], snd_color: hz.field_data['snd_player']}

hz.play_vs_bot = 2       # 0, 1, 2, 3 - the presence and number of the bot's move
hz.bot_difficult = 4

hz.debug_mod = True  # random turns by pc without players decisions
hz.second_bot = 3     # 0, 1, 2, 3 - difficult of second bot


if __name__ == "__main__":
    win_stat = copy.deepcopy(hz.stack)
    win_stat['nobody'] = []

    if hz.play_vs_bot == 1:
        print(f"main_{hz.bot_difficult}_lvl_bot VS debug_{hz.second_bot}_lvl_bot")
    else:
        print(f"debug_{hz.second_bot}_lvl_bot VS main_{hz.bot_difficult}_lvl_bot")

    # set configs for 3rd lvl bot
    bot_1_configs = Bot_3_lvl()
    # bot_1_configs.enemy_weights = {i: bot_1_configs.enemy_weights[i] ** 2 for i in bot_1_configs.enemy_weights}
    # bot_1_configs.own_weights = {i: bot_1_configs.own_weights[i] ** 2 for i in bot_1_configs.own_weights}

    for trying in trange(20):
        # breakpoint()
        color, i, is_win = single_game(rendering=render, bot_2_configs=None, bot_1_configs=bot_1_configs,
                                       Configs=hz, game_log_to_save=[])

        win_stat[color].append(i) if is_win else win_stat['nobody'].append(i)

    # stat analyse
    main_bot_color = list(hz.stack.keys())[hz.play_vs_bot - 1]
    debug_bot_color = list(hz.stack.keys())[hz.play_vs_bot % 2]

    wins = win_stat[main_bot_color].__len__()
    loses = win_stat[debug_bot_color].__len__()
    nobody = win_stat['nobody'].__len__()

    print(f'wins: {wins} / {trying + 1} = {wins / (trying + 1) * 100}%')
    print(f'loses: {loses} / {trying + 1} = {loses / (trying + 1) * 100}%')
    print(f'draw: {nobody} / {trying + 1} = {nobody / (trying + 1) * 100}%')
