DIMENSION = 3


class Configs:
    GRAVITY = True
    SHAPE = 4
    debug_mod = False

    stack = {'red': [], "green": []}
    play_vs_bot = 0


dict_of_shapes_wins = {i: None for i in range(2, 10)}

# TODO: [11.10.2021 by Lev] WA, need to remake
win_lines_4x4x4 = [([4, 1, 4], [4, 2, 4], [4, 3, 4], [4, 4, 4]), ([2, 1, 1], [2, 2, 2], [2, 3, 3], [2, 4, 4]),
                   ([2, 1, 1], [2, 1, 2], [2, 1, 3], [2, 1, 4]), ([1, 1, 2], [2, 2, 2], [3, 3, 2], [4, 4, 2]),
                   ([1, 4, 1], [1, 4, 2], [1, 4, 3], [1, 4, 4]), ([1, 4, 3], [2, 3, 3], [3, 2, 3], [4, 1, 3]),
                   ([2, 1, 4], [2, 2, 3], [2, 3, 2], [2, 4, 1]), ([1, 1, 1], [1, 2, 1], [1, 3, 1], [1, 4, 1]),
                   ([1, 2, 3], [2, 2, 3], [3, 2, 3], [4, 2, 3]), ([1, 4, 1], [2, 3, 1], [3, 2, 1], [4, 1, 1]),
                   ([4, 1, 1], [4, 1, 2], [4, 1, 3], [4, 1, 4]), ([1, 4, 3], [2, 4, 3], [3, 4, 3], [4, 4, 3]),
                   ([4, 4, 1], [4, 4, 2], [4, 4, 3], [4, 4, 4]), ([4, 1, 1], [4, 2, 2], [4, 3, 3], [4, 4, 4]),
                   ([2, 1, 2], [2, 2, 2], [2, 3, 2], [2, 4, 2]), ([1, 4, 4], [2, 4, 4], [3, 4, 4], [4, 4, 4]),
                   ([1, 1, 3], [1, 2, 3], [1, 3, 3], [1, 4, 3]), ([1, 1, 4], [2, 1, 3], [3, 1, 2], [4, 1, 1]),
                   ([1, 4, 2], [2, 4, 2], [3, 4, 2], [4, 4, 2]), ([2, 4, 1], [2, 4, 2], [2, 4, 3], [2, 4, 4]),
                   ([2, 2, 1], [2, 2, 2], [2, 2, 3], [2, 2, 4]), ([1, 3, 2], [2, 3, 2], [3, 3, 2], [4, 3, 2]),
                   ([1, 1, 2], [1, 2, 2], [1, 3, 2], [1, 4, 2]), ([1, 2, 4], [2, 2, 4], [3, 2, 4], [4, 2, 4]),
                   ([1, 4, 4], [2, 3, 4], [3, 2, 4], [4, 1, 4]), ([1, 4, 1], [2, 3, 2], [3, 2, 3], [4, 1, 4]),
                   ([1, 1, 2], [2, 1, 2], [3, 1, 2], [4, 1, 2]), ([1, 1, 4], [1, 2, 3], [1, 3, 2], [1, 4, 1]),
                   ([2, 1, 1], [2, 2, 1], [2, 3, 1], [2, 4, 1]), ([4, 3, 1], [4, 3, 2], [4, 3, 3], [4, 3, 4]),
                   ([4, 1, 2], [4, 2, 2], [4, 3, 2], [4, 4, 2]), ([1, 1, 1], [1, 1, 2], [1, 1, 3], [1, 1, 4]),
                   ([2, 1, 3], [2, 2, 3], [2, 3, 3], [2, 4, 3]), ([1, 1, 4], [1, 2, 4], [1, 3, 4], [1, 4, 4]),
                   ([1, 3, 3], [2, 3, 3], [3, 3, 3], [4, 3, 3]), ([2, 1, 4], [2, 2, 4], [2, 3, 4], [2, 4, 4]),
                   ([1, 4, 2], [2, 3, 2], [3, 2, 2], [4, 1, 2]), ([1, 1, 3], [2, 2, 3], [3, 3, 3], [4, 4, 3]),
                   ([1, 2, 1], [1, 2, 2], [1, 2, 3], [1, 2, 4]), ([3, 1, 1], [3, 2, 1], [3, 3, 1], [3, 4, 1]),
                   ([1, 1, 1], [2, 2, 2], [3, 3, 3], [4, 4, 4]), ([3, 1, 1], [3, 2, 2], [3, 3, 3], [3, 4, 4]),
                   ([1, 3, 1], [2, 3, 2], [3, 3, 3], [4, 3, 4]), ([1, 3, 4], [2, 3, 3], [3, 3, 2], [4, 3, 1]),
                   ([3, 1, 4], [3, 2, 3], [3, 3, 2], [3, 4, 1]), ([4, 1, 3], [4, 2, 3], [4, 3, 3], [4, 4, 3]),
                   ([3, 2, 1], [3, 2, 2], [3, 2, 3], [3, 2, 4]), ([3, 1, 4], [3, 2, 4], [3, 3, 4], [3, 4, 4]),
                   ([1, 2, 1], [2, 2, 1], [3, 2, 1], [4, 2, 1]), ([4, 1, 1], [4, 2, 1], [4, 3, 1], [4, 4, 1]),
                   ([1, 2, 4], [2, 2, 3], [3, 2, 2], [4, 2, 1]), ([3, 3, 1], [3, 3, 2], [3, 3, 3], [3, 3, 4]),
                   ([1, 1, 1], [1, 2, 2], [1, 3, 3], [1, 4, 4]), ([3, 1, 2], [3, 2, 2], [3, 3, 2], [3, 4, 2]),
                   ([1, 1, 1], [2, 1, 1], [3, 1, 1], [4, 1, 1]), ([1, 3, 1], [1, 3, 2], [1, 3, 3], [1, 3, 4]),
                   ([4, 2, 1], [4, 2, 2], [4, 2, 3], [4, 2, 4]), ([1, 1, 4], [2, 2, 3], [3, 3, 2], [4, 4, 1]),
                   ([1, 3, 1], [2, 3, 1], [3, 3, 1], [4, 3, 1]), ([1, 4, 1], [2, 4, 1], [3, 4, 1], [4, 4, 1]),
                   ([1, 1, 1], [2, 1, 2], [3, 1, 3], [4, 1, 4]), ([1, 1, 4], [2, 2, 4], [3, 3, 4], [4, 4, 4]),
                   ([1, 1, 4], [2, 1, 4], [3, 1, 4], [4, 1, 4]), ([3, 1, 1], [3, 1, 2], [3, 1, 3], [3, 1, 4]),
                   ([1, 2, 1], [2, 2, 2], [3, 2, 3], [4, 2, 4]), ([1, 4, 4], [2, 3, 3], [3, 2, 2], [4, 1, 1]),
                   ([1, 4, 4], [2, 4, 3], [3, 4, 2], [4, 4, 1]), ([3, 4, 1], [3, 4, 2], [3, 4, 3], [3, 4, 4]),
                   ([4, 1, 4], [4, 2, 3], [4, 3, 2], [4, 4, 1]), ([1, 1, 1], [2, 2, 1], [3, 3, 1], [4, 4, 1]),
                   ([2, 3, 1], [2, 3, 2], [2, 3, 3], [2, 3, 4]), ([1, 1, 3], [2, 1, 3], [3, 1, 3], [4, 1, 3]),
                   ([1, 2, 2], [2, 2, 2], [3, 2, 2], [4, 2, 2]), ([3, 1, 3], [3, 2, 3], [3, 3, 3], [3, 4, 3]),
                   ([1, 3, 4], [2, 3, 4], [3, 3, 4], [4, 3, 4]), ([1, 4, 1], [2, 4, 2], [3, 4, 3], [4, 4, 4])]


dict_of_shapes_wins[4] = win_lines_4x4x4
