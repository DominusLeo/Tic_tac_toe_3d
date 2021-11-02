import copy
import time
import sympy
import numpy as np
import itertools
import csv
import seaborn as sns
from tqdm import tqdm
import matplotlib.pyplot as plt

from constants import Configs, DIMENSION, dict_of_shapes_wins


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


def free_lines_counter(stack, turn, enemy_color):
    free_lines = []

    possible_lines = [t for t in dict_of_shapes_wins[Configs.SHAPE] if turn in t]

    for line_set in possible_lines:
        flag = True

        for point in stack[enemy_color]:
            if tuple(point) in line_set:
                flag = False
                break
        if flag:
            free_lines.append(line_set)

    return free_lines


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
