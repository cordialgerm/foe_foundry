from pathlib import Path

import pytest

from foe_foundry import (
    AllCreatureTemplates,
    AllRoles,
    BaseStatblock,
    CreatureTypeTemplate,
    RoleTemplate,
    general_use_stats,
    templates,
)


@pytest.mark.parametrize("n", range(1))
@pytest.mark.parametrize("role", [pytest.param(r, id=r.key) for r in AllRoles])
@pytest.mark.parametrize(
    "creature_template",
    [pytest.param(c, id=c.key) for c in AllCreatureTemplates],
)
@pytest.mark.parametrize(
    "base_stat", [pytest.param(s, id=s.key) for s in general_use_stats.All]
)
def test_all_combinations(
    base_stat: BaseStatblock,
    creature_template: CreatureTypeTemplate,
    role: RoleTemplate,
    n: int,
):
    examples_dir = Path(__file__).parent.parent / "examples"
    name = f"{base_stat.name}_{creature_template.name}_{role.name}_{n}"
    path = examples_dir / (name + ".html")
    stats = creature_template.create(base_stat, role_template=role)
    templates.render_html_inline_page(stats, path)
