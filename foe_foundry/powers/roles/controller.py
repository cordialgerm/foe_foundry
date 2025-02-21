from datetime import datetime
from typing import List

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import (
    conjuration,
    enchantment,
    evocation,
    illusion,
    necromancy,
    transmutation,
)
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)
from ..spell import SpellPower, StatblockSpell


class _PacifyingTouch(PowerWithStandardScoring):
    def __init__(self):
        def humanoid_is_divine(c: BaseStatblock):
            if c.creature_type == CreatureType.Humanoid:
                return c.secondary_damage_type == DamageType.Radiant
            else:
                return True

        super().__init__(
            name="Pacifying Touch",
            power_type=PowerType.Role,
            create_date=datetime(2023, 11, 19),
            theme="controller",
            source="FoeFoundry",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_types=[
                    CreatureType.Celestial,
                    CreatureType.Fey,
                    CreatureType.Humanoid,
                ],
                require_callback=humanoid_is_divine,
                bonus_damage=DamageType.Radiant,
                require_attack_types=AttackType.AllSpell(),
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.add_attack(
            name="Pacifying Touch",
            scalar=0.25,
            attack_type=AttackType.MeleeWeapon,
            damage_type=DamageType.Psychic,
            replaces_multiattack=1,
            additional_description="On a hit, the target must make a DC {dc} Wisdom saving throw. \
                On a failed save, the target is **Incapacitated** for 1 minute (save ends at end of turn).",
        )
        return stats


class _TongueTwister(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Tongue-Twister",
            power_type=PowerType.Role,
            create_date=datetime(2023, 11, 29),
            theme="controller",
            source="FoeFoundry",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_types=CreatureType.Fey,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Tongue-Twister",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} chooses a creature that can see and hear it within 60 feet. \
                The target must make a DC {dc} Charisma saving throw. On a failure, it is magically cursed. While cursed, \
                the target can only speak in Sylvan (but does not necessarily understand Sylvan). Whenever the target tries to cast a spell \
                with a verbal component, the target must make a DC {dc} Performance check. On a failure, the spell fails.",
        )
        return [feature]


class _Eyebite(SpellPower):
    def __init__(self):
        super().__init__(
            name="Eyebite",
            spell=necromancy.Eyebite.for_statblock(uses=1),
            create_date=datetime(2023, 11, 29),
            theme="controller",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_types=[CreatureType.Fey, CreatureType.Undead],
            ),
        )


