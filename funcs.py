import copy
import json
import os
import pickle
import time
import sympy
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import datetime as dt

from bot_utils import filter_lines_stack, filter_weight_calc, filter_cross_forks_stack, filter_over_forks_stack, \
    find_dead_points
from constants import Configs, DIMENSION, dict_of_shapes_wins, Bot_3_lvl, turns_alpha, Bot_4_lvl, need_size_cf
from utils import free_lines_counter, gravity_correction

# from matplotlib.widgets import TextBox
# from numba import jit, cuda, njit


pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
sns.set(style='darkgrid')


def obj_saver(obj, path='./obj.pickle'):
    parent = os.path.dirname(path)

    if parent:
        os.makedirs(parent, exist_ok=True)

    with open(path, 'wb') as file:
        pickle.dump(obj, file, pickle.HIGHEST_PROTOCOL)
    return path


def obj_reader(path, check_exists=False):
    if check_exists:
        if not os.path.exists(path):
            return None

    with open(path, 'rb') as file:
        res = pickle.load(file)
    return res


def json_saver(data, path):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4, default=str)


def json_reader(path, check_exists=False):
    if check_exists:
        if not os.path.exists(path):
            return None

    with open(path, 'r', encoding="utf8") as f:
        res = json.load(f)
    return res


def size_coef(coord, cf=0.5, need_fix=need_size_cf,):
    if need_size_cf:
        fix_coord = coord.copy()
        # [4,1,4] - max()
        # [1,4,1] - min()
        fix_coord[1] = Configs.SHAPE - coord[1] + 1

        res = np.product(fix_coord)
        max_coord = Configs.SHAPE ** 3
        return (res / max_coord + cf) / (1 + cf), (1 - res / max_coord + cf) / (1 + cf)
    else:
        return 1, 1


def init_field():
    # mpl.use('TkAgg')
    plt.style.use('bmh')

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
            c_s, c_a = size_coef([x, y, 4], cf=0.9)
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, Configs.SHAPE, 100), ys=np.linspace(y, y, 100),
                    c="grey", linewidth=10 * c_s, alpha=turns_alpha * c_s)

    ax.set_title(f"Tic Tac Toe 3d") if Configs.GRAVITY else ax.set_title(f"Levitating Tic Tac Toe 3d")
    ax.set_zlim([1, 4.2])

    x_scale = 4
    y_scale = 4
    z_scale = 2

    scale = np.diag([x_scale, y_scale, z_scale, 1.0])
    scale = scale * (1.0 / scale.max())
    scale[3, 3] = 1.0

    def short_proj():
        return np.dot(Axes3D.get_proj(ax), scale)

    ax.get_proj = short_proj
    # ax.legend()
    fig.show()

    return fig, ax


def render_turn(ax, fig, turn, color):
    coef_s, coef_a = size_coef(turn)
    ax.scatter(*turn, s=2000 * coef_s, c=color, marker='h', linewidths=1, norm=True, alpha=turns_alpha * coef_s,
               edgecolors='black')
    fig.show()


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


def up_layer(stack):
    coords_arr = [list(coords) for coords in itertools.product(*[[*range(1, Configs.SHAPE + 1)]] * DIMENSION)]
    coords_arr = [gravity_correction(coords, stack) for coords in coords_arr]
    coords_arr = [list(i) for i in set(tuple(j) for j in coords_arr)] if Configs.GRAVITY else coords_arr
    coords_arr = [coords for coords in coords_arr if coords not in itertools.chain(*stack.values())]

    return coords_arr


