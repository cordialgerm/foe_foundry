from typing import Dict

import numpy as np

from ..statblocks import BaseStatblock, MonsterDials

rng = np.random.default_rng(20210518)


def as_low_ac_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, ac_modifier=-2)
    return stats.apply_monster_dials(dials)


def as_low_hp_artillery_max_dmg(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=2, hp_multiplier=0.8)
    return stats.apply_monster_dials(dials)


def as_low_ac_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(attack_hit_modifier=1, attack_damage_dice_modifier=1, ac_modifier=-2)
    return stats.apply_monster_dials(dials)


def as_low_hp_artillery_balanced(stats: BaseStatblock) -> BaseStatblock:
    dials = MonsterDials(
        attack_hit_modifier=1, attack_damage_dice_modifier=1, hp_multiplier=0.8
    )
    return stats.apply_monster_dials(dials)


ArtilleryVariants = {
    "Artillery.LowAcMaxDmg": as_low_ac_artillery_max_dmg,
    "Artillery.LowHpMaxDmg": as_low_hp_artillery_max_dmg,
    "Artillery.LowAcBalanced": as_low_ac_artillery_balanced,
    "Artillery.LowHpBalanced": as_low_hp_artillery_balanced,
}


def as_artillery(stats: BaseStatblock, variant: str | None = None) -> BaseStatblock:
    if variant is None:
        keys = list(ArtilleryVariants.keys())
        v: str = rng.choice(keys)
        variant = v

    return ArtilleryVariants[variant](stats=stats)


def as_artillery_all(stats: BaseStatblock) -> Dict[str, BaseStatblock]:
    return {k: v(stats=stats) for k, v in ArtilleryVariants.items()}
