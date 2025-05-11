from datetime import datetime
from typing import List

from foe_foundry.references import Token

from ...creature_types import CreatureType
from ...damage import DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class IcyPower(PowerWithStandardScoring):
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
            power_type=PowerType.Theme,
            power_level=power_level,
            create_date=create_date,
            theme="icy",
            reference_statblock="Cryomancer Mage",
            score_args=dict(
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Beast,
                    CreatureType.Monstrosity,
                    CreatureType.Elemental,
                    CreatureType.Dragon,
                ],
                require_damage=DamageType.Cold,
            )
            | score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Cold)
        return stats


class _Frostbite(IcyPower):
    def __init__(self):
        super().__init__(
            name="Frostbite",
            source="Foe Foundry",
            require_cr=2,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(
            target=1.5 * min(stats.multiattack, 2), force_die=Die.d8
        )
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Frostbite",
            action=ActionType.Action,
            replaces_multiattack=2,
            recharge=5,
            description=f"{stats.selfref.capitalize()} causes numbing frost to form on one creature within 60 feet. The target must make a DC {dc} Constitution saving throw. \
                On a failure, it suffers {dmg.description} cold damage and is {frozen.caption}. On a success, it suffers half damage instead. {frozen.description_3rd}",
        )
        return [feature]


class _IcyTomb(IcyPower):
    def __init__(self):
        super().__init__(
            name="Icy Tomb",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.8, force_die=Die.d6)
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Icy Tomb",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} creates a 10-foot radius sphere of ice centered on a point within 60 feet. \
                Each creature in the area must make a DC {dc} Constitution saving throw. On a failed save, a creature takes {dmg.description} cold damage and is {frozen.caption}. \
                On a successful save, it takes only half damage. {frozen.description_3rd}",
        )
        return [feature]


class _FrostNova(IcyPower):
    def __init__(self):
        super().__init__(
            name="Frost Nova",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            require_cr=4,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d6)
        frozen = conditions.Frozen(dc=dc)

        feature = Feature(
            name="Frost Nova",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} blasts out waves of ice. \
                Each other creature within 30 feet must make a DC {dc} Constitution saving throw. \
                On a failed save, a creature takes {dmg.description} cold damage and is {frozen.caption}. \
                On a successful save, it takes only half damage. {frozen.description_3rd}",
        )
        return [feature]


class _Hoarfrost(IcyPower):
    def __init__(self):
        super().__init__(name="Hoarfrost", source="Foe Foundry", power_level=HIGH_POWER)

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        frozen = conditions.Frozen(dc=dc)
        feature = Feature(
            name="Hoarfrost",
            action=ActionType.Feature,
            description=f"When a creature within 10 feet of {stats.selfref} takes cold damage, it must make a DC {stats.difficulty_class} Constitution saving throw. \
            On a failure, it is {frozen.caption} until the end of its next turn. {frozen.description_3rd}",
        )
        return [feature]


class _IcyShield(IcyPower):
    def __init__(self):
        super().__init__(
            name="Icy Shield", source="Foe Foundry", require_spellcasting=True
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = round(stats.attributes.proficiency * 1.5)
        feature = Feature(
            name="Icy Shield",
            action=ActionType.Reaction,
            uses=max(1, round(stats.attributes.proficiency / 2)),
            description=f"When {stats.selfref} is targeted by an attack, it surrounds itself with protective ice. It gains +5 to its AC until the start of its next turn. \
                If the attack hits, the icy shield expodes, dealing {dmg} Cold damage to each other creature within 10 feet.",
        )
        return [feature]


class _Blizzard(IcyPower):
    def __init__(self):
        super().__init__(
            name="Blizzard", source="Foe Foundry", power_level=HIGH_POWER, require_cr=6
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(dpr_proportion=0.5, force_die=Die.d6)
        frozen = conditions.Frozen(dc=dc)
        token = Token(
            name="Heart of the Blizzard", dc=stats.difficulty_class_token, charges=3
        )

        feature = Feature(
            name="Blizzard",
            action=ActionType.Action,
            recharge=5,
            description=f"{stats.selfref.capitalize()} summons the heart of a howling blizzard at an unoccupied point it can see within 60 feet, creating a {token.caption}. \
                Howling wind and snow fills a 30-foot emanation from the token. Any creature that ends its turn in the area must make a DC {dc} Constitution saving throw. \
                On a failed save, it takes {dmg.description} cold damage and is {frozen.caption}. {frozen.description_3rd}",
        )
        return [feature]


Blizzard: Power = _Blizzard()
FrostNova: Power = _FrostNova()
Frostbite: Power = _Frostbite()
Hoarfrost: Power = _Hoarfrost()
IcyShield: Power = _IcyShield()
IcyTomb: Power = _IcyTomb()

IcyPowers: list[Power] = [
    Blizzard,
    Frostbite,
    FrostNova,
    Hoarfrost,
    IcyShield,
    IcyTomb,
]
