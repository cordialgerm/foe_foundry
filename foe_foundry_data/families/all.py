from functools import cached_property

from .data import MonsterFamilyModel
from .load import load_families as load_families_core


class _Cache:
    @cached_property
    def all_monster_families(self) -> list[MonsterFamilyModel]:
        return load_families_core()


_cache = _Cache()


def load_families() -> list[MonsterFamilyModel]:
    """
    Loads all monster families from the data files.

    Returns:
        list[MonsterFamilyModel]: A list of all loaded monster families.
    """
    return _cache.all_monster_families
