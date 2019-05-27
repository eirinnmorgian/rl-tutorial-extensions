import tcod

from entity import get_blocking_entities_at_location
from input_handlers import handle_keys, handle_mouse, handle_main_menu
from render_functions import clear_all, render_all
from fov_functions import initialize_fov, recompute_fov
from game_states import GameStates
from death_functions import kill_monster, kill_player

from game_messages import Message

from loader_functions.initialize_new_game import get_constants, get_game_variables
from loader_functions.data_loaders import save_game, load_game

from menus import main_menu, message_box




def play_game(player, entities, game_map, message_log, game_state, con, panel, constants):

    # FOV settings
    fov_recompute = True
    fov_map = initialize_fov(game_map)

    # init input handlers
    key = tcod.Key()
    mouse = tcod.Mouse()

    game_state = GameStates.PLAYER_TURN

    # hold onto previous state so that checking menus does not waste a turn
    previous_game_state = game_state

    # keep track of selcted targeting item
    targeting_item = None

    # game loop
    while not tcod.console_is_window_closed():

        # check for keypress or mouseover
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if fov_recompute:
            recompute_fov(
                fov_map, 
                player.x, 
                player.y, 
                constants['FOV_RADIUS'], 
                constants['FOV_LIGHT_WALLS'], 
                constants['FOV_ALGORITHM']
            )


        # call our custom render fn
        render_all(
            con, 
            panel, 
            entities, 
            player, 
            game_map, 
            fov_map, 
            fov_recompute, 
            message_log, 
            constants['SCR_W'], 
            constants['SCR_H'], 
            constants['BAR_W'], 
            constants['PANEL_H'], 
            constants['PANEL_Y'], 
            mouse, 
            constants['COLORS'], 
            game_state
        )
    
        fov_recompute = False

        # flush() puts everything onto the screen
        tcod.console_flush()

        # clear all previous positions
        clear_all(con, entities)

        # handle key inputs
        action = handle_keys(key, game_state)

        # handle mouse input
        mouse_action = handle_mouse(mouse)

        # get all possible player inputs and assign them
        # access value of dict via dict.get('key')
        move = action.get('move')
        wait = action.get('wait')
        pickup = action.get('pickup')
        show_inventory = action.get('show_inventory')
        drop_inventory = action.get('drop_inventory')
        inventory_index = action.get('inventory_index')
        take_stairs = action.get('take_stairs')
        level_up = action.get('level_up')
        show_character_screen = action.get('show_character_screen')

        exit = action.get('exit')
        fullscreen = action.get('fullscreen')

        left_click = mouse_action.get('left_click')
        right_click = mouse_action.get('right_click')

        # hold all player turn data here
        player_turn_results = []

        # handle movement / navigation
        if move and game_state == GameStates.PLAYER_TURN:
            dx, dy = move
            destination_x = player.x + dx
            destination_y = player.y + dy

            if not game_map.is_blocked(destination_x, destination_y):
                target = get_blocking_entities_at_location(entities, destination_x, destination_y)

                if target:
                    attack_results = player.fighter.attack(target)
                    player_turn_results.extend(attack_results)

                else:
                    player.move(dx, dy)
                    fov_recompute = True # change fov only on move
                    print('player location: {0}, {1}'.format(player.x, player.y))

                game_state = GameStates.ENEMY_TURN

        # handle waiting
        elif wait:
            game_state = GameStates.ENEMY_TURN

        # handle item pickup
        elif pickup and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.item and entity.x == player.x and entity.y == player.y:
                    pickup_results = player.inventory.add_item(entity)
                    player_turn_results.extend(pickup_results)

                    break # only allow one item at a time

            else:
                message_log.add_message(Message('There is nothing here to pick up', tcod.yellow))

        # handle inventory view
        if show_inventory:
            previous_game_state = game_state
            game_state = GameStates.SHOW_INVENTORY

        # handle dropping items
        if drop_inventory:
            previous_game_state = game_state
            game_state = GameStates.DROP_INVENTORY

        # handle using inventory objects
        if inventory_index is not None and previous_game_state != GameStates.PLAYER_DEAD and inventory_index < len(player.inventory.items):
            item = player.inventory.items[inventory_index]
            
            if game_state == GameStates.SHOW_INVENTORY:
                player_turn_results.extend(player.inventory.use(item, entities=entities, fov_map=fov_map))
            elif game_state == GameStates.DROP_INVENTORY:
                player_turn_results.extend(player.inventory.drop_item(item))

        # handle stairs
        if take_stairs and game_state == GameStates.PLAYER_TURN:
            for entity in entities:
                if entity.stairs and entity.x == player.x and entity.y == player.y:
                    print('constants in ENGINE {0}'.format(constants))
                    entities = game_map.next_floor(player, message_log, constants)
                    fov_map = initialize_fov(game_map)
                    fov_recompute = True
                    tcod.console_clear(con)

                    break

            else:
                message_log.add_message(Message('There are no stairs here', tcod.yellow))

        # handle levelling up
        if level_up:
            if level_up == 'hp':
                player.fighter.base_max_hp += 20
                player.fighter.hp += 20
            elif level_up == 'str':
                player.fighter.base_damage += 1
            elif level_up == 'def':
                player.fighter.base_defense += 1

            game_state = previous_game_state


        # handle character sheet display
        if show_character_screen:
            previous_game_state = game_state
            game_state = GameStates.CHARACTER_SCREEN


        # handle targeting
        if game_state == GameStates.TARGETING:
            if left_click:
                target_x, target_y = left_click

                item_use_results = player.inventory.use(
                    targeting_item, entities=entities, fov_map=fov_map, 
                    target_x=target_x, target_y=target_y
                )

                player_turn_results.extend(item_use_results)

            elif right_click:
                player_turn_results.append({'targeting_cancelled': True})

        # handle ESC key
        if exit:
            # if exiting from inventory menu
            if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY, GameStates.CHARACTER_SCREEN):
                game_state = previous_game_state
            elif game_state == GameStates.TARGETING:
                player_turn_results.append({'targeting_cancelled': True})
            else:
                save_game(player, entities, game_map, message_log, game_state)
                return True

        if fullscreen:
            tcod.console_set_fullscreen(not tcod.console_is_fullscreen())


        # could use a refacor here: handle_turn_result
        for player_turn_result in player_turn_results:
            message = player_turn_result.get('message')
            dead_entity = player_turn_result.get('dead')
            item_added = player_turn_result.get('item_added')
            item_consumed = player_turn_result.get('consumed')
            item_dropped = player_turn_result.get('item_dropped')
            equip = player_turn_result.get('equip')
            targeting = player_turn_result.get('targeting')
            targeting_cancelled = player_turn_result.get('targeting_cancelled')
            xp = player_turn_result.get('xp')


            if message:
                message_log.add_message(message)

            if dead_entity:
                if dead_entity == player:
                    message, game_state = kill_player(dead_entity)
                else:
                    message = kill_monster(dead_entity)

                message_log.add_message(message)

            if item_added:
                # remove item from entities on map
                entities.remove(item_added)
                game_state = GameStates.ENEMY_TURN

            if item_consumed:
                game_state = GameStates.ENEMY_TURN

            if item_dropped:
                entities.append(item_dropped)
                game_state = GameStates.ENEMY_TURN

            if equip:
                equip_results = player.equipment.toggle_equip(equip)

                for equip_result in equip_results:
                    equipped = equip_result.get('equipped')
                    dequipped = equip_result.get('dequipped')

                    if equipped:
                        message_log.add_message(Message('You equipped the {0}'.format(equipped.name)))

                    if dequipped:
                        message_log.add_message(Message('You dequipped the {0}'.format(dequipped.name)))

                game_state = GameStates.ENEMY_TURN

            if targeting:
                # set to player turn to avoid opening inventory if targeting cancelled
                previous_game_state = GameStates.PLAYER_TURN
                game_state = GameStates.TARGETING
                targeting_item = targeting
                message_log.add_message(targeting_item.item.targeting_message)

            if targeting_cancelled:
                game_state = previous_game_state
                message_log.add_message(Message('Targeting cancelled'))

            if xp:
                leveled_up = player.level.add_xp(xp)
                message_log.add_message(Message('You gain {0} experience points'. format(xp)))

                if leveled_up:
                    message_log.add_message(Message('You have reached level {0}'.format(player.level.current_level), tcod.yellow))
                    previous_game_state = game_state
                    game_state = GameStates.LEVEL_UP


        if game_state == GameStates.ENEMY_TURN:
            for entity in entities:
                if entity.ai:
                    enemy_turn_results = entity.ai.take_turn(player, fov_map, game_map, entities)

                    for enemy_turn_result in enemy_turn_results:
                        message = enemy_turn_result.get('message')
                        dead_entity = enemy_turn_result.get('dead')

                        if message:
                            message_log.add_message(message)

                        if dead_entity:
                            if dead_entity == player:
                                    message, game_state = kill_player(dead_entity)
                            else:
                                message = kill_monster(dead_entity)

                            message_log.add_message(message)

                            if game_state == GameStates.PLAYER_DEAD:
                                break

                    if game_state == GameStates.PLAYER_DEAD:
                        break

            else:
                game_state = GameStates.PLAYER_TURN



