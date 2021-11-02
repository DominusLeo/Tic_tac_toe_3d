import copy
import time
import sympy
import numpy as np
import matplotlib.pyplot as plt
import itertools
import csv
import seaborn as sns
from tqdm import tqdm
# from matplotlib.widgets import TextBox
# from numba import jit, cuda, njit

from constants import Configs, DIMENSION, dict_of_shapes_wins

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

    for x in range(1, Configs.SHAPE + 1):
        for y in range(1, Configs.SHAPE + 1):
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, Configs.SHAPE, 100), ys=np.linspace(y, y, 100),
                    c="grey", linewidth=5, alpha=0.8)

    ax.set_title(f"Tic Tac Toe 3d") if Configs.GRAVITY else ax.set_title(f"Levitating Tic Tac Toe 3d")
    # ax.legend()

    # WA for good scaling
    ax.scatter3D(0, 0, 1, s=1, c="w")
    ax.scatter3D(Configs.SHAPE + 1, Configs.SHAPE + 1, Configs.SHAPE, s=1, c="w")
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


def fill_all_field():
    stack = {'red': [list(coords) for coords in itertools.product(*[[*range(1, Configs.SHAPE + 1)]] * DIMENSION)]}
    return stack


# single uses
def all_win_lines():
    field = fill_all_field()
    lines_stack = []

    for line in tqdm(itertools.combinations(field['red'], Configs.SHAPE)):
        if sympy.Point.is_collinear(*line):
            lines_stack.append(set(tuple(i) for i in line))
    return lines_stack


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


def free_lines_counter(stack, turn, enemy_color):
    free_lines = []

    possible_lines = [t for t in dict_of_shapes_wins[Configs.SHAPE] if tuple(turn) in t]

    for line_set in possible_lines:
        flag = True

        for point in stack[enemy_color]:
            if tuple(point) in line_set:
                flag = False
                break
        if flag:
            free_lines.append(line_set)

    return free_lines


def bot_turn(i, stack, color, difficult=1):
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
        count_of_perspectives = {}
        for coord in coords_arr:
            temp_lines = free_lines_counter(stack=stack, turn=coord, enemy_color=enemy_color)
            count = len(temp_lines)

            if count_of_perspectives.get(count) is not None:
                count_of_perspectives[count].append(coord)
            else:
                count_of_perspectives[count] = []

        coords_arr_new = []
        for j in np.sort([*count_of_perspectives.keys()])[::-1]:
            coords_arr_new += count_of_perspectives[j]
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
    ax.scatter(*turn, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.7, edgecolors='black')
    fig.show()


# #FIXME: [10.10.2021 by Lev] multilines
def line_render(stack_render):
    fig, ax = init_field()

    for color in stack_render:
        for i in stack_render[color]:
            ax.scatter(*i, s=2000, c=color, marker='h', linewidths=1, norm=True, alpha=0.7, edgecolors='black')
    fig.show()
    return fig, ax


# # scratches___________________________________________________________________________________________________________
def debug_turn(i, stack, color):
    coords = list(np.random.randint(1, Configs.SHAPE + 1, DIMENSION))
    if coords in itertools.chain(*stack.values()):
        return debug_turn(i, stack, color)
    else:
        print(f'{color} turn: {coords}')
        return coords


# @njit(cache=True, nogil=True, fastmath=True)
# def _win_check(st, cl, sh, cmbs):
#     for line in cmbs:
#         if sympy.Point.is_collinear(*line):
#             return line
#     return False
#
#
# def win_check(stack, coords, color):
#     combs = np.array([i for i in itertools.combinations(stack[color], Configs.SHAPE) if coords in i])
#     return _win_check(stack[color], coords, Configs.SHAPE, combs)


old_lines = set()


def win_check(stack, coords, color):
    for line in itertools.combinations(stack[color], Configs.SHAPE):
        if coords in line:
            temp_line = line
            # temp_line = tuple(tuple(i) for i in line)
            # if temp_line in old_lines:
            #     continue
            # else:
            #     old_lines.add(temp_line)
            if sympy.Point.is_collinear(*temp_line):
                return temp_line
    return False


def win_check_from_db1(stack, coords, color):
    a = set([frozenset(tuple(i) for i in line) for line in itertools.combinations(stack[color], Configs.SHAPE) if coords in line])
    b = a & dict_of_shapes_wins[Configs.SHAPE]
    for i in b:
        return i
    return False


# corners = [[1, 1, 1], [1, 1, 4],
#            [4, 4, 4], [4, 4, 1],
#            [1, 4, 1], [1, 4, 4],
#            [4, 1, 1], [4, 1, 4]]
#
#
# def fast_win_check(stack=None, coords=None, color='green'):
#     all_poss_lines = []
#
#     for i in range(DIMENSION):
#         temp_line_one = []
#         temp_line_two = []
#         temp_line_three = []
#
#         for j in range(Configs.SHAPE):
#             temp_turn = coords.copy()
#             temp_turn[i] = (temp_turn[i] + j) % Configs.SHAPE + 1
#             temp_line_one.append(temp_turn)
#
#             temp_turn = coords.copy()
#             temp_turn[i] = (temp_turn[i] + j) % Configs.SHAPE + 1
#             temp_turn[i - 1] = (temp_turn[i - 1] + j) % Configs.SHAPE + 1
#             temp_line_two.append(temp_turn)
#
#             if coords in corners:
#                 temp_turn = coords.copy()
#                 temp_turn[i] = (temp_turn[i] + j) % Configs.SHAPE + 1
#                 temp_turn[i - 1] = (temp_turn[i - 1] + j) % Configs.SHAPE + 1
#                 temp_turn[i - 2] = (temp_turn[i - 2] + j) % Configs.SHAPE + 1
#                 temp_line_three.append(temp_turn)
#
#         all_poss_lines.append(temp_line_one)
#         if temp_line_two:
#             all_poss_lines.append(temp_line_two)
#         if temp_line_three:
#             all_poss_lines.append(temp_line_three)
#
#     return all_poss_lines


# with open('4x4x4.csv', 'w') as f:
#     # using csv.writer method from CSV package
#     write = csv.writer(f)
#     write.writerows(list(aaa))

# with open('4x4x4.csv', newline='\n') as f:
#     reader = csv.reader(f)
#     data = list(reader)
