import copy
from tqdm import trange

from constants import Configs, DIMENSION
from funcs import init_field, input_coords, render_turn, gravity_correction, line_render, win_check_from_db, bot_turn, \
    leader_bord_stat


Configs.GRAVITY = True
Configs.SHAPE = 4  # must be in range(3, 10) (WA)
Configs.stack = {'red': [], "green": []}  # set color and name for every player, used by matplotlib

Configs.debug_mod = False  # random turns by pc without players decisions
Configs.second_bot = 2      # 0, 1, 2 - difficult of second bot

Configs.play_vs_bot = 1  # 0, 1, 2 - the presence and number of the bot's move
Configs.bot_difficult = 3


def single_game(rendering=True, bot_1_configs=None, bot_2_configs=None):
    fig, ax = init_field() if rendering else [None, None]
    stack = copy.deepcopy(Configs.stack)

    turn, cancels = 0, 0

    if rendering:
        if not Configs.debug_mod:
            if Configs.play_vs_bot == 1:
                print(f"main_{Configs.bot_difficult}_lvl_bot VS player 2")
            else:
                print(f"player 1 VS main_{Configs.bot_difficult}_lvl_bot")
        else:
            if Configs.play_vs_bot == 1:
                print(f"main_{Configs.bot_difficult}_lvl_bot VS debug_{Configs.second_bot}_lvl_bot")
            else:
                print(f"debug_{Configs.second_bot}_lvl_bot VS main_{Configs.bot_difficult}_lvl_bot")

    i = 0
    while i < Configs.SHAPE ** DIMENSION:
        color = list(stack.keys())[i % 2]

        # turns logic
        if (i % 2 + 1) == Configs.play_vs_bot:
            turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.bot_difficult, configs=bot_1_configs)
            print(f'{color} turn: {turn}') if rendering else 0
        else:
            if Configs.debug_mod:
                turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.second_bot, configs=bot_2_configs)
                if rendering:
                    input()
                    print(f'{color} turn: {turn}')
            else:
                turn = input_coords(i=i, stack=stack, color=color)

        # logic for canceling last turn
        if turn == "cancel":
            i -= 2
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
        i += 1

        if is_win:
            print(f"{color} player win")
            line_render(stack_render={color: is_win}) if rendering else None
            i -= 1
            break

    if rendering:
        if turn == "exit":
            input()
        elif Configs.play_vs_bot and not Configs.debug_mod:
            leader_bord_stat(i=i, your_turn=(i % 2 + 1), is_win=((i % 2 + 1) == (Configs.play_vs_bot % 2 + 1)))
    return color, i, is_win


if __name__ == "__main__":
    single_game(rendering=True)