def main():
    # get all global constants
    constants = get_constants()

    # which font to use, which type of file we're reading
    tcod.console_set_custom_font('arial10x10.png', tcod.FONT_TYPE_GREYSCALE | tcod.FONT_LAYOUT_TCOD)
    # creates the console screen, with title and full-screen bool
    tcod.console_init_root(constants['SCR_W'], constants['SCR_H'], constants['WINDOW_TITLE'], False)

    # create the console
    con = tcod.console_new(constants['SCR_W'], constants['SCR_H'])
    # create the status bar / panel
    panel = tcod.console_new(constants['SCR_W'], constants['PANEL_H'])


    player = None
    entities = []
    game_map = None
    message_log = None
    game_state = None

    show_main_menu = True
    show_load_error_message = False

    # main_menu_background_image = tcod.image_load('menu_background.png')
    main_menu_background_image = None


    key = tcod.Key()
    mouse = tcod.Mouse()

    while not tcod.console_is_window_closed():
        tcod.sys_check_for_event(tcod.EVENT_KEY_PRESS | tcod.EVENT_MOUSE, key, mouse)

        if show_main_menu:
            main_menu(con, main_menu_background_image, constants['SCR_W'], constants['SCR_H'])

            if show_load_error_message:
                message_box(con, 'No save game to load', 50, constants['SCR_W'], constants['SCR_H'])

            tcod.console_flush()

            action = handle_main_menu(key)

            new_game = action.get('new_game')
            load_saved_game = action.get('load_game')
            exit_game = action.get('exit')

            if show_load_error_message and (new_game or load_saved_game or exit_game):
                show_load_error_message = False
            elif new_game:
                player, entities, game_map, message_log, game_state = get_game_variables(constants)
                game_state = GameStates.PLAYER_TURN

                show_main_menu = False

            elif load_saved_game:
                try:
                    player, entities, game_map, message_log, game_state = load_game()
                    show_main_menu = False
                except FileNotFoundError:
                    show_load_error_message = True
            elif exit_game:
                break

        else:
            tcod.console_clear(con)
            play_game(player, entities, game_map, message_log, game_state, con, panel, constants)

            show_main_menu = True

    # get all game variables
    player, entities, game_map, message_log, game_state = get_game_variables(constants)






if __name__ == '__main__':
    main()