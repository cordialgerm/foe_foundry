from math import ceil
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
from ..statblocks import BaseStatblock
from .power import Power, PowerType
from .scores import (
    EXTRA_HIGH_AFFINITY,
    HIGH_AFFINITY,
    LOW_AFFINITY,
    MODERATE_AFFINITY,
    NO_AFFINITY,
)


class _DamagingAura(Power):
    """Any creature who moves within 10 feet of this creature or who starts their turn there takes CR damage of a type appropriate for this creature."""

    def __init__(self):
        super().__init__(name="Damaging Aura", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for foes with a secondary damage type
        # it can also make sense for large STR-martials (wielding many weapons)

        if candidate.secondary_damage_type is not None:
            return HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=stats.primary_damage_type)

        damage_type = stats.secondary_damage_type

        if damage_type == DamageType.Acid:
            name = "Corrosive Fumes"
        elif damage_type == DamageType.Bludgeoning:
            name = "Flurry of Blows"
        elif damage_type == DamageType.Cold:
            name = "Arctic Chill"
        elif damage_type == DamageType.Fire:
            name = "Superheated"
        elif damage_type == DamageType.Force:
            name = "Disintegrating Presence"
        elif damage_type == DamageType.Lightning:
            name = "Arcing Electricity"
        elif damage_type == DamageType.Necrotic:
            name = "Deathly Presence"
        elif damage_type == DamageType.Piercing:
            name = "Bristling"
        elif damage_type == DamageType.Poison:
            name = "Toxic Presence"
        elif damage_type == DamageType.Psychic:
            name = "Unsettling Presence"
        elif damage_type == DamageType.Radiant:
            name = "Holy Presence"
        elif damage_type == DamageType.Slashing:
            name = "Constant Slashing"
        else:
            name = "Damaging Aura"

        dmg = int(ceil(stats.cr))

        feature = Feature(
            name=name,
            description=f"Any creature who moves within 10 feet of {stats.selfref} or who starts their turn there takes {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )

        return stats, feature


class _Defender(Power):
    """When an ally within 5 feet of this creature is targeted by an attack or spell, this creature can make themself the intended target of the attack."""

    def __init__(self):
        super().__init__(name="Defender", power_type=PowerType.Common)

    def _is_minion(self, candidate: BaseStatblock) -> bool:
        return candidate.cr <= 2 and candidate.role not in {
            MonsterRole.Ambusher,
            MonsterRole.Controller,
            MonsterRole.Leader,
            MonsterRole.Skirmisher,
        }

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for minions and defensive creatures
        # for now, I will interpret minions as low CR creatures
        score = 0
        if self._is_minion(candidate):
            score += MODERATE_AFFINITY

        if candidate.role == MonsterRole.Defender:
            score += EXTRA_HIGH_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        name = "Cannon Fodder" if self._is_minion(stats) else "Defender"

        feature = Feature(
            name=name,
            description=f"When an ally within 5 feet is targeted by an attack or spell, {stats.selfref} can make themselves the intended target of the attack or spell instead.",
            action=ActionType.Reaction,
        )
        return stats, feature


class _Frenzy(Power):
    """Frenzy (Trait). At the start of their turn, this creature can gain advantage on all melee weapon attack rolls made during this
    turn, but attack rolls against them have advantage until the start of their next turn."""

    def __init__(self):
        super().__init__(name="Frenzy", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this ability makes a lot of sense for brutes, STR-based foes, and low-WIS foes

        # high-WIS foes should be excluded
        # primarily ranged foes should be excluded
        if candidate.attributes.WIS >= 15 or not candidate.attack_type.is_melee():
            return NO_AFFINITY

        score = LOW_AFFINITY
        if candidate.role == MonsterRole.Bruiser:
            score += EXTRA_HIGH_AFFINITY
        if candidate.attributes.primary_attribute == Stats.STR:
            score += HIGH_AFFINITY
        if candidate.attributes.WIS <= 12:
            score += LOW_AFFINITY
        if candidate.attributes.WIS <= 10:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Frenzy",
            description=f"At the start of their turn, {stats.selfref} can gain advantage on all melee weapon attack rolls made during this turn, but attack rolls against them have advantage until the start of their next turn.",
            action=ActionType.Feature,
        )
        return stats, feature


class _NotDeadYet(Power):
    """When this creature is reduced to 0 hit points, they drop prone and are indistinguishable from a dead creature.
    At the start of their next turn, this creature stands up without using any movement and has 2x CR hit points.
    They can then take their turn normally."""

    def __init__(self):
        super().__init__(name="Not Dead Yet", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for undead, oozes, beasts, and monstrosities
        score = LOW_AFFINITY
        if candidate.creature_type in {
            CreatureType.Ooze,
            CreatureType.Undead,
            CreatureType.Beast,
            CreatureType.Monstrosity,
        }:
            score += HIGH_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += MODERATE_AFFINITY
        if Skills.Deception in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        hp = int(ceil(2.0 * stats.cr))

        feature = Feature(
            name="Not Dead Yet",
            description=f"When {stats.selfref} is reduced to 0 hit points, it drops prone and is indistinguishable from a dead creature. \
                        At the start of their next turn, {stats.selfref} stands up without using any movement and has {hp} hit points. It can take its turn normally",
            action=ActionType.Reaction,
            uses=1,
        )
        return stats, feature


class _GoesDownFighting(Power):
    """When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious."""

    def __init__(self):
        super().__init__(name="Goes Down Fighting", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this role makes sense for lots of monsters, but Defenders and Bruisers should be a bit more likely to have this
        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Bruiser}:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description=f"When {stats.selfref} is reduced to 0 hit points, they can immediately make one attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _RefuseToSurrender(Power):
    """When this creature’s current hit points are below half their hit point maximum,
    the creature deals CR extra damage with each of their attacks."""

    def __init__(self):
        super().__init__(name="Refuse to Surrender", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # the creature has to be somewhat aware to fight harder when it's hurt
        if candidate.attributes.INT <= 3 and candidate.attributes.WIS <= 3:
            return NO_AFFINITY

        # this power makes a lot of sense for larger creatures, creatures with more HP, higher CR creatures, and Bruisers
        score = 0
        if candidate.size in {Size.Large, Size.Huge, Size.Gargantuan}:
            score += LOW_AFFINITY
        if candidate.attributes.CON >= 14:
            score += LOW_AFFINITY
        if candidate.cr >= 4:
            score += LOW_AFFINITY
        if candidate.role in {MonsterRole.Bruiser, MonsterRole.Defender}:
            score += MODERATE_AFFINITY
        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        threshold = int(ceil(stats.hp.average / 2.0))
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Refuse to Surrender",
            description=f"When {stats.selfref}'s current hit points are below {threshold}, the creature deals an extra {dmg} damage with each of its attacks.",
            action=ActionType.Feature,
        )
        return stats, feature


class _DelightsInSuffering(Power):
    """When attacking a target whose current hit points are below half their hit point maximum,
    this creature has advantage on attack rolls and deals an extra CR damage when they hit."""

    def __init__(self):
        super().__init__(name="Delights in Suffering", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for cruel enemies
        # cruel factors: Fiend, Monstrosity, Intimidation proficiency, Intimidation expertise, high charisma, Ambusher, Bruiser, Leader
        score = LOW_AFFINITY
        if candidate.creature_type in {CreatureType.Fiend, CreatureType.Monstrosity}:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.proficient_skills:
            score += HIGH_AFFINITY
        if Skills.Intimidation in candidate.attributes.expertise_skills:
            score += EXTRA_HIGH_AFFINITY
        if candidate.attributes.CHA >= 15:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser, MonsterRole.Leader}:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # grant intimidation proficiency or expertise
        stats = stats.copy(
            attributes=stats.attributes.grant_proficiency_or_expertise(Skills.Intimidation)
        )

        # use secondary damage type, if there is one
        # if there isn't, set it to poison
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        damage_type = stats.secondary_damage_type
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Delights in Suffering",
            description=f"The attack is made at advantage and deals an additional {dmg} {damage_type} damage if the target is at or below half-health (included in the attack).",
            action=ActionType.Feature,
            modifies_attack=True,
        )
        return stats, feature


class _Lethal(Power):
    """This creature has a +CR bonus to damage rolls, and scores a critical hit on an unmodified attack roll of 18-20."""

    def __init__(self):
        super().__init__(name="Lethal", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this role makes sense for lots of monsters, but Ambushers and Artillery should be a bit more likely to have this
        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Artillery}:
            score += MODERATE_AFFINITY
        if candidate.secondary_damage_type == DamageType.Poison:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, List[Feature]]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
        dmg = int(ceil(stats.cr))
        dmg_type = stats.secondary_damage_type

        crit_lower = 19 if stats.cr <= 7 else 18

        feature1 = Feature(
            name="Lethal",
            description=f"The attack scores a critical hit on an unmodified attack roll of {crit_lower}-20",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
        )

        feature2 = Feature(
            name="Lethal",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} deals an additional {dmg} {dmg_type} to the target",
        )
        return stats, [feature1, feature2]


