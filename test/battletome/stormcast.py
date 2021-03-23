import unittest
import numpy as np
from unittest.mock import call, patch
from battletome.stormcast import Liberator


class TestLiberator(unittest.TestCase):

    def test_constructor(self):
        """
        Are all invalid Liberators disallowed
        """
        self.assertRaises(AssertionError, Liberator, weapon=4)
        self.assertRaises(AssertionError, Liberator, weapon=3, has_paired=True)
        self.assertRaises(AssertionError, Liberator, health=0)

        liberator = Liberator()
        self.assertEqual(liberator.weapon, 0)
        self.assertFalse(liberator.is_prime)
        self.assertFalse(liberator.has_paired)
        self.assertEqual(liberator.health, 2)
        self.assertEqual(liberator.attacks, 2)
        self.assertEqual(liberator.to_hit, 4)
        self.assertEqual(liberator.to_wound, 3)
        self.assertEqual(liberator.rend, 0)
        self.assertEqual(liberator.damage, 1)
        self.assertTrue(liberator.has_shield)

        self.assertEqual(Liberator(is_prime=True).attacks, 3)
        self.assertEqual(Liberator(weapon=1).to_hit, 3)
        self.assertEqual(Liberator(weapon=1).to_wound, 4)
        self.assertEqual(Liberator(weapon=2).rend, -1)
        self.assertEqual(Liberator(weapon=2).damage, 2)
        self.assertFalse(Liberator(has_paired=True).has_shield)


    def test_repr(self):
        """
        Is the string representation correct for all implementations?
        """
        self.assertEqual(str(Liberator()),
                         "Liberator (Warhammer and Sigmarite Shield) [2/2]")

        self.assertEqual(str(Liberator(is_prime=True)),
                         "Liberator-Prime (Warhammer and Sigmarite Shield) [2/2]")

        self.assertEqual(str(Liberator(has_paired=True)),
                         "Liberator (Paired Warhammers) [2/2]")

        self.assertEqual(str(Liberator(weapon=2)),
                         "Liberator (Grandhammer) [2/2]")


    def test_describe(self):
        """
        Is the describe string correct for all representations?
        """
        liberator = Liberator()
        self.assertEqual(liberator.describe(),
                         str(liberator) + "\nA:2, H:4+, W:3+, R:-, D:1")

        liberator = Liberator(weapon=2)
        self.assertEqual(liberator.describe(),
                         str(liberator) + "\nA:2, H:4+, W:3+, R:-1, D:2")


    @patch("battletome.roll_combat")
    def test_attack(self, mock_roll_combat):
        """
        does the combat function get passed the right parameters?
        """
        # default attack
        Liberator().attack()
        mock_roll_combat.assert_called_with(2, 4, 3, 4, 1,
                                            set(), set(), set(),
                                            0, 0, 0,
                                            100)

        # all arguments
        Liberator().attack(1, 2, 3, {4}, {5}, {6}, 1, 2, 3)
        mock_roll_combat.assert_called_with(2, 4, 3, 3, 1,
                                            {4}, {5}, {6},
                                            1, 2, 3,
                                            2)

        # paired weapons
        # WARNING: hit_rerolls needs to be reset because of Mock internals
        Liberator(has_paired=True).attack(hit_rerolls=set())
        mock_roll_combat.assert_called_with(2, 4, 3, 4, 1,
                                            {1}, set(), set(),
                                            0, 0, 0,
                                            100)


        # against tyrant
        Liberator().attack(is_tyrant=True)
        mock_roll_combat.assert_called_with(2, 4, 3, 4, 1,
                                            set(), set(), set(),
                                            1, 0, 0,
                                            100)


if __name__=="__main__":
    unittest.main()
