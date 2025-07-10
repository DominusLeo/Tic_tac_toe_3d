import itertools
import numpy as np
import matplotlib.pyplot as plt
import copy
from tqdm import trange

from constants import Configs, Bot_3_lvl, Bot_4_lvl
from game_process import single_game

hz = Configs()

render = False

hz.GRAVITY = True
hz.SHAPE = 4  # must be in range(3, 10) (WA)

fst_color = 'white'
snd_color = 'black'

hz.stack = {fst_color: [], snd_color: []}  # set color and name for every player, used by matplotlib
hz.field_data = {fst_color: hz.field_data['fst_player'], snd_color: hz.field_data['snd_player']}

hz.play_vs_bot = 1  # bot_1_configs       # 0, 1, 2, 3 - the presence and number of the bot's move
hz.bot_difficult = 4

hz.debug_mod = True  # random turns by pc without players decisions
hz.second_bot = 3     # 0, 1, 2, 3 - difficult of second bot


if __name__ == "__main__":
    win_stat = copy.deepcopy(hz.stack)
    win_stat['nobody'] = []

    # set configs for 3rd lvl bot
    if hz.second_bot == 3:
        bot_1_configs = Bot_3_lvl()  # hz.play_vs_bot = 2
        bot_1_configs.name = 'main_3_lvl_bot'

    elif hz.second_bot == 4:
        bot_1_configs = Bot_4_lvl()

        # # bot_1_configs.fork_weights[1] = 2
        bot_1_configs.name = 'test_4_lvl_bot_0_no_force_moves'
        bot_1_configs.win_points_force = 0
        bot_1_configs.force_weight = 0

    if hz.play_vs_bot == 1:
        print(f"const_{hz.bot_difficult}_lvl_bot VS {bot_1_configs.name}")
    else:
        print(f"{bot_1_configs.name} VS const_{hz.bot_difficult}_lvl_bot")


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
