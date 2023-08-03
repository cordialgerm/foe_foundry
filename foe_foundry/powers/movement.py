from math import ceil, floor
from typing import List, Tuple

import numpy as np

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ..attributes import Skills, Stats
from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..features import ActionType, Feature
from ..role_types import MonsterRole
from ..size import Size
from ..statblocks import BaseStatblock, MonsterDials
from .power import Power, PowerType
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _Aquatic(Power):
    def __init__(self):
        super().__init__(name="Aquatic", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        if candidate.secondary_damage_type == DamageType.Cold:
            score += HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(swim=stats.speed.walk)
        new_senses = stats.senses.copy(darkvision=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)

        feature = Feature(
            name="Aquatic",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is aquatic and has a swim speed equal to its walk speed. It can also breathe underwater.",
        )
        return stats, feature


class _Burrower(Power):
    def __init__(self):
        super().__init__(name="Burrower", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += EXTRA_HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(burrow=stats.speed.walk)
        new_senses = stats.senses.copy(blindsight=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)

        tunnel_width = 10 if stats.size >= Size.Huge else 5

        feature = Feature(
            name="Burrower",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can burrow through solid rock at half its burrow speed and leaves a {tunnel_width} foot wide diameter tunnel in its wake.",
        )

        return stats, feature


class _Climber(Power):
    def __init__(self):
        super().__init__(name="Climber", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += EXTRA_HIGH_AFFINITY
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Ambusher}:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Athletics, Skills.Acrobatics
        )
        stats = stats.copy(speed=new_speed, attributes=new_attrs)

        ## Spider Climb
        if stats.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            feature = Feature(
                name="Spider Climb",
                action=ActionType.Feature,
                description=f"{stats.selfref.capitalize()} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check",
            )
        else:
            feature = Feature(
                name="Climber",
                action=ActionType.Feature,
                description=f"{stats.selfref.capitalize()} gains a climb speed equal to its walk speed",
            )

        return stats, feature


class _Flyer(Power):
    def __init__(self):
        super().__init__(name="Flyer", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        score = LOW_AFFINITY
        if candidate.creature_type in {
            CreatureType.Dragon,
            CreatureType.Fiend,
            CreatureType.Aberration,
            CreatureType.Celestial,
        }:
            score += EXTRA_HIGH_AFFINITY
        elif candidate.creature_type in {CreatureType.Beast, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        elif candidate.creature_type in {CreatureType.Elemental, CreatureType.Fey}:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        speed_change = 10 + 10 * int(floor(stats.cr / 5.0))
        new_speed = stats.speed.delta(speed_change=speed_change)
        new_speed = new_speed.copy(fly=new_speed.walk)
        stats = stats.copy(speed=new_speed)

        feature = Feature(
            name="Flyer",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement speed increases by {speed_change} and it gains a fly speed equal to its walk speed",
            hidden=True,
        )

        return stats, feature


class _Speedy(Power):
    def __init__(self):
        super().__init__(name="Speedy", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes sense for monsters with reasonable DEX that aren't defenders
        if candidate.role == MonsterRole.Defender or candidate.attributes.DEX < 10:
            return NO_AFFINITY

        return MODERATE_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature | None]:
        # give the monster reasonable DEX stat
        new_attrs = (
            stats.attributes.boost(Stats.DEX, 2)
            .grant_proficiency_or_expertise(Skills.Acrobatics)
            .grant_save_proficiency(Stats.DEX)
        )
        stats = stats.copy(attributes=new_attrs).apply_monster_dials(
            MonsterDials(speed_modifier=10)
        )

        feature = Feature(
            name="Speedy",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s movement increases by 10ft and it gains proficiency in Acrobatics and Dexterity saves",
        )
        return stats, feature


class _Sneaky(Power):
    """Sneaky (Trait). This creature has advantage on Dexterity(Stealth) checks."""

    def __init__(self):
        super().__init__(name="Sneaky", power_type=PowerType.Movement)

    def score(self, candidate: BaseStatblock) -> float:
        # this is really good for ambushers that aren't yet expertise in stealth
        if candidate.role != MonsterRole.Ambusher:
            return NO_AFFINITY
        elif Skills.Stealth in candidate.attributes.expertise_skills:
            return NO_AFFINITY  # already has this ability basically
        else:
            return EXTRA_HIGH_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Deception
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Sneaky",
            description=f"{stats.selfref.capitalize()} gains proficiency (or expertise) in Stealth and Deception",
            action=ActionType.Feature,
        )
        return stats, feature


Aquatic: Power = _Aquatic()
Burrower: Power = _Burrower()
Climber: Power = _Climber()
Flyer: Power = _Flyer()
Speedy: Power = _Speedy()
Sneaky: Power = _Sneaky()

MovementPowers: List[Power] = [
    Aquatic,
    Burrower,
    Climber,
    Flyer,
    Speedy,
    Sneaky,
]
