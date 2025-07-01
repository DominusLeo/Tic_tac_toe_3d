import copy
from tqdm import trange

from bot_utils import filter_lines_stack, filter_cross_forks_stack, filter_over_forks_stack, find_dead_points, \
    bad_fork_logs, fork_logs, filter_weight_calc
from constants import Configs, DIMENSION, Bot_4_lvl
from funcs import init_field, input_coords, render_turn, gravity_correction, line_render, win_check_from_db, bot_turn, \
    leader_bord_stat, obj_saver, json_saver, obj_reader, up_layer


test_by_ready_game = False
save_res = False


render = True
game_log = obj_reader('test_data/test_game_log_n.pickle')
game_log_save = []


if __name__ == "__main__":
    test_by_ready_game = True
    save_res = 'test_data/test_game_log_n.pickle'

    Configs.GRAVITY = True
    Configs.SHAPE = 4  # must be in range(3, 10) (WA)

    # {'white': [], "black": []}
    fst_color = 'white'
    snd_color = 'black'

    Configs.stack = {fst_color: [], snd_color: []}  # set color and name for every player, used by matplotlib
    Configs.field_data = {fst_color: Configs.field_data['fst_player'], snd_color: Configs.field_data['snd_player']}

    Configs.play_vs_bot = 2  # 0, 1, 2 - the presence and number of the bot's move
    Configs.bot_difficult = 4

    Configs.debug_mod = True  # random turns by pc without players decisions
    Configs.second_bot = 2     # 0, 1, 2 - difficult of second bot


def single_game(rendering=True, bot_1_configs=None, bot_2_configs=None, Configs=Configs):
    fig, ax = init_field() if rendering else [None, None]
    stack = copy.deepcopy(Configs.stack)
    field_data = copy.deepcopy(Configs.field_data)

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
        enemy_color = list(stack.keys())[(i + 1) % 2]

        if i >= 30:
            ...

        # turns logic
        if (i % 2 + 1) == Configs.play_vs_bot:
            if turn != 'cancel':
                turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.bot_difficult, configs=bot_1_configs,
                                field_data=field_data)
                print(f'{color} turn: {turn}') if rendering else 0
        else:
            if Configs.debug_mod:
                if turn != 'cancel':
                    turn = bot_turn(i=i, stack=stack, color=color, difficult=Configs.second_bot, configs=bot_2_configs,
                                    field_data=field_data)
                if rendering:
                    # input()
                    print(f'{color} turn: {turn}')
            else:
                turn = input_coords(i=i, stack=stack, color=color, )

        if test_by_ready_game:
            turn, turn_weight_test = list(game_log[i].items())[0]

        turn = gravity_correction(coords=list(turn), stack=stack)

        field_data[color]['up_layer'] = set([tuple(ii) for ii in up_layer(stack)])
        stack[color].append(turn)

        field_data[color]['lines_left'] = filter_lines_stack(field_data[color]['lines_left'], tuple(turn), my_turn=True, stack=stack)
        field_data[enemy_color]['lines_left'] = filter_lines_stack(field_data[enemy_color]['lines_left'], tuple(turn), my_turn=False, stack=stack)

        # operations with dead points  # TODO: [21.06.2025 by Leo] ?
        field_data[color]['dead_points'], field_data[enemy_color]['dead_points'] = \
            find_dead_points(field_data[color]['lines_left'], field_data[enemy_color]['lines_left'], stack=stack, coord=turn,
                             up_layer=field_data[color]['up_layer'], turn_num=i, color=color)

        if i >= 29:
            ...

        field_data[color]['cross_forks_left'] = filter_cross_forks_stack(tuple(turn), enemy_color=enemy_color, color=color,
                                                                         my_turn=True, field_data=field_data, stack=stack)
        field_data[enemy_color]['cross_forks_left'] = filter_cross_forks_stack(tuple(turn), enemy_color=enemy_color, color=color,
                                                                               my_turn=False, field_data=field_data, stack=stack)

        field_data[color]['over_forks_left'] = filter_over_forks_stack(tuple(turn), enemy_color=enemy_color, color=color,
                                                                       my_turn=True, field_data=field_data, stack=stack)
        field_data[enemy_color]['over_forks_left'] = filter_over_forks_stack(tuple(turn), enemy_color=enemy_color, color=color,
                                                                             my_turn=False, field_data=field_data, stack=stack)

        turn_weight = filter_weight_calc({tuple(turn): field_data}, color, enemy_color, stack=stack, turn_number=i)

        if turn_weight[tuple(turn)] >= 100000:
            ...

        print(turn_weight, '\n\n')

        if test_by_ready_game:
            print(f"{turn_weight[tuple(turn)]} == {turn_weight_test}")
            if turn_weight[tuple(turn)] != turn_weight_test:
                print('error')
                ...
        game_log_save.append(turn_weight)

        # logic for canceling last turn
        if turn == "cancel":
            i -= 1
            if i >= 0:
                stack[list(stack.keys())[i % 2]].pop(-1)
                stack[color].pop(-1)
                ax.collections[-1].remove()
                fig.show()
            # fig, ax = line_render(stack_render=stack)
            continue

        if turn == "exit": break  # WA for exit

        render_turn(ax=ax, fig=fig, turn=list(turn), color=color) if rendering else None
        # print(f'give {turn_weight} points\n')

        is_win = win_check_from_db(stack=stack, coords=turn, color=color)

        # if (field_data[color]['dead_points']) or (field_data[enemy_color]['dead_points']):
        #     print(field_data[color]['dead_points'])
        #     print(field_data[enemy_color]['dead_points'])
        #     breakpoint()

        if i == 40 and Configs.debug_mod:
            ...
            # breakpoint()
        # is_win = False
        i += 1

        if is_win:
            if save_res:
                obj_saver(game_log_save, save_res)
            print(f"{color} player win")
            line_render(stack_render={color: is_win}) if rendering else None
            i -= 1
            # breakpoint()
            # obj_saver(bad_fork_logs, 'bad_fork_logs.pickle')
            # obj_saver(fork_logs, 'fork_logs.pickle')
            break
    else:
        print('draw game')

    if rendering:
        if turn == "exit":
            input()
        elif Configs.play_vs_bot and not Configs.debug_mod:
            leader_bord_stat(i=i, your_turn=(i % 2 + 1), is_win=((i % 2 + 1) == (Configs.play_vs_bot % 2 + 1)))
    return color, i, is_win


if __name__ == "__main__":
    single_game(rendering=render)
