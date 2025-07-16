import itertools
import pickle
import jmespath as jp
from constants import *
from utils import under_points, gravity_correction

bad_fork_logs = {'bad_one_line_cross_fork': {},
                 'bad_dead_point_cross_fork': {},
                 'bad_over_fork': {}}

fork_logs = {'cross_fork': {},
             'over_fork': {}}


def win_check_from_db(stack, coords, color):
    for line in itertools.combinations(stack[color], Configs.SHAPE):
        if coords in line:
            if set([tuple(i) for i in line]) in dict_of_shapes_wins[Configs.SHAPE]:
                return line
    return False


def pos_turns(coords_arr, stack, color, enemy_color):
    weight = 0

    # check for win turns
    for coord in coords_arr:
        temp_stack = pickle.loads(pickle.dumps(stack, -1))
        temp_stack[color].append(coord)

        if win_check_from_db(temp_stack, coord, color):
            weight = 1e6
            return [tuple([coord, weight])]

    # check for loosing turns
    # where to move to close enemy line
    for coord in coords_arr:
        temp_stack = pickle.loads(pickle.dumps(stack, -1))
        temp_stack[enemy_color].append(coord)

        if win_check_from_db(temp_stack, coord, enemy_color):
            # print('force move', end=' ')  # TODO: [02.07.2025 by Leo]
            return [tuple([coord, weight])]

    pos_turns_count = len(coords_arr)
    # print(f"{pos_turns = }")

    # remove turns under loose (forbieden turns)
    coords_arr_c = coords_arr.copy()
    for coord in coords_arr_c:
        temp_stack = pickle.loads(pickle.dumps(stack, -1))
        temp_coord = deepcopy(coord)
        temp_coord[-1] += 1
        temp_stack[enemy_color].append(temp_coord)

        if win_check_from_db(temp_stack, temp_coord, enemy_color):
            coords_arr.remove(coord)

    if len(coords_arr) == 0:
        print('no good turns found')
        weight = -1e6
        return [tuple([coord, weight])]

    return [(i, 0) for i in coords_arr]


def z_shift_point(point, z_shift):
    if isinstance(point, tuple):
        return (point[0], point[1], point[2] + z_shift)
    elif isinstance(point, list):
        return [point[0], point[1], point[2] + z_shift]
    return None


def up_layer(stack, return_tuple=False):
    coords_arr = [list(coords) for coords in itertools.product(*[[*range(1, Configs.SHAPE + 1)]] * DIMENSION)]
    coords_arr = [gravity_correction(coords, stack) for coords in coords_arr]
    coords_arr = [list(i) for i in set(tuple(j) for j in coords_arr)] if Configs.GRAVITY else coords_arr
    if return_tuple:
        coords_arr = [tuple(coords) for coords in coords_arr if coords not in itertools.chain(*stack.values())]
    else:
        coords_arr = [coords for coords in coords_arr if coords not in itertools.chain(*stack.values())]

    return coords_arr


def filter_lines_stack(orig_lines_set, coord, my_turn=True, bot_weights=Bot_4_lvl(), stack=None,):
    # new_lines_set =  deepcopy({k: deepcopy(v) for k, v in orig_lines_set.items()})
    new_lines_set = pickle.loads(pickle.dumps(orig_lines_set, -1))

    pop_lst = []

    for line, dct in new_lines_set.items():
        if coord in line:
            if my_turn:
                new_lines_set[line]['points'].append(coord)
                new_lines_set[line]['weight'] = bot_weights.diff_line_weights(line, new_lines_set[line]['points'], stack)
            else:
                pop_lst.append(line)

    for p in pop_lst:
        new_lines_set.pop(p)

    return new_lines_set


