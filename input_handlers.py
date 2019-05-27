import tcod

from game_states import GameStates

def handle_keys(key, game_state):
    if game_state == GameStates.PLAYER_TURN:
        return handle_player_turn_keys(key)
    elif game_state == GameStates.PLAYER_DEAD:
        return handle_player_dead_keys(key)
    elif game_state == GameStates.TARGETING:
        return handle_targeting_keys(key)
    elif game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        return handle_inventory_keys(key)
    elif game_state == GameStates.LEVEL_UP:
        return handle_level_up_menu(key)
    elif game_state == GameStates.CHARACTER_SCREEN:
        return handle_character_screen(key)

    return {}


def handle_player_turn_keys(key):
    key_char = chr(key.c)
    
    # Movement keys
    if key.vk == tcod.KEY_UP:
        return {'move': (0,-1)}
    elif key.vk == tcod.KEY_DOWN:
        return {'move': (0,1)}
    elif key.vk == tcod.KEY_LEFT:
        return {'move': (-1, 0)}
    elif key.vk == tcod.KEY_RIGHT:
        return {'move': (1, 0)}
    # diagonal movement a la QUD
    elif key_char == ';':
        return {'move': (-1, -1)}
    elif key_char == "'":
        return {'move': (1, -1)}
    elif key_char == '.':
        return {'move': (-1, 1)}
    elif key_char == '/':
        return {'move': (1, 1)}
    elif key_char == 'z':
        return {'wait': True}

    # get item
    if key_char == 'g':
        return {'pickup': True}

    # inventory menu
    elif key_char == 'i':
        return {'show_inventory': True}

    # drop items
    elif key_char == 'd':
        return {'drop_inventory': True}

    elif key.vk == tcod.KEY_ENTER:
        return {'take_stairs': True}

    elif key_char == 'c':
        return {'show_character_screen': True}

    # alt+enter for Fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Esc to exit the game
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    # no keypress
    return {}



def handle_player_dead_keys(key):
    key_char = chr(key.c)

    # inventory
    if key_char == 'i':
        return {'show_inventory': True}

    # alt+enter for Fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}

    # Esc to exit the game
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    # no keypress
    return {}


def handle_inventory_keys(key):
    index = key.c - ord('a')

    if index >= 0:
        return {'inventory_index': index}

    # alt+enter for Fullscreen
    if key.vk == tcod.KEY_ENTER and key.lalt:
        return {'fullscreen': True}
    # Esc to exit the game
    elif key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_targeting_keys(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_main_menu(key):
    key_char = chr(key.c)

    if key_char == 'a':
        return {'new_game': True}
    elif key_char == 'b':
        return {'load_game': True}
    elif key_char == 'c' or key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_level_up_menu(key):
    if key:
        key_char = chr(key.c)
        
        if key_char == 'a':
            return {'level_up': 'hp'}
        elif key_char == 'b':
            return {'level_up': 'str'}
        elif key_char == 'c':
            return {'level_up': 'def'}

    return {}


def handle_character_screen(key):
    if key.vk == tcod.KEY_ESCAPE:
        return {'exit': True}

    return {}


def handle_mouse(mouse):
    (x, y) = (mouse.cx, mouse.cy)

    if mouse.lbutton_pressed:
        return {'left_click': (x, y)}
    elif mouse.rbutton_pressed:
        return {'right_click': (x, y)}

    return {}