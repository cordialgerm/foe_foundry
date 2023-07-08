from typing import Dict

import numpy as np

from ..skills import Stats
from ..statblocks import BaseStatblock, MonsterDials

rng = np.random.default_rng(20210518)


defender_save_proficiencies = dict(proficient_saves=set(Stats.All()))


def as_high_ac_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-2,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials)


def as_high_ac_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        ac_modifier=3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials)


def as_high_hp_low_hit_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-2,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials)


def as_high_hp_low_damage_defender(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        hp_multiplier=1.3,
        attack_hit_modifier=-1,
        attack_damage_dice_modifier=-1,
        attribute_modifications=defender_save_proficiencies,
    )
    return stats.apply_monster_dials(dials)


DefenderVariants = {
    "Defender.HighAcLowDamage": as_high_ac_low_damage_defender,
    "Defender.HighAcLowHit": as_high_ac_low_hit_defender,
    "Defender.HighHpLowDamage": as_high_hp_low_damage_defender,
    "Defender.HighHpLowHit": as_high_hp_low_hit_defender,
}


def as_defender(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(DefenderVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return DefenderVariants[variant](stats=stats)


def as_defender_all(stats: BaseStatblock) -> Dict[str, BaseStatblock]:
    return {k: v(stats=stats) for k, v in DefenderVariants.items()}
