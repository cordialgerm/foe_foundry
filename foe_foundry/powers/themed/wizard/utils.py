from typing import List, Set

from ....spells import Spell, StatblockSpell


def spell_list(
    spells: List[Spell], uses: int, exclude: Set[Spell] | None = None
) -> List[StatblockSpell]:
    exclude = exclude if exclude is not None else set()
    l = [s.for_statblock(uses=uses if not s.upcast else 1) for s in spells if s not in exclude]
    return sorted(l, key=lambda s: s.name)
