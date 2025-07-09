import copy
from tqdm import trange
import pickle

from bot_utils import bad_fork_logs, fork_logs, full_data_update, weight_calc
from constants import Configs, DIMENSION, Bot_4_lvl
from funcs import init_field, input_coords, render_turn, line_render, win_check_from_db, bot_turn, \
    leader_bord_stat, obj_saver, obj_reader, up_layer, update_game_title
from utils import gravity_correction


test_by_ready_game = False
to_save_res_name = False


render = True
prev_game_log = obj_reader('test_data/test_game_log_n.pickle')
game_log_to_save = []


if __name__ == "__main__":
    test_by_ready_game = False
    start_turn_num = 96 if test_by_ready_game else 0

    to_save_res_name = 'test_data/test_game_log_n.pickle'

    Configs.debug_mod = False  # random turns by pc without players decisions
    Configs.second_bot = 3     # 0, 1, 2 - difficult of second bot
    Configs.interactive_input = True  # True - интерактивный ввод, False - терминальный

    Configs.GRAVITY = True
    Configs.SHAPE = 4  # must be in range(3, 10) (WA)

    # {'white': [], "black": []}
    fst_color = 'white'
    snd_color = 'black'

    Configs.stack = {fst_color: [], snd_color: []}  # set color and name for every player, used by matplotlib
    Configs.field_data = {fst_color: Configs.field_data['fst_player'], snd_color: Configs.field_data['snd_player']}

    Configs.play_vs_bot = 2  # 0, 1, 2 - the presence and number of the bot's move
    Configs.bot_difficult = 4


def single_game(rendering=True, bot_1_configs=None, bot_2_configs=None, Configs=Configs, game_log_to_save=None):
    fig, ax = init_field() if rendering else [None, None]
    stack = copy.deepcopy(Configs.stack)
    field_data = pickle.loads(pickle.dumps(Configs.field_data, -1))
    
    # Инициализируем отображение линий сетки с правильной сортировкой по глубине
    if rendering:
        render_all_pieces_depth_sorted(ax, fig, stack)

    turn, cancels = 0, 0
    if game_log_to_save is None:
        game_log_to_save = []

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
                # Обновляем заголовок перед ходом игрока
                if rendering:
                    update_game_title(ax, fig, color, i % 2 + 1)
                
                # Передаем fig и ax только если включен интерактивный режим
                if Configs.interactive_input:
                    turn = input_coords(i=i, stack=stack, color=color, fig=fig, ax=ax)
                else:
                    turn = input_coords(i=i, stack=stack, color=color)

        if test_by_ready_game:
            if (i <= start_turn_num) and i < len(prev_game_log):
                turn, turn_weight_test = (prev_game_log[i])
            else:
                turn, turn_weight_test = turn, 0

        turn = gravity_correction(coords=list(turn), stack=stack)

        field_data[color]['up_layer'] = set([tuple(ii) for ii in up_layer(stack)])
        stack[color].append(turn)

        full_data_update(field_data, tuple(turn), color, enemy_color, stack, turn_num=i)

        turn_weight = weight_calc(field_data, color, ) - weight_calc(field_data, enemy_color, )
        # turn_weight = filter_weight_calc({tuple(turn): field_data}, color, enemy_color, stack=stack, turn_number=i)

        if turn_weight >= 100000:
            ...

        if i >= 48:
            ...

        if rendering:
            print(turn_weight, '\n\n')

        if test_by_ready_game:
            print(f"{turn_weight} == {turn_weight_test}")
            if turn_weight != turn_weight_test:
                print('error')
                ...
        game_log_to_save.append((turn, turn_weight))

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

        if rendering:
            render_turn(ax=ax, fig=fig, turn=list(turn), color=color, label=f"{color}_{turn}")  # label=f'{color}_{turn}'
            render_all_pieces_depth_sorted(ax, fig, stack)
        
        # Восстанавливаем обычный заголовок после хода
        if rendering and not Configs.interactive_input:
            update_game_title(ax, fig)
        
        # print(f'give {turn_weight} points\n')

        is_win = win_check_from_db(stack=stack, coords=turn, color=color)

        # if (field_data[color]['dead_points']) or (field_data[enemy_color]['dead_points']):
        #     print(field_data[color]['dead_points'])
        #     print(field_data[enemy_color]['dead_points'])
        #     breakpoint()

        i += 1

        if is_win:
            if to_save_res_name:
                obj_saver(game_log_to_save, to_save_res_name)
            print(f"{color} player win")
            if ((Configs.play_vs_bot == 1) and color == 'black') \
                    or ((Configs.play_vs_bot == 2) and color == 'white'):
                ...
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
    single_game(rendering=render, game_log_to_save=None)
