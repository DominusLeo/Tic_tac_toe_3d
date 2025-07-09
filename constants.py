from copy import deepcopy

DIMENSION = 3
turns_alpha = 0.9
need_size_cf = False

def create_intersecting_lines_dict():
    """
    Создает словарь пар линий, которые пересекаются в одной точке,
    аналогично dict_of_shapes_wins, но вместо отдельных линий - пары пересекающихся линий.
    """
    dict_of_intersecting_lines = {i: [] for i in range(2, 10)}

    for shape_size in dict_of_shapes_wins:
        if not dict_of_shapes_wins[shape_size]:  # пропускаем пустые размеры
            continue

        lines_list = list(dict_of_shapes_wins[shape_size])
        intersecting_pairs = []

        # Проверяем все возможные пары линий
        for i in range(len(lines_list)):
            for j in range(i + 1, len(lines_list)):
                line1 = lines_list[i]
                line2 = lines_list[j]

                # Находим пересечение двух линий (общие точки)
                intersection = line1 & line2

                # Если линии пересекаются ровно в одной точке
                if len(intersection) == 1:
                    intersecting_pairs.append((line1, line2))

        dict_of_intersecting_lines[shape_size] = intersecting_pairs

    return dict_of_intersecting_lines


def find_adjacent_z_intersections(line1, line2):
    """
    Находит пары точек с одинаковыми X,Y и соседними Z координатами (разница = 1).

    Args:
        line1: первая линия
        line2: вторая линия

    Returns:
        list: список пар соседних по Z точек
    """
    adjacent_pairs = []

    for point1 in line1:
        for point2 in line2:
            x1, y1, z1 = point1
            x2, y2, z2 = point2

            # Проверяем одинаковые X,Y и соседние Z (разница = 1)
            if x1 == x2 and y1 == y2 and abs(z1 - z2) == 1:
                if z1 < z2:
                    adjacent_pairs.append((point1, point2))
                else:
                    adjacent_pairs.append((point2, point1))

    return tuple(adjacent_pairs)


def create_adjacent_z_intersecting_lines_dict():
    """
    Создает словарь пар линий, которые пересекаются в точках с соседними Z координатами
    (например, (1,1,1) и (1,1,2) - разница в Z равна 1).

    Returns:
        dict: словарь с парами линий, пересекающимися в соседних по Z точках
    """
    dict_of_adjacent_z_lines = {i: [] for i in range(2, 10)}

    # TODO: [22.06.2025 by Leo]
    # remove vertical lines
    ...

    for shape_size in dict_of_shapes_wins:
        if not dict_of_shapes_wins[shape_size]:
            continue

        lines_list = list(dict_of_shapes_wins[shape_size])
        adjacent_z_pairs = []

        for i in range(len(lines_list)):
            for j in range(i + 1, len(lines_list)):
                line1 = lines_list[i]
                line2 = lines_list[j]

                # Ищем пересечения с соседними Z
                adjacent_intersections = find_adjacent_z_intersections(line1, line2)

                if adjacent_intersections:
                    if (len(set(adjacent_intersections[0]) & line1) == 2) or (len(set(adjacent_intersections[0]) & line2) == 2):
                        continue
                    adjacent_z_pairs.append((line1, line2, adjacent_intersections[0]))

        dict_of_adjacent_z_lines[shape_size] = adjacent_z_pairs

    return dict_of_adjacent_z_lines





dict_of_shapes_wins = {i: [] for i in range(2, 10)}

