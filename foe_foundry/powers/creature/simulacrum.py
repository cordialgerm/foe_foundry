from typing import List

from ...features import ActionType, Feature
from ...spells import abjuration, evocation, illusion
from ...statblocks import BaseStatblock
from ..power import Power
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
            reference_statblock="Simulacrum",
            **kwargs,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Illusory Reality",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} is hit by an attack, it fades out of existence and re-appears in an unoccupied location up to 15 feet away.",
        )

        return [feature]


SimulacrumSpellcasting: Power = _Simulacrum(
    name="Simulacrum Spellcasting", spells=SimulacrumSpells
)

SimulacrumPowers: List[Power] = [SimulacrumSpellcasting]
