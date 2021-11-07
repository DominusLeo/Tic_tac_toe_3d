import copy
import time
import sympy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import pandas as pd
import seaborn as sns
from tqdm import tqdm
import datetime as dt
# from matplotlib.widgets import TextBox
# from numba import jit, cuda, njit

from constants import Configs, DIMENSION, dict_of_shapes_wins, Bot_3_lvl
from utils import free_lines_counter


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
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

    # render verticals
    for x in range(1, Configs.SHAPE + 1):
        for y in range(1, Configs.SHAPE + 1):
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, Configs.SHAPE, 100), ys=np.linspace(y, y, 100),
                    c="grey", linewidth=10, alpha=0.9)

    ax.set_title(f"Tic Tac Toe 3d") if Configs.GRAVITY else ax.set_title(f"Levitating Tic Tac Toe 3d")
    # ax.legend()

    # # WA for good scaling
    ax.scatter3D(0.8, 0.8, 1, s=1, c="w", alpha=0)
    ax.scatter3D(Configs.SHAPE + 0.2, Configs.SHAPE + 0.2, Configs.SHAPE, s=1, c="w", alpha=0)
    fig.show()

    return fig, ax


def gravity_correction(coords, stack):
    if Configs.GRAVITY:
        if coords[-1] == 1:
            return coords
        else:
            temp = coords.copy()
            temp[-1] = temp[-1] - 1
            if temp in itertools.chain(*stack.values()):
                return coords
            else:
                return gravity_correction(temp, stack)
    else:
        return coords


def win_check_from_db(stack, coords, color):
    for line in itertools.combinations(stack[color], Configs.SHAPE):
        if coords in line:
            if set([tuple(i) for i in line]) in dict_of_shapes_wins[Configs.SHAPE]:
                return line
    return False


def input_coords(i, stack: dict, color):
    input_data = input(f"{color} player {i % 2 + 1}\nprint your coords: ")

    # TODO: [06.10.2021 by Lev] replace terminal input into matplotlib box
    # text_box = TextBox(ax, f"{color} player {i % 2 + 1}\nprint your coords: ")
    # print(text_box.text)
    # input_data = text_box.on_submit(print)

    try:
        # exit condition
        if input_data == "ex":
            return "exit"

        # rollback turn condition
        if input_data == 'c':
            return "cancel"

        coords = [int(i) for i in input_data]
        print()

    except:  # TODO: [06.10.2021 by Lev] set right exception
        print("input is wrong\n")
        coords = input_coords(i, stack, color)

    if (coords in itertools.chain(*stack.values())) \
            or any(np.array(coords) < 1) \
            or any(np.array(coords) > Configs.SHAPE) \
            or len(coords) != DIMENSION:
        print('this turn is impossible\n')
        coords = input_coords(i, stack, color)

    return coords


def bot_turn(i, stack, color, difficult=1, configs=None):
    # all possible turns list
    coords_arr = [list(coords) for coords in itertools.product(*[[*range(1, Configs.SHAPE + 1)]] * DIMENSION)]
    coords_arr = [gravity_correction(coords, stack) for coords in coords_arr]
    coords_arr = [list(i) for i in set(tuple(j) for j in coords_arr)] if Configs.GRAVITY else coords_arr
    coords_arr = [coords for coords in coords_arr if coords not in itertools.chain(*stack.values())]

    if difficult == 0:
        coord = coords_arr[np.random.choice(range(len(coords_arr)))]
        return coord

    # check for win turns
    for coord in coords_arr:
        temp_stack = copy.deepcopy(stack)
        temp_stack[color].append(coord)

        if win_check_from_db(temp_stack, coord, color):
            return coord

    # check for loosing turns
    enemy_color = list(stack.keys())[(i + 1) % 2]
    for coord in coords_arr:
        temp_stack = copy.deepcopy(stack)
        temp_stack[enemy_color].append(coord)

        if win_check_from_db(temp_stack, coord, enemy_color):
            return coord

    if difficult >= 1:
        coords_arr = [coords_arr[i] for i in np.random.choice(range(len(coords_arr)), len(coords_arr), False)]

    if difficult >= 2:  # find the most position attractive turns
        count_of_lines = {}
        for coord in coords_arr:
            temp_coord = tuple(coord)

            temp_lines = free_lines_counter(stack=stack, turn=temp_coord, enemy_color=enemy_color)
            # enemy analyse
            temp_lines_enemy = free_lines_counter(stack=stack, turn=temp_coord, enemy_color=color)

            if difficult == 2:
                weight_1 = len(temp_lines)
                weight_2 = len(temp_lines_enemy)

            elif difficult >= 3:
                weights = Bot_3_lvl() if configs is None else configs

                weight_1 = 0
                for line in temp_lines:
                    weight_1 += weights.own_weights[len(set(tuple(i) for i in stack[color]) & line)]

                weight_2 = 0
                for line in temp_lines_enemy:
                    weight_2 += weights.enemy_weights[len(set(tuple(i) for i in stack[enemy_color]) & line)]

            count_of_lines[temp_coord] = weight_1 + weight_2

        count_of_points = {}
        for i in count_of_lines:
            if count_of_points.get(count_of_lines[i]) is not None:
                count_of_points[count_of_lines[i]].append(list(i))
            else:
                count_of_points[count_of_lines[i]] = [list(i)]

        coords_arr_new = []
        for j in np.sort([*count_of_points.keys()])[::-1]:
            coords_arr_new += count_of_points[j]
        coords_arr = coords_arr_new

    # check for not turning under loose
    for coord in coords_arr:
        temp_stack = copy.deepcopy(stack)
        temp_coord = copy.deepcopy(coord)
        temp_coord[-1] += 1
        temp_stack[enemy_color].append(temp_coord)

        if not win_check_from_db(temp_stack, temp_coord, enemy_color):
            return coord

    return coord


def render_turn(ax, fig, turn, color):
    ax.scatter(*turn, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.8, edgecolors='black')
    fig.show()


def line_render(stack_render):
    fig, ax = init_field()

    for color in stack_render:
        for i in stack_render[color]:
            ax.scatter(*i, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.8, edgecolors='black')
    fig.show()
    return fig, ax


def leader_bord_stat(i, your_turn, is_win):
    your_turn = your_turn if is_win else (your_turn % 2 + 1)
    leader_name = input('print yor name:\n') or "Leo"
    type_game = 'x'.join(map(str, [Configs.SHAPE] * DIMENSION))
    type_game = type_game if Configs.GRAVITY else type_game + "_levitate"
    date = dt.date.fromtimestamp(time.time()).isoformat()

    labels = ['leader_name', 'game_type', 'date', 'number_of_turns', 'your_turn_number', "is_win", 'difficult']

    board = pd.read_csv('data/leaderboard.csv')
    line = [leader_name, type_game, date, i, your_turn, is_win, Configs.bot_difficult]

    board.loc[len(board), :] = line
    board.to_csv('data/leaderboard.csv', index=False)
