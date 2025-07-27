from datetime import datetime
from typing import List

from ...features import ActionType, Feature
from ...power_types import PowerType
from ...spells import abjuration, evocation, illusion
from ...statblocks import BaseStatblock
from ..power import Power, PowerCategory, PowerWithStandardScoring
from ..spellcaster.base import WizardPower
from ..spellcaster.utils import spell_list

_spells = [
    abjuration.Banishment,
    evocation.WallOfForce,
    evocation.ConeOfCold,
    evocation.LightningBolt,
    evocation.ChainLightning,
    illusion.MajorImage,
    illusion.GreaterInvisibility,
    abjuration.DispelMagic,
]

SimulacrumSpells = spell_list(spells=_spells, uses=1)


class _Simulacrum(WizardPower):
    def __init__(self, **kwargs):
        super().__init__(
            creature_name="Simulacrum",
            theme="simulacrum",
            icon="relationship-bounds",
            reference_statblock="Simulacrum",
            power_types=[PowerType.Magic, PowerType.Movement],
            **kwargs,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Illusory Nature",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} is hit by an attack, it fades out of existence and re-appears in an unoccupied location up to 15 feet away.",
        )

        return [feature]


class _MirrorbladeSimulacrum(PowerWithStandardScoring):
    def __init__(
        self,
        **score_args,
    ):
        super().__init__(
            name="Mirrorblade Simulacrum",
            source="Foe Foundry",
            power_types=[PowerType.Movement, PowerType.Magic],
            create_date=datetime(2025, 7, 25),
            power_category=PowerCategory.Creature,
            icon="sword-spin",
            theme="simulacrum",
            reference_statblock="Simulacrum Mirrorblade",
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Illusory Reality",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} is hit by an attack, it fades out of existence and re-appears in an unoccupied location up to 15 feet away.",
        )

        dc = stats.difficulty_class

        feature2 = Feature(
            name="Shred Space",
            action=ActionType.BonusAction,
            recharge=4,
            description=f"Immediately after hitting a creature with an attack, {stats.selfref} forces the creature to make a DC {dc} Charisma save. On a failure, the creature is teleported to an unoccupied space on the ground or floor up to 60 feet away.",
        )

        return [feature1, feature2]


SimulacrumSpellcasting: Power = _Simulacrum(
    name="Simulacrum Spellcasting", spells=SimulacrumSpells
)
SimulacrumMirrorblade: Power = _MirrorbladeSimulacrum()

SimulacrumPowers: List[Power] = [SimulacrumSpellcasting, SimulacrumMirrorblade]