# TODO: [11.10.2021 by Lev] WA, need to remake
dict_of_shapes_wins[3] = [{(1, 1, 3), (1, 1, 1), (1, 1, 2)}, {(1, 2, 1), (1, 3, 1), (1, 1, 1)},
                          {(1, 2, 2), (1, 1, 1), (1, 3, 3)}, {(2, 1, 1), (3, 1, 1), (1, 1, 1)},
                          {(3, 1, 3), (2, 1, 2), (1, 1, 1)}, {(3, 3, 1), (1, 1, 1), (2, 2, 1)},
                          {(3, 3, 3), (1, 1, 1), (2, 2, 2)}, {(1, 2, 2), (1, 3, 2), (1, 1, 2)},
                          {(2, 1, 2), (3, 1, 2), (1, 1, 2)}, {(2, 2, 2), (3, 3, 2), (1, 1, 2)},
                          {(1, 1, 3), (1, 2, 2), (1, 3, 1)}, {(1, 1, 3), (1, 2, 3), (1, 3, 3)},
                          {(1, 1, 3), (2, 1, 2), (3, 1, 1)}, {(1, 1, 3), (2, 1, 3), (3, 1, 3)},
                          {(1, 1, 3), (3, 3, 1), (2, 2, 2)}, {(1, 1, 3), (2, 2, 3), (3, 3, 3)},
                          {(1, 2, 1), (1, 2, 2), (1, 2, 3)}, {(1, 2, 1), (3, 2, 1), (2, 2, 1)},
                          {(1, 2, 1), (3, 2, 3), (2, 2, 2)}, {(1, 2, 2), (3, 2, 2), (2, 2, 2)},
                          {(3, 2, 1), (1, 2, 3), (2, 2, 2)}, {(2, 2, 3), (1, 2, 3), (3, 2, 3)},
                          {(1, 3, 1), (1, 3, 2), (1, 3, 3)}, {(1, 3, 1), (3, 1, 1), (2, 2, 1)},
                          {(3, 1, 3), (1, 3, 1), (2, 2, 2)}, {(2, 3, 1), (3, 3, 1), (1, 3, 1)},
                          {(2, 3, 2), (1, 3, 1), (3, 3, 3)}, {(1, 3, 2), (3, 1, 2), (2, 2, 2)},
                          {(3, 3, 2), (2, 3, 2), (1, 3, 2)}, {(3, 1, 1), (1, 3, 3), (2, 2, 2)},
                          {(2, 2, 3), (3, 1, 3), (1, 3, 3)}, {(3, 3, 1), (2, 3, 2), (1, 3, 3)},
                          {(3, 3, 3), (2, 3, 3), (1, 3, 3)}, {(2, 1, 1), (2, 1, 2), (2, 1, 3)},
                          {(2, 3, 1), (2, 1, 1), (2, 2, 1)}, {(2, 1, 1), (2, 3, 3), (2, 2, 2)},
                          {(2, 3, 2), (2, 1, 2), (2, 2, 2)}, {(2, 3, 1), (2, 1, 3), (2, 2, 2)},
                          {(2, 2, 3), (2, 3, 3), (2, 1, 3)}, {(2, 2, 3), (2, 2, 1), (2, 2, 2)},
                          {(2, 3, 1), (2, 3, 2), (2, 3, 3)}, {(3, 1, 3), (3, 1, 1), (3, 1, 2)},
                          {(3, 2, 1), (3, 3, 1), (3, 1, 1)}, {(3, 3, 3), (3, 2, 2), (3, 1, 1)},
                          {(3, 2, 2), (3, 3, 2), (3, 1, 2)}, {(3, 1, 3), (3, 3, 1), (3, 2, 2)},
                          {(3, 1, 3), (3, 2, 3), (3, 3, 3)}, {(3, 2, 1), (3, 2, 2), (3, 2, 3)},
                          {(3, 3, 1), (3, 3, 2), (3, 3, 3)}]

