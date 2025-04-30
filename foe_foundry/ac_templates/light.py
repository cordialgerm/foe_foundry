from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..attributes import Stats
from ..statblocks.base import BaseStatblock


class _LightArmor(ArmorClassTemplate):
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
        quality_level = stats.ac_boost
        ac = (
            self._baseline_ac
            + min(stats.attributes.stat_mod(Stats.DEX), 5)
            + quality_level
            + (2 if uses_shield else 0)
        )

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
            quality_level=quality_level,
            score=ac + 0.2,
        )


LeatherArmor: ArmorClassTemplate = _LightArmor("Leather Armor", 11)
StuddedLeatherArmor: ArmorClassTemplate = _LightArmor("Studded Leather Armor", 12)
