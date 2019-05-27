
import tcod
import math

from render_functions import RenderOrder

from components.item import Item


class Entity:
    """
    A generic object to represent players, enemies, items, etc
    """
    def __init__(
        self, 
        x, 
        y, 
        char, 
        color, 
        name, 
        blocks=False, 
        render_order=RenderOrder.CORPSE, 
        fighter=None, 
        ai=None, 
        item=None, 
        inventory=None, 
        stairs=None,
        level=None,
        equipment=None,
        equippable=None
    ):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.render_order = render_order
        self.fighter = fighter
        self.ai = ai
        self.item = item
        self.inventory = inventory
        self.stairs = stairs
        self.level = level
        self.equipment = equipment
        self.equippable = equippable

        # fighter and ai are passed in as Components
        # owner needs to be set upon initializing the entity
        if self.fighter:
            self.fighter.owner = self

        if self.ai:
            self.ai.owner = self

        if self.item:
            self.item.owner = self

        if self.inventory:
            self.inventory.owner = self

        if self.stairs:
            self.stairs.owner = self

        if self.level:
            self.level.owner = self

        if self.equipment:
            self.equipment.owner = self

        if self.equippable:
            self.equippable.owner = self

            if not self.item:
                item = Item()
                self.item = item
                self.item.owner = self

    def move(self, dx, dy):
        # Move the entity by a given amount
        self.x += dx
        self.y += dy

    def move_towards(self, target_x, target_y, game_map, entities):
        # AI movement of entity toward the player (or any target)
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))

        if not (game_map.is_blocked(self.x + dx, self.y + dy) or get_blocking_entities_at_location(entities, self.x + dx, self.y + dy)):
            self.move(dx, dy)

    # AI movement using A* pathfinding algorithm
    def move_astar(self, target, entities, game_map):
        # create a FOV map that has the dimensions of the game map
        fov = tcod.map_new(game_map.width, game_map.height)

        # scan the current map each turn, set all walls as unwalkable
        for y1 in range(game_map.height):
            for x1 in range(game_map.width):
                tcod.map_set_properties(fov, x1, y1, not game_map.tiles[x1][y1].block_sight, not game_map.tiles[x1][y1].blocked)

        # scan all objects to see if there are objects to be navigated around
        # check that obj is not self or target (so that start/end points are free)
        # AI class handles the situation of self is next to target (bypasses A*)
        for entity in entities:
            if entity.blocks and entity != self and entity != target:
                # set tile as a wall so that it must be navigated around
                tcod.map_set_properties(fov, entity.x, entity.y, True, False)

        # allocate an A* path
        # 1.41 is normal directional cost of moving, can be set as 0.0 if diagonals are prohibitied
        my_path = tcod.path_new_using_map(fov, 1.41)

        # compute path btwn self and target coordinates
        tcod.path_compute(my_path, self.x, self.y, target.x, target.y)

        # check if the path exists, and is shorter than 25 tiles
        # path size matters if you want monster to use alternate longer paths (eg. thru other rooms if player is in corridor)
        # keep path size low to prevent monters from running around map if there's a far-away alternate path
        if not tcod.path_is_empty(my_path) and tcod.path_size(my_path) < 25:
            # find next coords in computed full path
            x, y = tcod.path_walk(my_path, True)
            if x or y:
                # set self's coords to next path tile
                self.x = x
                self.y = y

        else:
            # keep old move fn as a backup so if there are no paths (corridor blocked) will still try to move toward player
            self.move_towards(target.x, target.y, game_map, entities)

        # delete path to free memory
        tcod.path_delete(my_path)


    def distance(self, x, y):
        return math.sqrt((x - self.x) ** 2 + (y - self.y) ** 2)


    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)


# fn outside of class
# return any entity that is 'blocking' at specified coordinates
def get_blocking_entities_at_location(entities, destination_x, destination_y):
    for entity in entities:
        if entity.blocks and entity.x == destination_x and entity.y == destination_y:
            return entity

    return None