import tcod

from components.fighter import Fighter
from components.inventory import Inventory
from components.level import Level
from components.equipment import Equipment
from components.equippable import Equippable

from entity import Entity
from game_messages import MessageLog
from game_states import GameStates
from map_objects.game_map import GameMap
from render_functions import RenderOrder
from equipment_slots import EquipmentSlots


def get_constants():
    WINDOW_TITLE = 'W I T C H'

    SCR_W = 80
    SCR_H = 50

    BAR_W = 20
    PANEL_H = 7
    PANEL_Y = SCR_H - PANEL_H

    MESSAGE_X = BAR_W + 2
    MESSAGE_W = SCR_W - BAR_W - 2
    MESSAGE_H = PANEL_H - 1

    MAP_W = 80
    MAP_H = 43

    ROOM_MAX_SIZE = 10
    ROOM_MIN_SIZE = 6
    MAX_ROOMS = 30

    FOV_ALGORITHM = 0
    FOV_LIGHT_WALLS = True
    FOV_RADIUS = 10

    MAX_MONSTERS_PER_ROOM = 3
    MAX_ITEMS_PER_ROOM = 2

    COLORS = {
        'dark_wall': tcod.black,
        'dark_ground':tcod.darker_sepia,
        'light_wall': tcod.darkest_sepia,
        'light_ground': tcod.dark_sepia
    }

    constants = {
        'WINDOW_TITLE': WINDOW_TITLE,
        'SCR_W': SCR_W,
        'SCR_H': SCR_H,
        'BAR_W': BAR_W,
        'PANEL_H': PANEL_H,
        'PANEL_Y': PANEL_Y,
        'MESSAGE_X': MESSAGE_X,
        'MESSAGE_W': MESSAGE_W,
        'MESSAGE_H': MESSAGE_H,
        'MAP_W': MAP_W,
        'MAP_H': MAP_H,
        'ROOM_MAX_SIZE': ROOM_MAX_SIZE,
        'ROOM_MIN_SIZE': ROOM_MIN_SIZE,
        'MAX_ROOMS': MAX_ROOMS,
        'FOV_ALGORITHM': FOV_ALGORITHM,
        'FOV_LIGHT_WALLS': FOV_LIGHT_WALLS,
        'FOV_RADIUS': FOV_RADIUS,
        'MAX_MONSTERS_PER_ROOM': MAX_MONSTERS_PER_ROOM,
        'MAX_ITEMS_PER_ROOM': MAX_ITEMS_PER_ROOM,
        'COLORS': COLORS,
    }

    return constants


def get_game_variables(constants):

# init components and compose them into the player
    fighter_component = Fighter(hp=100, base_defense=11, base_damage=2, base_to_hit=1)
    inventory_component = Inventory(capacity=26)
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(
        0, 
        0, 
        '@', 
        tcod.light_grey, 
        'Player', 
        blocks=True, 
        render_order=RenderOrder.ACTOR, 
        fighter=fighter_component, 
        inventory=inventory_component, 
        level=level_component,
        equipment=equipment_component
    )
    entities = [player]

    # instantiate starting weapon, add to inventory, and equip
    dagger_dice = {'number': 1, 'sides': 4}

    equippable_component = Equippable(EquipmentSlots.MAIN_HAND, damage_dice=dagger_dice)
    
    dagger = Entity(0, 0, '-', tcod.sky, 'Dagger', equippable=equippable_component)
    
    player.inventory.add_item(dagger)
    player.equipment.toggle_equip(dagger)

    # init map 
    game_map = GameMap(constants['MAP_W'], constants['MAP_H'])
    game_map.make_map(
        constants['MAX_ROOMS'], 
        constants['ROOM_MIN_SIZE'], 
        constants['ROOM_MAX_SIZE'], 
        constants['MAP_W'], 
        constants['MAP_H'], 
        player, 
        entities
    )

    # init message log
    message_log = MessageLog(
        constants['MESSAGE_X'], 
        constants['MESSAGE_W'], 
        constants['MESSAGE_H']
    )

    # set initial game state
    game_state = GameStates.PLAYER_TURN

    return player, entities, game_map, message_log, game_state
