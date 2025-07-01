from constants import *
from utils import under_points, gravity_correction

bad_fork_logs = {'bad_one_line_cross_fork': {},
                 'bad_dead_point_cross_fork': {},
                 'bad_over_fork': {}}

fork_logs = {'cross_fork': {},
             'over_fork': {}}


def filter_lines_stack(orig_lines_set, coord, my_turn=True, bot_weights=Bot_4_lvl(), stack=None):
    # new_lines_set =  deepcopy({k: deepcopy(v) for k, v in orig_lines_set.items()})
    new_lines_set =  deepcopy(orig_lines_set)

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


def filter_weight_calc(field_data, color, enemy_color, bot_weights=Bot_4_lvl(), stack=None, turn_number=None):
    coords_weights = {}
    num_player = 1 if (len(stack[color]) == len(stack[enemy_color])) else 2

    # if bot_weights is None:
    #     bot_weights = Bot_4_lvl()
    deb_flag = False

    for coord, val in field_data.items():
        over_coord = (coord[0], coord[1], coord[2] + 1) if (coord[2] < 4) else None

        # lines_points
        # our_lines_points1 = sum([bot_weights.diff_line_weights(line, points, stack) for line, points in val[color]['lines_left'].items()])
        # enemy_lines_points1 = sum([bot_weights.diff_line_weights(line, points, stack) for line, points in val[enemy_color]['lines_left'].items()])
        our_lines_points1 = sum([data['weight'] for line, data in val[color]['lines_left'].items()])
        enemy_lines_points1 = sum([data['weight'] for line, data in val[enemy_color]['lines_left'].items()])
        our_lines_points_weights = our_lines_points1 - enemy_lines_points1

        # our_3rd_dead_points_weights = bot_weights.dead_points_weights(val[color]['dead_points'], val[enemy_color]['dead_points'], num_player,)
        our_3rd_dead_points_weights1 = sum([v['weight'] for i, v in val[color]['dead_points'].items()])
        enemy_3rd_dead_points_weights1 = sum([v['weight'] for i, v in val[enemy_color]['dead_points'].items()])
        our_3rd_dead_points_weights = our_3rd_dead_points_weights1 - enemy_3rd_dead_points_weights1

        # if our_3rd_dead_points_weights != 0:
        #     ...

        # our_over_fork_weights1, enemy_over_fork_weights1 = bot_weights.over_fork_weights(val[color]['over_forks_left'], val[enemy_color]['over_forks_left'],
        #                                                     val[color]['dead_points'], val[enemy_color]['dead_points'])
        our_over_fork_weights1 = sum([v['weight'] for i, v in val[color]['over_forks_left'].items()])
        enemy_over_fork_weights1 = sum([v['weight'] for i, v in val[enemy_color]['over_forks_left'].items()])
        our_over_fork_weights = our_over_fork_weights1 - enemy_over_fork_weights1

        # our_cross_fork_weights1, enemy_cross_fork_weights1 = bot_weights.cross_fork_weights(val[color]['cross_forks_left'], val[enemy_color]['cross_forks_left'], stack)
        our_cross_fork_weights1 = sum([v['weight'] for i, v in val[color]['cross_forks_left'].items()])
        enemy_cross_fork_weights1 = sum([v['weight'] for i, v in val[enemy_color]['cross_forks_left'].items()])
        our_cross_fork_weights = our_cross_fork_weights1 - enemy_cross_fork_weights1

        # if over_coord is not None:
        #     stack_copy = deepcopy(stack)
        #     stack_copy[color].append(list(over_coord))
        #
        #     our_lines_points2 = sum([bot_weights.diff_line_weights(line, points, stack_copy) for line, points in val[enemy_color]['lines_left'].items()])
        #     enemy_lines_points2 = sum([bot_weights.diff_line_weights(line, points, stack_copy) for line, points in val[color]['lines_left'].items()])
        #     enemy_lines_points_weights = our_lines_points2 - enemy_lines_points2
        #
        #     enemy_3rd_dead_points = bot_weights.dead_points_weights(val[enemy_color]['dead_points'], val[color]['dead_points'], num_player, )
        #
        #     enemy_over_fork_weights2, our_over_fork_weights2 = bot_weights.over_fork_weights(val[enemy_color]['over_forks_left'], val[color]['over_forks_left'],
        #                                                           val[enemy_color]['dead_points'], val[color]['dead_points'])
        #     enemy_over_fork_weights = enemy_over_fork_weights2 - our_over_fork_weights2
        #
        #     enemy_cross_fork_weights2, our_cross_fork_weights2 = bot_weights.cross_fork_weights(val[enemy_color]['cross_forks_left'], val[color]['cross_forks_left'], stack_copy)
        #     enemy_cross_fork_weights = enemy_cross_fork_weights2 - our_cross_fork_weights2
        #

        # force moves
        ...


        coords_weights[coord] = our_lines_points_weights + our_3rd_dead_points_weights + our_over_fork_weights + our_cross_fork_weights # - \
            # enemy_lines_points_weights - enemy_3rd_dead_points - enemy_over_fork_weights - enemy_cross_fork_weights

    return coords_weights
