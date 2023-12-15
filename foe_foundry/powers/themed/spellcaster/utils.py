from typing import List, Set

from ....spells import Spell, StatblockSpell


def spell_list(
    spells: List[Spell],
    uses: int,
    exclude: Set[Spell] | None = None,
    mark_schools: Set[str] | None = None,
) -> List[StatblockSpell]:
    exclude = exclude if exclude is not None else set()
    mark_schools = mark_schools if mark_schools is not None else set()

    unsorted = []
    for s in spells:
        if s in exclude:
            continue
        symbols = "\\*" if s.school in mark_schools else None
        unsorted.append(s.for_statblock(uses=uses, symbols=symbols))

    return sorted(unsorted, key=lambda s: s.name)
