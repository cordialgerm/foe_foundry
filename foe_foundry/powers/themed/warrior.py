from datetime import datetime
from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import natural, weapon
from ...attributes import Skills
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, Dazed
from ...die import Die
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring
from .organized import score_could_be_organized


def is_organized(c: BaseStatblock) -> bool:
    return score_could_be_organized(c, requires_intelligence=True) > 0


class Warrior(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            power_level=power_level,
            create_date=create_date,
            power_type=PowerType.Theme,
            theme="warrior",
            score_args=dict(
                require_attack_types=AttackType.AllMelee(),
                bonus_roles=MonsterRole.Bruiser,
                bonus_skills=Skills.Athletics,
            )
            | score_args,
        )


class _PackTactics(Warrior):
    def __init__(self):
        super().__init__(
            name="Pack Tactics",
            source="SRD5.1 Wolf",
            require_types={CreatureType.Beast, CreatureType.Humanoid, CreatureType.Monstrosity},
            bonus_roles={
                MonsterRole.Leader,
                MonsterRole.Bruiser,
                MonsterRole.Ambusher,
                MonsterRole.Skirmisher,
            },
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Pack Tactics",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on attack rolls against a target if at least one of {stats.selfref}'s allies is within 5 feet and isn't incapacitated.",
        )
        return [feature]


class _Disciplined(Warrior):
    def __init__(self):
        def fights_in_formation(c: BaseStatblock) -> bool:
            return is_organized(c) and c.size <= Size.Large

        super().__init__(
            name="Disciplined",
            source="Foe Foundry",
            require_callback=fights_in_formation,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Disciplined",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} misses an attack or fails a saving throw while another friendly creature is within 10 feet, it may use its reaction to re-roll the attack or saving throw.",
        )
        return [feature]


class _ParryAndRiposte(Warrior):
    def __init__(self):
        super().__init__(
            name="Parry and Riposte",
            source="Foe Foundry",
            require_attack_types=AttackType.MeleeWeapon,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Parry and Riposte",
            description=f"{stats.selfref.capitalize()} adds +3 to their Armor Class against one melee attack that would hit them.\
                         If the attack misses, this creature can immediately make a weapon attack against the creature making the parried attack.",
            action=ActionType.Reaction,
            recharge=6,
        )
        return [feature]


class _PommelStrike(Warrior):
    def __init__(self):
        super().__init__(
            name="Pommel Strike",
            source="Foe Foundry",
            attack_names=[
                "-",
                weapon.SwordAndShield,
                weapon.SpearAndShield,
            ],
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dazed = Dazed()
        dc = stats.difficulty_class_easy

        stats = stats.add_attack(
            scalar=0.6,
            damage_type=DamageType.Bludgeoning,
            attack_type=AttackType.MeleeWeapon,
            reach=5,
            die=Die.d4,
            replaces_multiattack=1,
            name="Pommel Strike",
            additional_description=f"On a hit, the target must make a DC {dc} Constitution saving throw or become {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _PushingAttack(Warrior):
    def __init__(self):
        super().__init__(
            name="Pushing Attack",
            source="Foe Foundry",
            attack_names={
                "-",
                weapon.Maul,
                natural.Claw,
                natural.Slam,
            },
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.size >= Size.Huge:
            distance = 15
        elif stats.size >= Size.Large:
            distance = 10
        else:
            distance = 5

        feature = Feature(
            name="Pushing Attack",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, the target is pushed up to {distance} feet horizontally.",
        )

        return [feature]


class _ActionSurge(Warrior):
    def __init__(self):
        super().__init__(
            name="Action Surge",
            source="SRD5.1 Action Surge",
            power_level=HIGH_POWER,
            require_callback=is_organized,
            bonus_roles={MonsterRole.Bruiser, MonsterRole.Defender, MonsterRole.Leader},
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Action Surge",
            uses=1,
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} takes another action this round. If it has any recharge abilities, it may roll to refresh these abilities.",
        )
        return [feature]


class _Leap(Warrior):
    def __init__(self):
        def is_ground(c: BaseStatblock) -> bool:
            return (c.speed.fly or 0) == 0

        super().__init__(
            name="Mighty Leap",
            source="A5E SRD Bulette",
            create_date=datetime(2023, 11, 23),
            bonus_size=Size.Large,
            require_callback=is_ground,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, force_die=Die.d6)
        dc = stats.difficulty_class

        feature = Feature(
            name="Mighty Leap",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} can use its action to jump up to half its speed horizontally and up to half its speed vertically \
                without provoking opportunity attacks, and can land in a space containing one or more creatures. \
                Each creature in its space when {stats.selfref} lands makes a DC {dc} Dexterity saving throw, taking {dmg.description} bludgeoning damage and being knocked **Prone** \
                on a failure. On a success, the creature takes half damage and is pushed 5 feet to a space of its choice.",
        )

        return [feature]


class _Strangle(Warrior):
    def __init__(self):
        super().__init__(
            name="Strangle",
            source="A5E SRD - Bugbear",
            create_date=datetime(2023, 11, 23),
            attack_names=["-", weapon.Whip, natural.Slam, natural.Tentacle],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy
        return stats.add_attack(
            name="Strangle",
            scalar=0.8,
            damage_type=DamageType.Bludgeoning,
            replaces_multiattack=1,
            additional_description=f"On a hit, the target is **Grappled** (escape DC {dc}) and is pulled 5 feet toward {stats.selfref}. \
                Until this grapple ends, {stats.selfref} automatically hits with its Strangle attack and the target can't breathe. \
                If the target attempts to cast a spell with a verbal component, it must succeed on a DC {dc} Constitution saving throw or the spell fails.",
        )


# TODO A5E SRD - Horned Devil
# Pin (1/Day). When a creature misses the
# devil with a melee attack, the devil makes
# a fork attack against that creature. On a
# hit, the target is impaled by the fork and
# grappled (escape DC 17). Until this
# grapple ends, the devil can’t make fork
# attacks or use Inferno, but the target
# takes 7 (2d6) piercing damage plus 3
# A5E System Reference Document
# (1d6) fire damage at the beginning of
# each of its turns.

# TODO A5E SRD - Dread Knight
# Break Magic. The dread knight ends all
# spell effects created by a 5th-level or
# lower spell slot on a creature, object, or
# point it can see within 30 feet.


ActionSurge: Power = _ActionSurge()
Disciplined: Power = _Disciplined()
MightyLeap: Power = _Leap()
PackTactics: Power = _PackTactics()
ParryAndRiposte: Power = _ParryAndRiposte()
PommelStrike: Power = _PommelStrike()
PushingAttack: Power = _PushingAttack()
Strangle: Power = _Strangle()

WarriorPowers: List[Power] = [
    ActionSurge,
    Disciplined,
    MightyLeap,
    PackTactics,
    ParryAndRiposte,
    PommelStrike,
    PushingAttack,
    Strangle,
]
