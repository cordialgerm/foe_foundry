from datetime import datetime
from typing import List

from ...attack_template import natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import Power, PowerType, PowerWithStandardScoring

# TODO - Controlling Spells
# TODO - Advanced Controlling Spells


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
                require_types=[CreatureType.Celestial, CreatureType.Fey, CreatureType.Humanoid],
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


class _Eyebite(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Eyebite",
            power_type=PowerType.Role,
            create_date=datetime(2023, 11, 29),
            source="SRD5.1 Eyebite",
            theme="controller",
            score_args=dict(
                require_roles=MonsterRole.Controller,
                require_types=[CreatureType.Fey, CreatureType.Undead],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Eyebite",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} casts *Eyebite* at a creature it can see within 60 feet using a DC of {dc}.",
        )
        return [feature]


class _HeartTremors(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Heart Tremors",
            power_type=PowerType.Role,
            create_date=datetime(2023, 11, 29),
            theme="controller",
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
            source="FoeFoundry",
            action=ActionType.BonusAction,
            recharge=5,
            description=f"Immediately after {stats.selfref} hits with an attack, it can force the target to make a DC {dc} Constitution save. On a failure, \
                the target experiences piercing pain in its chest for 1 minute. Whenever the target takes an action other than the Dodge action, it must repeat the save. \
                If the target has three failures, the target takes {dmg.description} necrotic damage and the effect ends. The effect also ends after three successes.",
        )
        return [feature]


# Enemies Abound cast on you. If you hit someone. Chance to spread to them - controller caster - controller caste
# Nervefire - if you take an action other than dodge, suffer X psychic damage. Save ends at end of turn - controller caster
# Bonerot - bones begin to turn to dust. Necrotic damage and fatigue - controller poison, necrotic


Eyebite: Power = _Eyebite()
HeartTremors: Power = _HeartTremors()
PacifyingTouch: Power = _PacifyingTouch()
TongueTwister: Power = _TongueTwister()

ControllerPowers: List[Power] = [Eyebite, HeartTremors, PacifyingTouch, TongueTwister]
