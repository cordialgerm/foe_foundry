from math import ceil
from typing import List, Tuple

from foe_foundry.features import Feature
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
        elif (
            candidate.size in [Size.Large, Size.Huge, Size.Gargantuan]
            and candidate.primary_attribute == Stats.STR
        ):
            return MODERATE_AFFINITY
        else:
            return LOW_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
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
            description=f"Any creature who moves within 10 feet of this creature or who starts their turn there takes {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )

        return stats, feature


class _DamagingWeapon(Power):
    """This creature’s melee weapon attacks deal an extra CR damage of a type appropriate for the creature."""

    def __init__(self):
        super().__init__(name="Damaging Weapon", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for monsters that use a dedicated weapon
        # monsters that have a secondary damage type are also preferred (if not, use poison)
        # ambushers get a boost to this as well

        score = LOW_AFFINITY

        if candidate.attack_type in {AttackType.MeleeWeapon, AttackType.RangedWeapon}:
            score += EXTRA_HIGH_AFFINITY
        if candidate.secondary_damage_type is not None:
            score += LOW_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += LOW_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        damage_type = stats.secondary_damage_type

        # TODO - integrate this directly into the Attack

        if damage_type == DamageType.Acid:
            name = "Corrosive Attacks"
        elif damage_type == DamageType.Cold:
            name = "Chilling Attacks"
        elif damage_type == DamageType.Fire:
            name = "Superheated Attacks"
        elif damage_type == DamageType.Force:
            name = "Energetic Attacks"
        elif damage_type == DamageType.Lightning:
            name = "Electrified Attacks"
        elif damage_type == DamageType.Necrotic:
            name = "Draining Attacks"
        elif damage_type == DamageType.Poison:
            name = "Poisoned Attacks"
        elif damage_type == DamageType.Psychic:
            name = "Unsettling Attacks"
        elif damage_type == DamageType.Radiant:
            name = "Divine Smite"
        else:
            name = "Damaging Weapon"

        dmg = int(ceil(stats.cr))

        feature = Feature(
            name=name,
            description=f"This creature's attacks deal an extra {dmg} {damage_type} damage",
            action=ActionType.Feature,
        )
        return stats, feature


class _Defender(Power):
    """When an ally within 5 feet of this creature is targeted by an attack or spell, this creature can make themself the intended target of the attack."""

    def __init__(self):
        super().__init__(name="Defender", power_type=PowerType.Common)

    def _is_minion(self, candidate: BaseStatblock) -> bool:
        return candidate.cr <= 3

    def score(self, candidate: BaseStatblock) -> float:
        # TODO - should I have some sort of "encounter context"
        # this power makes a lot of sense for minions and defensive creatures
        # for now, I will interpret minions as low CR creatures
        score = LOW_AFFINITY
        if self._is_minion(candidate):
            score += HIGH_AFFINITY
        if candidate.role == MonsterRole.Defender:
            score += EXTRA_HIGH_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        name = "Cannon Fodder" if self._is_minion(stats) else "Defender"

        feature = Feature(
            name=name,
            description="When an ally within 5 feet is targeted by an attack or spell, this creature can make themselves the intended target of the attack or spell.",
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
        if candidate.attributes.WIS >= 16 or candidate.attack_type in {
            AttackType.RangedSpell,
            AttackType.RangedWeapon,
        }:
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Frenzy",
            description="At the start of their turn, this creature can gain advantage on all melee weapon attack rolls made during this turn, but atack rolls against them have advantage until the start of their next turn.",
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Deception)
        stats = stats.copy(attributes=new_attrs)

        hp = int(ceil(2.0 * stats.cr))

        feature = Feature(
            name="Not Dead Yet",
            description=f"When this creature is reduced to 0 hit points, it drops prone and is indistinguishable from a dead creature. \
                        At the start of their next turn, this creature stands up without using any movement and has {hp} hit points. It can take its turn normally",
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Goes Down Fighting",
            description="When this creature is reduced to 0 hit points, they can immediately make one melee or ranged weapon attack before they fall unconscious",
            action=ActionType.Reaction,
        )
        return stats, feature


class _RefuseToSurrender(Power):
    """When this creature’s current hit points are below half their hit point maximum,
    the creature deals CR extra damage with each of their attacks."""

    def __init__(self):
        super().__init__(name="Refuse to Surrender", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this power makes a lot of sense for larger creatures, creatures with more HP, higher CR creatures, and Bruisers
        score = LOW_AFFINITY
        if candidate.size in {Size.Large, Size.Huge, Size.Gargantuan}:
            score += MODERATE_AFFINITY
        if candidate.attributes.CON >= 14:
            score += MODERATE_AFFINITY
        if candidate.cr >= 4:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Bruiser:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        threshold = int(ceil(stats.hp.average / 2.0))
        dmg = int(ceil(stats.cr))
        feature = Feature(
            name="Refuse to Surrender",
            description=f"When this creature's current hit points are below {threshold}, the creature deals an extra {dmg} damage with each of its attacks.",
            action=ActionType.Feature,
        )
        return stats, feature


class _Sneaky(Power):
    """Sneaky (Trait). This creature has advantage on Dexterity(Stealth) checks."""

    def __init__(self):
        super().__init__(name="Sneaky", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is really good for ambushers that aren't yet expertise in stealth
        if candidate.role != MonsterRole.Ambusher:
            return NO_AFFINITY
        elif Skills.Stealth in candidate.attributes.expertise_skills:
            return NO_AFFINITY  # already has this ability basically
        else:
            return EXTRA_HIGH_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(
            Skills.Stealth, Skills.Deception
        )
        stats = stats.copy(attributes=new_attrs)
        feature = Feature(
            name="Sneaky",
            description="This creature gainst proficiency (or expertise) in Stealth and Deception",
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
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
            description=f"When attacking a target whose current hit points are below half their hit point maximum, this creature has advantage on attack rolls and deals an extra {dmg} {damage_type} damage when they hit.",
            action=ActionType.Feature,
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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)
        dmg = int(ceil(stats.cr))
        dmg_type = stats.secondary_damage_type
        feature = Feature(
            name="Lethal",
            description=f"This creature deals an additional {dmg} {dmg_type} on attacks and scores a critical hit on an unmodified attack roll of 18-20",
            action=ActionType.Feature,
        )
        return stats, feature


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

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Mark the Target",
            description=f"Immediately after hitting a target, this creature can mark the target. All allies of this creature who can see the target have advantage on attack rolls against the target until the start of this creature's next turn.",
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

        score = MODERATE_AFFINITY
        if candidate.role in {MonsterRole.Defender, MonsterRole.Leader}:
            score += HIGH_AFFINITY
        if candidate.attributes.INT >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.WIS >= 14:
            score += MODERATE_AFFINITY
        if candidate.attributes.DEX >= 14:
            score += MODERATE_AFFINITY

        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description="This creature adds +3 to their Armor Class against one melee attack that would hit them.\
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
        score = LOW_AFFINITY
        if candidate.cr >= 8:
            score += MODERATE_AFFINITY
        if candidate.cr >= 12:
            score += MODERATE_AFFINITY
        if candidate.attributes.CON >= 16:
            score += MODERATE_AFFINITY
        if candidate.attributes.CHA >= 16:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Leader:
            score += MODERATE_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        # add CON save proficiency
        new_attrs = stats.attributes.grant_save_proficiency(Stats.CON)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Quick Recovery",
            description="At the start of this creature's turn, they can attempt a saving throw \
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

        if candidate.role == MonsterRole.Leader or candidate.attributes.INT >= 16:
            return EXTRA_HIGH_AFFINITY
        else:
            return NO_AFFINITY

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        feature = Feature(
            name="Reposition",
            description="Each ally within 60 ft that can see and hear this creature \
                can immediately move its speed without provoking opportunity attacks",
            action=ActionType.BonusAction,
            uses=1,
        )
        return stats, feature


class _Telekinetic(Power):
    """This creature chooses one creature they can see within 100 feet of them
    weighing less than 400 pounds. The target must succeed on a Strength saving throw
    (DC = 11 + 1/2 CR) or be pulled up to 80 feet directly toward this creature."""

    def __init__(self):
        super().__init__(name="Telekinetic", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is great for aberrations, psychic focused creatures, and controllers
        score = LOW_AFFINITY
        if candidate.creature_type == CreatureType.Aberration:
            score += MODERATE_AFFINITY
        if candidate.secondary_damage_type == DamageType.Psychic:
            score += MODERATE_AFFINITY
        if candidate.role == MonsterRole.Controller:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        dc = int(ceil(11 + stats.cr / 2.0))

        feature = Feature(
            name="Telekinetic Grasp",
            description=f"This creature chooses one creature they can see within 100 feet weighting less than 400 pounds. \
                The target must succeed on a DC {dc} Strength saving throw or be pulled up to 80 feet directly toward this creature",
            action=ActionType.BonusAction,
        )
        return stats, feature


class _Vanish(Power):
    """This creature can use the Disengage action, then can hide if they have cover"""

    def __init__(self):
        super().__init__(name="Vanish", power_type=PowerType.Common)

    def score(self, candidate: BaseStatblock) -> float:
        # this is amazing for ambushers and stealth / DEX fighters
        score = LOW_AFFINITY
        if candidate.primary_attribute == Stats.DEX:
            score += LOW_AFFINITY
        if Skills.Stealth in candidate.attributes.proficient_skills:
            score += MODERATE_AFFINITY
        if Skills.Stealth in candidate.attributes.expertise_skills:
            score += HIGH_AFFINITY
        if candidate.role == MonsterRole.Ambusher:
            score += HIGH_AFFINITY
        return score

    def apply(self, stats: BaseStatblock) -> Tuple[BaseStatblock, Feature]:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)

        feature = Feature(
            name="Vanish",
            description="This creature can use the Disengage action, then can hide if they have cover.",
            action=ActionType.BonusAction,
        )
        return stats, feature


DelightsInSuffering: Power = _DelightsInSuffering()
Lethal: Power = _Lethal()
MarkTheTarget: Power = _MarkTheTarget()
ParryAndRiposte: Power = _ParryAndRiposte()
QuickRecovery: Power = _QuickRecovery()
Reposition: Power = _Reposition()
Telekinetic: Power = _Telekinetic()
Vanish: Power = _Vanish()
DamagingAura: Power = _DamagingAura()
DamagingWeapon: Power = _DamagingWeapon()
Defender: Power = _Defender()
Frenzy: Power = _Frenzy()
NotDeadYet: Power = _NotDeadYet()
GoesDownFighting: Power = _GoesDownFighting()
RefuseToSurrender: Power = _RefuseToSurrender()
Sneaky: Power = _Sneaky()

CommonPowers: List[Power] = [
    DamagingAura,
    DamagingWeapon,
    Defender,
    Frenzy,
    NotDeadYet,
    GoesDownFighting,
    RefuseToSurrender,
    Sneaky,
    DelightsInSuffering,
    Lethal,
    MarkTheTarget,
    ParryAndRiposte,
    QuickRecovery,
    Reposition,
    Telekinetic,
    Vanish,
]