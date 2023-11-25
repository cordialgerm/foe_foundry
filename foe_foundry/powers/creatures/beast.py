from datetime import datetime
from typing import List

import numpy as np

from ...attack_template import natural as natural_attacks
from ...attributes import Skills
from ...creature_types import CreatureType
from ...damage import AttackType, Bleeding, DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class BeastPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(require_types=CreatureType.Beast, **score_args)

        super().__init__(
            name=name,
            power_type=PowerType.Creature,
            source=source,
            create_date=create_date,
            power_level=power_level,
            theme="Beast",
            score_args=standard_score_args,
        )


class _FeedingFrenzy(BeastPower):
    def __init__(self):
        super().__init__(
            name="Feeding Frenzy",
            source="FoeFoundryOriginal",
            create_date=datetime(2023, 11, 21),
            require_attack_types=AttackType.MeleeNatural,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Feeding Frenzy",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} moves up to 30 feet without provoking opportunity attacks. \
                If it ends the movement next to a target that has lost half its hit points or more, it may make an attack against that target.",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _BestialRampage(BeastPower):
    def __init__(self):
        super().__init__(
            name="Bestial Rampage",
            source="FoeFoundryOriginal",
            create_date=datetime(2023, 11, 21),
            power_level=LOW_POWER,
            require_attack_types=AttackType.MeleeNatural,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bestial Rampage",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.selfref} is reduced to half its health or lower, it moves up to 30 feet without provoking opportunity attacks and makes a melee attack against another target in rage.",
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Survival)
        stats = stats.copy(attributes=new_attrs)
        return stats


class _Gore(BeastPower):
    def __init__(self):
        super().__init__(
            name="Gore", source="SRD 5.1 Minotaur", attack_names=["-", natural_attacks.Horns]
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Gore",
            description="This creature gets an additional Gore attack",
            action=ActionType.Feature,
            hidden=True,
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        dc = stats.difficulty_class

        bleeding_damage = stats.target_value(0.5)
        bleeding = Bleeding(damage=bleeding_damage)

        stats = stats.add_attack(
            scalar=1.5,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            name="Gore",
            replaces_multiattack=2,
            additional_description=f"If {stats.selfref} moved at least 10 feet before making this attack, then the target must make a DC {dc} Dexterity saving throw. On a failure, the target is gored and gains {bleeding}.",
        )
        return stats


class _Web(BeastPower):
    def __init__(self):
        super().__init__(
            name="Web",
            source="SRD 5.1 Giant Spider",
            attack_names={
                "-",
                natural_attacks.Bite,
                natural_attacks.Claw,
                natural_attacks.Stinger,
            },
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class

        feature1 = Feature(
            name="Spider Climb",
            action=ActionType.Feature,
            description=f"{stats.selfref} can climb difficult surfaces, including upside down on ceilings, without needing to make an ability check.",
        )

        feature2 = Feature(
            name="Web Sense",
            action=ActionType.Feature,
            description=f"While in contact with a web, {stats.selfref} knows the exact location of any other creature in contact with the same web.",
        )

        feature3 = Feature(
            name="Web",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=1,
            description=f"{stats.selfref.capitalize()} shoots a sticky web at a point it can see within 60 feet. \
                Each creature within a 20 foot cube centered at the point must make a DC {dc} Dexterity saving throw or become **Restrained** (save ends at end of turn). \
                The area of the web is considered difficult terrain, and any creature that ends its turn in the area must repeat the save or become restrained.",
        )

        return [feature1, feature2, feature3]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(climb=stats.speed.walk)
        stats = stats.copy(speed=new_speed)
        return stats


class _Packlord(BeastPower):
    def __init__(self):
        super().__init__(
            name="Packlord", source="FoeFoundryOriginal", power_level=HIGH_POWER, require_cr=3
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        if stats.speed.fly:
            options = summoning.FlyingBeasts
        elif stats.speed.swim:
            options = summoning.SwimmingBeasts
        else:
            options = summoning.LandBeasts

        # TODO - replace randomness here
        rng = np.random.default_rng(20210518)
        _, _, description = summoning.determine_summon_formula(
            options, stats.cr / 3.5, rng, max_quantity=10
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
            source="FoeFoundryOriginal",
            power_level=RIBBON_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Wild Instinct",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} identifies the creature with the lowest Strength score that it can see. It then Dashes towards that creature.",
        )
        return [feature]


BestialRampage: Power = _BestialRampage()
FeedingFrenzy: Power = _FeedingFrenzy()
Gore: Power = _Gore()
Packlord: Power = _Packlord()
Web: Power = _Web()
WildInstinct: Power = _WildInstinct()

BeastPowers: List[Power] = [BestialRampage, FeedingFrenzy, Gore, Packlord, Web, WildInstinct]