dict_of_shapes_wins[4] = ({(4, 1, 4), (4, 4, 4), (4, 2, 4), (4, 3, 4)}, {(2, 4, 4), (2, 1, 1), (2, 3, 3), (2, 2, 2)},
                          {(2, 1, 1), (2, 1, 2), (2, 1, 3), (2, 1, 4)}, {(2, 2, 2), (3, 3, 2), (4, 4, 2), (1, 1, 2)},
                          {(1, 4, 3), (1, 4, 4), (1, 4, 1), (1, 4, 2)}, {(1, 4, 3), (4, 1, 3), (2, 3, 3), (3, 2, 3)},
                          {(2, 2, 3), (2, 3, 2), (2, 4, 1), (2, 1, 4)}, {(1, 2, 1), (1, 3, 1), (1, 1, 1), (1, 4, 1)},
                          {(2, 2, 3), (1, 2, 3), (4, 2, 3), (3, 2, 3)}, {(2, 3, 1), (3, 2, 1), (4, 1, 1), (1, 4, 1)},
                          {(4, 1, 4), (4, 1, 1), (4, 1, 2), (4, 1, 3)}, {(1, 4, 3), (3, 4, 3), (4, 4, 3), (2, 4, 3)},
                          {(4, 4, 4), (4, 4, 1), (4, 4, 2), (4, 4, 3)}, {(4, 4, 4), (4, 1, 1), (4, 3, 3), (4, 2, 2)},
                          {(2, 3, 2), (2, 1, 2), (2, 4, 2), (2, 2, 2)}, {(2, 4, 4), (4, 4, 4), (1, 4, 4), (3, 4, 4)},
                          {(1, 1, 3), (1, 2, 3), (1, 4, 3), (1, 3, 3)}, {(1, 1, 4), (4, 1, 1), (2, 1, 3), (3, 1, 2)},
                          {(3, 4, 2), (4, 4, 2), (2, 4, 2), (1, 4, 2)}, {(2, 4, 4), (2, 4, 1), (2, 4, 2), (2, 4, 3)},
                          {(2, 2, 3), (2, 2, 4), (2, 2, 1), (2, 2, 2)}, {(3, 3, 2), (2, 3, 2), (1, 3, 2), (4, 3, 2)},
                          {(1, 2, 2), (1, 3, 2), (1, 4, 2), (1, 1, 2)}, {(2, 2, 4), (1, 2, 4), (3, 2, 4), (4, 2, 4)},
                          {(4, 1, 4), (1, 4, 4), (2, 3, 4), (3, 2, 4)}, {(4, 1, 4), (2, 3, 2), (3, 2, 3), (1, 4, 1)},
                          {(2, 1, 2), (4, 1, 2), (3, 1, 2), (1, 1, 2)}, {(1, 1, 4), (1, 2, 3), (1, 4, 1), (1, 3, 2)},
                          {(2, 3, 1), (2, 1, 1), (2, 4, 1), (2, 2, 1)}, {(4, 3, 1), (4, 3, 2), (4, 3, 3), (4, 3, 4)},
                          {(4, 4, 2), (4, 3, 2), (4, 1, 2), (4, 2, 2)}, {(1, 1, 3), (1, 1, 4), (1, 1, 1), (1, 1, 2)},
                          {(2, 2, 3), (2, 3, 3), (2, 1, 3), (2, 4, 3)}, {(1, 1, 4), (1, 4, 4), (1, 2, 4), (1, 3, 4)},
                          {(3, 3, 3), (2, 3, 3), (1, 3, 3), (4, 3, 3)}, {(2, 4, 4), (2, 2, 4), (2, 3, 4), (2, 1, 4)},
                          {(2, 3, 2), (4, 1, 2), (3, 2, 2), (1, 4, 2)}, {(1, 1, 3), (2, 2, 3), (3, 3, 3), (4, 4, 3)},
                          {(1, 2, 1), (1, 2, 2), (1, 2, 3), (1, 2, 4)}, {(3, 2, 1), (3, 3, 1), (3, 1, 1), (3, 4, 1)},
                          {(4, 4, 4), (3, 3, 3), (1, 1, 1), (2, 2, 2)}, {(3, 3, 3), (3, 2, 2), (3, 4, 4), (3, 1, 1)},
                          {(4, 3, 4), (2, 3, 2), (1, 3, 1), (3, 3, 3)}, {(3, 3, 2), (4, 3, 1), (2, 3, 3), (1, 3, 4)},
                          {(3, 3, 2), (3, 1, 4), (3, 2, 3), (3, 4, 1)}, {(4, 2, 3), (4, 4, 3), (4, 3, 3), (4, 1, 3)},
                          {(3, 2, 1), (3, 2, 2), (3, 2, 3), (3, 2, 4)}, {(3, 1, 4), (3, 4, 4), (3, 2, 4), (3, 3, 4)},
                          {(1, 2, 1), (3, 2, 1), (2, 2, 1), (4, 2, 1)}, {(4, 3, 1), (4, 1, 1), (4, 4, 1), (4, 2, 1)},
                          {(2, 2, 3), (3, 2, 2), (1, 2, 4), (4, 2, 1)}, {(3, 3, 1), (3, 3, 2), (3, 3, 3), (3, 3, 4)},
                          {(1, 2, 2), (1, 4, 4), (1, 1, 1), (1, 3, 3)}, {(3, 2, 2), (3, 3, 2), (3, 1, 2), (3, 4, 2)},
                          {(2, 1, 1), (4, 1, 1), (3, 1, 1), (1, 1, 1)}, {(1, 3, 1), (1, 3, 2), (1, 3, 3), (1, 3, 4)},
                          {(4, 2, 3), (4, 2, 4), (4, 2, 1), (4, 2, 2)}, {(2, 2, 3), (1, 1, 4), (3, 3, 2), (4, 4, 1)},
                          {(2, 3, 1), (3, 3, 1), (1, 3, 1), (4, 3, 1)}, {(4, 4, 1), (3, 4, 1), (2, 4, 1), (1, 4, 1)},
                          {(3, 1, 3), (2, 1, 2), (1, 1, 1), (4, 1, 4)}, {(2, 2, 4), (4, 4, 4), (1, 1, 4), (3, 3, 4)},
                          {(4, 1, 4), (3, 1, 4), (1, 1, 4), (2, 1, 4)}, {(3, 1, 3), (3, 1, 4), (3, 1, 1), (3, 1, 2)},
                          {(1, 2, 1), (4, 2, 4), (3, 2, 3), (2, 2, 2)}, {(4, 1, 1), (1, 4, 4), (2, 3, 3), (3, 2, 2)},
                          {(1, 4, 4), (3, 4, 2), (4, 4, 1), (2, 4, 3)}, {(3, 4, 3), (3, 4, 4), (3, 4, 1), (3, 4, 2)},
                          {(4, 1, 4), (4, 3, 2), (4, 4, 1), (4, 2, 3)}, {(3, 3, 1), (4, 4, 1), (1, 1, 1), (2, 2, 1)},
                          {(2, 3, 1), (2, 3, 2), (2, 3, 3), (2, 3, 4)}, {(1, 1, 3), (2, 1, 3), (3, 1, 3), (4, 1, 3)},
                          {(1, 2, 2), (4, 2, 2), (3, 2, 2), (2, 2, 2)}, {(3, 1, 3), (3, 4, 3), (3, 2, 3), (3, 3, 3)},
                          {(4, 3, 4), (3, 3, 4), (2, 3, 4), (1, 3, 4)}, {(4, 4, 4), (3, 4, 3), (2, 4, 2), (1, 4, 1)})