def weight_calc(field_data, color):
    # over_coord = (coord[0], coord[1], coord[2] + 1) if (coord[2] < 4) else None

    # lines_points
    our_lines_points1 = sum([data['weight'] for line, data in field_data[color]['lines_left'].items()])
    our_3rd_dead_points_weights1 = sum([v['weight'] for i, v in field_data[color]['dead_points'].items()])

    # forks points
    our_over_fork_weights1 = sum([v['weight'] for i, v in field_data[color]['over_forks_left'].items()])
    our_cross_fork_weights1 = sum([v['weight'] for i, v in field_data[color]['cross_forks_left'].items()])

    # force moves
    force_moves_weights = sum([v['weight'] for i, v in field_data[color]['force_moves'].items()])

    our_after_turn_sum = our_lines_points1 + our_3rd_dead_points_weights1 + our_over_fork_weights1 + our_cross_fork_weights1 + force_moves_weights

    return our_after_turn_sum


# def filter_weight_calc(field_data_dct, color, enemy_color, stack=None, turn_number=None):
#     coords_weights = {}
#     # num_player = 1 if (len(stack[color]) == len(stack[enemy_color])) else 2
#
#     # if bot_weights is None:
#     #     bot_weights = Bot_4_lvl()
#     deb_flag = False
#
#     for coord, val in field_data_dct.items():
#         our_after_turn_sum = weight_calc(val, color, )
#         enemy_after_block_sum = weight_calc(val, enemy_color, )
#
#         coords_weights[coord] = our_after_turn_sum - enemy_after_block_sum
#
#     return coords_weights
# ____________________________________________________________


def find_force_moves(field_data, coord, color, stack=None, bot_weights=Bot_5_lvl(), turn_num=None, my_turn=True, comment='', enemy_color=None,):
    force_moves = {}

    two_point_lines = {i: v for i, v in field_data[color]['lines_left'].items() if len(v['points']) == 2}
    three_point_lines = {i: v for i, v in field_data[color]['lines_left'].items() if len(v['points']) == 3}

    # if color == 'black':
    #     ...

    for line, v in three_point_lines.items():
        last_point = list(set(line) - set(v['points']))[0]
        if last_point in field_data[enemy_color]['dead_points']:
            continue

        if last_point in field_data[color]['up_layer']:
            # if comment in ()
            if coord not in force_moves:
                force_moves[coord] = {'force_coord': [last_point], 'weight': -bot_weights.force_weight}
            else:
                force_moves[coord]['force_coord'].append(last_point)
                if len(set(force_moves[coord]['force_coord'])) >= 2:
                    force_moves[coord]['weight'] = bot_weights.win_points_force

            if (last_point[0], last_point[1], last_point[2] + 1) in field_data[color]['dead_points']:
                force_moves[coord] = {'force_coord': [last_point], 'weight': bot_weights.win_points_force}

    for line, v in two_point_lines.items():
        empty_points = list(set(line) - set(v['points']))

        # Проверяем, находятся ли оба пустых места на верхнем доступном слое
        if all([(i in field_data[color]['up_layer']) for i in empty_points]):
            if z_shift_point(empty_points[0], 1) not in field_data[enemy_color]['dead_points']:
                if (empty_points[0] not in force_moves):
                    force_moves[empty_points[0]] = {'force_coord': [empty_points[1]], 'weight': bot_weights.force_weight}
                else:
                    force_moves[empty_points[0]]['force_coord'].append(empty_points[1])
                    # if not my_turn:
                        # force_moves[empty_points[0]]['weight'] = bot_weights.win_points_force

            if z_shift_point(empty_points[1], 1) not in field_data[enemy_color]['dead_points']:
                if empty_points[1] not in force_moves:
                    force_moves[empty_points[1]] = {'force_coord': [empty_points[0]], 'weight': bot_weights.force_weight}
                else:
                    force_moves[empty_points[1]]['force_coord'].append(empty_points[0])
                    # if not my_turn:
                    #     force_moves[empty_points[1]]['weight'] = bot_weights.win_points_force

        # Проверяем, может ли верхняя точка упасть на нижнюю по гравитации
        elif tuple(gravity_correction(list(max(empty_points)), stack)) == min(empty_points):
            if max(empty_points) not in field_data[enemy_color]['dead_points']:
                if min(empty_points) not in force_moves:
                    force_moves[min(empty_points)] = {'force_coord': [max(empty_points)], 'weight': bot_weights.force_weight}
                else:
                    force_moves[min(empty_points)]['force_coord'].append(max(empty_points))
                    # if not my_turn:
                    #     force_moves[min(empty_points)]['weight'] = bot_weights.win_points_force


    # three_point_dead_line = {}  # force move under dead_point
    for d_p in field_data[color]['dead_points']:
        f_m = (d_p[0], d_p[1], d_p[2] - 1) if (d_p[2] > 1) else None

        if gravity_correction(list(f_m), stack, return_tuple=True) == f_m:
            if f_m not in force_moves:
                force_moves[f_m] = {'force_coord': [d_p], 'weight': bot_weights.force_weight}
            else:
                force_moves[f_m]['force_coord'].append(d_p)
                force_moves[f_m]['weight'] += bot_weights.force_weight
                # if not my_turn:
                #     force_moves[f_m]['weight'] = bot_weights.win_points_force

    return force_moves


