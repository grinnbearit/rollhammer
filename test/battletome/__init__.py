import unittest
import numpy as np
import battletome as bt
from unittest.mock import patch


class TestRollDice(unittest.TestCase):

    def test_shape(self):
        """
        the size should be set correctly
        """
        self.assertEqual(bt.roll_dice(3, 4).shape, (3, 4))
        self.assertEqual(bt.roll_dice(4).shape, (4, 100))


    def test_contents(self):
        """
        the rolls should be between 1 and 6 inclusive
        """
        self.assertTrue(np.isin(bt.roll_dice(100), range(1, 7)).all())


class TestRerollDice(unittest.TestCase):

    @patch("battletome.roll_dice")
    def test(self, mock_roll_dice):
        """
        only marked values should be rerolled
        """
        rolls = np.array([[1, 2, 3, 4]])
        rerolls = np.array([[5, 5, 6, 6]])
        rerolled = np.array([[5, 2, 3, 6]])

        mock_roll_dice.return_value = rerolls

        self.assertTrue((bt.reroll_dice(rolls, [1, 4]) == rerolled).all())
        mock_roll_dice.assert_called_once_with(1, 4)


    @patch("battletome.roll_dice")
    def test_set(self, mock_roll_dice):
        """
        passing sets should work as well
        """
        rolls = np.array([[1, 2, 3, 4]])
        rerolls = np.array([[5, 5, 6, 6]])
        rerolled = np.array([[5, 2, 3, 6]])

        mock_roll_dice.return_value = rerolls

        self.assertTrue((bt.reroll_dice(rolls, {1, 4}) == rerolled).all())
        mock_roll_dice.assert_called_once_with(1, 4)


class TestModifyDice(unittest.TestCase):

    def test_positive(self):
        """
        zeroes shouldn't be modified
        """
        rolls = np.array([0, 1, 6])
        modified = np.array([[0, 2, 7]])

        self.assertTrue((bt.modify_dice(rolls, 1) == modified).all())


    def test_negative(self):
        """
        zeroes shouldn't be modified
        values can't be modified below 1
        """
        rolls = np.array([[0, 1, 6]])
        modified = np.array([[0, 1, 5]])

        self.assertTrue((bt.modify_dice(rolls, -1) == modified).all())


