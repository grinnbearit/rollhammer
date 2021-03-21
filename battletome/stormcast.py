import battletome as bt


class Liberator():
# https://drive.google.com/drive/folders/15UFIYr5Nzb0VCTnjTegoO1SioE8J-trj

    WEAPONS = {0: "Warhammer",
               1: "Warblade",
               2: "Grandhammer",
               3: "Grandblade"}


    def __init__(self, weapon=0, is_prime=False, has_paired=False, health=2):
        """
        `weapon` is the weapon code [0 - 3]
        `is_prime` marks if models are Prime
        `has_paired` marked if models have paired weapons, valid for {0, 1}
        `health` can be 1 or 2
        """
        assert(weapon in [0, 1, 2, 3])
        assert(not((weapon in [2, 3]) and has_paired))
        assert(health in [1, 2])

        self.weapon = weapon
        self.is_prime = is_prime
        self.has_paired = has_paired
        self.health = health

        self.attacks = 3 if is_prime else 2
        self.to_hit = 4 if weapon in [0, 2] else 3
        self.to_wound = 3 if weapon in [0, 2] else 4
        self.rend = 0 if weapon in [0, 1] else -1
        self.damage = 1 if weapon in [0, 1] else 2

        self.has_shield = not (self.has_paired or (weapon in [2, 3]))


    def __repr__(self):
        name_str = "Liberator-Prime" if self.is_prime else "Liberator"
        if self.has_paired:
            weapon_str = "Paired {0}s".format(self.WEAPONS[self.weapon])
        elif self.has_shield:
            weapon_str = "{0} and Sigmarite Shield".format(self.WEAPONS[self.weapon])
        else:
            weapon_str = self.WEAPONS[self.weapon]

        return f"{name_str} ({weapon_str}) [{self.health}/2]"


    def describe(self):
        """
        returns a string representation of all important flags and weapons
        """
        self_str = str(self)
        stats_str = ("A:{0}, H:{1}+, W:{2}+, R:{3}, D:{4}"
                     .format(self.attacks,
                             self.to_hit,
                             self.to_wound,
                             self.rend if self.rend != 0 else "-",
                             self.damage))
        return f"{self_str}\n{stats_str}"


    def attack(self, n=1, size=100, to_save=4, save_rerolls=[], save_modifier=0,
               is_tyrant=False):
        """
        `n` is the number of models attacking
        `size` if the number of simulations
        `is_tyrant` set if the attack is against a tyrant
        """
        attacks = n * self.attacks
        hit_rerolls = []
        hit_modifier = 0
        wound_rerolls = []
        wound_modifier = 0

        if self.has_paired:
            hit_rerolls = [1]

        if is_tyrant:
            hit_modifier = 1

        save_modifier += self.rend

        damage = bt.roll_combat(attacks, self.to_hit, self.to_wound,
                                to_save, self.damage,
                                hit_rerolls, wound_rerolls, save_rerolls,
                                hit_modifier, wound_modifier, save_modifier,
                                size)

        return damage
