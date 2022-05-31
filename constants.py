DIMENSION = 3
turns_alpha = 0.9


class Configs:
    debug_mod = False  # random turns by pc without players decisions

    GRAVITY = True     # set or not mod when chips will fall on the lowest position or will levitate in set coords
    SHAPE = 4          # must be in range(3, 10) (WA)
    play_vs_bot = 0    # 0, 1, 2 - the presence and number of the bot's move
    bot_difficult = 1
    second_bot = 0     # 0, 1, 2 - difficult of second bot

    stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib


class Bot_3_lvl:
    def __init__(self):
        self.own_weights = {i: i + 1 for i in range(Configs.SHAPE - 1)}
        # self.own_weights[Configs.SHAPE - 1] = 2e6

        self.enemy_weights = {i: i + 1 for i in range(Configs.SHAPE - 1)}
        # self.enemy_weights[Configs.SHAPE - 1] = 1e6


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

dict_of_shapes_wins[4] = set(frozenset(i) for i in dict_of_shapes_wins[4])
dict_of_shapes_wins[3] = set(frozenset(i) for i in dict_of_shapes_wins[3])