class _HeartTremors(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Heart Tremors",
            power_type=PowerType.Role,
            create_date=datetime(2023, 11, 29),
            theme="controller",
            source="FoeFoundry",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                attack_names=["-", weapon.Staff, natural.Slam, spell.Shock],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(2.5, force_die=Die.d10)
        feature = Feature(
            name="Heart Tremors",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after {stats.selfref} hits with an attack, it can force the target to make a DC {dc} Constitution save. On a failure, \
                the target experiences piercing pain in its chest for 1 minute. Whenever the target takes an action other than the Dodge action, it must repeat the save. \
                If the target has three failures, the target takes {dmg.description} necrotic damage and the effect ends. The effect also ends after three successes.",
        )
        return [feature]


class _UnhingedParanoia(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Unhinged Paranoia",
            power_type=PowerType.Role,
            create_date=datetime(2023, 12, 10),
            theme="controller",
            source="FoeFoundry",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_damage=DamageType.Psychic,
                require_damage_exact_match=True,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Unhinged Paranoia",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} attempts to destabilize the mind of a creature it can see within 60 feet. \
                    That creature must make a DC {dc} Intelligence saving throw. On a failure, the creature becomes unable to distinguish friend from foe. \
                    At the start of each of the creature's turns, it must roll a die to determine its behavior. \
                    On an odd roll, the creature considers its former allies to be its enemies and must act accordingly during this turn. \
                    The condition ends when the creature causes damage to one of its former allies in this manner.",
        )
        return [feature]


class _Nervefire(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Nervefire",
            power_type=PowerType.Role,
            create_date=datetime(2023, 12, 10),
            theme="controller",
            source="FoeFoundry",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_damage=DamageType.Poison,
                require_damage_exact_match=True,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(0.75, force_die=Die.d6)
        feature = Feature(
            name="Nervefire",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} can force the target to make a DC {dc} Constitution saving throw. \
                On a failure, the target is **Poisoned** (save ends at end of turn). While poisoned in this way, the target takes {dmg.description} psychic damage \
                whenever it takes an action other than the Dodge action.",
        )
        return [feature]


class _TiringAttack(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Tiring Attack",
            power_type=PowerType.Role,
            create_date=datetime(2023, 12, 10),
            theme="controller",
            source="FoeFoundry",
            power_level=HIGH_POWER,
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_damage=DamageType.Necrotic,
                require_damage_exact_match=True,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Tiring Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            description=f"On a hit, the target must make a DC {dc} Constitution saving throw. \
                On a failure, the target's bones begin to turn to dust and it gains a level of **Exhaustion**.",
        )
        return [feature]


class _ControllingSpellPower(SpellPower):
    def __init__(self, spell: StatblockSpell, **kwargs):
        # all spells in this class are controller spells
        score_args = dict(require_roles=MonsterRole.Controller) | kwargs.get(
            "score_args", {}
        )
        args = kwargs.copy()
        args.pop("score_args", None)

        super().__init__(
            spell=spell,
            create_date=datetime(2023, 12, 10),
            theme="controller",
            score_args=score_args,
            **args,
        )


def _ControllingSpells() -> List[Power]:
    return [
        _ControllingSpellPower(
            spell=necromancy.BlindnessDeafness.for_statblock(),
            score_args=dict(
                require_damage=[DamageType.Necrotic, DamageType.Poison],
            ),
        ),
        _ControllingSpellPower(
            spell=enchantment.Command.for_statblock(),
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Fey,
                    CreatureType.Fiend,
                    CreatureType.Celestial,
                ],
            ),
        ),
        _ControllingSpellPower(
            spell=conjuration.Entangle.for_statblock(),
            score_args=dict(
                require_types=[
                    CreatureType.Plant,
                    CreatureType.Fey,
                    CreatureType.Humanoid,
                ]
            ),
        ),
        _ControllingSpellPower(
            spell=conjuration.Grease.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(require_types=CreatureType.Humanoid),
        ),
        _ControllingSpellPower(
            spell=evocation.GustOfWind.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(require_damage=[DamageType.Lightning, DamageType.Thunder]),
        ),
        _ControllingSpellPower(
            spell=enchantment.HideousLaughter.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(require_damage=DamageType.Psychic),
        ),
        _ControllingSpellPower(
            spell=enchantment.HoldPerson.for_statblock(),
            power_level=MEDIUM_POWER,
            score_args=dict(require_attack_types=AttackType.AllSpell()),
        ),
        _ControllingSpellPower(
            spell=transmutation.Levitate.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(
                require_types=[CreatureType.Elemental, CreatureType.Humanoid]
            ),
        ),
        _ControllingSpellPower(
            spell=conjuration.SleetStorm.for_statblock(),
            score_args=dict(require_damage=DamageType.Cold),
        ),
        _ControllingSpellPower(
            spell=illusion.Silence.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(require_attack_types=AttackType.AllSpell()),
        ),
        _ControllingSpellPower(
            spell=enchantment.Suggestion.for_statblock(),
            power_level=MEDIUM_POWER,
            score_args=dict(require_attack_types=AttackType.AllSpell()),
        ),
        _ControllingSpellPower(
            spell=conjuration.Web.for_statblock(),
            power_level=MEDIUM_POWER,
            score_args=dict(
                require_types=[CreatureType.Monstrosity, CreatureType.Humanoid]
            ),
        ),
        _ControllingSpellPower(
            spell=transmutation.Slow.for_statblock(),
            power_level=MEDIUM_POWER,
            score_args=dict(
                require_types=[CreatureType.Humanoid, CreatureType.Construct]
            ),
        ),
        _ControllingSpellPower(
            spell=conjuration.FogCloud.for_statblock(),
            power_level=LOW_POWER,
            score_args=dict(require_attack_types=AttackType.AllSpell()),
        ),
    ]


Eyebite: Power = _Eyebite()
HeartTremors: Power = _HeartTremors()
NerveFire: Power = _Nervefire()
PacifyingTouch: Power = _PacifyingTouch()
TiringAttack: Power = _TiringAttack()
TongueTwister: Power = _TongueTwister()
UnhingedParanoia: Power = _UnhingedParanoia()
ControllingSpells: List[Power] = _ControllingSpells()

ControllerPowers: List[Power] = [
    Eyebite,
    HeartTremors,
    NerveFire,
    PacifyingTouch,
    TongueTwister,
    UnhingedParanoia,
] + ControllingSpells
