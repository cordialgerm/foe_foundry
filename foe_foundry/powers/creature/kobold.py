from datetime import datetime
from typing import List

from foe_foundry.references import Token, action_ref, creature_ref, feature_ref
from foe_foundry.utils import easy_multiple_of_five

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...skills import Stats
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring
from ..themed.breath import breath


def is_kobold(s: BaseStatblock) -> bool:
    return s.creature_class == "Kobold"


class KoboldPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = datetime(2025, 4, 9),
        **score_args,
    ):
        super().__init__(
            name=name,
            source=source,
            theme="kobold",
            reference_statblock="Kobold",
            power_level=power_level,
            power_type=PowerType.Creature,
            create_date=create_date,
            score_args=dict(
                require_callback=is_kobold,
                require_types=[CreatureType.Dragon],
            )
            | score_args,
        )


class _DraconicServants(KoboldPower):
    def __init__(self):
        super().__init__(
            name="Draconic Servants",
            source="Foe Foundry",
            power_level=LOW_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Draconic Servants",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} has resistance to the damage type of its draconic overlord (Fire, Cold, Lightning, Poison, or Acid). \
                Additionally, if {stats.selfref} is within 60 feet of a True Dragon then its attacks deal an additional 1d6 damage of that dragon's element.",
        )
        return [feature]


class _DraconicStandard(KoboldPower):
    def __init__(self):
        super().__init__(
            name="Draconic Standard",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        draconic_standard = Token(
            name="Draconic Standard", dc=stats.difficulty_class_token, charges=1
        )

        feature2 = breath(
            name="Aspirant's Breath",
            damage_type=DamageType.Force,
            stats=stats,
            save="Dexterity",
            verb="breathes draconic",
            damage_multiplier=1.5,  # should be notably higher than CR due to special conditions to active
            special_condition="When Draconic Standard Charged",
        )

        feature1 = Feature(
            name="Draconic Standard",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} reverently places its {draconic_standard.caption} in an unoccupied space within 5ft. \
                Whenever another Kobold dies within a 60ft emanation of the standard, its draconic zeal is absorbed by the standard, which gains 1 charge. \
                Whenever the standard has at least 5 charges, it grants all Kobolds within a 60 foot emanation the ability to use the {feature_ref(feature2.name)} as an Action at the cost of expending a charge",
        )

        return [feature1, feature2]


class _DraconicAscension(KoboldPower):
    def __init__(self):
        super().__init__(
            name="Draconic Ascension",
            source="Foe Foundry",
            power_level=MEDIUM_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        wyrmling = creature_ref("Red Dragon Wyrmling")
        temp_hp = easy_multiple_of_five(
            stats.attributes.stat_mod(Stats.CHA) + stats.attributes.proficiency * 2,
            min_val=5,
        )

        feature = Feature(
            name="Draconic Ascension",
            action=ActionType.Feature,
            description=f"Whenever another Kobold within 60 feet dies, {stats.selfref} rolls a d20. On a roll of a 20, the soul of the dying Kobold ascends into a True Dragon. \
                A wyrmling of the appropriate brood (such as a {wyrmling}) appears in the nearest unoccupied space. All Kobolds within 60 feet also gain {temp_hp} temporary hit points.",
        )
        return [feature]


class _ScurryingFormation(KoboldPower):
    def __init__(self):
        super().__init__(
            name="Scurrying Formation",
            source="Foe Foundry",
            power_level=LOW_POWER,
            require_roles=MonsterRole.Soldier,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Scurrying Formation",
            action=ActionType.BonusAction,
            description=f"{stats.selfref.capitalize()} climbs up the back of an ally within 5 feet and jumps up to 10 feet. If it lands within 5 feet of an enemy, it makes an attack with advantage against that enemy.",
        )
        return [feature]


class _FalseRetreat(KoboldPower):
    def __init__(self):
        super().__init__(
            name="False Retreat",
            source="Foe Foundry",
            power_level=LOW_POWER,
            require_roles=MonsterRole.Soldier,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        prone = Condition.Prone.caption
        disengage = action_ref("Disengage")
        feature = Feature(
            name="False Retreat",
            action=ActionType.Action,
            description=f"{stats.selfref.capitalize()} uses {disengage}. It also secretly places a hidden caltrop. \
                If an enemy moves over the caltrop, it must make a DC {dc} Dexterity saving throw, taking 1d4 piercing damage on a failure and falling {prone}.",
        )
        return [feature]


DraconicServants: Power = _DraconicServants()
DraconicStandard: Power = _DraconicStandard()
DraconicAscension: Power = _DraconicAscension()
ScurryingFormation: Power = _ScurryingFormation()
FalseRetreat: Power = _FalseRetreat()

KoboldPowers: list[Power] = [
    DraconicServants,
    DraconicStandard,
    DraconicAscension,
    FalseRetreat,
    ScurryingFormation,
]
