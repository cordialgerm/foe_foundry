from typing import Callable, Dict, TypeAlias

import pytest

from foe_foundry import (
    BaseStatblock,
    CreatureTypeTemplate,
    Power,
    Statblock,
    all_creature_templates,
)
from foe_foundry import as_ambusher_all as ambusher
from foe_foundry import as_artillery_all as artillery
from foe_foundry import as_bruiser_all as bruiser
from foe_foundry import as_controller_all as controller
from foe_foundry import as_defender_all as defender
from foe_foundry import as_leader_all as leader
from foe_foundry import as_skirmisher_all as skirmisher
from foe_foundry import common_powers, general_use_stats

roles_all_variants = [ambusher, artillery, bruiser, controller, defender, leader, skirmisher]


@pytest.mark.parametrize("power", [pytest.param(p, id=p.key) for p in common_powers()])
@pytest.mark.parametrize("role_variants", roles_all_variants)
@pytest.mark.parametrize(
    "creature_template", [pytest.param(t, id=t.key) for t in all_creature_templates()]
)
@pytest.mark.parametrize(
    "base_stat", [pytest.param(s, id=s.key) for s in general_use_stats.All]
)
def test_all_combinations(
    base_stat: BaseStatblock,
    creature_template: CreatureTypeTemplate,
    role_variants: Callable[[BaseStatblock], Dict[str, BaseStatblock]],
    power: Power,
):
    with_creature_type = creature_template.apply(base_stat)
    with_roles = role_variants(with_creature_type)

    for variant, with_role in with_roles.items():
        with_power, feature = power.apply(with_role)
        features = [feature]
        name = f"{base_stat.name}-{base_stat.creature_type}-{variant}-{power.name}"
        stats = Statblock.from_base_stats(name=name, stats=with_power, features=features)
