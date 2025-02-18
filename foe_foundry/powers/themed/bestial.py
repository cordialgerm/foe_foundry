from datetime import datetime
from typing import List

from ...attack_template import natural
from ...creature_types import CreatureType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...size import Size
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring


class BestialPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = dict(
            require_types=[
                CreatureType.Monstrosity,
                CreatureType.Beast,
                CreatureType.Dragon,
            ],
            bonus_roles=MonsterRole.Bruiser,
            bonus_size=Size.Large,
            **score_args,
        )
        super().__init__(
            name=name,
            source=source,
            theme="Bestial",
            create_date=create_date,
            power_type=PowerType.Theme,
            power_level=power_level,
            score_args=standard_score_args,
        )


class _RetributiveStrike(BestialPower):
    def __init__(self):
        super().__init__(
            name="Retributive Strike", source="A5E SRD Roc", power_level=HIGH_POWER
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        hp = easy_multiple_of_five(stats.hp.average / 2, min_val=5)

        feature = Feature(
            name="Retributive Strike",
            description=f"When a creature {stats.selfref} can see hits it with a melee weapon attack, {stats.selfref} can make an attack against its attacker. \
                If {stats.selfref} is below {hp} hp then the attack is made with advantage.",
            action=ActionType.Reaction,
        )
        return [feature]


class _OpportuneBite(BestialPower):
    def __init__(self):
        super().__init__(
            name="Opportune Bite",
            source="A5E SRD Lion",
            create_date=datetime(2023, 11, 23),
            attack_names=["-", natural.Bite],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Opportune Bite",
            description=f"{stats.selfref} makes a Bite attack against a prone creature.",
            action=ActionType.BonusAction,
        )
        return [feature]


class _Trample(BestialPower):
    def __init__(self):
        super().__init__(
            name="Trample",
            source="A5E SRD Mammoth",
            create_date=datetime(2023, 11, 23),
            attack_names=["-", natural.Stomp],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Trample",
            description=f"{stats.selfref} makes a Stomp attack against a prone creature.",
            action=ActionType.BonusAction,
        )
        return [feature]


class _BurrowingAmbush(BestialPower):
    def __init__(self):
        def can_burrow(stats: BaseStatblock) -> bool:
            return (stats.speed.burrow or 0) > 0

        super().__init__(
            name="Burrowing Ambush",
            source="A5E SRD Ankheg Queen",
            create_date=datetime(2023, 11, 22),
            attack_names=natural.Claw,
            require_callback=can_burrow,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Burrowing Ambush",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref} can burrow up to its burrowing speed without provoking opportunity attacks, and then resurface. \
                If within melee range of an enemy, it makes an attack with advantage.",
        )
        return [feature]


class _TurboTrot(BestialPower):
    def __init__(self):
        super().__init__(
            name="Turbo Trot",
            source="A5E SRD Centaur",
            create_date=datetime(2023, 11, 28),
            attack_names=["-", natural.Stomp],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Turbo Trot",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, {stats.selfref}'s movement doesn't provoke opportunity attacks from the target for the rest of the turn.",
        )
        return [feature]


BurrowingAmbush: Power = _BurrowingAmbush()
RetributiveStrike: Power = _RetributiveStrike()
OpportuneBite: Power = _OpportuneBite()
Trample: Power = _Trample()
TurboTrot: Power = _TurboTrot()

BestialPowers: List[Power] = [
    BurrowingAmbush,
    RetributiveStrike,
    OpportuneBite,
    Trample,
    TurboTrot,
]
