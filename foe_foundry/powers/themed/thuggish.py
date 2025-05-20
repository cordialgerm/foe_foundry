from datetime import datetime
from typing import List

from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class ThuggishPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        create_date: datetime | None = datetime(2025, 3, 22),
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_attack_types=AttackType.AllMelee(),
            require_types=[
                CreatureType.Humanoid,
            ],
            bonus_skills=Skills.Intimidation,
            bonus_stats=Stats.CHA,
            require_roles={
                MonsterRole.Bruiser,
                MonsterRole.Leader,
            },
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source=source,
            theme="thuggish",
            icon=icon,
            reference_statblock="Thug",
            create_date=create_date,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _MobBoss(ThuggishPower):
    def __init__(self):
        super().__init__(
            name="Mob Boss",
            icon="minions",
            source="Foe Foundry",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Mob Boss",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has advantage on d20 tests as long as at least two other lower-CR allies are within 10 feet.",
        )

        return [feature]


class _KickTheLickspittle(ThuggishPower):
    def __init__(self):
        super().__init__(
            name="Kick the Lickspittle",
            icon="boot-kick",
            source="Foe Foundry",
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.from_expression("2d4")
        feature = Feature(
            name="Kick the Lickspittle",
            action=ActionType.Reaction,
            description=f"If {stats.selfref} fails a d20 test, they can use a reaction to blame a nearby ally within 5 feet. The ally must be a smaller size or lower CR than {stats.selfref}. \
                The ally takes {dmg.description} bludgeoning damage and the {stats.selfref} adds this total to the attack or saving throw, potentially turning a failure or miss into a success.",
        )
        return [feature]


class _ExploitTheChaos(ThuggishPower):
    def __init__(self):
        super().__init__(
            name="Exploit the Chaos", source="Foe Foundry", icon="target-dummy"
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Exploit the Chaos",
            action=ActionType.Reaction,
            description=f"If a nearby enemy within 15 feet misses an attack against a friendly creature, {stats.selfref} can use its reaction to dart forward up to 15 feet and make an attack against that creature.",
        )
        return [feature]


MobBoss: Power = _MobBoss()
KickTheLickspittle: Power = _KickTheLickspittle()
ExploitTheChaos: Power = _ExploitTheChaos()

ThuggishPowers: List[Power] = [
    MobBoss,
    KickTheLickspittle,
    ExploitTheChaos,
]