# ____________________________________________________________


def find_force_moves():
    return


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

            if (p_under is not None) and (p_under not in stack_points) and (p_under != tuple(coord)):
                our_dead_points[p] = {'layer': p[2], 'type': None, 'weight': 0, 'under_slots': p_under_lst, 'fork_move': None}
                our_copy.append(p)

    enemy_dead_points = {}
    enemy_copy = []
    for line, points in enemy_lines_dct.items():
        points = points['points']
        if len(points) == 3:
            p = list(line - set(points))[0]
            p_under_lst = [(p[0], p[1], p[2] - i) for i in range(1, p[2])]
            p_under = p_under_lst[0] if p_under_lst else None

            if (p_under is not None) and (p_under not in stack_points) and (p_under != tuple(coord)):
                enemy_dead_points[p] = {'layer': p[2], 'type': None, 'weight': 0, 'under_slots': p_under_lst, 'fork_move': None}
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
            v['weight'] = bot_weights.win_points // (len(v['under_slots']) + 1)
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
            v['weight'] = bot_weights.win_points // (len(v['under_slots']) + 1)
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

        if (coord in cross_fork[0]) or (coord in cross_fork[1]):
            if my_turn:
                points.append(coord)
                if ((len(set(points) & cross_fork[0]) == 3) or (len(set(points) & cross_fork[1]) == 3)) \
                        and (com_point not in points):
                    # bad_fork_logs['bad_one_line_cross_fork'][cross_fork] = points
                    pop_lst.append(cross_fork)

                # TODO: [21.06.2025 by Leo]
                elif (com_point in points) and (len(points) < 5):
                    # bad_fork_logs['bad_dead_point_cross_fork'][cross_fork] = points
                    pop_lst.append(cross_fork)
                else:
                    fork_logs['cross_fork'][cross_fork] = points

                if (len(points) >= 5) and (cross_fork not in pop_lst):
                    p_1 = list(cross_fork[0] - set(points) - {com_point})
                    p_2 = list(cross_fork[1] - set(points) - {com_point})
                    if len(p_1) and len(p_2):
                        p_1 = p_1[0]
                        p_2 = p_2[0]
                        new_cross_forks_set[cross_fork]['final_pair'] = {(p_1), (p_2)}

                        if (gravity_correction(list(p_1), stack) == list(p_1)) and (gravity_correction(list(p_2), stack) == list(p_2)) \
                            and (com_point in points):
                            win_weight = bot_weights.win_points
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
                # (len(set(points) & set(fork_points)) == 1)
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
                            win_weight = bot_weights.win_points // 2
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

def full_data_update():
    return