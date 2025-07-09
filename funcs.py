import copy
import json
import os
import pickle
import time
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import itertools
import pandas as pd
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
from tqdm import tqdm
import datetime as dt

from bot_utils import full_data_update, weight_calc, up_layer
from constants import Configs, DIMENSION, dict_of_shapes_wins, Bot_3_lvl, turns_alpha, Bot_4_lvl, need_size_cf
from utils import free_lines_counter, gravity_correction, debug_turn

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
    mpl.use('TkAgg')  # Включаем TkAgg backend для интерактивности
    plt.style.use('bmh')

    fig = plt.figure()
    ax = fig.add_subplot(projection='3d')

    ax.set_xticks(np.arange(1, Configs.SHAPE + 1, 1))
    ax.set_yticks(np.arange(1, Configs.SHAPE + 1, 1))
    ax.set_zticks(np.arange(1, Configs.SHAPE + 1, 1))

    ax.set_xlabel('x axis', fontsize=10, rotation=1, loc='left')
    ax.set_ylabel('y axis', fontsize=10, rotation=1)
    ax.set_zlabel('z axis', fontsize=10, rotation=1)

    # render verticals
    for x in range(1, Configs.SHAPE + 1):
        for y in range(1, Configs.SHAPE + 1):
            c_s, c_a = size_coef([x, y, 4], cf=0.9)
            ax.plot(xs=np.linspace(x, x, 100), zs=np.linspace(1, Configs.SHAPE, 100), ys=np.linspace(y, y, 100),
                    c="grey", linewidth=10 * c_s, alpha=turns_alpha * c_s)

    game_title = f"Tic Tac Toe 3d" if Configs.GRAVITY else f"Levitating Tic Tac Toe 3d"
    ax.set_title(game_title)
    ax.set_zlim([1, 4.2])
    
    # # Инвертировать X-ось (справа налево)
    # ax.invert_xaxis()

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
    
    # Принудительно активируем интерактивность
    plt.ion()  # Включаем интерактивный режим
    fig.canvas.draw()
    fig.canvas.flush_events()

    return fig, ax


def update_game_title(ax, fig, current_player=None, player_num=None):
    """Обновляет заголовок игры в зависимости от режима"""
    game_title = f"Tic Tac Toe 3d" if Configs.GRAVITY else f"Levitating Tic Tac Toe 3d"
    
    # В обычном режиме (не интерактивном) показываем текущего игрока
    if not Configs.interactive_input and current_player and player_num is not None:
        game_title += f" - {current_player} player {player_num} turn"
    
    ax.set_title(game_title)
    if fig:
        fig.canvas.draw()


def render_turn(ax, fig, turn, color, label=None):
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