def find_dead_points(our_lines_dct, enemy_lines_dct, coord=None, color=None, stack=None, turn_num=None, up_layer=None,
                     bot_weights=Bot_4_lvl(), enemy_color=None):
    stack_points = (list(stack.values())[0] + list(stack.values())[1])

    our_dead_points = {}
    our_copy = []
    for line, points in our_lines_dct.items():
        points = points['points']
        if len(points) == 3:
            p = list(line - set(points))[0]
            p_under_lst = [(p[0], p[1], p[2] - i) for i in range(1, p[2])]
            p_under = p_under_lst[0] if p_under_lst else None

            if (p_under is not None) and (list(p_under) not in stack_points) and (p_under != tuple(coord)):
                our_dead_points[p] = {'layer': p[2], 'type': None, 'weight': bot_weights.odd_dead_points, 'under_slots': p_under_lst, 'fork_move': None}
                our_copy.append(p)

    enemy_dead_points = {}
    enemy_copy = []
    for line, points in enemy_lines_dct.items():
        points = points['points']
        if len(points) == 3:
            p = list(line - set(points))[0]
            p_under_lst = [(p[0], p[1], p[2] - i) for i in range(1, p[2])]
            p_under = p_under_lst[0] if p_under_lst else None

            if (p_under is not None) and (list(p_under) not in stack_points) and (p_under != tuple(coord)):
                enemy_dead_points[p] = {'layer': p[2], 'type': None, 'weight': bot_weights.odd_dead_points, 'under_slots': p_under_lst, 'fork_move': None}
                enemy_copy.append(p)

    # if our_dead_points != {i: v for i, v in our_dead_points.items() if not (set(v['under_slots']) & set(enemy_copy))} \
    #         or enemy_dead_points != {i: v for i, v in enemy_dead_points.items() if not (set(v['under_slots']) & set(our_copy))}:
    #     ...
    our_dead_points = {i: v for i, v in our_dead_points.items() if not (set(v['under_slots']) & set(enemy_copy))} # set(our_dead_points) - set(enemy_copy)
    enemy_dead_points = {i: v for i, v in enemy_dead_points.items() if not (set(v['under_slots']) & set(our_copy))}

    if turn_num == 39:
        ...
    for dp, v in our_dead_points.items():
        if v['under_slots'][0] in our_dead_points:
            v['type'] = 'fork'
            v['weight'] = bot_weights.win_points_dead // (len(v['under_slots']) + 1)
            v['fork_move'] = set(v['under_slots'])

        elif v['layer'] == 3:
            if dp in enemy_dead_points:
                v['type'] = 'com'
            else:
                v['type'] = 'own'
                v['weight'] = bot_weights.own_3rd_dead_point

    for dp, v in enemy_dead_points.items():
        if v['under_slots'][0] in enemy_dead_points:
            v['type'] = 'fork'
            v['weight'] = bot_weights.win_points_dead // (len(v['under_slots']) + 1)
            v['fork_move'] = set(v['under_slots'])

        elif v['layer'] == 3:
            if dp in our_dead_points:
                v['type'] = 'com'
            else:
                v['type'] = 'own'
                v['weight'] = bot_weights.own_3rd_dead_point


    com_points = [i for i, v in enemy_dead_points.items() if v['type'] == 'com']
    if len(com_points):
        com_points_weight = bot_weights.common_3rd_dead_point / len(com_points) if (turn_num % 2) != (len(com_points) % 2) \
            else -bot_weights.common_3rd_dead_point / len(com_points)
    else:
        com_points_weight = 0


    for dp in com_points:
        our_dead_points[dp]['weight'] = com_points_weight
        enemy_dead_points[dp]['weight'] = -com_points_weight
        ...

    return our_dead_points, enemy_dead_points