class _MarkTheTarget(Power):
    """When this creature hits a target with a ranged attack, allies of this creature who can see the target
    have advantage on attack rolls against the target until the start of this creature's next turn.
    """

    def __init__(self):
        super().__init__(name="Mark the Target", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for leaders, artillery, controllers, high intelligence foes, and ranged foes
        score = LOW_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attack_type in {AttackType.RangedSpell, AttackType.RangedWeapon}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Artillery, MonsterRole.Controller}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Leader}:
            score += HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mark the Target",
            description=f"Immediately after hitting a target, {stats.selfref} can mark the target. All allies of {stats.selfref} who can see the target have advantage on attack rolls against the target until the start of this creature's next turn.",
            uses=3,
            action=ActionType.BonusAction,
        )
        return stats, feature


class _ParryAndRiposte(Power):
    """This creature adds +3 to their Armor Class against one melee attack that would hit them.
    If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.
    """

    def __init__(self):
        super().__init__(name="Parry and Riposte", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this monster requires a melee weapon
        # it makes a ton of sense for defenders and leaders
        # clever and dextrous foes get a boost as well
        if candidate.attack_type != AttackType.MeleeWeapon:
            return NO_AFFINITY

        score = 0
        if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
            score += HIGH_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.WIS >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.DEX >= 14:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description=f"{stats.selfref.capitalize()} adds +3 to their Armor Class against one melee attack that would hit them.\
                         If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.",
            action=ActionType.Reaction,
            recharge=6,
        )
        return stats, feature


