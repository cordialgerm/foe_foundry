from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock, MonsterDials
from ..power import HIGH_POWER, Power, PowerBackport, PowerType
from ..scoring import score


def score_aberrant(candidate: BaseStatblock, **kwargs) -> float:
    def is_aberrant_creature(c: BaseStatblock) -> bool:
        if (
            c.creature_type in {CreatureType.Humanoid, CreatureType.Fey}
            and c.attack_type.is_spell()
            and c.secondary_damage_type == DamageType.Psychic
        ):
            return True
        else:
            return c.creature_type in {CreatureType.Aberration}

    args: dict = dict(
        candidate=candidate,
        require_callback=is_aberrant_creature,
        bonus_roles=[MonsterRole.Controller, MonsterRole.Ambusher, MonsterRole.Skirmisher],
        bonus_attack_types=AttackType.AllSpell(),
        bonus_damage=DamageType.Psychic,
    )
    args.update(kwargs)
    return score(**args)


class _EraseMemory(PowerBackport):
    def __init__(self):
        super().__init__(name="Erase Memory", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberrant(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Erase Memory",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} becomes **Invisible** to the target as the target's memories of {stats.selfref} are temporarily erased. \
                The target makes a DC {dc} Intelligence saving throw at the end of each of its turns to end the effect. \
                If a creature fails three saves, the memory loss is permanent and can only be undone with a Greater Restoration or equivalent magic. \
                A creature that succeeds on a saving throw is immune to this effect for 5 minutes.",
        )
        return stats, feature


class _WarpReality(PowerBackport):
    def __init__(self):
        super().__init__(name="Warp Reality", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberrant(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class
        distance = 20 + (20 if stats.cr >= 7 else 0)
        feature = Feature(
            name="Warp Reality",
            description=f"Each creature of {stats.selfref}'s choice within 30 ft must succeed on a DC {dc} Charisma save or be teleported up to {distance} ft to an unoccupied space that {stats.selfref} can see.\
                If the target space is a hazard (such as an open pit, lava, or in the air) then the target may use its reaction to attempt a DC {dc} Dexterity save.\
                On a success, the target reduces the damage taken from the hazard this turn by half, or narrowly escapes the hazard. Creatures may choose to fail this save.",
            action=ActionType.Action,
            replaces_multiattack=1,
            recharge=4,
        )
        return stats, feature


class _AdhesiveSkin(PowerBackport):
    def __init__(self):
        super().__init__(name="Adhesive Skin", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberrant(candidate)

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Adhesive Skin",
            action=ActionType.Feature,
            description=f"When {stats.selfref} is hit by a melee weapon attack, the weapon becomes stuck to them. \
                A creature can use an action to remove the weapon with a successful DC 14 Athletics check. \
                All items stuck to {stats.selfref} become unstuck when it dies.",
        )

        return stats, feature


class _Incubation(PowerBackport):
    def __init__(self):
        super().__init__(name="Incubation", power_type=PowerType.Theme, power_level=HIGH_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score_aberrant(
            candidate,
            attack_names=["-", natural.Claw],
            require_types=CreatureType.Aberration,
        )

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        dc = stats.difficulty_class_easy
        timespan = "three months" if stats.cr <= 5 else "three days"

        feature = Feature(
            name="Incubation",
            action=ActionType.Feature,
            description=f"If a humanoid is hit by {stats.selfref}'s attack, it must make a DC {dc} Constitution saving throw. \
                            On a failure, the target is infected by a terrible parasite. The target can carry only one such parasite at a time. \
                            Over the next {timespan}, the parasite gestates and moves to the chest cavity. \
                            In the 24-hour period before the parasite gives birth, the target feels unwell. Its speed is halved, and it has disadvantage on attack rolls, ability checks, and saving throws. \
                            At birth, the parasite burrows its way out of the target's chest in one round, killing it.\
                            If the disease is cured, the parasite disintigrates.",
        )

        return stats, feature


EraseMemory: Power = _EraseMemory()
WarpReality: Power = _WarpReality()
AdhesiveSkin: Power = _AdhesiveSkin()
Incubation: Power = _Incubation()

AberrantPowers: List[Power] = [EraseMemory, WarpReality, AdhesiveSkin, Incubation]
