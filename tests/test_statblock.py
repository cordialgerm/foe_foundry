from typing import Callable, Dict, TypeAlias

import pytest

from foundry_of_foes import BaseStatblock
from foundry_of_foes import as_aberration as aberration
from foundry_of_foes import as_ambusher_all as ambusher
from foundry_of_foes import as_artillery_all as artillery
from foundry_of_foes import as_bruiser_all as bruiser
from foundry_of_foes import as_controller_all as controller
from foundry_of_foes import as_defender_all as defender
from foundry_of_foes import as_leader_all as leader
from foundry_of_foes import as_skirmisher_all as skirmisher
from foundry_of_foes import general_use_stats

StatCallable: TypeAlias = Callable[[BaseStatblock], BaseStatblock]

roles_all_variants = [ambusher, artillery, bruiser, controller, defender, leader, skirmisher]
monster_types = [aberration]


@pytest.mark.parametrize("role_variants", roles_all_variants)
@pytest.mark.parametrize("monster_type", monster_types)
@pytest.mark.parametrize("name", general_use_stats.Names)
def test_minion(
    name: str,
    monster_type: StatCallable,
    role_variants: Callable[[BaseStatblock], Dict[str, BaseStatblock]],
):
    base_stats = general_use_stats.get_named_stats(name)
    monster = monster_type(base_stats)
    variants = role_variants(monster)
