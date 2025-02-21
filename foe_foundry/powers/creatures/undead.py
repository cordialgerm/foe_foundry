from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import DamageType, Frozen
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class UndeadPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Undead, **score_args)
        super().__init__(
            name=name,
            power_type=PowerType.Creature,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Undead",
            score_args=standard_score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        bonus_damage = self.score_args.get("bonus_damage") if self.score_args else None
        if bonus_damage is not None and stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=bonus_damage)
        return stats


class _UndeadFortitude(UndeadPower):
    def __init__(self):
        super().__init__(name="Undead Fortitude", source="SRD5.1 Zombie")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Undead Resilience",
            action=ActionType.Reaction,
            description=f"When damage reduces {stats.selfref} to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, \
                unless the damage is radiant or from a critical hit. On a success, {stats.selfref} instead drops to 1 hit point.",
        )
        return [feature]


class _StenchOfDeath(UndeadPower):
    def __init__(self):
        super().__init__(name="Stench of Death", source="SRD5.1 Hezrou")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Stench of Death",
            action=ActionType.Feature,
            description=f"Any creature that starts its turn within 10 feet of {stats.selfref} must make a DC {dc} Constitution saving throw or become poisoned until the start of their next turn. \
                On a successful saving throw, the creature is immune to {stats.selfref}'s stench for 24 hours.",
        )
        return [feature]


def not_burning_undead(stats: BaseStatblock) -> bool:
    return stats.secondary_damage_type != DamageType.Fire


class _StygianBurst(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Stygian Burst",
            source="Foe Foundry",
            bonus_damage=DamageType.Cold,
            require_callback=not_burning_undead,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(1.5, force_die=Die.d8)
        frozen = Frozen(dc=dc)
        hp = easy_multiple_of_five(stats.hp.average / 2)
        distance = easy_multiple_of_five(2.5 * stats.cr, min_val=10, max_val=40)

        feature = Feature(
            name="Stygian Burst",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} takes a critical hit, or when it is reduced to {hp} hitpoints or fewer, it releases a burst of deathly cold. \
                Each non-undead creature within {distance} feet must make a DC {dc} Consitution saving throw. On a failure, the creature takes {dmg.description} cold damage and is {frozen}",
        )
        return [feature]


class _Frostbite(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Frostbite",
            source="Foe Foundry",
            bonus_damage=DamageType.Cold,
            require_callback=not_burning_undead,
            require_cr=2,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(1.5 * min(stats.multiattack, 2), force_die=Die.d8)
        frozen = Frozen(dc=dc)

        feature = Feature(
            name="Frostbite",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes numbing frost to form on one creature within 60 feet. The target must make a DC {dc} Constitution saving throw. \
                On a failure, it suffers {dmg.description} cold damage and is {frozen}. On a success, it suffers half damage instead.",
        )
        return [feature]


class _SoulChill(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Soul Chill",
            source="Foe Foundry",
            bonus_damage=DamageType.Cold,
            require_callback=not_burning_undead,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 10, min_val=15, max_val=60)

        feature = Feature(
            name="Soul Chill",
            action=ActionType.Reaction,
            description=f"Whenever a creature within {distance} feet that {stats.selfref} can see fails a saving throw, {stats.selfref} can attempt to leech away a portion of its spirit. \
                The creature must succeed on a DC {dc} Charisma saving throw. On a failure, it gains one level of **Exhaustion**.",
        )
        return [feature]


class _SoulTether(UndeadPower):
    def __init__(self):
        super().__init__(name="Soul Tether", source="SRD5.1 Lich", require_cr=6)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Soul Tether",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 30 feet of it. A crackling cord of negative energy tethers {stats.selfref} to the target. \
                Whenever {stats.selfref} takes damage, the target must succeed on a DC {dc} Constitution saving throw. On a failed save, {stats.selfref} takes half the damage (rounded down) and the target takes the remaining. \
                The tether lasts until the beginning of {stats.selfref}'s next turn.",
        )
        return [feature]


class _AntithesisOfLife(UndeadPower):
    def __init__(self):
        super().__init__(name="Antithesis of Life", source="Foe Foundry", require_cr=4)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Antithesis of Life",
            action=ActionType.Feature,
            description=f"Whenever a creature within 30 feet of the {stats.selfref} regains hit points, it must make a DC {dc} Charisma saving throw. \
                On a failure, the healing received is reduced to zero. On a success, the creature is immune to this effect for 1 hour.",
        )
        return [feature]


AntithesisOfLife: Power = _AntithesisOfLife()
Frostbite: Power = _Frostbite()
SoulChill: Power = _SoulChill()
SoulTether: Power = _SoulTether()
StenchOfDeath: Power = _StenchOfDeath()
StygianBurst: Power = _StygianBurst()
UndeadFortitude: Power = _UndeadFortitude()

UndeadPowers: List[Power] = [
    AntithesisOfLife,
    Frostbite,
    SoulChill,
    SoulTether,
    StenchOfDeath,
    StygianBurst,
    UndeadFortitude,
]
