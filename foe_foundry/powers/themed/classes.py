from typing import List, Tuple

import numpy as np
from numpy.random import Generator

from ...ac_templates import HeavyArmor
from ...attack_template import natural, spell, weapon
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
from ..power import Power, PowerType
from ..scores import NO_AFFINITY
from ..themed.reckless import Toss
from ..utils import score


class _DeathKnight(Power):
    def __init__(self):
        super().__init__(name="Death Knight", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_no_creature_class=True,
            require_types=[CreatureType.Undead, CreatureType.Humanoid],
            require_roles=[MonsterRole.Leader, MonsterRole.Default, MonsterRole.Bruiser],
            require_stats=[Stats.CHA, Stats.STR],
            bonus_damage=DamageType.Necrotic,
            attack_modifiers=[
                "-",  # default is NO_AFFINITY - that's what - means
                weapon.SwordAndShield,
                weapon.MaceAndShield,
                weapon.Greataxe,
                weapon.Greatsword,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        if stats.secondary_damage_type != DamageType.Necrotic:
            stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        stats = stats.copy(creature_class="Death Knight")
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(2)})

        dc = stats.difficulty_class
        cr_target = stats.cr / 4

        feature1 = Feature(
            name="Death Knight's Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.roleref.capitalize()} curses up to four targets it can see within 30 feet. \
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
            description=f"{stats.roleref.capitalize()} calls upon the dead to serve. {description}",
        )

        return stats, [feature1, feature2]


class _EldritchKnight(Power):
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
            require_no_creature_class=True,
            require_types=[CreatureType.Humanoid, CreatureType.Humanoid],
            bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Bruiser],
            require_stats=[Stats.INT, Stats.STR],
            bonus_damage=self.elements,
            attack_modifiers=[
                "-",
                weapon.SwordAndShield,
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.MaceAndShield,
                weapon.RapierAndShield,
                weapon.Polearm,
                weapon.Maul,
                weapon.Staff,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        element = stats.secondary_damage_type or choose_enum(rng, list(self.elements))
        stats = stats.copy(secondary_damage_type=element)
        stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})
        stats = stats.copy(creature_class="Eldritch Knight")

        dc = stats.difficulty_class_easy
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage)

        feature1 = Feature(
            name="Misty Step",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.roleref.capitalize()} teleports up to 30 feet to an unoccupied space it can see",
        )

        feature2 = Feature(
            name="Elemental Burst",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.roleref.capitalize()} unleashes an explosion of arcane power. \
                Each creature in a 20-foot radius sphere centered on a point within 60 feet must make \
                a DC {dc} Dexterity saving throw, taking {dmg.description} {element} damage on a failure. \
                On a success, a creature takes half damage instead.",
        )

        return stats, [feature1, feature2]


class _Artificer(Power):
    def __init__(self):
        super().__init__(name="Artificer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_no_creature_class=True,
            bonus_roles=[MonsterRole.Defender, MonsterRole.Leader],
            require_types=CreatureType.Humanoid,
            require_stats=Stats.INT,
            attack_modifiers=["-", weapon.MaceAndShield, weapon.SwordAndShield, natural.Slam],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.add_ac_template(HeavyArmor)
        stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})
        stats = stats.copy(creature_class="Artificer")
        stats = stats.copy(secondary_damage_type=DamageType.Force)

        dc = stats.difficulty_class
        dazed = conditions.Dazed()
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage, force_die=Die.d10)
        feature = Feature(
            name="Artificer's Cannon",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} fires an arcane cannon at a creature it can see within 60 feet. \
                The target must make a DC {dc} Dexterity saving throw, taking {dmg.description} force damage on a failure. \
                On a success, the target takes half damage instead. If the save fails by 5 or more, the target is also {dazed.caption} for 1 minute (save ends at end of turn). {dazed.description_3rd}",
        )

        return stats, feature


