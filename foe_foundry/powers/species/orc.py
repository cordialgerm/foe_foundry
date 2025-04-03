from datetime import datetime
from typing import List

from foe_foundry.references import action_ref

from ...creature_types import CreatureType
from ...damage import AttackType, Condition, conditions
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import abjuration, evocation, illusion
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    RIBBON_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)
from ..roles.bruiser import StunningBlow
from ..themed.reckless import RelentlessEndurance


def is_orc(stats: BaseStatblock) -> bool:
    return (
        stats.creature_subtype is not None and stats.creature_subtype.lower() == "orc"
    )


class OrcPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        create_date: datetime | None = None,
        power_level: float = MEDIUM_POWER,
        **score_args,
    ):
        standard_score_args = (
            dict(
                require_types=CreatureType.Humanoid,
                require_callback=is_orc,
            )
            | score_args
        )
        super().__init__(
            name=name,
            power_type=PowerType.Species,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Orc",
            score_args=standard_score_args,
        )


class OrcPowerWrapper(OrcPower):
    def __init__(
        self,
        name: str,
        source: str,
        wrapped_power: Power,
        create_date: datetime | None = None,
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            create_date=create_date,
            power_level=wrapped_power.power_level,
            **score_args,
        )
        self.wrapped_power = wrapped_power

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        new_features = self.wrapped_power.generate_features(stats)
        if len(new_features) == 1:
            f = new_features[0]
            f.name = self.name
            return [f]
        else:
            return new_features

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return self.wrapped_power.modify_stats_inner(stats)


