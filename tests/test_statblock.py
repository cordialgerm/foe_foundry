import hashlib
from pathlib import Path

import numpy as np
import pytest

from foe_foundry import (
    AllCreatureTemplates,
    AllRoles,
    BaseStatblock,
    CreatureTypeTemplate,
    RoleTemplate,
    benchmark,
    general_use_stats,
    templates,
)


@pytest.mark.parametrize("n", range(3))
@pytest.mark.parametrize("role", [pytest.param(r, id=r.key) for r in AllRoles])
@pytest.mark.parametrize(
    "creature_template",
    [pytest.param(c, id=c.key) for c in AllCreatureTemplates if c],
)
@pytest.mark.parametrize(
    "base_stat", [pytest.param(s, id=s.key) for s in general_use_stats.All if s.cr >= 1]
)
def test_all_combinations(
    base_stat: BaseStatblock,
    creature_template: CreatureTypeTemplate,
    role: RoleTemplate,
    n: int,
):
    examples_dir = Path(__file__).parent.parent / "examples"
    examples_dir.mkdir(exist_ok=True)
    name = f"{base_stat.name}_{creature_template.name}_{role.name}_{n}"
    seed = _seed_for_text(name)
    path = examples_dir / (name + ".html")
    stats = creature_template.create(base_stat, role_template=role, rng_seed=seed)

    benchmarks = benchmark(stats)

    templates.render_html_inline_page(stats, path, benchmarks)


def _seed_for_text(text: str) -> int:
    bytes = hashlib.sha256(text.encode("utf-8")).digest()
    random_state = int.from_bytes(bytes)
    return random_state
