from datetime import datetime
from typing import List

from foe_foundry.references import action_ref
from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import AttackType, Condition, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...skills import Stats
from ...spells import abjuration, evocation, illusion
from ...statblocks import BaseStatblock
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
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
        icon: str,
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
            icon=icon,
            theme="Orc",
            reference_statblock="Orc",
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
            icon=wrapped_power.icon or "orc-head",
            **score_args,
        )
        self.wrapped_power = wrapped_power

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        new_features = self.wrapped_power.generate_features(stats)
        if len(new_features) == 1:
            f = new_features[0]
            return [f.copy(name=self.name)]
        else:
            return new_features

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return self.wrapped_power.modify_stats_inner(stats)


class _BloodrageDash(OrcPower):
    def __init__(self):
        super().__init__(
            name="Bloodrage Dash",
            source="Foe Foundry",
            icon="sprint",
            power_level=LOW_POWER,
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
            icon="striking-arrows",
            power_level=LOW_POWER,
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
            icon="fast-forward-button",
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
            icon="enrage",
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
            icon="totem-mask",
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
            icon="heart-burn",
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
            icon="thunder-struck",
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
            icon="snake-totem",
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
            icon="strong",
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


class _SanguineOffering(OrcPower):
    def __init__(self):
        super().__init__(
            name="Sanguine Offering",
            source="Foe Foundry",
            icon="cut-palm",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 3, 31),
            require_cr=1,
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[
                MonsterRole.Bruiser,
                MonsterRole.Soldier,
                MonsterRole.Artillery,
                MonsterRole.Ambusher,
                MonsterRole.Support,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        self_dmg_target = stats.target_value(dpr_proportion=0.2).average
        if self_dmg_target <= 4.0:
            self_dmg = max(1, round(self_dmg_target))
        else:
            self_dmg = easy_multiple_of_five(
                number=self_dmg_target, min_val=5, max_val=25
            )

        dmg = DieFormula.target_value(3.0 * self_dmg_target, force_die=Die.d6)

        feature = Feature(
            name="Sanguine Offering",
            description=f"{stats.selfref.capitalize()} deals {self_dmg} necrotic damage to itself. The next attack it makes this turn is made with advantage, and if the attack hits it deals an additional {dmg.description} necrotic damage.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _BloodkinBond(OrcPower):
    def __init__(self):
        # don't give this power to higher CR creatures unless they're defenders
        # it's silly for an awesome high-CR creature to just set itself to 1 hp unless it's explicitly a defender
        def is_valid(stats: BaseStatblock) -> bool:
            return is_orc(stats) and (
                MonsterRole.Defender in stats.additional_roles or stats.cr <= 5
            )

        super().__init__(
            name="Bloodkin Bond",
            source="Foe Foundry",
            icon="lovers",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 3, 31),
            require_callback=is_valid,
            require_roles=[
                MonsterRole.Defender,
                MonsterRole.Support,
                MonsterRole.Soldier,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(0.25 * stats.hp.average)
        feature = Feature(
            name="Bloodkin Bond",
            description=f"{stats.selfref.capitalize()} is ritually bound to protect an ally through its very blood. If the ally would suffer a lethal blow, {stats.selfref} prevents that damage. \
                Instead, {stats.selfref} drops to 1 HP, and the ally gains {temp_hp} temporary hit points.",
            action=ActionType.Feature,
            uses=1,
        )
        return [feature]


class _WarCryOfTheBloodiedFang(OrcPower):
    def __init__(self):
        super().__init__(
            name="War-Cry of the Bloodied Fang",
            source="Foe Foundry",
            icon="shouting",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 3, 31),
            require_cr=4,
            bonus_roles=[MonsterRole.Leader, MonsterRole.Soldier, MonsterRole.Bruiser],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(
            2 * stats.attributes.proficiency + 2 * stats.attributes.stat_mod(Stats.CHA)
        )
        feature = Feature(
            name="War-Cry of the Bloodied Fang",
            description=f"All bloodied Orcs within 30 feet gain {temp_hp} temporary hit points.",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


class _WarCryOfTheChillheart(OrcPower):
    def __init__(self):
        super().__init__(
            name="War-Cry of the Chillheart",
            source="Foe Foundry",
            icon="shouting",
            power_level=MEDIUM_POWER,
            create_date=datetime(2025, 3, 31),
            require_cr=4,
            bonus_roles=[MonsterRole.Leader, MonsterRole.Soldier, MonsterRole.Bruiser],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        frightened = conditions.Condition.Frightened.caption
        feature = Feature(
            name="War-Cry of the Chillheart",
            description=f"Once bloodied, {stats.selfref} releases a heart-chilling howl. Each non-orc creature within 60 feet must make a DC {dc} Wisdom save or become {frightened} (save ends at end of turn).",
            action=ActionType.BonusAction,
            uses=1,
        )
        return [feature]


AncestralGuidance: Power = _AncestralGuidance()
BloodburnTattoo: Power = _BloodburnTattoo()
Bloodfury: Power = _Bloodfury()
BloodkinBond: Power = _BloodkinBond()
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
SanguineOffering: Power = _SanguineOffering()
SpiritSeek: Power = _SpiritSneakTatoo()
ThunderwrathTattoo: Power = _ThunderwrathTatoo()
WarCryOfTheBloodiedFang: Power = _WarCryOfTheBloodiedFang()
WarCryOfTheChillheart: Power = _WarCryOfTheChillheart()


OrcPowers: List[Power] = [
    AncestralGuidance,
    Bloodfury,
    BloodrageDash,
    BloodrageBarrage,
    BloodrageBlow,
    BloodrageEndurance,
    EmpoweringTatoo,
    SavageMomentum,
    SanguineOffering,
    SpiritSeek,
    ThunderwrathTattoo,
    WarCryOfTheBloodiedFang,
    WarCryOfTheChillheart,
]
