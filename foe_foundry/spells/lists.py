## Diviner Spell List
## greater invisibility


from typing import List

from . import conjuration, divination, enchantment, evocation, illusion, transmutation
from .spell import Spell, StatblockSpell


def spell_list(spells: List[Spell], uses: int) -> List[StatblockSpell]:
    l = [s.for_statblock(uses=uses if not s.upcast else 1) for s in spells]
    return sorted(l, key=lambda s: s.name)


_DivinationAdept = [
    divination.DetectMagic,
    divination.DetectThoughts,
    divination.ArcaneEye,
    illusion.Invisibility,
    enchantment.HoldPerson,
    transmutation.Fly,
]
_DivinationMaster = [
    evocation.LightningBolt,
    divination.Scrying,
    illusion.GreaterInvisibility,
]
_DivinationExpert = [conjuration.Maze, divination.Foresight]

DivinationAdept = spell_list(_DivinationAdept, uses=1)
DivinationMaster = spell_list(_DivinationAdept, uses=2) + spell_list(_DivinationMaster, uses=1)
DivinationExpert = (
    spell_list(_DivinationAdept, uses=3)
    + spell_list(_DivinationMaster, uses=2)
    + spell_list(_DivinationExpert, uses=1)
)