class InteractiveInput:
    def __init__(self, fig, ax, stack, color, player_num):
        self.fig = fig
        self.ax = ax
        self.stack = stack
        self.color = color
        self.player_num = player_num
        self.coords = None
        self.click_count = 0
        self.temp_coords = [0, 0, 0]
        self.preview_scatter = None
        self.text_display = None
        
        # Обновляем заголовок
        self.ax.set_title(f"{color} player {player_num} - Click to select coordinates (x, y, z)")
        
        # Подключаем только обработчик клавиш
        self.fig.canvas.mpl_connect('key_press_event', self.on_key_press)
        
        # Добавляем текстовый дисплей для текущих координат
        self.update_instruction_text()
        
    def update_instruction_text(self):
        if self.click_count == 0:
            instruction = f"Press key 1-{Configs.SHAPE} for X coordinate (Backspace to undo)"
        elif self.click_count == 1:
            instruction = f"X={self.temp_coords[0]}, Press key 1-{Configs.SHAPE} for Y coordinate (Backspace to undo)"
        elif self.click_count == 2:
            if self.temp_coords[2] == 0:
                instruction = f"X={self.temp_coords[0]}, Y={self.temp_coords[1]}, Press key 1-{Configs.SHAPE} for Z coordinate (Backspace to undo)"
            else:
                instruction = f"X={self.temp_coords[0]}, Y={self.temp_coords[1]}, Z={self.temp_coords[2]} - Press ENTER to confirm (Backspace to undo)"
        else:
            instruction = f"Selected: {self.temp_coords}, Press ENTER to confirm or ESC to cancel"
            
        self.ax.set_title(f"{self.color} player {self.player_num} - {instruction}")
        self.fig.canvas.draw()


    def on_key_press(self, event):
        if event.key == 'enter' and self.click_count == 2 and all(coord > 0 for coord in self.temp_coords):
            # Подтверждаем выбор только если все координаты введены
            if self.is_valid_position():
                self.coords = self.temp_coords.copy()
                self.disconnect_events()
                if self.preview_scatter:
                    self.preview_scatter.remove()
                # Восстанавливаем название игры
                game_title = f"Tic Tac Toe 3d" if Configs.GRAVITY else f"Levitating Tic Tac Toe 3d"
                self.ax.set_title(game_title)
                self.fig.canvas.draw()
            else:
                print("Position already taken or invalid!")
                self.reset_selection()
            
        elif event.key == 'escape':
            self.reset_selection()
            
        elif event.key == 'c':
            self.coords = "cancel"
            self.disconnect_events()
            
        elif event.key == 'q':
            self.coords = "exit"
            self.disconnect_events()
            
        # Обработка цифровых клавиш для всех координат
        elif event.key.isdigit():
            coord_value = int(event.key)
            if 1 <= coord_value <= Configs.SHAPE:
                if self.click_count == 0:  # X coordinate
                    self.temp_coords[0] = coord_value
                    self.click_count = 1
                elif self.click_count == 1:  # Y coordinate
                    self.temp_coords[1] = coord_value
                    self.click_count = 2
                    self.temp_coords[2] = 1  # Default Z
                elif self.click_count == 2:  # Z coordinate
                    self.temp_coords[2] = coord_value
                    # НЕ подтверждаем автоматически, ждем Enter
                    # click_count остается 2, чтобы показать что нужен Enter
                        
                self.show_preview()
                self.update_instruction_text()
                
        # Backspace для стирания последней координаты
        elif event.key == 'backspace':
            if self.click_count > 0:
                self.click_count -= 1
                if self.click_count == 0:
                    self.temp_coords = [0, 0, 0]
                elif self.click_count == 1:
                    self.temp_coords[1] = 0
                    self.temp_coords[2] = 0
                elif self.click_count == 2:
                    self.temp_coords[2] = 0
                    
                if self.preview_scatter:
                    self.preview_scatter.remove()
                    self.preview_scatter = None
                    
                self.show_preview()
                self.update_instruction_text()
                
    def disconnect_events(self):
        self.fig.canvas.mpl_disconnect('key_press_event')
            
    def reset_selection(self):
        self.click_count = 0
        self.temp_coords = [0, 0, 0]
        self.coords = None
        if self.preview_scatter:
            self.preview_scatter.remove()
            self.preview_scatter = None
        self.update_instruction_text()
        
    def show_preview(self):
        if self.preview_scatter:
            self.preview_scatter.remove()
            
        if self.click_count >= 2 and self.temp_coords[2] > 0:
            # Показываем предварительный просмотр позиции
            coef_s, coef_a = size_coef(self.temp_coords)
            self.preview_scatter = self.ax.scatter(*self.temp_coords, s=2000 * coef_s, 
                                                 c=self.color, marker='h', linewidths=3,
                                                 alpha=0.5, edgecolors='red')
            self.fig.canvas.draw()
            
    def is_valid_position(self):
        # Проверяем, не занята ли позиция
        if self.temp_coords in itertools.chain(*self.stack.values()):
            return False
            
        # Проверяем границы
        if any(np.array(self.temp_coords) < 1) or any(np.array(self.temp_coords) > Configs.SHAPE):
            return False
            
        # Проверяем размерность
        if len(self.temp_coords) != DIMENSION:
            return False
            
        return True
        
    def wait_for_input(self):
        while self.coords is None:
            self.fig.canvas.start_event_loop(timeout=0.1)
        return self.coords


