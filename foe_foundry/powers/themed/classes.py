from typing import List, Set, Tuple, TypeVar

import numpy as np
from numpy.random import Generator

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import spell, weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ...utils.rng import choose_enum
from ...utils.summoning import determine_summon_formula
from ..attack import relevant_damage_types
from ..attack_modifiers import AttackModifiers, resolve_attack_modifier
from ..power import Power, PowerType
from ..scores import HIGH_AFFINITY, LOW_AFFINITY, MODERATE_AFFINITY, NO_AFFINITY

T = TypeVar("T")


def clean_set(a: T | None | List[T] | Set[T]) -> Set[T]:
    if a is None:
        return set()
    elif isinstance(a, list):
        return set(a)
    elif isinstance(a, set):
        return a
    else:
        return {a}


def score(
    candidate: BaseStatblock,
    require_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    require_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    require_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    bonus_roles: MonsterRole | Set[MonsterRole] | List[MonsterRole] | None = None,
    bonus_types: CreatureType | Set[CreatureType] | List[CreatureType] | None = None,
    bonus_damage: DamageType | Set[DamageType] | List[DamageType] | None = None,
    attack_modifiers: AttackModifiers = None,
    bonus: float = MODERATE_AFFINITY,
    min_cr: float | None = 3,
) -> float:
    require_roles = clean_set(require_roles)
    require_types = clean_set(require_types)
    require_damage = clean_set(require_damage)
    bonus_roles = clean_set(bonus_roles)
    bonus_types = clean_set(bonus_types)
    bonus_damage = clean_set(bonus_damage)

    candidate_damage_types = relevant_damage_types(candidate)

    if min_cr and candidate.cr < min_cr:
        return NO_AFFINITY

    if require_roles and not candidate.role in require_roles:
        return NO_AFFINITY

    if require_types and not candidate.creature_type in require_types:
        return NO_AFFINITY

    if require_damage and not any(candidate_damage_types.intersection(require_damage)):
        return NO_AFFINITY

    score = resolve_attack_modifier(candidate, attack_modifiers)

    if candidate.creature_type in bonus_types:
        score += bonus

    if candidate.role in bonus_roles:
        score += bonus

    if any(candidate_damage_types.intersection(bonus_damage)):
        score += bonus

    return score


class _DeathKnight(Power):
    def __init__(self):
        super().__init__(name="Death Knight", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_types=[CreatureType.Undead, CreatureType.Humanoid],
            require_roles=[MonsterRole.Leader, MonsterRole.Default, MonsterRole.Bruiser],
            bonus_damage=DamageType.Necrotic,
            attack_modifiers={
                "*": NO_AFFINITY,
                weapon.SwordAndShield: HIGH_AFFINITY,
                weapon.MaceAndShield: HIGH_AFFINITY,
                weapon.Greataxe: HIGH_AFFINITY,
                weapon.Greatsword: HIGH_AFFINITY,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        if stats.secondary_damage_type != DamageType.Necrotic:
            stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        dc = stats.difficulty_class
        cr_target = stats.cr / 4

        feature1 = Feature(
            name="Death Knight's Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.selfref} curses up to four targets it can see within 30 feet. \
                Each target must make a DC {dc} Charisma save or be affected as by the *Bane* spell (save ends at end of turn).",
        )

        _, _, description = determine_summon_formula(
            summoner=CreatureType.Undead, summon_cr_target=cr_target, rng=rng
        )

        feature2 = Feature(
            name="Death Knight's Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref} calls upon the dead to serve. {description}",
        )

        return stats, [feature1, feature2]


class _EldritchKnight(Power):
    # misty step
    # elemental weapon damage
    # recharge - impose a condition
    def __init__(self):
        super().__init__(name="Eldritch Knight", power_type=PowerType.Theme)
        self.elements = {DamageType.Fire, DamageType.Lightning, DamageType.Cold}

    def score(self, candidate: BaseStatblock) -> float:
        if (
            candidate.secondary_damage_type is not None
            and candidate.secondary_damage_type not in self.elements
        ):
            return NO_AFFINITY

        return score(
            candidate,
            require_types=[CreatureType.Humanoid, CreatureType.Humanoid],
            bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Bruiser],
            bonus_damage=self.elements,
            attack_modifiers={
                "*": NO_AFFINITY,
                weapon.SwordAndShield: HIGH_AFFINITY,
                weapon.Greataxe: HIGH_AFFINITY,
                weapon.Greatsword: HIGH_AFFINITY,
                weapon.MaceAndShield: HIGH_AFFINITY,
                weapon.RapierAndShield: HIGH_AFFINITY,
                weapon.Polearm: HIGH_AFFINITY,
                weapon.Maul: HIGH_AFFINITY,
                weapon.Staff: HIGH_AFFINITY,
            },
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        element = stats.secondary_damage_type or choose_enum(rng, list(self.elements))
        stats = stats.copy(secondary_damage_type=element)
        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage)

        feature1 = Feature(
            name="Misty Step",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.selfref.capitalize()} teleports up to 30 feet to an unoccupied space it can see",
        )

        feature2 = Feature(
            name="Elemental Burst",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} unleashes an explosion of arcane power. \
                Each creature in a 20-foot radius sphere centered on a point within 60 feet must make \
                a DC {dc} Dexterity saving throw, taking {dmg.description} {element} damage on a failure. \
                On a success, a creature takes half damage instead.",
        )

        return stats, [feature1, feature2]