dict_of_shapes_wins[3] = set(frozenset(i) for i in dict_of_shapes_wins[3])
dict_of_shapes_wins[4] = set(frozenset(i) for i in dict_of_shapes_wins[4])

dict_of_shapes_wins_3rd = {}
dict_of_shapes_wins_3rd[4] = {i for i in dict_of_shapes_wins[4] if any(ii for ii in i if ii[2] == 3)}

# line on 3rd level + 3rd poin
dict_of_shapes_wins_3rd_dct = {}
# dict_of_shapes_wins_3rd_dct[4] = {i: tuple(ii for ii in i if ii[2] == 3) for i in dict_of_shapes_wins_3rd[4]}
dict_of_shapes_wins_3rd_dct[4] = {i for i in dict_of_shapes_wins_3rd[4] if tuple(ii for ii in i if ii[2] == 3) }

dict_of_intersecting_lines = create_intersecting_lines_dict()
# cross lines with cross coord and hole cross
dict_of_intersecting_lines_cross = {}
# dict_of_intersecting_lines_cross[4] = [tuple([i, tuple(i[0] & i[1])[0], (i[0] - (i[0] & i[1]), i[1] - (i[0] & i[1]))])
#                                       for i in  dict_of_intersecting_lines[4]]
dict_of_intersecting_lines_cross[4] = set(dict_of_intersecting_lines[4])

dict_of_adjacent_z_intersecting_lines = create_adjacent_z_intersecting_lines_dict()
# overlay cross lines with over-cross coord and over-hole over-cross
dict_of_adjacent_z_intersecting_lines_cross = {}
# dict_of_adjacent_z_intersecting_lines_cross[4] = set(tuple([tuple([i[0], i[1]]), i[2], tuple([i[0] - set(i[2]), i[1] - set(i[2])])])
#                                                   for i in dict_of_adjacent_z_intersecting_lines[4])
dict_of_adjacent_z_intersecting_lines_cross[4] = {(i[0], i[1]) for i in dict_of_adjacent_z_intersecting_lines[4]}


def get_fork_points(over_fork):
    """Находит fork_points для данной over_fork."""
    return [
        {p, pp} for p in over_fork[1] for pp in over_fork[0]
        if (p[0], p[1], p[2] - 1) == pp or (p[0], p[1], p[2] + 1) == pp
    ]


