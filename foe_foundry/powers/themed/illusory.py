from datetime import datetime
from typing import List

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class Illusory(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        def humanoid_is_magical(c: BaseStatblock) -> bool:
            if c.creature_type == CreatureType.Humanoid:
                return (
                    any(t.is_spell() for t in c.attack_types)
                    and c.attributes.spellcasting_mod >= 3
                    and c.secondary_damage_type != DamageType.Radiant
                    and c.caster_type != CasterType.Divine
                )
            else:
                return True

        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_type=PowerCategory.Theme,
            power_level=power_level,
            theme="illusory",
            icon=icon,
            reference_statblock="Adult Green Dragon",
            score_args=dict(
                require_types={
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Aberration,
                    CreatureType.Humanoid,
                },
                require_callback=humanoid_is_magical,
                bonus_roles={MonsterRole.Ambusher, MonsterRole.Controller},
                require_stats=[Stats.CHA, Stats.INT],
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        # this creature should be tricky
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Deception
        ).boost(Stats.CHA, 2)
        stats = stats.grant_spellcasting(CasterType.Innate)
        changes: dict = dict(attributes=new_attrs)
        return stats.copy(**changes)


class _Projection(Illusory):
    def __init__(self):
        super().__init__(
            name="Projection", icon="invisible", source="SRD5.1 Project Image"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Projection",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is the sole target of an attack or spell, {stats.selfref} may use their reaction to turn invisible and teleport up to 30 ft to an unoccupied location they can see. \
                The invisibility lasts for up to 1 minute or until {stats.selfref} makes an attack or casts a spell. \
                Simultaneously, an illusionary version of {stats.selfref} appears in the previous location and appears to be subjected to the attack or spell. \
                The illusion ends when the invisibility ends and also fails to stand up to physical interaction. A character may also use an action to perform a DC {dc} Investigation check to identify the illusion.",
        )
        return [feature]


class _SpectralDuplicate(Illusory):
    def __init__(self):
        super().__init__(
            name="Spectral Duplicate",
            icon="backup",
            source="Foe Foundry",
            power_level=HIGH_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spectral Duplicate",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} creates a spectral duplicate of itself in an unoccupied space it can see within 60 feet. \
                While the duplicate exists, {stats.selfref} is {Condition.Invisible.caption} and {Condition.Unconscious.caption}. The duplicate has the same statistics and knowledge as {stats.selfref} \
                and acts immediately in initiative after {stats.selfref}. The duplicate disappears when {stats.selfref} drops to 0 hp.",
        )
        return [feature]


class _MirrorImage(Illusory):
    def __init__(self):
        super().__init__(
            name="Mirror Image", icon="backup", source="SRD5.1 Mirror Image"
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        ac = 10 + stats.attributes.stat_mod(Stats.DEX)

        feature = Feature(
            name="Mirror Images",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} magically creates three illusory duplicates of itself as in the *Mirror Image* spell. The duplicates have AC {ac}",
        )
        return [feature]


class _HypnoticPattern(Illusory):
    def __init__(self):
        super().__init__(
            name="Hypnotic Pattern",
            icon="star-swirl",
            source="SRD5.1 Hypnotic Pattern",
            require_cr=5,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Hypnotic Pattern",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} magically creates the effect of the *Hypnotic Pattern* spell, using a DC of {dc}",
        )

        return [feature]


class _ReverseFortune(Illusory):
    def __init__(self):
        super().__init__(name="Reverse Fortune", icon="dice-fire", source="Foe Foundry")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Reverse Fortune",
            action=ActionType.Reaction,
            recharge=4,
            description=f"When {stats.selfref} is hit by an attack, {stats.selfref} magically reverses the fortune of the attack and forces it to miss. \
                Until the end of its next turn, {stats.selfref} gains advantage on the next attack it makes against the attacker.",
        )
        return [feature]


class _PhantomMirage(Illusory):
    def __init__(self):
        super().__init__(
            name="Phantom Mirage",
            icon="heat-haze",
            source="Foe Foundry",
            power_level=LOW_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        bloodied = Condition.Bloodied.caption
        feature = Feature(
            name="Phantom Mirage",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} becomes {bloodied}, it creates 4 illusory duplicates of itself in unoccupied spaces within 30 feet. \
                The duplicates vanish at the end of {stats.selfref}'s next turn or when struck by an attack. \
                When a creature makes an attack against {stats.selfref} that creature must roll a d6 for each duplicate. On a roll of 1, the attack hits a duplicate instead.",
        )
        return [feature]


# TODO A5E SRD - Chain Devil
# Unneverving Visage
# Unnerving Mask. When damaged by a
# creature within 30 feet that can see the
# devil, the devil momentarily assumes the
# magical illusory form of one of the
# attacker’s enemies or loved ones, alive or
# dead. The illusory figure may speak
# words that only the attacker can hear. The
# attacker makes a DC 15 Wisdom saving
# throw. On a failure, it takes 9 (2d8)
# psychic damage and is frightened until
# the end of its next turn.The attacker is
# then immune to this effect for the next 24
# hours.


# TODO A5E SRD - Marilith
# Reactive Teleport. When the marilith
# is hit or missed by a ranged
# attack, it uses Teleport. If it
# teleports within 5 feet of a
# creature, it can attack
# with its tail.


HypnoticPatern: Power = _HypnoticPattern()
MirrorImage: Power = _MirrorImage()
Projection: Power = _Projection()
PhantomMirage: Power = _PhantomMirage()
ReverseFortune: Power = _ReverseFortune()
SpectralDuplicate: Power = _SpectralDuplicate()

IllusoryPowers: List[Power] = [
    HypnoticPatern,
    MirrorImage,
    Projection,
    PhantomMirage,
    ReverseFortune,
    SpectralDuplicate,
]