# ___________________________________________________________


def filter_cross_forks_stack(coord, my_turn=True, field_data=None, color=None, enemy_color=None, stack=None, bot_weights=Bot_4_lvl()):
    new_cross_forks_set = (field_data[color]['cross_forks_left']) if my_turn else (field_data[enemy_color]['cross_forks_left'])
    pop_lst = []

    for cross_fork in new_cross_forks_set:
        win_weight = 0
        com_point = new_cross_forks_set[cross_fork]['common_point']

        points = new_cross_forks_set[cross_fork]['points']
        # non_com_points = ...

        if (coord in cross_fork[0]) or (coord in cross_fork[1]):
            if my_turn:
                points.append(coord)
                if ((len(set(points) & cross_fork[0]) == 3) or (len(set(points) & cross_fork[1]) == 3)) \
                        and (com_point not in points):
                    bad_fork_logs['bad_one_line_cross_fork'][cross_fork] = points
                    pop_lst.append(cross_fork)

                # TODO: [21.06.2025 by Leo]
                elif (com_point in points) and (len(points) < 5):
                    bad_fork_logs['bad_dead_point_cross_fork'][cross_fork] = points
                    pop_lst.append(cross_fork)
                else:
                    fork_logs['cross_fork'][cross_fork] = points

                # if dead points under com_point
                ...

                if (len(points) >= 5) and (cross_fork not in pop_lst):
                    p_1 = list(cross_fork[0] - set(points) - {com_point})
                    p_2 = list(cross_fork[1] - set(points) - {com_point})
                    if len(p_1) and len(p_2):
                        p_1 = p_1[0]
                        p_2 = p_2[0]
                        new_cross_forks_set[cross_fork]['final_pair'] = {(p_1), (p_2)}

                        if (gravity_correction(list(p_1), stack) == list(p_1)) and (gravity_correction(list(p_2), stack) == list(p_2)) \
                            and (com_point in points):
                            win_weight = bot_weights.win_points_cross
                    # elif not (set(under_points(p_1)) & set(field_data[enemy_color]['dead_points'].keys())):
                    #     win_weight = bot_weights.win_points // 2
            else:
                pop_lst.append(cross_fork)

        # win_weight = 0
        new_cross_forks_set[cross_fork]['weight'] = win_weight + \
            bot_weights.fork_weights[len(cross_fork[0] & set(points))] + bot_weights.fork_weights[len(cross_fork[1] & set(points))]

    for p in set(pop_lst):
        new_cross_forks_set.pop(p)

    return new_cross_forks_set


# def filter_cross_forks_weight_calc(cross_fork_set_dct, color, enemy_color, bot_weights, stack):
#     coords_weights = {}
#
#     return coords_weights
# ____________________________________________________________


