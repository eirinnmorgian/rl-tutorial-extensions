


class Equippable:
    def __init__(self, slot, damage_dice=0, defense_bonus=0, to_hit_bonus=0, max_hp_bonus=0):
        self.slot = slot
        self.damage_dice = damage_dice
        self.defense_bonus = defense_bonus
        self.to_hit_bonus = to_hit_bonus
        self.max_hp_bonus = max_hp_bonus

