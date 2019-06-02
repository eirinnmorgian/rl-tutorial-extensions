# 3rd party imports
import tcod
import json

from random import randint

# local imports
from entity import Entity
from game_messages import Message
from render_functions import RenderOrder
from item_functions import heal, cast_lightning, cast_fireball, cast_confuse
from random_utils import random_choice_from_dict, from_dungeon_level

from map_objects.tile import Tile
from map_objects.rectangle import Rect

from components.fighter import Fighter
from components.ai import BasicMonster
from components.item import Item
from components.stairs import Stairs
from components.equipment import EquipmentSlots, Equipment
from components.equippable import Equippable

from create_equipment import create_weapon


class GameMap:
    '''
    setup map and populate with rooms, tunnels, monsters.
    init all monster stats here.
    '''
    def __init__(self, width, height, dungeon_level=1):
        self.width = width
        self.height = height
        self.tiles = self.initialize_tiles()

        self.dungeon_level = dungeon_level

    def initialize_tiles(self):
        # generate map grid
        tiles = [[Tile(True) for y in range (self.height)] for x in range(self.width)]

        return tiles

    def make_map(
            self, 
            max_rooms, 
            room_min_size, 
            room_max_size, 
            map_width, 
            map_height, 
            player,
            entities
        ):
        rooms = []
        num_rooms = 0

        center_of_last_room_x = None
        center_of_last_room_y = None

        for r in range(max_rooms):
            # random width and height
            w = randint(room_min_size, room_max_size)
            h = randint(room_min_size, room_max_size)
            # random position w/o overflowing map
            x = randint(0, map_width - w - 1)
            y = randint(0, map_height - h - 1)

            # 'Rect' class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # loop thru other rooms, break out of loop if any intersect
            for other_room in rooms:
                if new_room.intersects(other_room):
                    break
            else:
                # pythonic for-else statement:
                # if didn't break, room valid, do this
                self.create_room(new_room)
                # get center coords of room
                (new_x, new_y) = new_room.center()

                # for stairs
                center_of_last_room_x = new_x
                center_of_last_room_y = new_y

                # start player @ 1st room
                if num_rooms == 0:
                    player.x = new_x
                    player.y = new_y
                else:
                    # all other rooms: 
                    # connect to prev room w tunnel

                    # center coords of prev
                    (prev_x, prev_y) = rooms[num_rooms - 1].center()

                    # coin toss
                    if randint(0, 1) == 1:
                        # move horiz, then vert
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # move vert, then horiz
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                self.place_entities(new_room, entities)

                # finally, apprend new room to list and increment
                rooms.append(new_room)
                num_rooms += 1

        # create stairs @ center of last room created
        stairs_component = Stairs(self.dungeon_level + 1)
        down_stairs = Entity(
            center_of_last_room_x, 
            center_of_last_room_y, 
            '>', 
            tcod.white, 
            'Stairs', 
            render_order=RenderOrder.STAIRS, 
            stairs=stairs_component
        )
        entities.append(down_stairs)
        print('stairs created: {0}, {1}'.format(down_stairs.x, down_stairs.y))


    def create_room(self, room):
        # loop thru tiles in rectangle and unblock them
        # increase x + y by one to ensure a wall on each side
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self.tiles[x][y].blocked = False
                self.tiles[x][y].block_sight = False


    def create_h_tunnel(self, x1, x2, y):
        # horizontal
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        # vertical
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self.tiles[x][y].blocked = False
            self.tiles[x][y].block_sight = False

    def is_blocked(self, x, y):
        if self.tiles[x][y].blocked:
            return True

        return False


    def place_entities(self, room, entities):

        # use random utility and tables to determine how many of each per level
        # table is laid out [number/weight, level]
        max_monsters_per_room = from_dungeon_level([[2, 1], [3, 4], [5, 6]], self.dungeon_level)
        max_items_per_room = from_dungeon_level([[1, 1], [2, 4]], self.dungeon_level)

        # get random num of monsters and items
        number_of_monsters = randint(0, max_monsters_per_room)
        number_of_items = randint(0, max_items_per_room)


        # get monster, equipment data from json file

        with open('data_files/monsters.json') as f:
            monsters = json.load(f)

        orc = monsters['orc']
        troll = monsters['troll']


        with open('data_files/equipment.json') as f:
            equipment = json.load(f)

        short_sword = equipment['short_sword']
        small_shield = equipment['small_shield']
        long_sword = equipment['long_sword']


        with open('data_files/consumables.json') as f:
            consumables = json.load(f)

        healing_potion = consumables['healing_potion']
        confusion_scroll = consumables['confusion_scroll']
        fireball_scroll = consumables['fireball_scroll']
        lightning_scroll = consumables['lightning_scroll']


        monster_chances = {
            'orc': from_dungeon_level(orc['from_dungeon_level'], self.dungeon_level),
            'troll': from_dungeon_level(troll['from_dungeon_level'], self.dungeon_level)
        }
        
        item_chances = {
            'short_sword': from_dungeon_level(short_sword['from_dungeon_level'], self.dungeon_level),
            'long_sword': from_dungeon_level(long_sword['from_dungeon_level'], self.dungeon_level),            
            'small_shield': from_dungeon_level(small_shield['from_dungeon_level'], self.dungeon_level), 

            'healing_potion': from_dungeon_level(healing_potion['from_dungeon_level'], self.dungeon_level),
            'confusion_scroll': from_dungeon_level(confusion_scroll['from_dungeon_level'], self.dungeon_level), 
            'lightning_scroll': from_dungeon_level(lightning_scroll['from_dungeon_level'], self.dungeon_level), 
            'fireball_scroll': from_dungeon_level(fireball_scroll['from_dungeon_level'], self.dungeon_level),
        }

        # place monsters
        for i in range(number_of_monsters):
            # choose a random location in the room
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            # if no entity currently at location
            if not any([entity for entity in entities if entity.x == x and entity.y ==y]):

                monster_choice = random_choice_from_dict(monster_chances)

                if monster_choice == 'orc':

                    hp = orc['hp']
                    base_defense = orc['base_defense']
                    base_damage = orc['base_damage']
                    base_to_hit = orc['base_to_hit']
                    xp = orc['xp']
                    char = orc['char']
                    color = getattr(tcod, orc['color'])
                    name = orc['name']
                    starting_weapon = orc['starting_weapon']

                    # init fighter and ai components
                    fighter_component = Fighter(hp=hp, base_defense=base_defense, base_damage=base_damage, base_to_hit=base_to_hit, xp=xp)
                    ai_component = BasicMonster()
                    equipment_component = Equipment()

                    monster = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                        equipment=equipment_component
                    )

                    weapon = create_weapon(starting_weapon, 0, 0)
                    monster.equipment.toggle_equip(weapon)

                elif monster_choice == 'troll':

                    hp = troll['hp']
                    base_defense = troll['base_defense']
                    base_damage = troll['base_damage']
                    base_to_hit = troll['base_to_hit']
                    xp = troll['xp']
                    char = troll['char']
                    color = getattr(tcod, troll['color'])
                    name = troll['name']
                    starting_weapon = troll['starting_weapon']

                    # init fighter and ai components
                    fighter_component = Fighter(hp=hp, base_defense=base_defense, base_damage=base_damage, base_to_hit=base_to_hit, xp=xp)
                    ai_component = BasicMonster()
                    equipment_component = Equipment()

                    monster = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        blocks=True,
                        render_order=RenderOrder.ACTOR,
                        fighter=fighter_component,
                        ai=ai_component,
                        equipment=equipment_component
                    )

                    weapon = create_weapon(starting_weapon, 0, 0)
                    monster.equipment.toggle_equip(weapon)

                entities.append(monster)

        # place items

        for i in range(number_of_items):
            x = randint(room.x1 + 1, room.x2 - 1)
            y = randint(room.y1 + 1, room.y2 - 1)

            if not any([entity for entity in entities if entity.x == x and entity.y == y]):
                
                item_choice = random_choice_from_dict(item_chances)
                # randomize dropped items

                if item_choice == 'healing_potion':

                    amount = healing_potion['amount']
                    char = healing_potion['char']
                    color = getattr(tcod, healing_potion['color'])
                    name = healing_potion['name']

                    item_component = Item(
                        use_function=heal, 
                        amount=amount
                    )

                    item = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        render_order=RenderOrder.ITEM, 
                        item=item_component
                    )

                elif item_choice == 'confusion_scroll':

                    targeting = confusion_scroll['targeting']
                    targeting_message = Message(confusion_scroll['targeting_message'], getattr(tcod, confusion_scroll['message_color']))
                    char = confusion_scroll['char']
                    color = getattr(tcod, confusion_scroll['color'])
                    name = confusion_scroll['name']

                    item_component = Item(
                        use_function=cast_confuse, 
                        targeting=targeting, 
                        targeting_message=targeting_message
                    )

                    item = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        render_order=RenderOrder.ITEM, 
                        item=item_component, 
                    )

                elif item_choice == 'fireball_scroll':

                    targeting = fireball_scroll['targeting']
                    targeting_message = Message(fireball_scroll['targeting_message'], getattr(fireball_scroll['message_color']))
                    damage = fireball_scroll['damage']
                    radius = fireball_scroll['radius']
                    char = fireball_scroll['char']
                    color = getattr(tcod, fireball_scroll['color'])
                    name = fireball_scroll['name']

                    item_component = Item(
                        use_function=cast_fireball, 
                        targeting=targeting, 
                        targeting_message=targeting_message,
                        damage=damage,
                        radius=radius
                    )

                    item = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        render_order=RenderOrder.ITEM, 
                        item=item_component, 
                    )

                elif item_choice == 'lightning_scroll':

                    damage = lightning_scroll['damage']
                    max_range = lightning_scroll['max_range']
                    char = lightning_scroll['char']
                    color = getattr(tcod, lightning_scroll['color'])
                    name = lightning_scroll['name']

                    item_component = Item(
                        use_function=cast_lightning, 
                        damage=damage, 
                        max_range=max_range
                    )
                    item = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name, 
                        render_order=RenderOrder.ITEM, 
                        item=item_component, 
                    )

                elif item_choice == 'short_sword':

                    item = create_weapon('short_sword', x, y)

                elif item_choice == 'long_sword':

                    item = create_weapon('long_sword', x, y)

                elif item_choice == 'small_shield':

                    slot = getattr(EquipmentSlots, small_shield['slot'])
                    defense_bonus = small_shield['defense_bonus']
                    char = small_shield['char']
                    color = getattr(tcod, small_shield['color'])
                    name = small_shield['name']

                    equippable_component = Equippable(
                        slot,
                        defense_bonus=defense_bonus
                    )
                    item = Entity(
                        x, 
                        y, 
                        char, 
                        color, 
                        name,
                        equippable=equippable_component
                    )

                entities.append(item)



    def next_floor(self, player, message_log, constants):
        self.dungeon_level += 1
        entities = [player]

        self.tiles = self.initialize_tiles()

        print('constants in GAME_MAP {0}'.format(constants))
        self.make_map(constants['MAX_ROOMS'], 
            constants['ROOM_MIN_SIZE'], 
            constants['ROOM_MAX_SIZE'], 
            constants['MAP_W'], 
            constants['MAP_H'], 
            player, 
            entities
        )

        player.fighter.heal(player.fighter.max_hp // 2)

        message_log.add_message(Message('You take a moment to rest, and recover your strength', tcod.light_violet))

        return entities




