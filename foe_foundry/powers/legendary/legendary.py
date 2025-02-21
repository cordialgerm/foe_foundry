from ...attributes import Skills, Stats
from ...features import ActionType, Feature
from ...powers import LOW_POWER
from ...statblocks import BaseStatblock, MonsterDials
from ...utils.rounding import easy_multiple_of_five
from .features import get_legendary_actions


def make_legendary(
    stats: BaseStatblock, features: list[Feature], has_lair: bool
) -> tuple[BaseStatblock, list[Feature]]:
    if stats.cr <= 4:
        n = 1
    elif stats.cr <= 7:
        n = 2
    else:
        n = 3

    original_dpr = stats.dpr

    # HP and LR Adjustments

    # each legendary resistance will cost the monster some HP
    # so we'll want to increase the creature's HP to accomodate
    # we want bosses to die in about 4 turns so with a 4 person party that's 16 hits
    # the legendary action shouldn't feel like a waste, so it needs to do something on the order of 1/16th of the creature's HP
    # so we'll increase the creature's HP by half the amount of damage that each legendary resistance inflicts to help compensate

    turns_to_die = 4
    assumed_pcs = 4
    hits_to_die = turns_to_die * assumed_pcs
    average_damage_per_hit = stats.hp.average / hits_to_die
    lr_damage_effectiveness = (
        0.75  # it can't be 1.0 because then draining the LR would be too good
    )

    legendary_resistance_damage = easy_multiple_of_five(
        lr_damage_effectiveness * average_damage_per_hit, min_val=5
    )
    new_hp_multiplier = 1.0 + 0.5 * legendary_resistance_damage * n / stats.hp.average

    features.append(
        Feature(
            name="Legendary Prowess",
            action=ActionType.Feature,
            uses=n,
            description=f"The {stats.name} can choose to succeed on a saving throw or ability check instead of failing. When it does so, it takes {legendary_resistance_damage} force damage",
        )
    )

    # AC Adjustments
    if stats.cr <= 8:
        ac_increase = 1
    elif stats.cr <= 12:
        ac_increase = 2
    elif stats.cr <= 17:
        ac_increase = 3
    elif stats.cr <= 23:
        ac_increase = 4
    else:
        ac_increase = 5

    # Damage Adjustments

    # The legendary creature will have an Attack legendary action, so its total damage output will go up dramatically
    # we need to adjust the creature's total damage output to account for this
    # we also want to reduce the total number of attacks the creature can make in a turn to not make it take too long
    stats = stats.with_reduced_attacks(reduce_by=1)

    # Power Adjustments
    # legendary creature will have some more powers
    recommended_powers_modifier = LOW_POWER

    # Apply HP, AC, and power adjustments
    stats = stats.apply_monster_dials(
        MonsterDials(
            hp_multiplier=new_hp_multiplier,
            ac_modifier=ac_increase,
            recommended_powers_modifier=recommended_powers_modifier,
        )
    )

    # Stat Adjustments
    stats = stats.scale({Stats.CON: 2})

    # Skill Adjustments
    # Initiative

    if stats.cr >= 8 and not stats.attributes.has_proficiency_or_expertise(
        Skills.Initiative
    ):
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    if stats.cr >= 16 and Skills.Initiative not in stats.attributes.expertise_skills:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # Save Adjustments
    stats = stats.grant_save_proficiency(stats.primary_attribute, Stats.CON)

    if stats.cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # Legendary Action Adjustments
    stats = stats.as_legendary(actions=n, resistances=n, has_lair=has_lair)

    # Rescale Attack Damage
    target_dpr = 1.3 * original_dpr
    new_dpr = stats.dpr
    new_multiplier = target_dpr / new_dpr
    stats = stats.apply_monster_dials(
        MonsterDials(attack_damage_multiplier=new_multiplier)
    )

    # Legendary Actions
    legendary_actions = get_legendary_actions(stats, features)

    new_features = features.copy() + legendary_actions
    return stats, new_features
