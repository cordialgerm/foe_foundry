from math import ceil, floor
from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType, Weakened
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock, MonsterDials
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, LOW_POWER, Power, PowerBackport, PowerType
from ..utils import score


def score_deathly(
    candidate: BaseStatblock, undead_only: bool = False, caster_or_undead_only: bool = False
) -> float:
    creature_types = (
        {CreatureType.Undead, CreatureType.Fiend, CreatureType.Humanoid}
        if not undead_only
        else {CreatureType.Undead}
    )

    def humanoid_is_necromancer(c: BaseStatblock) -> bool:
        if c.creature_type == CreatureType.Humanoid:
            return c.attack_type.is_spell() and c.secondary_damage_type == DamageType.Necrotic
        else:
            return True

    return score(
        candidate=candidate,
        require_types=creature_types,
        require_callback=humanoid_is_necromancer if caster_or_undead_only else None,
        bonus_damage=DamageType.Necrotic,
    )


class _AuraOfDoom(PowerBackport):
    def __init__(self):
        super().__init__(name="Aura of Doom", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, caster_or_undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = easy_multiple_of_five(3 * stats.cr, min_val=5, max_val=30)

        feature = Feature(
            name="Aura of Doom",
            description=f"Each enemy within {distance} ft of {stats.selfref} who makes a death saving throw does so at disadvantage.",
            action=ActionType.Feature,
        )

        return stats, feature


class _AuraOfAnnihilation(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Aura of Annihilation", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, caster_or_undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        distance = 5 if stats.cr <= 11 else 10
        dmg = DieFormula.target_value(max(5 + stats.cr, 1.5 * stats.cr), force_die=Die.d6)
        dc = stats.difficulty_class_easy
        qualifier = f"non-{stats.creature_type.lower()}"

        feature = Feature(
            name="Aura of Annihilation",
            description=f"Each {qualifier} creature that ends its turn within {distance} ft of {stats.selfref} must make a DC {dc} Constitution saving throw. \
                On a failure, they take {dmg.description} necrotic damage and gain one Death Save failure. With three failures, a creature dies. \
                On a success, a creature takes half damage and does not gain a Death Save failure. With three successes, a creature is immune to this effect",
            action=ActionType.Feature,
        )

        return stats, feature


class _UndyingMinions(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Undying Minions", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, caster_or_undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Undying Minions",
            description=f"When a non-zombie ally who can see {stats.selfref} is reduced to 0 hp, that ally immediately becomes a zombie (retaining its current stats). \
                The ally gains the Undead type and stands up with 1 hit point. If damage reduces the zombie to 0 hit points, it may make a DC 15 Constitution saving throw. \
                On a success, the zombie drops to 1 hit point instead.",
            action=ActionType.Feature,
        )

        return stats, feature


class _WitheringBlow(PowerBackport):
    def __init__(self):
        super().__init__(name="Withering Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, None]:
        dc = stats.difficulty_class_easy

        withering_blow = stats.attack.scale(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            name="Withering Blow",
            replaces_multiattack=2,
        ).split_damage(DamageType.Necrotic, split_ratio=0.9)

        # the ongoing bleed damage should be equal to the necrotic damage formula for symmetry
        bleeding_dmg = (
            withering_blow.additional_damage.formula
            if withering_blow.additional_damage
            else DieFormula.from_expression("1d6")
        )
        bleeding = Bleeding(damage=bleeding_dmg, damage_type=DamageType.Necrotic, dc=dc)

        withering_blow = withering_blow.copy(
            additional_description=f"On a hit, the target gains {bleeding}."
        )

        stats = stats.add_attack(withering_blow)

        return stats, None


class _DrainingBlow(PowerBackport):
    def __init__(self):
        super().__init__(name="Draining Blow", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, undead_only=True)

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature]]:
        stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        feature = Feature(
            name="Draining Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, the {stats.selfref} converts all of that attack's damage to necrotic damage and {stats.selfref} regains hit points equal to the necrotic damage dealt.",
        )

        return stats, feature


class _ShadowStride(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Shadow Stride", power_type=PowerType.Theme, power_level=LOW_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, undead_only=False)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Shadow Stride",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports from one source of shadows to another that it can see within 60 feet.",
        )

        return stats, feature


class _FleshPuppets(PowerBackport):
    def __init__(self):
        super().__init__(
            name="Flesh Puppets", power_type=PowerType.Theme, power_level=HIGH_POWER
        )

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, undead_only=False, caster_or_undead_only=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        cr = int(ceil(stats.cr / 3))

        feature = Feature(
            name="Flesh Puppets",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"{stats.selfref.capitalize()} uses dark necromancy to resurrect the corpse of a nearby creature of CR {cr} or less. \
                The creature acts in initiative immediately after {stats.selfref} and obeys the commands of {stats.selfref} (no action required). \
                The flesh puppet has the same statistics as when the creature was living except it is now Undead, or uses the statistics of a **Skeleton**, **Zombie**, or **Ghoul**. \
                When the flesh puppet dies, the corpse is mangled beyond repair and is turned into a pile of viscera.",
        )

        return stats, feature


class _DevourSoul(PowerBackport):
    def __init__(self):
        super().__init__(name="Devour Soul", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, undead_only=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, force_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Devour Soul",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 30 feet of it that is not a Construct or an Undead. \
                The creature must succeed on a DC {dc} Charisma saving throw or take {dmg.description} necrotic damage. \
                If this damage reduces the target to 0 hit points, it dies and immediately rises as a **Ghoul** under {stats.selfref}'s control.",
        )

        return stats, feature


class _DrainStrength(PowerBackport):
    def __init__(self):
        super().__init__(name="Drain Strength", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_deathly(candidate, undead_only=True)

    def apply(self, stats: BaseStatblock, rng: Generator) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy

        dmg = DieFormula.target_value(1.1 * stats.attack.average_damage, force_die=Die.d6)
        weakened = Weakened(save_end_of_turn=True)

        feature = Feature(
            name="Drain Strength",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} attempts to magically drain the strength from a creature it can see within 5 feet. \
                The creature must make a DC {dc} Constitution save. On a failure, the creature takes {dmg.description} necrotic damage and is {weakened.caption} \
                for 1 minute (save ends at end of turn). {weakened.description_3rd}",
        )

        return stats, feature


AuraOfDoom: Power = _AuraOfDoom()
AuraOfAnnihilation: Power = _AuraOfAnnihilation()
DevourSoul: Power = _DevourSoul()
DrainingBlow: Power = _DrainingBlow()
DrainStrength: Power = _DrainStrength()
FleshPuppets: Power = _FleshPuppets()
ShadowStride: Power = _ShadowStride()
UndyingMinions: Power = _UndyingMinions()
WitheringBlow: Power = _WitheringBlow()

DeathlyPowers: List[Power] = [
    AuraOfDoom,
    AuraOfAnnihilation,
    DevourSoul,
    DrainingBlow,
    DrainStrength,
    FleshPuppets,
    ShadowStride,
    UndyingMinions,
    WitheringBlow,
]