class _Artificer:
    # grants good armor
    # gives an arcane cannon attack
    pass


class _TotemicWarrior:
    # bear totem
    pass


class _BardicWarrior:
    # BA - if attack hits, try confuse and Daze the target
    # Reaction - force oppoenent to subract a die roll from attack roll or save
    pass


class _WarPriest:
    # mass cure wounds
    # warding flare
    pass


class _Ranger:
    # spike growth
    # perception
    # invisibility
    pass


class _ArcaneArcher:
    pass

    # Banishing Arrow
    # You use abjuration magic to try to temporarily banish your target to a harmless location in the Feywild. The creature hit by the arrow must also succeed on a Charisma saving throw or be banished. While banished in this way, the target’s speed is 0, and it is incapacitated. At the end of its next turn, the target reappears in the space it vacated or in the nearest unoccupied space if that space is occupied.

    # After you reach 18th level in this class, a target also takes 2d6 force damage when the arrow hits it.

    # Bursting Arrow
    # You imbue your arrow with force energy drawn from the school of evocation. The energy detonates after your attack. Immediately after the arrow hits the creature, the target and all other creatures within 10 feet of it take 2d6 force damage each.

    # The force damage increases to 4d6 when you reach 18th level in this class.

    # Enfeebling Arrow
    # You weave necromantic magic into your arrow. The creature hit by the arrow takes an extra 2d6 necrotic damage. The target must also succeed on a Constitution saving throw, or the damage dealt by its weapon attacks is halved until the start of your next turn.

    # The necrotic damage increases to 4d6 when you reach 18th level in this class.


class _PsiWarrior:
    # jump
    # psychic damage
    # protective field - reduce damage reaction
    # cast telekenises
    pass


class _Cavalier:
    # BA to summon a mount
    # Mounted Combatant
    # Attacks are made at advantage while mounted
    pass


class _RuneKnight:
    # Giants Might
    # also grant one of the giant runes
    pass


class _Samurai:
    # fighting spirit - bonus action to gain temp HP and advantage on attack rolls
    # strength before death - "Not Dead Yet" ability but renamed
    pass


class _Monk:
    # stunning strike
    # evasion
    pass


class _Paladin:
    # divine smite
    # aura of protection
    pass


class _BlessedWarrior(Power):
    def __init__(self):
        super().__init__(name="Blessed Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_types=CreatureType.Humanoid,
            bonus_damage=DamageType.Radiant,
            attack_modifiers=[
                weapon.SwordAndShield,
                weapon.MaceAndShield,
                weapon.Maul,
                weapon.Greatsword,
                spell.HolyBolt,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(1), Stats.WIS: Stats.WIS.Boost(1)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Radiant)

        damage = DieFormula.target_value(0.6 * stats.attack.average_damage, force_die=Die.d6)
        dc = stats.difficulty_class

        feature1 = Feature(
            name="Favored by the Gods",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} fails a saving throw or misses an attack it may add 2d4 to that result",
        )

        feature2 = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )
        return stats, [feature1, feature2]


class _Druid(Power):
    def __init__(self):
        super().__init__(name="Druidic Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_types=[CreatureType.Humanoid, CreatureType.Fey, CreatureType.Giant],
            bonus_roles=[MonsterRole.Leader, MonsterRole.Controller, MonsterRole.Skirmisher],
            attack_modifiers=[weapon.Staff, weapon.Longbow, weapon.Shortbow, spell.Poisonbolt],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        healing = DieFormula.target_value(
            0.5 * stats.attack.average_damage, force_die=Die.d4, flat_mod=stats.attributes.WIS
        )
        uses = stats.attributes.stat_mod(Stats.WIS)
        temp_hp = easy_multiple_of_five(stats.cr, min_val=5, max_val=20)

        bestial_fury = stats.attack.scale(
            2.0,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            name="Bestial Fury",
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            additional_description=f"On a hit, {stats.selfref} gains {temp_hp} temporary hp and the target is \
                pushed back 10 feet if it is Large or smaller",
        )
        stats = stats.add_attack(bestial_fury)

        feature = Feature(
            name="Druidic Healing",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.selfref.capitalize()} utters a word of primal encouragement to a friendly ally it can see within 60 feet. \
                The ally regains {healing.description} hitpoints.",
        )
        return stats, feature


# TODO - allow base statblock to specify classes and subtypes

BlessedWarrior: Power = _BlessedWarrior()
DeathKnight: Power = _DeathKnight()
Druid: Power = _Druid()
EldritchKnight: Power = _EldritchKnight()


ClassPowers: List[Power] = [BlessedWarrior, DeathKnight, Druid, EldritchKnight]