def input_coords(i, stack: dict, color, fig=None, ax=None):
    # Проверяем настройку интерактивного ввода
    if Configs.interactive_input and fig is not None and ax is not None:
        interactive_input = InteractiveInput(fig, ax, stack, color, i % 2 + 1)
        coords = interactive_input.wait_for_input()
        
        if coords == "exit" or coords == "cancel":
            return coords
            
        # Выводим в терминал куда походил игрок
        print(f'{color} turn: {coords}')
            
        # Применяем гравитацию если нужно
        coords = gravity_correction(coords=coords, stack=stack)
        return coords
    
    # Fallback к текстовому вводу
    input_data = input(f"{color} player {i % 2 + 1}\nprint your coords: ")

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
        coords = input_coords(i, stack, color, fig, ax)

    if (coords in itertools.chain(*stack.values())) \
            or any(np.array(coords) < 1) \
            or any(np.array(coords) > Configs.SHAPE) \
            or len(coords) != DIMENSION:
        print('this turn is impossible\n')
        coords = input_coords(i, stack, color, fig, ax)

    return coords


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
            # print('force move', end=' ')  # TODO: [02.07.2025 by Leo] 
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
        field_data_variants = {tuple(coord): pickle.loads(pickle.dumps(field_data, -1)) for coord in coords_arr}  # TODO: [30.06.2025 by Leo] very slow
        bot_weights = Bot_4_lvl()

        debug_weights = {}
        coords_weights = {}
        for coord in coords_arr:
            coord = tuple(coord)
            temp_field_data = field_data_variants[coord]
            enemy_alt_data = pickle.loads(pickle.dumps(temp_field_data, -1))

            # weights before turn
            start_our_weight = weight_calc(temp_field_data, color, )
            start_enemy_weight = weight_calc(temp_field_data, enemy_color, )   # best comp for next up

            # weights for our turn now
            full_data_update(temp_field_data, coord, color, enemy_color, stack, turn_num=i, bot_weights=bot_weights)
            our_weight = weight_calc(temp_field_data, color, )
            enemy_weight = weight_calc(temp_field_data, enemy_color, )

            # weights if enemy same turn
            full_data_update(enemy_alt_data, coord, enemy_color, color, stack, turn_num=i + 1, bot_weights=bot_weights)
            alt_our_weight = weight_calc(enemy_alt_data, color, )
            alt_enemy_weight = weight_calc(enemy_alt_data, enemy_color, )  # cool fork pred

            # weights after enemy up turn on our
            over_coord = (coord[0], coord[1], coord[2] + 1) if coord[2] < Configs.SHAPE else None
            if over_coord is not None:
                full_data_update(temp_field_data, over_coord, enemy_color, color, stack, turn_num=i + 1, bot_weights=bot_weights)
                our_future_weight = weight_calc(temp_field_data, color, )
                enemy_future_weight = weight_calc(temp_field_data, enemy_color, )  # cool fork pred
            else:
                our_future_weight = start_our_weight
                enemy_future_weight = start_enemy_weight

            enemy_improv_for_fork_now = -(alt_enemy_weight - start_enemy_weight)  # when very good we need block it
            enemy_improv_for_fork_up = (enemy_future_weight - start_enemy_weight)

            our_improv_for_alt_enemy_turn = (alt_our_weight - start_our_weight)
            our_improv_for_enemy_up_turn = (our_future_weight - start_our_weight)

            if (our_improv_for_alt_enemy_turn < -bot_weights.win_points // 10) or (our_improv_for_enemy_up_turn < -bot_weights.win_points // 10):
                best_our_weight = our_weight - enemy_improv_for_fork_now - enemy_improv_for_fork_up + \
                                  our_improv_for_alt_enemy_turn + our_improv_for_enemy_up_turn
            else:
                best_our_weight = our_weight - enemy_improv_for_fork_now - enemy_improv_for_fork_up

            coords_weights[coord] = best_our_weight - enemy_weight# our_weight - enemy_weight

            # debug_weights[coord] = {'was': {'our': start_our_weight, 'enemy': start_enemy_weight, },
            #                          "now_we": {'our': our_weight, 'enemy': enemy_weight, },
            #                          'alt_enemy': {'our': alt_our_weight, 'enemy': alt_enemy_weight, },
            #                          "next_up_enemy": {'our': our_future_weight, 'enemy': enemy_future_weight, }}

            # if any([start_our_weight > 1e5, start_enemy_weight > 1e5, our_weight > 1e5, enemy_weight > 1e5,
            #     alt_our_weight > 1e5, alt_enemy_weight > 1e5, our_future_weight > 1e5, enemy_future_weight > 1e5]):
            #     print(color, coord, debug_weights[coord])
            #     ...

        # if i >= 0:
        #     next_min_was = []
        #     next_min_now = []
        #     next_min_alt = []
        #     for ind, val in debug_weights.items():
        #         if val['next_up_enemy']['enemy']:
        #             nmw = val['next_up_enemy']['enemy'] - val['was']['enemy']  # best var
        #             nmn = val['next_up_enemy']['enemy'] - val['now_we']['enemy']  # almost always >= 0
        #             nma = val['next_up_enemy']['enemy'] - val['alt_enemy']['enemy']  # almost always <= 0
        #
        #             next_min_was.append(nmw)
        #             next_min_now.append(nmn)
        #             next_min_alt.append(nma)
        #
        #             # print(f"{val['next_up_enemy']['enemy']} - {val['was']['enemy']} = {nmw}")
        #             # print(f"{val['next_up_enemy']['enemy']} - {val['now_we']['enemy']} = {nmn}")
        #             # print(f"{val['next_up_enemy']['enemy']} - {val['alt_enemy']['enemy']} = {nmn}")
        #             # print()
        #     print(f'up - was {next_min_was}')
        #     print(f'up - now {next_min_now}')
        #     print(f'up - alt {next_min_alt}')

        # coords_weights = filter_weight_calc(field_data_dct=field_data_variants, color=color, enemy_color=enemy_color,
        #                                     stack=stack, turn_number=i)

        coords_arr = list(dict(sorted(coords_weights.items(), key=lambda item: item[1], reverse=True)).keys())

    if i >= 46:
        ...

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
