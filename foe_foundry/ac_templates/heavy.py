from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..statblocks.base import BaseStatblock


class _HeavyArmor(ArmorClassTemplate):
    def __init__(self, name: str, base_ac: int):
        self._name = name
        self._base_ac = base_ac

    @property
    def name(self) -> str:
        return self._name

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return True

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        quality_level = min(max(stats.ac_boost, 0), 3)
        ac = self._base_ac + (2 if uses_shield else 0) + quality_level

        if quality_level > 0:
            text = f"{self.name} +{quality_level}"
        else:
            text = self.name

        return ResolvedArmorClass(
            value=ac,
            armor_type=text,
            has_shield=uses_shield,
            is_armored=True,
            quality_level=quality_level,
            score=ac + 0.5 - (1000 if stats.attributes.STR < 15 else 0),
        )


PlateArmor: ArmorClassTemplate = _HeavyArmor("Plate Armor", 18)
SplintArmor: ArmorClassTemplate = _HeavyArmor("Splint Armor", 17)
ChainmailArmor: ArmorClassTemplate = _HeavyArmor("Chainmail Armor", 16)
