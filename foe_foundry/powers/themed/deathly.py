from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Bleeding, DamageType, Weakened
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class DeathlyPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        def undead_or_necromancer(c: BaseStatblock) -> bool:
            if c.creature_type == CreatureType.Undead:
                return True
            else:
                return (
                    any(t.is_spell() for t in c.attack_types)
                    and c.secondary_damage_type == DamageType.Necrotic
                )

        callback = score_args.pop("require_callback", None)

        def required_callback(c: BaseStatblock) -> bool:
            if callback is None:
                return undead_or_necromancer(c)
            else:
                return undead_or_necromancer(c) and callback(c)

        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            create_date=create_date,
            theme="death",
            power_level=power_level,
            score_args=dict(
                require_types={
                    CreatureType.Undead,
                    CreatureType.Fiend,
                    CreatureType.Humanoid,
                },
                require_callback=required_callback,
                bonus_damage=DamageType.Necrotic,
                bonus_types=CreatureType.Undead,
                **score_args,
            ),
        )


class _EndlessServitude(DeathlyPower):
    def __init__(self):
        super().__init__(
            name="Endless Servitude",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=3,
            bonus_roles=MonsterRole.Leader,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Endless Servitude",
            action=ActionType.Feature,
            description=f"When a non-zombie, non-skeleton ally who can see {stats.selfref} is reduced to 0 hp, that ally immediately becomes a *Zombie* or *Skeleton* under {stats.selfref}'s control, acting at initiative count 0.",
        )
        return [feature]


def _has_no_other_attacks(stats: BaseStatblock) -> bool:
    return len(stats.additional_attacks) == 0


class _WitheringBlow(DeathlyPower):
    def __init__(self):
        super().__init__(
            name="Withering Blow",
            source="Foe Foundry",
            require_attack_types=AttackType.AllMelee(),
            require_callback=_has_no_other_attacks,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class_easy

        def customize(a: Attack) -> Attack:
            a = a.split_damage(DamageType.Necrotic, split_ratio=0.9)

            # the ongoing bleed damage should be equal to the necrotic damage formula for symmetry
            bleeding_dmg = (
                a.additional_damage.formula
                if a.additional_damage
                else DieFormula.from_expression("1d6")
            )
            bleeding = Bleeding(
                damage=bleeding_dmg, damage_type=DamageType.Necrotic, dc=dc
            )

            return a.copy(
                additional_description=f"On a hit, the target gains {bleeding}."
            )

        stats = stats.add_attack(
            scalar=1.4,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            name="Withering Blow",
            replaces_multiattack=2,
            callback=customize,
        )
        return stats


class _DrainingBlow(DeathlyPower):
    def __init__(self):
        super().__init__(name="Draining Blow", source="Foe Foundry")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Draining Blow",
            action=ActionType.BonusAction,
            description=f"Immediately after hitting with an attack, {stats.selfref} converts all of that attack's damage to necrotic damage and {stats.selfref} regains hit points equal to the necrotic damage dealt.",
        )
        return [feature]


def no_unique_movement(stats: BaseStatblock) -> bool:
    return not stats.has_unique_movement_manipulation


class _ShadowWalk(DeathlyPower):
    def __init__(self):
        super().__init__(
            name="Shadow Walk",
            source="A5E SRD Adept",
            power_level=LOW_POWER,
            require_callback=no_unique_movement,
            require_speed=30,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Shadow Walk",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} teleports from one source of shadows to another that it can see within 60 feet.",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        return stats.copy(has_unique_movement_manipulation=True)


class _FleshPuppets(DeathlyPower):
    def __init__(self):
        super().__init__(
            name="Flesh Puppets", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        cr = int(ceil(stats.cr / 3))

        feature = Feature(
            name="Flesh Puppets",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"{stats.selfref.capitalize()} uses dark necromancy to resurrect the corpse of a nearby creature of CR {cr} or less. \
                The creature acts in initiative immediately after {stats.selfref} and obeys the commands of {stats.selfref} (no action required). \
                The flesh puppet has the same statistics as when the creature was living except it is now Undead, or uses the statistics of a **Skeleton**, **Zombie**, or **Ghoul**. \
                When the flesh puppet dies, the corpse is mangled beyond repair and is turned into a pile of viscera.",
        )
        return [feature]


class _DevourSoul(DeathlyPower):
    def __init__(self):
        super().__init__(
            name="Devour Soul", source="Foe Foundry", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(1.5, force_die=Die.d6)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Devour Soul",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} targets one creature it can see within 30 feet of it that is not a Construct or an Undead. \
                The creature must succeed on a DC {dc} Charisma saving throw or take {dmg.description} necrotic damage. \
                If this damage reduces the target to 0 hit points, it dies and immediately rises as a **Ghoul** under {stats.selfref}'s control.",
        )
        return [feature]


class _DrainStrength(DeathlyPower):
    def __init__(self):
        super().__init__(name="Drain Strength", source="SRD5.1 Shadow")

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy

        dmg = stats.target_value(1.5, force_die=Die.d6)
        weakened = Weakened(save_end_of_turn=True)

        feature = Feature(
            name="Drain Strength",
            action=ActionType.Action,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} attempts to magically drain the strength from a creature it can see within 5 feet. \
                The creature must make a DC {dc} Constitution save. On a failure, the creature takes {dmg.description} necrotic damage and is {weakened.caption} \
                for 1 minute (save ends at end of turn). On a success, the creature takes half damage instead. {weakened.description_3rd}",
        )
        return [feature]


DevourSoul: Power = _DevourSoul()
DrainingBlow: Power = _DrainingBlow()
DrainStrength: Power = _DrainStrength()
FleshPuppets: Power = _FleshPuppets()
ShadowWalk: Power = _ShadowWalk()
EndlessServitude: Power = _EndlessServitude()
WitheringBlow: Power = _WitheringBlow()

DeathlyPowers: List[Power] = [
    DevourSoul,
    DrainingBlow,
    DrainStrength,
    EndlessServitude,
    FleshPuppets,
    ShadowWalk,
    WitheringBlow,
]
