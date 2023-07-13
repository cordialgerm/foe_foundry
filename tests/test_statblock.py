import pytest

from foe_foundry import (
    AllCreatureTemplates,
    BaseStatblock,
    CreatureTypeTemplate,
    Power,
    RoleVariant,
    Statblock,
    all_role_variants,
    general_use_stats,
)
from foe_foundry.powers import (
    AberrationPowers,
    AttackPowers,
    BeastPowers,
    CelestialPowers,
    CommonPowers,
    ConstructPowers,
    MovementPowers,
    StaticPowers,
)


@pytest.mark.parametrize(
    "power",
    [
        pytest.param(p, id=p.key)
        for p in CommonPowers
        + StaticPowers
        + MovementPowers
        + AberrationPowers
        + AttackPowers
        + BeastPowers
        + CelestialPowers
        + ConstructPowers
    ],
)
@pytest.mark.parametrize(
    "role_variant", [pytest.param(r, id=r.key) for r in all_role_variants()]
)
@pytest.mark.parametrize(
    "creature_template", [pytest.param(t, id=t.key) for t in AllCreatureTemplates]
)
@pytest.mark.parametrize(
    "base_stat", [pytest.param(s, id=s.key) for s in general_use_stats.All]
)
def test_all_combinations(
    base_stat: BaseStatblock,
    creature_template: CreatureTypeTemplate,
    role_variant: RoleVariant,
    power: Power,
):
    with_creature_type = creature_template.apply(base_stat)
    with_role = role_variant.apply(with_creature_type)
    with_power, feature = power.apply(with_role)
    features = [feature]
    name = f"{base_stat.key}-{base_stat.creature_type}-{role_variant.key}-{power.name}"
    stats = Statblock.from_base_stats(name=name, stats=with_power, features=features)