class _BloodrageDash(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodrage Dash",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 17),
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[
                MonsterRole.Bruiser,
                MonsterRole.Soldier,
                MonsterRole.Ambusher,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dash = action_ref("Dash")
        feature = Feature(
            name="Bloodrage Dash",
            description=f"The orc uses {dash} as a bonus action and moves directly towards an enemy. The next attack it makes this turn is made with advantage.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _BloodrageBarrage(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodrage Barrage",
            source="Foe Foundry",
            power_level=RIBBON_POWER,
            create_date=datetime(2025, 2, 17),
            require_attack_types=AttackType.AllRanged(),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Bloodrage Barrage",
            description="When the orc misses with a ranged attack, it can make another ranged attack at the same target using its reaction. The attack is made with advantage.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


class _SavageMomentum(OrcPower):
    def __init__(self):
        super().__init__(
            name="Savage Momentum",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 3, 31),
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Soldier],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        prone = Condition.Prone.caption
        feature = Feature(
            name="Savage Momentum",
            description=f"When {stats.selfref} moves at least 20 ft in a straight line before hitting an enemy with a melee attack, it can choose to either knock the creature {prone} or knock the creature back 10 feet.",
            action=ActionType.Feature,
        )
        return [feature]


class _Bloodfury(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodfury",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            create_date=datetime(2025, 3, 31),
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Soldier],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        bloodied = Condition.Bloodied.caption
        enraged = conditions.Enraged()
        feature = Feature(
            name="Bloodfury",
            description=f"When {stats.selfref} becomes {bloodied} it becomes {enraged.caption} for the next minute. {enraged.description_3rd}.",
            action=ActionType.Feature,
        )
        return [feature]


class _AncestralGuidance(OrcPower):
    def __init__(self):
        def require_callback(stats: BaseStatblock) -> bool:
            return is_orc(stats) and not stats.is_legendary

        super().__init__(
            name="Ancestral Guidance",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 3, 31),
            require_cr=1,
            bonus_roles=[
                MonsterRole.Support,
                MonsterRole.Leader,
                MonsterRole.Controller,
            ],
            require_callback=require_callback,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Ancestral Guidance",
            description=f"When {stats.selfref} fails a d20 test, it succeeds instead.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


class _BloodburnTattoo(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodburn Tattoo",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 3, 31),
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Soldier],
            require_cr=1,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        spell = evocation.BurningHands.for_statblock().scale_for_cr(stats.cr)
        dc = stats.difficulty_class_easy

        feature = Feature(
            name="Bloodburn Tattoo",
            description=f"Immediately after hitting with a melee attack, {stats.selfref} unleashes the rage imbued into its ancestral tattoo. It casts {spell.caption_md} with a DC of {dc}.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _ThunderwrathTatoo(OrcPower):
    def __init__(self):
        super().__init__(
            name="Thunderwrath Tattoo",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 3, 31),
            require_attack_types=AttackType.AllRanged(),
            bonus_roles=[MonsterRole.Artillery, MonsterRole.Controller],
            require_cr=1,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        spell = evocation.Shatter.for_statblock().scale_for_cr(stats.cr)
        dc = stats.difficulty_class_easy
        feature = Feature(
            name="Thunderwrath Tattoo",
            description=f"Immediately after hitting with a ranged attack, {stats.selfref} unleashes the elemental fury imbued into its ancestral tattoo. It casts {spell.caption_md} centered on the creature it hit with a DC of {dc}.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _SpiritSneakTatoo(OrcPower):
    def __init__(self):
        super().__init__(
            name="Spirit Sneak Tattoo",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 3, 31),
            require_roles=[MonsterRole.Ambusher, MonsterRole.Skirmisher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        spell = illusion.Invisibility.for_statblock()
        feature = Feature(
            name="Spirit Sneak Tattoo",
            description=f"Immediately after hitting with a melee attack, {stats.selfref} activates its tatoo and casts {spell.caption_md} on itself.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _EmpoweringTatoo(OrcPower):
    def __init__(self):
        super().__init__(
            name="Empowering Tattoo",
            source="Foe Foundry",
            power_level=LOW_POWER,
            create_date=datetime(2025, 3, 31),
            require_cr=1,
            require_roles=[
                MonsterRole.Leader,
                MonsterRole.Defender,
                MonsterRole.Support,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        spell = abjuration.CureWounds.for_statblock().scale_for_cr(stats.cr)
        feature = Feature(
            name="Empowering Tattoo",
            description=f"Immediately after hitting with an attack, {stats.selfref} unleashes the empowering energy in its tatoo, casting {spell.caption_md} on a creature within 30 feet.",
            action=ActionType.Reaction,
            uses=1,
        )
        return [feature]


AncestralGuidance: Power = _AncestralGuidance()
BloodburnTattoo: Power = _BloodburnTattoo()
Bloodfury: Power = _Bloodfury()
BloodrageDash: Power = _BloodrageDash()
BloodrageBarrage: Power = _BloodrageBarrage()
BloodrageBlow: Power = OrcPowerWrapper(
    name="Bloodrage Blow",
    source="Foe Foundry",
    wrapped_power=StunningBlow,
    create_date=datetime(2025, 2, 17),
    require_attack_types=AttackType.AllMelee(),
    bonus_roles=[MonsterRole.Bruiser, MonsterRole.Soldier],
)
BloodrageEndurance: Power = OrcPowerWrapper(
    name="Bloodrage Endurance",
    source="Foe Foundry",
    wrapped_power=RelentlessEndurance,
    create_date=datetime(2025, 2, 17),
    bonus_roles=[
        MonsterRole.Defender,
        MonsterRole.Soldier,
        MonsterRole.Bruiser,
        MonsterRole.Leader,
    ],
)
EmpoweringTatoo: Power = _EmpoweringTatoo()
SavageMomentum: Power = _SavageMomentum()
SpiritSeek: Power = _SpiritSneakTatoo()
ThunderwrathTattoo: Power = _ThunderwrathTatoo()


OrcPowers: List[Power] = [
    AncestralGuidance,
    Bloodfury,
    BloodrageDash,
    BloodrageBarrage,
    BloodrageBlow,
    BloodrageEndurance,
    EmpoweringTatoo,
    SavageMomentum,
    SpiritSeek,
    ThunderwrathTattoo,
]