def filter_over_forks_stack(coord, my_turn=True, color=None, enemy_color=None,  field_data=None, stack=None, bot_weights=Bot_4_lvl()):
    new_over_forks_set = (field_data[color]['over_forks_left']) if my_turn else (field_data[enemy_color]['over_forks_left'])  # TODO: [30.06.2025 by Leo] very slow
    pop_lst = []

    for over_fork in new_over_forks_set:
        win_weight = 0
        points = new_over_forks_set[over_fork]['points']
        fork_points = new_over_forks_set[over_fork]['fork_points']

        if (coord in over_fork[0]) or (coord in over_fork[1]):
            if my_turn:
                points.append(coord)

                # if dead points under fork_points
                ...

                # TODO: [21 \ 30.06.2025 by Leo] 5 or 6 before fork closing
                if len(points) != 7: # >= 5
                    d_p = [fp for fp in fork_points if not (fp & set(points))]
                    if not d_p:
                        bad_fork_logs['bad_over_fork'][over_fork] = points
                        pop_lst.append(over_fork)
                    else:
                        fork_logs['over_fork'][over_fork] = points
                        # TODO: [30.06.2025 by Leo] need we extra weight calcs for closed fork?
                        if (len(d_p) == 1) and (len((over_fork[0] | over_fork[1]) - set(points)) == 2) \
                                and not (set(under_points(max(d_p[0]))) & set(field_data[enemy_color]['dead_points'])):
                            win_weight = bot_weights.win_points_over // 2
            else:
                pop_lst.append(over_fork)

        # win_weight = 0
        new_over_forks_set[over_fork]['weight'] =  win_weight + \
            bot_weights.fork_weights[len(over_fork[0] & set(points))] + bot_weights.fork_weights[len(over_fork[1] & set(points))]

    for p in pop_lst:
        new_over_forks_set.pop(p)

    return new_over_forks_set

def filter_over_cross_forks_stack(orig_over_cross_forks_set, coord, my_turn=True,  field_data=None, stack=None, bot_weights=Bot_4_lvl()):
    return


def full_data_update(temp_field_data, coord, color, enemy_color, stack, turn_num, bot_weights=Bot_4_lvl(), comment=''):
    our_field = temp_field_data[color]
    enemy_field = temp_field_data[enemy_color]

    copy_stack = pickle.loads(pickle.dumps(stack, -1))
    copy_stack[color].append(list(coord))

    # filter lines left
    our_field['lines_left'] = filter_lines_stack(our_field['lines_left'], coord, my_turn=True, stack=copy_stack)
    enemy_field['lines_left'] = filter_lines_stack(enemy_field['lines_left'], coord, my_turn=False, stack=copy_stack)

    # operations with dead points  # TODO: [21.06.2025 by Leo]
    our_field['dead_points'], enemy_field['dead_points'] = find_dead_points(our_field['lines_left'],
                                                                            enemy_field['lines_left'], color=color,
                                                                            stack=copy_stack, coord=coord,  # is copy_stack right?
                                                                            up_layer=temp_field_data[color]['up_layer'],
                                                                            bot_weights=bot_weights, turn_num=turn_num)

    # find force moves combs  # TODO: [04.07.2025 by Leo]
    our_field['up_layer'] = up_layer(copy_stack, return_tuple=True)
    enemy_field['up_layer'] = up_layer(copy_stack, return_tuple=True)

    our_field['force_moves'] = find_force_moves(temp_field_data, coord=coord, color=color, stack=copy_stack, comment=comment, enemy_color=enemy_color)
    enemy_field['force_moves'] = find_force_moves(temp_field_data, coord=coord, color=enemy_color, stack=copy_stack, my_turn=False, comment=comment, enemy_color=color)

    # filter cross forks
    our_field['cross_forks_left'] = filter_cross_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=True,
                                                             field_data=temp_field_data, stack=copy_stack,  # is copy_stack right?
                                                             bot_weights=bot_weights)
    enemy_field['cross_forks_left'] = filter_cross_forks_stack(coord, enemy_color=enemy_color, color=color,
                                                               my_turn=False,
                                                               field_data=temp_field_data, stack=copy_stack,  # is copy_stack right?
                                                               bot_weights=bot_weights)

    # filter over forks
    our_field['over_forks_left'] = filter_over_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=True,
                                                           field_data=temp_field_data, stack=copy_stack,
                                                           bot_weights=bot_weights)
    enemy_field['over_forks_left'] = filter_over_forks_stack(coord, enemy_color=enemy_color, color=color, my_turn=False,
                                                             field_data=temp_field_data, stack=copy_stack,
                                                             bot_weights=bot_weights)

    stack[color].append(list(coord))


