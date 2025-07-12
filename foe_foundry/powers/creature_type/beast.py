from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...attack_template import natural as natural_attacks
from ...attributes import Skills
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, Condition
from ...die import Die
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerCategory,
    PowerWithStandardScoring,
)


class BeastPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = MEDIUM_POWER,
        reference_statblock: str = "Dire Wolf",
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Beast, **score_args)

        super().__init__(
            name=name,
            power_category=PowerCategory.CreatureType,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Beast",
            icon=icon,
            reference_statblock=reference_statblock,
            score_args=standard_score_args,
        )


class _FeedingFrenzy(BeastPower):
    def __init__(self):
        super().__init__(
            name="Feeding Frenzy",
            source="Foe Foundry",
            icon="gluttony",
            create_date=datetime(2023, 11, 21),
            require_attack_types=AttackType.MeleeNatural,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Feeding Frenzy",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} moves up to 30 feet without provoking opportunity attacks. \
                If it ends the movement next to a target that has lost half its hit points or more, it may make an attack against that target.",
        )
        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _BestialRampage(BeastPower):
    def __init__(self):
        super().__init__(
            name="Bestial Rampage",
            source="Foe Foundry",
            icon="wolverine-claws",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
            require_attack_types=AttackType.MeleeNatural,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bestial Rampage",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is reduced to half its health or lower, it moves up to 30 feet without provoking opportunity attacks \
                and makes a melee attack against another target in its rage.",
        )

        return [feature]

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Survival)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _Gore(BeastPower):
    def __init__(self):
        super().__init__(
            name="Gore",
            source="SRD 5.1 Minotaur",
            icon="charging-bull",
            reference_statblock="Giant Boar",
            attack_names=["-", natural_attacks.Horns],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        bleeding_damage = stats.target_value(target=0.5, force_die=Die.d6)
        bleeding = Bleeding(damage=bleeding_damage)
        prone = Condition.Prone

        damage = stats.target_value(
            target=1.5 if stats.multiattack > 1 else 0.75, force_die=Die.d6
        )

        feature = Feature(
            name="Gore",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} moves up to half its movement speed in a straight line. Each creature in the path must make a DC {dc} Dexterity saving throw. \
                On a failure, the target is {prone.caption}, takes {damage.description} piercing damage, and gains {bleeding.caption}. On a success, the target takes half damage instead. {bleeding.description_3rd}",
        )
        return [feature]


class _Packlord(BeastPower):
    def __init__(self):
        super().__init__(
            name="Packlord",
            icon="wolf-head",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_cr=3,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        if stats.speed.fly:
            options = summoning.FlyingBeasts
        elif stats.speed.swim:
            options = summoning.SwimmingBeasts
        else:
            options = summoning.LandBeasts

        _, _, description = summoning.determine_summon_formula(
            options, stats.cr / 3.5, stats.create_rng(), max_quantity=10
        )

        feature = Feature(
            name="Packlord",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} roars, summoning its pack to its aid. {description}",
        )

        return [feature]


class _WildInstinct(BeastPower):
    def __init__(self):
        super().__init__(
            name="Wild Instinct",
            source="Foe Foundry",
            icon="shark-bite",
            power_level=RIBBON_POWER,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        feature = Feature(
            name="Wild Instinct",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} identifies the creature with the lowest Strength score that it can see. It then uses {dash} towards that creature.",
        )
        return [feature]


class _ScentOfWeakness(BeastPower):
    def __init__(self):
        super().__init__(
            name="Scent of Weakness",
            source="Foe Foundry",
            icon="sniffing-dog",
            power_level=LOW_POWER,
            require_attack_types=AttackType.MeleeNatural,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        bloodied = Condition.Bloodied.caption
        feature = Feature(
            name="Scent of Weakness",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can smell blood. It has advantage on attacks against any {bloodied} creature and always knows the location of any {bloodied} creature within 60 feet of it.",
        )
        return [feature]


BestialRampage: Power = _BestialRampage()
FeedingFrenzy: Power = _FeedingFrenzy()
Gore: Power = _Gore()
Packlord: Power = _Packlord()
ScentOfWeakness: Power = _ScentOfWeakness()
WildInstinct: Power = _WildInstinct()

BeastPowers: List[Power] = [
    BestialRampage,
    FeedingFrenzy,
    Gore,
    Packlord,
    ScentOfWeakness,
    WildInstinct,
]
