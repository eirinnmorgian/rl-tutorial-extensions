import tcod

from enum import Enum

from game_states import GameStates

from menus import inventory_menu, level_up_menu, character_screen


class RenderOrder(Enum):
    STAIRS = 1
    CORPSE = 2
    ITEM = 3
    ACTOR = 4


def get_names_under_mouse(mouse, entities, fov_map):
    (x, y) = (mouse.cx, mouse.cy)

    names = [entity.name for entity in entities
        if entity.x == x and entity.y == y and tcod.map_is_in_fov(fov_map, entity.x, entity.y)]
    names = ', '.join(names)

    return names.capitalize()

def render_bar(panel, x, y, total_width, name, value, maximum, bar_color, back_color):
    bar_width = int(float(value) / maximum * total_width)

    tcod.console_set_default_background(panel, back_color)
    tcod.console_rect(panel, x, y, total_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_background(panel, bar_color)
    if bar_width > 0:
        tcod.console_rect(panel, x, y, bar_width, 1, False, tcod.BKGND_SCREEN)

    tcod.console_set_default_foreground(panel, tcod.white)
    tcod.console_print_ex(panel, int(x + total_width / 2), y, tcod.BKGND_NONE, tcod.CENTER, '{0}: {1}/{2}'.format(name, value, maximum))

def render_all(
    con, panel, entities, player, game_map, fov_map, 
    fov_recompute, message_log, screen_width, screen_height, 
    bar_width, panel_height, panel_y, mouse, colors, game_state):

    if fov_recompute:
        # Draw all tiles in game_map
        for y in range(game_map.height):
            for x in range(game_map.width):
                # check FOV of each tile's position
                visible = tcod.map_is_in_fov(fov_map, x, y)
                wall = game_map.tiles[x][y].block_sight
                if visible:
                    if wall:
                        tcod.console_set_char_background(
                            con, x, y, colors.get('light_wall'), 
                            tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(
                            con, x, y, colors.get('light_ground'), 
                            tcod.BKGND_SET)
                    game_map.tiles[x][y].explored = True
                elif game_map.tiles[x][y].explored:
                    if wall:
                        tcod.console_set_char_background(
                            con, x, y, colors.get('dark_wall'), 
                            tcod.BKGND_SET)
                    else:
                        tcod.console_set_char_background(
                            con, x, y, colors.get('dark_ground'), 
                            tcod.BKGND_SET)


    entities_in_render_order = sorted(entities, key=lambda x: x.render_order.value)

    # Draw all entities in the list, in correct order!

    for entity in entities_in_render_order:
        draw_entity(con, entity, fov_map, game_map)

    tcod.console_blit(con, 0, 0, screen_width, screen_height, 0, 0, 0)


    # new calls to set render for health bar and status panel
    tcod.console_set_default_background(panel, tcod.black)
    tcod.console_clear(panel)

    # print game messages, one line at a time
    y = 1
    for message in message_log.messages:
        tcod.console_set_default_foreground(panel, message.color)
        tcod. console_print_ex(panel, message_log.x, y, tcod.BKGND_NONE, tcod.LEFT, message.text)
        y += 1

    # display HP meter
    render_bar(panel, 1, 1, bar_width, 'HP', player.fighter.hp, player.fighter.max_hp, tcod.light_red, tcod.darker_red)

    # display dungeon level
    tcod.console_print_ex(panel, 1, 3, tcod.BKGND_NONE, tcod.LEFT, 'Dungeon level: {0}'.format(game_map.dungeon_level))

    # display mouseover names
    tcod.console_set_default_foreground(panel, tcod.light_gray)
    tcod.console_print_ex(panel, 1, 0, tcod.BKGND_NONE, tcod.LEFT, get_names_under_mouse(mouse, entities, fov_map))
    
    # blit console to screen
    tcod.console_blit(panel, 0, 0, screen_width, panel_height, 0, 0, panel_y)

    # display / drop inventory menu
    if game_state in (GameStates.SHOW_INVENTORY, GameStates.DROP_INVENTORY):
        if game_state == GameStates.SHOW_INVENTORY:
            inventory_title = 'Press the key next to an item to use it, or ESC to cancel.\n'
        else:
            inventory_title = 'Press the key next to an item to drop it, or ESC to cancel.\n'
        inventory_menu(con, inventory_title, player, 50, screen_width, screen_height)

    # display level up menu
    elif game_state == GameStates.LEVEL_UP:
        level_up_menu(con, 'Level up! Choose a stat to raise:', player, 40, screen_width, screen_height)

    elif game_state == GameStates.CHARACTER_SCREEN:
        character_screen(player, 30, 10, screen_width, screen_height)

def clear_all(con, entities):
    for entity in entities:
        clear_entity(con, entity)


def draw_entity(con, entity, fov_map, game_map):
    # draw only if shown in FOV OR if stairs tile has been explored
    if tcod.map_is_in_fov(fov_map, entity.x, entity.y) or (entity.stairs and game_map.tiles[entity.x][entity.y].explored):
        # set foreground color, 0 (or console) determines which console to draw onto
        tcod.console_set_default_foreground(con, entity.color)
        # params: console, x/y coords, text char, bkgrnd
        tcod.console_put_char(con, entity.x, entity.y, entity.char, tcod.BKGND_NONE)


def clear_entity(con, entity):
    # overwrite previous entity position
    tcod.console_put_char(con, entity.x, entity.y, ' ', tcod.BKGND_NONE)


