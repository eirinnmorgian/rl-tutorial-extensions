import tcod
import json

from components.fighter import Fighter, PassiveHealing
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

from create_equipment import create_weapon


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

    with open('data_files/player.json') as f:
        player_data = json.load(f)

    passive_healing = player_data['passive_healing']
    fighter = player_data['fighter']
    inventory = player_data['inventory']
    char = player_data['char']
    color = getattr(tcod, player_data['color'])
    name = player_data['name']

    # init components and compose them into the player
    passive_healing_component = PassiveHealing(
        turnover=passive_healing['turnover'], 
        rate=passive_healing['rate']
    )
    fighter_component = Fighter(
        hp=fighter['hp'], 
        base_defense=fighter['base_defense'], 
        base_damage=fighter['base_damage'], 
        base_to_hit=fighter['base_to_hit'], 
        passive_healing=passive_healing_component
    )
    inventory_component = Inventory(capacity=inventory['capacity'])
    level_component = Level()
    equipment_component = Equipment()

    player = Entity(
        0, 
        0, 
        char, 
        color, 
        name, 
        blocks=True, 
        render_order=RenderOrder.ACTOR, 
        fighter=fighter_component, 
        inventory=inventory_component, 
        level=level_component,
        equipment=equipment_component
    )
    entities = [player]

    # # instantiate starting weapon, add to inventory, and equip
    # with open('data_files/equipment.json') as f:
    #     equipment = json.load(f)

    # dagger = equipment['dagger']  

    # slot = getattr(EquipmentSlots, dagger['slot'])
    # damage_dice = dagger['damage_dice']
    # char = dagger['char']
    # color = getattr(tcod, dagger['color'])
    # name = dagger['name']

    # equippable_component = Equippable(
    #     slot,
    #     damage_dice=damage_dice
    # )

    # starting_weapon = Entity(
    #     0, 
    #     0, 
    #     char, 
    #     color, 
    #     name,
    #     equippable=equippable_component
    # )

    starting_weapon = create_weapon('dagger', 0, 0)

    player.inventory.add_item(starting_weapon)
    player.equipment.toggle_equip(starting_weapon)

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
