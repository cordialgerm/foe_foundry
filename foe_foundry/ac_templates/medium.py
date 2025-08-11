from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import AbilityScore
from ..statblocks.base import BaseStatblock


def _medium_armor_ac(stats: BaseStatblock, baseline_ac: int, uses_shield: bool) -> int:
    quality_level = stats.ac_boost
    ac = (
        baseline_ac
        + max(0, min(stats.attributes.stat_mod(AbilityScore.DEX), 2))
        + quality_level
        + (2 if uses_shield else 0)
    )
    return ac


class _MediumArmor(ArmorClassTemplate):
    def __init__(self, name: str, baseline_ac: int):
        self._name = name
        self._baseline_ac = baseline_ac

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        ac = _medium_armor_ac(stats, self._baseline_ac, uses_shield)

        quality_level = max(stats.ac_boost, 0)
        if quality_level > 0:
            text = f"{self._name} +{quality_level}"
        else:
            text = self._name

        return ResolvedArmorClass(
            value=ac,
            armor_type=text,
            has_shield=uses_shield,
            is_armored=True,
            display_detail=True,
            quality_level=stats.ac_boost,
            score=ac + 0.3,
        )


HideArmor: ArmorClassTemplate = _MediumArmor("Hide Armor", 12)
ChainShirt: ArmorClassTemplate = _MediumArmor("Chain Shirt", 13)
Breastplate: ArmorClassTemplate = _MediumArmor("Breastplate", 14)
PatchworkArmor: ArmorClassTemplate = _MediumArmor("Patchwork Armor", 14)