class _Barbarian(Power):
    def __init__(self):
        super().__init__(name="Barbarian", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_no_creature_class=True,
            require_roles=MonsterRole.Bruiser,
            require_types=[CreatureType.Humanoid, CreatureType.Giant],
            require_stats=Stats.STR,
            attack_modifiers=[
                "-",
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.Polearm,
                weapon.Maul,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.copy(creature_class="Barbarian")
        stats = stats.scale({Stats.STR: Stats.STR.Boost(2)})

        feature1 = Feature(
            name="Rage",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, {stats.roleref} gains resistance to Bludgeoning, Slashing, and Piercing damage until the end of its next turn",
        )

        stats, feature2 = Toss.apply(stats, rng)

        features = [feature1]
        if isinstance(feature2, list):
            features.extend(feature2)
        elif feature2 is not None:
            features.append(feature2)

        return stats, features


class _BardicWarrior(Power):
    def __init__(self):
        super().__init__(name="Bardic Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_no_creature_class=True,
            require_types=[CreatureType.Humanoid, CreatureType.Fey],
            bonus_roles=[MonsterRole.Controller, MonsterRole.Leader],
            require_stats=Stats.CHA,
            attack_modifiers=[
                "-",
                weapon.RapierAndShield,
                weapon.Shortswords,
                weapon.Shortbow,
                weapon.Longbow,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.copy(secondary_damage_type=DamageType.Psychic, creature_class="Bard")
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(2)})

        dc = stats.difficulty_class
        dmg = DieFormula.target_value(0.5 * stats.attack.average_damage, force_die=Die.d4)
        dazed = conditions.Dazed()

        feature1 = Feature(
            name="Vicious Mockery",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} viciously mocks a target it can see within 60 ft. If the target can hear the insult, it must make a DC {dc} Wisdom save. \
                On a failure, it takes {dmg.description} psychic damage. Also, if {stats.roleref} has hit the target with an attack this turn and the target fails the save, \
                it becomes {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        feature2 = Feature(
            name="Bardic Inspiration",
            action=ActionType.Reaction,
            uses=stats.attributes.stat_mod(Stats.CHA),
            description=f"Whenever an ally within 30 feet that can hear {stats.roleref} misses with an attack or fails a saving throw, it can roll 1d4 and add the total to its result, potentially turning a failure into a success.",
        )

        return stats, [feature1, feature2]


class _WarPriest:
    # mass cure wounds
    # war god's blessing
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


class _PsiWarrior(Power):
    def __init__(self):
        super().__init__(name="Psi Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_no_creature_class=True,
            require_types=[CreatureType.Humanoid],
            bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Leader],
            require_stats=Stats.INT,
            bonus_stats=Stats.WIS,
            bonus_damage=DamageType.Psychic,
            attack_modifiers=[
                "-",
                weapon.RapierAndShield,
                weapon.SwordAndShield,
                weapon.Shortswords,
            ],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.copy(
            secondary_damage_type=DamageType.Psychic,
            creature_class="Psi Warrior",
        )
        stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})
        protection = easy_multiple_of_five(stats.cr * 1.5, min_val=5, max_val=60)

        feature1 = Feature(
            name="Psionic Jump",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.roleref.capitalize()} performes a psionically boosted jump of up to 30 feet.",
        )

        feature2 = Feature(
            name="Protective Field",
            action=ActionType.Reaction,
            uses=1,
            description=f"When an ally within 30 feet of {stats.roleref} takes damage, {stats.roleref} creates a protective barrier around that ally, \
                preventing up to {protection} of the triggering damage",
        )

        feature3 = Feature(
            name="Telekinesis",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} casts the *Telekinesis* spell",
        )

        return stats, [feature1, feature2, feature3]


class _Cavalier(Power):
    def __init__(self):
        super().__init__(name="Cavalier", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_no_creature_class=True,
            require_types=CreatureType.Humanoid,
            bonus_roles=MonsterRole.Leader,
            attack_modifiers=["-", weapon.Greatsword, weapon.Greataxe],
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.copy(creature_class="Cavalier")

        feature1 = Feature(
            name="Summon Mount",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.roleref.capitalize()} summons a *Warhorse* mount to an unoccupied location within 30 feet which acts as a controlled mount. \
                {stats.roleref.capitalize()} may mount the warhorse without expending any movement",
        )

        feature2 = Feature(
            name="Expert Rider",
            action=ActionType.Feature,
            description=f"{stats.roleref.capitalize()} may force any attack targeting its mount to target {stats.roleref} instead",
        )

        feature3 = Feature(
            name="Mounted Advantage",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"The attack is made at advantage if {stats.roleref} is mounted",
        )

        return stats, [feature1, feature2, feature3]


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
            require_no_creature_class=True,
            require_types=CreatureType.Humanoid,
            bonus_damage=DamageType.Radiant,
            require_stats=Stats.WIS,
            attack_modifiers=[
                "-",
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

        stats = stats.copy(creature_class="Cleric")

        damage = DieFormula.target_value(0.6 * stats.attack.average_damage, force_die=Die.d6)
        dc = stats.difficulty_class

        feature1 = Feature(
            name="Favored by the Gods",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.roleref} fails a saving throw or misses an attack it may add 2d4 to that result",
        )

        feature2 = Feature(
            name="Word of Radiance",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} utters a divine word and it shines with burning radiance. \
                Each hostile creature within 10 feet must make a DC {dc} Constitution saving throw or take {damage.description} radiant damage.",
        )
        return stats, [feature1, feature2]


class _Druid(Power):
    def __init__(self):
        super().__init__(name="Druidic Warrior", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate,
            require_no_creature_class=True,
            require_types=[CreatureType.Humanoid, CreatureType.Fey, CreatureType.Giant],
            bonus_roles=[MonsterRole.Leader, MonsterRole.Controller, MonsterRole.Skirmisher],
            attack_modifiers=[
                "-",
                weapon.Staff,
                weapon.Longbow,
                weapon.Shortbow,
                spell.Poisonbolt,
                spell.Frostbolt,
                spell.Firebolt,
            ],
            require_stats=Stats.WIS,
        )

    def apply(
        self, stats: BaseStatblock, rng: Generator
    ) -> Tuple[BaseStatblock, Feature | List[Feature] | None]:
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        stats = stats.copy(creature_class="Druid")

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
            additional_description=f"On a hit, {stats.roleref} gains {temp_hp} temporary hp and the target is \
                pushed back 10 feet if it is Large or smaller",
        )
        stats = stats.add_attack(bestial_fury)

        feature = Feature(
            name="Druidic Healing",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.roleref.capitalize()} utters a word of primal encouragement to a friendly ally it can see within 60 feet. \
                The ally regains {healing.description} hitpoints.",
        )
        return stats, feature


# TODO - allow base statblock to specify classes and subtypes

Artificer: Power = _Artificer()
Barbarian: Power = _Barbarian()
Bard: Power = _BardicWarrior()
BlessedWarrior: Power = _BlessedWarrior()
Cavalier: Power = _Cavalier()
DeathKnight: Power = _DeathKnight()
Druid: Power = _Druid()
EldritchKnight: Power = _EldritchKnight()
PsiWarrior: Power = _PsiWarrior()


ClassPowers: List[Power] = [
    Artificer,
    Barbarian,
    Bard,
    BlessedWarrior,
    Cavalier,
    DeathKnight,
    Druid,
    EldritchKnight,
    PsiWarrior,
]
