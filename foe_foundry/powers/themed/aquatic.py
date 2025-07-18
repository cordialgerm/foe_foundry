from typing import List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...statblocks import BaseStatblock
from ..power import RIBBON_POWER, Power, PowerCategory, PowerWithStandardScoring


class AquaticBase(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        source: str,
        icon: str,
        power_level: float = RIBBON_POWER,
        power_types: List[PowerType] | None = None,
        **args,
    ):
        def not_already_special_movement(c: BaseStatblock) -> bool:
            return not c.has_unique_movement_manipulation

        score_args = (
            dict(
                require_callback=not_already_special_movement,
                require_swimming=True,
            )
            | args
        )

        super().__init__(
            name=name,
            power_category=PowerCategory.Theme,
            theme="Aquatic",
            reference_statblock="Merfolk",
            icon=icon,
            source=source,
            power_level=power_level,
            score_args=score_args,
            power_types=power_types or [PowerType.Movement],
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(swim=stats.speed.walk)
        new_senses = stats.senses.copy(darkvision=60)
        stats = stats.copy(
            speed=new_speed, senses=new_senses, has_unique_movement_manipulation=True
        )
        return stats


class _Aquatic(AquaticBase):
    def __init__(self):
        super().__init__(name="Aquatic", source="SRD5.1 Merfolk", icon="triton-head")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Aquatic",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is aquatic and has a swim speed equal to its walk speed. It can also breathe underwater.",
        )
        return [feature]


class _Amphibious(AquaticBase):
    def __init__(self):
        super().__init__(name="Amphibious", source="SRD5.1 Merfolk", icon="triton-head")

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Amphibious",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} can breathe air and underwater.",
        )
        return [feature]


class _InkCloud(AquaticBase):
    def __init__(self):
        super().__init__(
            name="Ink Cloud",
            icon="octopus",
            source="SRD5.1 Octopus",
            power_level=RIBBON_POWER,
            power_types=[PowerType.AreaOfEffect, PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Ink Cloud",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} can emit a cloud of ink in a 10-foot-radius sphere while underwater. The area is heavily obscured for 1 minute unless dispersed by a strong current.",
        )
        return [feature]


class _SlimyCloud(AquaticBase):
    def __init__(self):
        super().__init__(
            name="Slimy Cloud",
            source="SRD5.1 Aboleth",
            icon="transparent-slime",
            require_types=[CreatureType.Aberration, CreatureType.Monstrosity],
            bonus_damage=DamageType.Poison,
            require_cr=3,
            power_types=[PowerType.AreaOfEffect, PowerType.Debuff, PowerType.Attack],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(target=1.5)
        poisoned = Condition.Poisoned
        feature = Feature(
            name="Slimy Cloud",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} exudes a cloud of inky slime in a 30-ft radius sphere. \
                Each other creature in the area when the cloud appears or that starts its turn in the cloud must make a DC {dc} Constitution saving throw. \
                On a failure, it takes {dmg.description} poison damage and is {poisoned.caption} for 1 minute. \
                The slime extends around corners, and the area is heavily obscured for 1 minute or until a strong current dissipates the cloud.",
        )
        return [feature]


Amphibious: Power = _Amphibious()
Aquatic: Power = _Aquatic()
InkCloud: Power = _InkCloud()
SlimyCloud: Power = _SlimyCloud()

AquaticPowers: List[Power] = [Amphibious, Aquatic, InkCloud, SlimyCloud]
