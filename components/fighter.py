import tcod

from game_messages import Message

from random import randint

from random_utils import roll

class Fighter:
    def __init__(self, hp, base_to_hit, base_damage, base_defense, xp=0):

        self.base_max_hp = hp
        self.hp = hp

        self.base_to_hit = base_to_hit
        self.base_damage = base_damage
        self.base_defense = base_defense
        
        self.xp = xp



    @property
    def max_hp(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.max_hp_bonus
        else:
            bonus = 0

        return self.base_max_hp + bonus

    @property
    def to_hit(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.to_hit_bonus
        else:
            bonus = 0

        return self.base_to_hit + bonus        
    
    # try changing attack to include rolls/randomization
    # range provided for character card stats only
    @property
    def damage_range(self):

        min_damage = self.base_damage
        max_damage = self.base_damage

        if self.owner and self.owner.equipment:
            dice = self.owner.equipment.damage_dice

            for die in dice:
                number = die.get('number')
                sides = die.get('sides')
                min_damage += number
                max_damage += sides

        return [min_damage, max_damage]
    
    # keep defense flat for now
    @property
    def defense(self):
        if self.owner and self.owner.equipment:
            bonus = self.owner.equipment.defense_bonus
        else:
            bonus = 0

        return self.base_defense + bonus
    

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



    def defend(self):
        # code here in case we want to randomize defense (dodge roll, saves, etc)
        return self.defense


    def attack(self, target):
        results = []

        swing = self.base_to_hit + roll(1, 20)

        # if swing beats AC
        if swing >= target.fighter.defend():

            # get base damage
            damage = self.base_damage
            
            # roll equipment damage
            if self.owner and self.owner.equipment:
                dice = self.owner.equipment.damage_dice

                print('has dice')

                for die in dice:
                    number = die.get('number')
                    sides = die.get('sides')
                    damage += roll(number, sides)

                    print('rolled dice')


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

        else:
            results.append({
                'message': Message('{0} swings wildly and misses {1} [{2} vs {3}]'
                    .format(self.owner.name.capitalize(), target.name, swing, target.fighter.defend()), tcod.white)
                })

        return results