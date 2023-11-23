from typing import List

from foe_foundry.features import Feature
from foe_foundry.powers.power_type import PowerType
from foe_foundry.statblocks import BaseStatblock

from ...creature_types import CreatureType
from ...damage import DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerType, PowerWithStandardScoring


class _Aquatic(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[CreatureType.Beast, CreatureType.Monstrosity, CreatureType.Humanoid],
            bonus_swimming=True,
            score_multiplier=0.5,
        )

        super().__init__(
            name="Aquatic",
            power_type=PowerType.Theme,
            source="SRD5.1 Merfolk",
            theme="Aquatic",
            power_level=LOW_POWER,
            score_args=score_args,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_speed = stats.speed.copy(swim=stats.speed.walk)
        new_senses = stats.senses.copy(darkvision=60)
        stats = stats.copy(speed=new_speed, senses=new_senses)
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Aquatic",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()} is aquatic and has a swim speed equal to its walk speed. It can also breathe underwater.",
        )
        return [feature]


class _InkCloud(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(require_swimming=True)

        super().__init__(
            name="Ink Cloud",
            power_type=PowerType.Theme,
            source="SRD5.1 Octopus",
            theme="Aquatic",
            power_level=LOW_POWER,
            score_args=score_args,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Ink Cloud",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} can emit a cloud of ink in a 10-foot-radius sphere while underwater. The area is heavily obscured for 1 minute unless dispersed by a strong current.",
        )
        return [feature]


class _SlimyCloud(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_swimming=True,
            require_types=[CreatureType.Aberration, CreatureType.Monstrosity],
            bonus_damage=DamageType.Poison,
            require_cr=3,
        )

        super().__init__(
            name="Slimy Cloud",
            power_type=PowerType.Theme,
            source="SRD5.1 Aboleth",
            theme="Aquatic",
            score_args=score_args,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = DieFormula.target_value(1.5 * stats.attack.average_damage)
        feature = Feature(
            name="Slimy Cloud",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.selfref.capitalize()} exudes a cloud of inky slime in a 30-ft radius sphere. \
                Each other creature in the area when the cloud appears or that starts its turn in the cloud must make a DC {dc} Constitution saving throw. \
                On a failure, it takes {dmg.description} poison damage and is **Poisoned** for 1 minute. \
                The slime extends around corners, and the area is heavily obscured for 1 minute or until a strong current dissipates the cloud.",
        )
        return [feature]


Aquatic: Power = _Aquatic()
InkCloud: Power = _InkCloud()
SlimyCloud: Power = _SlimyCloud()

AquaticPowers: List[Power] = [Aquatic, InkCloud, SlimyCloud]
