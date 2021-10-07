import itertools
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from constants import Configs
from funcs import init_field, input_coords, render_turn, gravity_correction


Configs.GRAVITY = True
Configs.SHAPE = 3  # must be less then 10 (WA)
Configs.stack = {'red': [], "green": []}


if __name__ == "__main__":
    fig, ax = init_field()

    stack = Configs.stack

    for i in range(Configs.SHAPE ** 3):
        color = list(stack.keys())[0] if i % 2 else list(stack.keys())[1]
        turn = input_coords(i=i, stack=stack, ax=ax, color=color)

        turn = gravity_correction(coords=turn, stack=stack)
        stack[color].append(turn)

        render_turn(i=i, ax=ax, fig=fig, turn=turn, color=color)

    input('end')
