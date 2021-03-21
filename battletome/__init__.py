import numpy as np
import scipy.stats as stats


def roll_dice(n, size=100):
    """
    returns a matrix of `n` D6 x size
    """
    return stats.randint(1, 7).rvs((n, size))


def reroll_dice(rolls, values):
    """
    rerolls dice which match `values` and returns a new rolls matrix
    """
    n, size = rolls.shape
    mask = np.isin(rolls, values)
    rerolls = mask * roll_dice(n, size)
    return (rolls * (1 - mask)) + rerolls


def modify_dice(rolls, modifier):
    """
    changes dice values by modifier to a minimum of 1
    """
    mask = rolls > 0
    modified = rolls + modifier
    modified = np.where(modified < 1, 1, modified)
    modified = mask * modified
    return modified


def mark_attacks(rolls, up, rerolls=[], modifier=0):
    """
    marks specific dice rolls as successes, `up` is the minimum needed
    after rerolls, 1s are auto fails and 6s are auto successes
    after modifiers, for the remaining >= up are successes
    returns a binary matrix with the same shape as `rolls`
    valid for hits and wounds
    """
    rerolled = reroll_dice(rolls, rerolls)
    autopass = rerolled == 6
    autofail = rerolled == 1
    modified = modify_dice(rolls, modifier)
    successes = np.where(autopass, 1,
                         np.where(autofail, 0,
                                  modified >= up))
    return successes


def mark_fails(rolls, below, rerolls=[], modifier=0):
    """
    marks specific dice rolls as failures, `below` is the min safe threshold
    after rerolls, 1s are auto fails
    after modifiers, for the remaining < below are failures
    returns a binary matrix with the same shape as `rolls`
    valid for saves
    """
    rerolled = reroll_dice(rolls, rerolls)
    autofail = rerolled == 1
    modified = modify_dice(rolls, modifier)
    failures = np.where(autofail, 1,
                        np.where(modified != 0, modified < below, 0))
    return failures


def roll_hits(attacks, to_hit, rerolls=[], modifier=0,
              size=100):
    """
    returns a binary matrix of dice x size with successful hits
    marked as 1s
    """
    hit_rolls = roll_dice(attacks, size)
    hits = mark_attacks(hit_rolls, to_hit, rerolls, modifier)
    return hits


def roll_wounds(hits, to_wound, rerolls=[], modifier=0):
    """
    marks successful wounds as 1
    """
    attacks, size = hits.shape
    wound_rolls = hits * roll_dice(attacks, size)
    wounds = mark_attacks(wound_rolls, to_wound, rerolls, modifier)
    return wounds


def roll_fails(wounds, to_save, rerolls=[], modifier=0):
    """
    marks unsuccessful saves as 1
    """
    attacks, size = wounds.shape
    save_rolls = wounds * roll_dice(attacks, size)
    fails = mark_fails(save_rolls, to_save, rerolls, modifier)
    return fails


def deal_damage(fails, damage):
    """
    returns a 1D array of damage
    """
    return (fails * damage).sum(axis=0)


def roll_combat(attacks, to_hit, to_wound, to_save, damage,
                hit_rerolls=[], wound_rerolls=[], save_rerolls=[],
                hit_modifier=0, wound_modifier=0, save_modifier=0,
                size=100):
    """
    simulates combat with hit, wound, save rolls
    """
    hits = roll_hits(attacks, to_hit, hit_rerolls, hit_modifier, size)
    wounds = roll_wounds(hits, to_wound, wound_rerolls, wound_modifier)
    fails = roll_fails(wounds, to_save, save_rerolls, save_modifier)
    damage = deal_damage(fails, damage)
    return damage
