import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

from funcs import init_field, input_coords, render_turn


if __name__ == "__main__":
    fig, ax = init_field()

    stack = {'red': [], "green": []}

    for i in range(64):
        color = list(stack.keys())[0] if i % 2 else list(stack.keys())[1]
        turn = input_coords(i=i, stack=stack, ax=ax, color=color)
        stack[color].append(turn)
        render_turn(i=i, ax=ax, fig=fig, turn=turn, color=color)

    input('end')