class TestMarkAttacks(unittest.TestCase):

    def test_default(self):
        """
        no rerolls or modifiers by default
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        marked = np.array([[0, 0, 0, 1, 1, 1]])

        self.assertTrue((bt.mark_attacks(rolls, 3) == marked).all())


    @patch("battletome.roll_dice")
    def test_rerolls(self, mock_roll_dice):
        """
        rerolls should happen before auto checks
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        rerolls = np.array([[1, 6, 1, 1, 2, 1]])
        marked = np.array([[0, 1, 0, 1, 0, 0]])

        mock_roll_dice.return_value = rerolls

        self.assertTrue((bt.mark_attacks(rolls, 3, [1, 4, 6]) == marked).all())
        mock_roll_dice.assert_called_once_with(1, 6)


    def test_modifiers(self):
        """
        modifiers should be added after autochecks
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        marked_pos = np.array([[0, 0, 1, 1, 1, 1]])
        marked_neg = np.array([[0, 0, 0, 0, 0, 1]])

        self.assertTrue((bt.mark_attacks(rolls, 3, modifier=2) == marked_pos).all())
        self.assertTrue((bt.mark_attacks(rolls, 3, modifier=-4) == marked_neg).all())


class TestMarkFails(unittest.TestCase):

    def test_default(self):
        """
        no rerolls or modifiers by default
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        marked = np.array([[0, 1, 1, 0, 0, 0]])

        self.assertTrue((bt.mark_fails(rolls, 3) == marked).all())


    @patch("battletome.roll_dice")
    def test_rerolls(self, mock_roll_dice):
        """
        rerolls should happen before auto checks
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        rerolls = np.array([[1, 6, 1, 1, 2, 1]])
        marked = np.array([[0, 0, 1, 0, 1, 1]])

        mock_roll_dice.return_value = rerolls

        self.assertTrue((bt.mark_fails(rolls, 3, [1, 4, 6]) == marked).all())
        mock_roll_dice.assert_called_once_with(1, 6)


    def test_modifiers(self):
        """
        modifiers should be added after autochecks
        """
        rolls = np.array([[0, 1, 2, 3, 4, 6]])
        marked_pos = np.array([[0, 1, 0, 0, 0, 0]])
        marked_neg = np.array([[0, 1, 1, 1, 1, 1]])

        self.assertTrue((bt.mark_fails(rolls, 3, modifier=2) == marked_pos).all())
        self.assertTrue((bt.mark_fails(rolls, 3, modifier=-4) == marked_neg).all())


class TestRollHits(unittest.TestCase):

    @patch("battletome.mark_attacks")
    @patch("battletome.roll_dice")
    def test(self, mock_roll_dice, mock_mark_attacks):
        """
        tests run through
        """
        hit_rolls = np.array([[1, 2, 3]])
        hits = np.array([[0, 0, 1]])

        mock_roll_dice.return_value = hit_rolls
        mock_mark_attacks.return_value = hits

        self.assertTrue((bt.roll_hits(1, 3, size=3) == hits).all())

        mock_roll_dice.called_once_with(1, 3)
        mock_mark_attacks.called_once_with(hit_rolls, 3, [], 0)


class TestRollWounds(unittest.TestCase):

    @patch("battletome.mark_attacks")
    @patch("battletome.roll_dice")
    def test(self, mock_roll_dice, mock_mark_attacks):
        """
        tests run through
        """
        hits = np.array([[0, 1, 1]])
        dice_rolls = np.array([[1, 2, 3]])
        wound_rolls = np.array([[0, 2, 3]])
        wounds = np.array([[0, 0, 1]])

        mock_roll_dice.return_value = dice_rolls
        mock_mark_attacks.return_value = wounds

        self.assertTrue((bt.roll_wounds(hits, 3) == wounds).all())

        mock_roll_dice.called_once_with(1, 3)
        mock_mark_attacks.called_once_with(wound_rolls, 3, [], 0)


class TestRollFails(unittest.TestCase):

    @patch("battletome.mark_fails")
    @patch("battletome.roll_dice")
    def test(self, mock_roll_dice, mock_mark_fails):
        """
        tests run through
        """

        wounds = np.array([[0, 1, 1]])
        dice_rolls = np.array([[1, 2, 3]])
        save_rolls = np.array([[0, 2, 3]])
        fails = np.array([[0, 1, 0]])

        mock_roll_dice.return_value = dice_rolls
        mock_mark_fails.return_value = fails

        self.assertTrue((bt.roll_fails(wounds, 3) == fails).all())

        mock_roll_dice.called_once_with(1, 3)
        mock_mark_fails.called_once_with(save_rolls, 3, [], 0)


class TestDealDamage(unittest.TestCase):

    def test(self):
        """
        does the damage add up?
        """
        # 2 attacks x size 3
        fails = np.array([[0, 0, 1],
                          [0, 1, 1]])

        damage = np.array([0, 1, 2])
        self.assertTrue((bt.deal_damage(fails, 1) == damage).all())


class TestRollCombat(unittest.TestCase):

    @patch("battletome.deal_damage")
    @patch("battletome.roll_fails")
    @patch("battletome.roll_wounds")
    @patch("battletome.roll_hits")
    def test(self, mock_roll_hits, mock_roll_wounds, mock_roll_fails, mock_deal_damage):
        """
        tests run through
        """
        hits = np.array([[1, 1, 1]])
        wounds = np.array([[0, 1, 1]])
        fails = np.array([[0, 1, 0]])
        damage = np.array([0, 5, 0])

        mock_roll_hits.return_value = hits
        mock_roll_wounds.return_value = wounds
        mock_roll_fails.return_value = fails
        mock_deal_damage.return_value = damage

        self.assertTrue((bt.roll_combat(1, 2, 3, 4, 5, [1], [2], [3], 1, 2, 3, size=3) == damage).all())

        mock_roll_hits.called_once_with(1, 2, [1], 1, 3)
        mock_roll_wounds.called_once_with(hits, 3, [2], 2)
        mock_roll_fails.called_once_with(wounds, 4, [3], 3)
        mock_deal_damage.called_once_with(fails, 5)


if __name__=="__main__":
    unittest.main()
