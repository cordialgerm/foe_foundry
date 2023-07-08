from typing import Callable, Dict, TypeAlias

import pytest

from foe_foundry import BaseStatblock
from foe_foundry import as_aberration as aberration
from foe_foundry import as_ambusher_all as ambusher
from foe_foundry import as_artillery_all as artillery
from foe_foundry import as_bruiser_all as bruiser
from foe_foundry import as_controller_all as controller
from foe_foundry import as_defender_all as defender
from foe_foundry import as_leader_all as leader
from foe_foundry import as_skirmisher_all as skirmisher
from foe_foundry import general_use_stats

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