class Configs:
    debug_mod = False  # random turns by pc without players decisions

    GRAVITY = True     # set or not mod when chips will fall on the lowest position or will levitate in set coords
    SHAPE = 4          # must be in range(3, 10) (WA)
    play_vs_bot = 0    # 0, 1, 2 - the presence and number of the bot's move
    bot_difficult = 1
    second_bot = 0     # 0, 1, 2 - difficult of second bot
    
    interactive_input = False  # True - интерактивный ввод через matplotlib, False - терминальный ввод

    depth_sorting = True      # True - sort objects by depth (closer objects in front), False - render in order added
    reverse_depth = False     # True - reverse depth sorting (further objects in front)
    sort_all_axes = True      # True - sort by all coordinates (x,y,z), False - sort only by z

    stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib

    field_data = {
        'fst_player': {
            'up_layer': set(),
            'lines_left': {i: {'weight': 1, 'points': []} for i in deepcopy(dict_of_shapes_wins[SHAPE])},
            'cross_forks_left': {i: {'weight': 1, 'points': [], 'common_point': list(i[0] & i[1])[0], 'final_pair': []}
                                 for i in deepcopy(dict_of_intersecting_lines_cross[SHAPE])},
            'over_forks_left': {i: {'weight': 1, 'points': [], 'fork_points': get_fork_points(i)}
                                for i in deepcopy(dict_of_adjacent_z_intersecting_lines_cross[SHAPE])}
,
            'dead_points': {},  # {coord: {value: tuple, type: str, weight: int, 'fork_move': tuple, 'under_slots': list, 'layer': int}}
            'force_moves': {},
        },
        "snd_player": {
            'up_layer': set(),
            'lines_left': {i: {'weight': 1, 'points': []} for i in deepcopy(dict_of_shapes_wins[SHAPE])},
            'cross_forks_left': {i: {'weight': 1, 'points': [], 'common_point': list(i[0] & i[1])[0], 'final_pair': []}
                                 for i in deepcopy(dict_of_intersecting_lines_cross[SHAPE])},
            'over_forks_left': {i: {'weight': 1, 'points': [], 'fork_points': get_fork_points(i)}
                                for i in deepcopy(dict_of_adjacent_z_intersecting_lines_cross[SHAPE])},
            'dead_points': {},
            'force_moves': {},
        }
    }


class Bot_3_lvl:
    def __init__(self):
        # self.own_weights = {i: (i + 1) * 10**i for i in range(Configs.SHAPE - 1)}
        self.own_weights = {i: i + 1 for i in range(Configs.SHAPE - 1)}
        # self.own_weights[Configs.SHAPE - 1] = 2e6

        self.enemy_weights = {i: i + 1 for i in range(Configs.SHAPE - 1)}
        # self.enemy_weights[Configs.SHAPE - 1] = 1e6


