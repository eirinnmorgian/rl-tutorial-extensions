import tcod
import json

from enum import Enum

from components.equippable import Equippable
from entity import Entity

from equipment_slots import EquipmentSlots


# class WeaponTypes(Enum):
#     DAGGER = 1
#     WARHAMMER = 2
#     SHORT_SWORD = 3
#     LONG_SWORD = 4


# class ArmorTypes(Enum):
#     SMALL_SHIELD = 1


def create_weapon(weapon_type, x, y):

    # load all equipment data
    with open('data_files/equipment.json') as f:
        equipment = json.load(f)

    dagger = equipment['dagger']  
    warhammer = equipment['warhammer']
    short_sword = equipment['short_sword']
    long_sword = equipment['long_sword']


    if weapon_type == 'dagger':
        slot = getattr(EquipmentSlots, dagger['slot'])
        damage_dice = dagger['damage_dice']
        char = dagger['char']
        color = getattr(tcod, dagger['color'])
        name = dagger['name']

    elif weapon_type == 'warhammer':
        slot = getattr(EquipmentSlots, warhammer['slot'])
        damage_dice = warhammer['damage_dice']
        char = warhammer['char']
        color = getattr(tcod, warhammer['color'])
        name = warhammer['name']

    elif weapon_type == 'short_sword':
        slot = getattr(EquipmentSlots, short_sword['slot'])
        damage_dice = short_sword['damage_dice']
        char = short_sword['char']
        color = getattr(tcod, short_sword['color'])
        name = short_sword['name']

    elif weapon_type == 'long_sword':
        slot = getattr(EquipmentSlots, long_sword['slot'])
        damage_dice = long_sword['damage_dice']
        char = long_sword['char']
        color = getattr(tcod, long_sword['color'])
        name = long_sword['name']

    equippable_component = Equippable(
        slot,
        damage_dice=damage_dice
    )

    weapon = Entity(
        x, 
        y, 
        char, 
        color, 
        name,
        equippable=equippable_component
    )

    return weapon