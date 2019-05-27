import tcod

from game_messages import Message

from random import randint

class Fighter:
    def __init__(self, hp, defense, power, xp=0):
        self.base_max_hp = hp
        self.hp = hp
        self.base_defense = defense
        self.base_power = power
        self.xp = xp

    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus
    
    # try changing attack to include rolls/randomization
    @property
    def power(self):
        base_power_roll = 1 + randint(0, self.base_power)

        if self.owner and self.owner.equipment:
            bonus_roll = 1 + randint(0, self.owner.equipment.power_bonus)
        else:
            bonus_roll = 0
        return base_power_roll + bonus_roll
    
    # change defense too!
    @property
    def defense(self):
        base_defense_roll = 1 + randint(0, self.base_defense)

        if self.owner and self.owner.equipment:
            bonus_roll = 1 + randint(0, self.owner.equipment.defense_bonus)
        else:
            bonus_roll = 0
            
        return base_defense_roll + bonus_roll
    

    def take_damage(self, amount):
        results = []

        self.hp -= amount

        if self.hp <= 0:
            results.append({'dead': self.owner, 'xp': self.xp})

        return results

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

    def attack(self, target):
        results = []

        damage = self.power - target.fighter.defense

        if damage > 0:
            results.append({
                'message': Message('{0} attacks {1} for {2} damage'
                    .format(self.owner.name.capitalize(), target.name, str(damage)), tcod.white)
                })
            results.extend(target.fighter.take_damage(damage))

        else:
            results.append({
                'message': Message('{0} attacks {1} but does no damage'
                    .format(self.owner.name.capitalize(), target.name), tcod.white)
                })

        return results