class Bot_4_lvl:
    # line_weights = {i: i + 1 for i in range(Configs.SHAPE - 1)}

    def __init__(self):
        self.name = "Bot_4_lvl_orig"

        self.win_points = int(1e6)

        self.line_weights = {i: i + 1 for i in range(Configs.SHAPE)}
        self.third_points_lines = {i: v * 2 for i, v in self.line_weights.items()}  # v * 2

        self.line_weights[Configs.SHAPE] = self.win_points

        self.fork_weights = {
            0:1,
            1:20,  # 20
            2:30,
            3:40,
            4:50,
        }

        # self.block_almost_line = (Configs.SHAPE - 1) * 2

        self.odd_dead_points = 10000
        self.common_3rd_dead_point = 50000 #400
        self.own_3rd_dead_point = 100000 # 800

        # self.needed_count_3rd_dead_point = 8  # TODO: [21.06.2025 by Leo]
        
    def diff_line_weights(self, line, points, stack):

        # force line 3p with z-1 or z=0,
        # third_line_bonus = 0
        third_points = [i for i in line if (i not in points) and (i[2] == 3)]

        if len(third_points):
            base_weight = self.third_points_lines[len(points)]
        else:
            base_weight = self.line_weights[len(points)]

        sum_weight = base_weight

        return sum_weight

    # def dead_points_weights(self, our_dead_points, enemy_dead_points, num_player, our_force_moves=None, enemy_force_moves=None):
    #     our_3rd_dead_points = {p: v for p, v in our_dead_points.items() if v['layer'] == 3}
    #     enemy_3rd_dead_points = {p: v for p, v in enemy_dead_points.items() if v['layer'] == 3}
    #
    #     sum_weight = 0
    #
    #     our_live_3rd_dead_points = {'com': set(), 'own': set()}
    #     enemy_live_3rd_dead_points = {'com': set(), 'own': set()}
    #
    #     # -1 + 0 - enemy fork # -1 - useless # 0 - com # nothing - own
    #     for p, v in our_3rd_dead_points.items():
    #         cur = (p[0], p[1], p[2]) in enemy_dead_points
    #         down = (p[0], p[1], p[2] - 1) in enemy_dead_points
    #         if cur and down:
    #             if down not in our_dead_points:
    #                 sum_weight = -self.win_points
    #         elif cur:
    #             our_live_3rd_dead_points['com'].add(p)
    #         # elif down:
    #         else:
    #             our_live_3rd_dead_points['own'].add(p)
    #
    #     for p in enemy_3rd_dead_points:
    #         cur = (p[0], p[1], p[2]) in our_dead_points
    #         down = (p[0], p[1], p[2] - 1) in our_dead_points
    #         if cur and down:
    #             if down not in enemy_dead_points:
    #                 sum_weight = self.win_points
    #         elif cur:
    #             enemy_live_3rd_dead_points['com'].add(p)
    #         else:
    #             enemy_live_3rd_dead_points['own'].add(p)
    #
    #
    #     com_3rd_dp = len(set(enemy_live_3rd_dead_points['com']) & set(our_live_3rd_dead_points['com']))
    #     own_3rd_dp_diff = (len(our_live_3rd_dead_points['own']) - len(enemy_live_3rd_dead_points['own']))
    #
    #     com_3rd_dp_weight = self.common_3rd_dead_point if ((com_3rd_dp % 2) == num_player) else -self.common_3rd_dead_point
    #     our_3rd_dp_weight = self.own_3rd_dead_point * own_3rd_dp_diff
    #
    #     return sum_weight + com_3rd_dp_weight + our_3rd_dp_weight

    # def cross_fork_weights(self, our_cross_forks, enemy_cross_forks, stack):
    #     stack_points = set([tuple(i) for i in list(stack.values())[0] + list(stack.values())[1]])
    #
    #     our_weights = 0
    #     for pair, points in our_cross_forks.items():
    #         points = points['points']
    #         left_line_w = len(set(points) & set(pair[0]))
    #         right_line_w = len(set(points) & set(pair[1]))
    #
    #         our_weights += (self.fork_weights[left_line_w] + self.fork_weights[right_line_w])
    #         # TODO: [26.06.2025 by Leo] - init fork situation
    #         # if len(points) == 6:
    #         #     com_point = list(set(pair[0]) & set(pair[1]))[0]
    #         #     under_com_points = [(com_point[0], com_point[1], com_point[2] - i) for i in range(1, com_point[2])]
    #         #     if (com_point[2] == 1) or ():
    #         #         ...
    #
    #     enemy_weights = 0
    #     for pair, points in enemy_cross_forks.items():
    #         points = points['points']
    #         left_line_w = len(set(points) & set(pair[0]))
    #         right_line_w = len(set(points) & set(pair[1]))
    #
    #         enemy_weights += (self.fork_weights[left_line_w] + self.fork_weights[right_line_w])
    #
    #     return our_weights, enemy_weights

    # def over_fork_weights(self, our_over_forks, enemy_over_forks, our_dead_p, enemy_dead_p):
    #     our_weights = 0
    #     for pair, points in our_over_forks.items():
    #         points = points['points']
    #         left_line_w = len(set(points) & set(pair[0]))
    #         right_line_w = len(set(points) & set(pair[1]))
    #
    #         our_weights += (self.fork_weights[left_line_w] + self.fork_weights[right_line_w])
    #         # TODO: [26.06.2025 by Leo] - init fork situation
    #         if (len(set(pair[0]) & set(pair[1])) - len(points)) < 3:
    #             ...
    #
    #     enemy_weights = 0
    #     for pair, points in enemy_over_forks.items():
    #         points = points['points']
    #         left_line_w = len(set(points) & set(pair[0]))
    #         right_line_w = len(set(points) & set(pair[1]))
    #
    #         enemy_weights += (self.fork_weights[left_line_w] + self.fork_weights[right_line_w])
    #         if (len(set(pair[0]) & set(pair[1])) - len(points)) < 3:
    #             ...
    #
    #     return our_weights, enemy_weights

    # def line_weights_3rd(self, line, stack):
    #     return self.line_weights[line[0]] + self.line_weights[line[1]] + self.line_weights[line[2]]