def bot_turn(i, stack, color, difficult=1, configs=None, field_data=None):
    enemy_color = list(stack.keys())[(i + 1) % 2]

    # all possible turns list
    coords_arr = up_layer(stack)
    field_data[color]['up_layer'] = set(tuple(ii) for ii in coords_arr)

    count_of_points = {0: None}

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
    # where to move to close enemy line
    for coord in coords_arr:
        temp_stack = copy.deepcopy(stack)
        temp_stack[enemy_color].append(coord)

        if win_check_from_db(temp_stack, coord, enemy_color):
            print('force move', end=' ')
            return coord

    pos_turns = len(coords_arr)
    # print(f"{pos_turns = }")

    # remove turns under loose (forbieden turns)
    coords_arr_c = coords_arr.copy()
    for coord in coords_arr_c:
        temp_stack = copy.deepcopy(stack)
        temp_coord = copy.deepcopy(coord)
        temp_coord[-1] += 1
        temp_stack[enemy_color].append(temp_coord)

        if win_check_from_db(temp_stack, temp_coord, enemy_color):
            coords_arr.remove(coord)

    # check for fork move:
    for m, v in field_data[color]['dead_points'].items():
        if v['fork_move'] and (v['fork_move'] & set([tuple(j) for j in coords_arr])):
            print('fork move', end=' ')
            return list(v['fork_move'])[-1]

    if len(coords_arr) == 0:
        print('no good turns found')
        return coord

    if difficult >= 1:
        coords_arr = list(np.random.permutation(coords_arr))

    if difficult < 4:
        if difficult >= 2:  # find the most position attractive turns
            count_of_lines = {}
            for coord in coords_arr:
                temp_coord = tuple(coord)

                temp_lines = free_lines_counter(stack=stack, turn=temp_coord, enemy_color=enemy_color)
                # enemy analyse
                temp_lines_enemy = free_lines_counter(stack=stack, turn=temp_coord, enemy_color=color)

                if 2 <= difficult <= 2.9:
                    weight_1 = len(temp_lines)
                    weight_2 = len(temp_lines_enemy)

                elif 3 <= difficult <= 3.9:
                    weights = Bot_3_lvl() if configs is None else configs

                    weight_1 = 0
                    for line in temp_lines:
                        weight_1 += weights.own_weights[len(set(tuple(i) for i in stack[color]) & line)]

                    weight_2 = 0
                    for line in temp_lines_enemy:
                        weight_2 += weights.enemy_weights[len(set(tuple(i) for i in stack[enemy_color]) & line)]

                # max defense strat
                our_cf = 1
                enemy_cf = 1
                if (difficult == 2.5) or (difficult == 3.5):
                    our_cf = 1
                    enemy_cf = 100

                count_of_lines[temp_coord] = weight_1 * our_cf + weight_2 * enemy_cf


            count_of_points = {}
            for ii in count_of_lines:
                if count_of_points.get(count_of_lines[ii]) is not None:
                    count_of_points[count_of_lines[ii]].append(list(ii))
                else:
                    count_of_points[count_of_lines[ii]] = [list(ii)]

            coords_arr_new = []
            for j in np.sort([*count_of_points.keys()])[::-1]:
                coords_arr_new += count_of_points[j]
            coords_arr = coords_arr_new

    if i >= 42:
        ...

    if difficult == 4:
        field_data_variants = {tuple(coord): copy.deepcopy(field_data) for coord in coords_arr}  # TODO: [30.06.2025 by Leo] very slow
        bot_weights = Bot_4_lvl()

        for coord in (coords_arr):
            coord = tuple(coord)
            temp_field_data = field_data_variants[coord]
            our_field = temp_field_data[color]
            enemy_field = temp_field_data[enemy_color]

            # filter lines left
            our_field['lines_left'] = filter_lines_stack(our_field['lines_left'], coord, my_turn=True, stack=stack)
            enemy_field['lines_left'] = filter_lines_stack(enemy_field['lines_left'], coord, my_turn=False, stack=stack)

            # operations with dead points  # TODO: [21.06.2025 by Leo]
            our_field['dead_points'], enemy_field['dead_points'] = find_dead_points(our_field['lines_left'], enemy_field['lines_left'], color=color,
                                                                                    stack=stack, coord=coord, up_layer=field_data[color]['up_layer'],
                                                                                    bot_weights=bot_weights, turn_num=i)

            # find force moves combs
            # our_field['force_moves'], enemy_field['force_moves'] =

            # filter cross forks
            our_field['cross_forks_left'] = filter_cross_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=True,
                                                                     field_data=temp_field_data, stack=stack, bot_weights=bot_weights)
            enemy_field['cross_forks_left'] = filter_cross_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=False,
                                                                       field_data=temp_field_data, stack=stack, bot_weights=bot_weights)

            # filter over forks
            our_field['over_forks_left'] = filter_over_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=True,
                                                                   field_data=temp_field_data, stack=stack, bot_weights=bot_weights)
            enemy_field['over_forks_left'] = filter_over_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=False,
                                                                     field_data=temp_field_data, stack=stack, bot_weights=bot_weights)

            # field_data_variants[coord] = {color: our_field, enemy_color: enemy_field}

        coords_weights = filter_weight_calc(field_data=field_data_variants, color=color, enemy_color=enemy_color,
                                            bot_weights=bot_weights, stack=stack, turn_number=i)

        coords_arr = list(dict(sorted(coords_weights.items(), key=lambda item: item[1], reverse=True)).keys())

    coord = coords_arr[0]
    # _________________________________________

    return coord


def line_render(stack_render, label=None):
    fig, ax = init_field()

    # Флаг для отслеживания первой точки каждого цвета
    first_point_per_color = {}

    for color in stack_render:
        for i in stack_render[color]:
            coef_s, coef_a = size_coef([ii for ii in i])

            # Устанавливаем label только для первой точки каждого цвета
            point_label = None
            if color not in first_point_per_color:
                point_label = f"{label} ({color})" if label else color
                first_point_per_color[color] = True

            ax.scatter(*i, s=2000 * coef_s, c=color, marker='h', linewidths=1, norm=True,
                       alpha=turns_alpha * coef_s, edgecolors='grey', label=point_label)

    # Показываем легенду, если есть лейблы
    if label is not None or len(stack_render) > 1:
        ax.legend()

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
