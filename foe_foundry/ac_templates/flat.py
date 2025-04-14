from ..ac import ArmorClassTemplate, ResolvedArmorClass
from ..statblocks.base import BaseStatblock


class _FlatAmorClassTemplate(ArmorClassTemplate):
    def __init__(self, ac: int):
        self.ac = ac

    @property
    def name(self) -> str:
        return "Flat"

    @property
    def is_armored(self) -> bool:
        return True

    @property
    def is_heavily_armored(self) -> bool:
        return False

    def resolve(self, stats: BaseStatblock, uses_shield: bool) -> ResolvedArmorClass:
        return ResolvedArmorClass(
            value=self.ac,
            armor_type="Flat",
            has_shield=uses_shield,
            is_armored=True,
            quality_level=0,
            score=self.ac,
        )


def flat(ac: int) -> ArmorClassTemplate:
    return _FlatAmorClassTemplate(ac)