def build_chains(fm_dct, new_field_data, turn_num, new_stack, cur_color, cur_enemy_color, bot_weights=Bot_5_lvl(), comment=''):
    chains = []

    def dfs(current_fd, chain, turn_num, up_field_data, up_stack, our_w_diff=0, enemy_w_diff=0, comment=comment):
        # Depth-First Search
        # Базовый случай: если словарь пуст, сохраняем цепочку
        if not current_fd:
            chains.append(chain.copy())
            return

        if chain and ((abs(our_w_diff) >= bot_weights.th_points) or (abs(enemy_w_diff) >= bot_weights.th_points)):
            chains.append(chain.copy())
            return

        # Иначе — для каждого ключа/значения создаём новый ответвляющийся путь
        for k, v in current_fd.items():
            new_fd = pickle.loads(pickle.dumps(up_field_data, -1))
            new_st = pickle.loads(pickle.dumps(up_stack, -1))

            pos_turns_arr = pos_turns(up_layer(up_stack, return_tuple=False), up_stack, cur_color, cur_enemy_color)
            coords_arr = [tuple(i[0]) for i in pos_turns_arr]
            # if len(pos_turns_arr) == 1:
            #     next_fd = new_fd[cur_color]['force_moves']
            #     next_fd.pop(k)
            #     if chain and (chain not in chains):
            #         dfs(next_fd, chain, turn_num, new_fd, new_st)

            our_weights0 = weight_calc(new_fd, cur_color, )
            enemy_weights0 = weight_calc(new_fd, cur_enemy_color, )
            start_weight0 = our_weights0 - enemy_weights0

            if (k[0], k[1], k[2]) in coords_arr: # not in up_field_data[cur_enemy_color]['dead_points']:
                # 2) Получим следующий словарь
                full_data_update(new_fd, k, cur_color, cur_enemy_color, stack=new_st, turn_num=turn_num)

                our_weights1 = weight_calc(new_fd, cur_color, )
                enemy_weights1 = weight_calc(new_fd, cur_enemy_color, )
                weight1 = our_weights1 - enemy_weights1

                full_data_update(new_fd, v['force_coord'][0], cur_enemy_color, cur_color, stack=new_st, turn_num=turn_num + 1)
                our_weights2 = weight_calc(new_fd, cur_color)
                enemy_weights2 = weight_calc(new_fd, cur_enemy_color, )
                weight2 = enemy_weights2 - our_weights2

                next_fd = new_fd[cur_color]['force_moves']  # transform(current_fd, k, v)

                # 1) Запомним текущий шаг
                chain.append({k: weight1})
                chain.append({v['force_coord'][0]: weight2})

                # 3) Спустимся глубже
                dfs(next_fd, chain, turn_num + 2, new_fd, new_st, comment=comment,
                    our_w_diff=our_weights2 - our_weights0, enemy_w_diff=enemy_weights2 - enemy_weights0)

                # 4) Откатим изменения chain для следующей ветки
                chain.pop()
                chain.pop()
            else:
                if len(coords_arr) >= 1:
                    next_fd = new_fd[cur_color]['force_moves']
                    next_fd.pop(k)
                    if chain and (chain not in chains):
                        dfs(next_fd, chain, turn_num, new_fd, new_st)
                else:
                    chain.append({coords_arr[0][0]: coords_arr[0][1]})
                    dfs({}, chain, turn_num, new_fd, new_st, coords_arr[0][1], -coords_arr[0][1], comment=comment)

    # Запускаем обход
    dfs(fm_dct, [], turn_num, new_field_data, new_stack)
    return chains
