from datetime import datetime
from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType, Frozen
from ...die import Die
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import MEDIUM_POWER, Power, PowerCategory, PowerWithStandardScoring


class UndeadPower(PowerWithStandardScoring):
    def __init__(
        self,
        *,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = None,
        reference_statblock: str = "Wight",
        power_level: float = MEDIUM_POWER,
        power_types: List[PowerType],
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Undead, **score_args)
        super().__init__(
            name=name,
            power_category=PowerCategory.CreatureType,
            source=source,
            create_date=create_date,
            power_level=power_level,
            power_types=power_types,
            icon=icon,
            theme="Undead",
            reference_statblock=reference_statblock,
            score_args=standard_score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        bonus_damage = self.score_args.get("bonus_damage") if self.score_args else None
        if bonus_damage is not None and stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=bonus_damage)
        return stats


class _UndeadFortitude(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Undead Fortitude",
            icon="raise-zombie",
            reference_statblock="Zombie",
            source="SRD5.1 Zombie",
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Undead Resilience",
            action=ActionType.Reaction,
            description=f"When damage reduces {stats.selfref} to 0 hit points, it must make a Constitution saving throw with a DC of 5 + the damage taken, \
                unless the damage is radiant or from a critical hit. On a success, {stats.selfref} instead drops to 1 hit point and this ability does not consume {stats.selfref}'s reaction.",
        )
        return [feature]


class _StenchOfDeath(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Stench of Death",
            icon="carrion",
            reference_statblock="Ghast",
            source="SRD5.1 Hezrou",
            power_types=[PowerType.Environmental, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        poisoned = Condition.Poisoned
        feature = Feature(
            name="Stench of Death",
            action=ActionType.Feature,
            description=f"Any creature that starts its turn within 10 feet of {stats.selfref} must make a DC {dc} Constitution saving throw or become {poisoned.caption} until the start of their next turn. \
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
            icon="icicles-aura",
            bonus_damage=DamageType.Cold,
            require_callback=not_burning_undead,
            power_types=[PowerType.AreaOfEffect, PowerType.Attack, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.5, force_die=Die.d8)
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


class _SoulChill(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Soul Chill",
            source="Foe Foundry",
            icon="brain-freeze",
            bonus_damage=DamageType.Cold,
            require_callback=not_burning_undead,
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        distance = easy_multiple_of_five(stats.cr * 10, min_val=15, max_val=60)
        exhaustion = Condition.Exhaustion

        feature = Feature(
            name="Soul Chill",
            action=ActionType.Reaction,
            description=f"Whenever a creature within {distance} feet that {stats.selfref} can see fails a saving throw, {stats.selfref} can attempt to leech away a portion of its spirit. \
                The creature must succeed on a DC {dc} Charisma saving throw. On a failure, it gains one level of {exhaustion.caption}.",
        )
        return [feature]


class _SoulTether(UndeadPower):
    def __init__(self):
        super().__init__(
            name="Soul Tether",
            reference_statblock="Lich",
            source="SRD5.1 Lich",
            icon="elysium-shade",
            require_cr=6,
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
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
        super().__init__(
            name="Antithesis of Life",
            reference_statblock="Lich",
            source="Foe Foundry",
            icon="grim-reaper",
            require_cr=4,
            power_types=[PowerType.Environmental, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Antithesis of Life",
            action=ActionType.Feature,
            description=f"Whenever a creature within 30 feet of the {stats.selfref} regains hit points, it must make a DC {dc} Charisma saving throw. \
                On a failure, the healing received is reduced to zero. On a success, the creature is immune to this effect for 1 hour.",
        )
        return [feature]


AntithesisOfLife: Power = _AntithesisOfLife()
SoulChill: Power = _SoulChill()
SoulTether: Power = _SoulTether()
StenchOfDeath: Power = _StenchOfDeath()
StygianBurst: Power = _StygianBurst()
UndeadFortitude: Power = _UndeadFortitude()

UndeadPowers: List[Power] = [
    AntithesisOfLife,
    SoulChill,
    SoulTether,
    StenchOfDeath,
    StygianBurst,
    UndeadFortitude,
]