class _QuickRecovery(Power):
    """Quick Recovery (Trait). At the start of this creature's turn, they can attempt a saving throw
    against any effect on them that can be ended by a successful saving throw."""

    def __init__(self):
        super().__init__(name="Quick Recovery", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for high CR creatures, creatures with high CON (resilient), or high CHA (luck)
        score = 0
        if candidate.cr >= 7:
            score += MODERATE_AFFINITY
        if candidate.cr >= 11:
            score += MODERATE_AFFINITY
        if candidate.attributes.CON >= 16:
            score += MODERATE_AFFINITY
        if candidate.attributes.CHA >= 16:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY
        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        # add CON save proficiency
        new_attrs = stats.attributes.grant_save_proficiency(Stats.CON)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Quick Recovery",
            description=f"At the start of {stats.selfref}'s turn, they can attempt a saving throw \
                         against any effect on them that can be ended by a successful saving throw",
            action=ActionType.Feature,
        )
        return stats, feature


class _Reposition(Power):
    """Each ally within 60 feet of this creature who can see and hear them
    can immediately move their speed without provoking opportunity attacks."""

    def __init__(self):
        super().__init__(name="Reposition", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this trait makes a lot of sense for leaders and high-int enemies

        score = 0

        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY

        if candidate.attributes.INT >= 16:
            score += MODERATE_AFFINITY

        return score if score > 0 else NO_AFFINITY

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Reposition",
            description=f"Each ally within 60 ft that can see and hear {stats.selfref} \
                can immediately move its speed without provoking opportunity attacks",
            action=ActionType.BonusAction,
            recharge=5,
        )
        return stats, feature


class _Vanish(Power):
    """This creature can use the Disengage action, then can hide if they have cover"""

    def __init__(self):
        super().__init__(name="Vanish", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is amazing for ambushers and stealth / DEX fighters
        score = 0
        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY
        if candidate.attributes.has_proficiency_or_expertise(Skills.Stealth):
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Vanish",
            description=f"{stats.selfref.capitalize()} can use the Disengage action, then can hide if they have cover.",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _AdrenalineRush(Power):
    def __init__(self):
        super().__init__(name="Adrenaline Rush", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is amazing for ambushers, bruisers, and melee fighters
        score = 0
        if candidate.primary_attribute in {Stats.DEX, Stats.STR}:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Ambusher, MonsterRole.Bruiser}:
            score += MODERATE_AFFINITY
        if candidate.creature_type == CreatureType.Humanoid:
            score += LOW_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Adrenaline Rush",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )

        return stats, feature


class _MagicResistance(Power):
    def __init__(self):
        super().__init__(name="Magic Resistance", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is common amongst fiends, celestials, and fey and high-CR creatures
        score = 0
        if candidate.creature_type in {
            CreatureType.Fey,
            CreatureType.Fiend,
            CreatureType.Celestial,
        }:
            score += MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
            score += MODERATE_AFFINITY
        if candidate.cr >= 7:
            score += MODERATE_AFFINITY
        return score

    def apply(
        self, stats: BaseStatblock, rng: np.random.Generator
    ) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Magic Resistance",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on saves against spells and other magical effects.",
        )

        return stats, feature


AdrenalineRush: Power = _AdrenalineRush()
DamagingAura: Power = _DamagingAura()
Defender: Power = _Defender()
DelightsInSuffering: Power = _DelightsInSuffering()
Frenzy: Power = _Frenzy()
GoesDownFighting: Power = _GoesDownFighting()
Lethal: Power = _Lethal()
MarkTheTarget: Power = _MarkTheTarget()
MagicResistance: Power = _MagicResistance()
NotDeadYet: Power = _NotDeadYet()
ParryAndRiposte: Power = _ParryAndRiposte()
QuickRecovery: Power = _QuickRecovery()
RefuseToSurrender: Power = _RefuseToSurrender()
Reposition: Power = _Reposition()
Vanish: Power = _Vanish()

CommonPowers: List[Power] = [
    AdrenalineRush,
    DamagingAura,
    Defender,
    DelightsInSuffering,
    Frenzy,
    GoesDownFighting,
    Lethal,
    MagicResistance,
    MarkTheTarget,
    NotDeadYet,
    ParryAndRiposte,
    QuickRecovery,
    RefuseToSurrender,
    Reposition,
    Vanish,
]
