import copy
from tqdm import trange

from constants import Configs, DIMENSION, dict_of_shapes_wins
from funcs import init_field, input_coords, render_turn, gravity_correction, line_render, win_check_from_db, \
    bot_turn, debug_turn


Configs.GRAVITY = True
Configs.SHAPE = 4  # must be in range(3, 10) (WA)
Configs.stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib

Configs.debug_mod = False  # random turns by pc without players decisions
Configs.second_bot = 1      # 0, 1, 2 - difficult of second bot

Configs.play_vs_bot = 1  # 0, 1, 2 - the presence and number of the bot's move
Configs.bot_difficult = 2


def single_game(rendering=True, range_func=trange):
    fig, ax = init_field() if rendering else [None, None]
    stack = copy.deepcopy(Configs.stack)

    turn, cancels = 0, 0

    for i in range_func(Configs.SHAPE ** DIMENSION + cancels):
        # WA for multi canceling turns
        if turn == "cancel":
            turn = 0
            continue

        color = list(stack.keys())[i % 2]

        # turns logic
        if (i % 2 + 1) == Configs.play_vs_bot:
            turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.bot_difficult)
            print(f'{color} turn: {turn}') if rendering else 0
        else:
            if Configs.debug_mod:
                turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.second_bot)
                if rendering:
                    input()
                    print(f'{color} turn: {turn}')
            else:
                turn = input_coords(i=i, stack=stack, color=color)

        # logic for canceling last turn
        if turn == "cancel":
            cancels += 2
            stack[color].pop(-1)
            stack[list(stack.keys())[i % 2 - 1]].pop(-1)

            fig, ax = line_render(stack_render=stack)
            continue

        if turn == "exit": break  # WA for exit

        turn = gravity_correction(coords=turn, stack=stack)
        stack[color].append(turn)

        render_turn(ax=ax, fig=fig, turn=turn, color=color) if rendering else None

        is_win = win_check_from_db(stack=stack, coords=turn, color=color)
        # is_win = False
        if is_win:
            print(f"{color} player win")
            line_render(stack_render={color: is_win}) if rendering else None
            break

    input('end\n') if rendering else None
    return color, i


if __name__ == "__main__":
    single_game(rendering=True)
