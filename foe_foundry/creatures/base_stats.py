from functools import cached_property

from ..attributes import Attributes, proficiency_bonus_for_cr
from ..benchmarks.fof import FoFBenchmark
from ..damage import Attack, Damage, DamageType
from ..die import DieFormula
from ..movement import Movement
from ..skills import Stats, StatScaler, StatScaling
from ..statblocks import BaseStatblock


class _Loader:
    @cached_property
    def benchmark(self) -> FoFBenchmark:
        return FoFBenchmark()


loader = _Loader()


def base_stats(
    *,
    name: str,
    template_key: str,
    variant_key: str,
    monster_key: str,
    species_key: str | None = None,
    cr: float,
    stats: list[StatScaler],
    hp_multiplier: float = 1.0,
    damage_multiplier: float = 1.0,
) -> BaseStatblock:
    benchmark = loader.benchmark
    expected_hp = benchmark.benchmark_hp(cr)
    expected_attacks = benchmark.benchmark_attacks(cr)
    expected_attack_damage_int = benchmark.benchmark_attack_damage(cr)
    expected_attack_damage = expected_attack_damage_int + 0.5
    expected_hit = benchmark.benchmark_hit(cr)
    proficiency = proficiency_bonus_for_cr(cr)

    # default CON modifiers
    stat_vals = {
        Stats.CON: int(Stats.CON.scaler(StatScaling.Constitution).scale(cr)),
    }
    for stat in stats:
        stat_vals[stat.stat] = int(stat.scale(cr))

    attributes = Attributes(proficiency=proficiency, **stat_vals)  # type: ignore
    hp = DieFormula.target_value(
        target=hp_multiplier * expected_hp,
        per_die_mod=attributes.stat_mod(Stats.CON),
    )

    attack_damage = damage_multiplier * expected_attack_damage
    attack_damage_int = int(attack_damage)

    return BaseStatblock(
        name=name,
        template_key=template_key,
        variant_key=variant_key,
        monster_key=monster_key,
        species_key=species_key,
        cr=cr,
        hp=hp,
        speed=Movement(walk=30),
        primary_attribute_score=attributes.primary_attribute_score,
        attributes=attributes,
        multiattack=expected_attacks,
        multiattack_benchmark=expected_attacks,
        attack=Attack(
            name="Attack",
            hit=expected_hit,
            damage=Damage.from_expression(
                f"{attack_damage_int}", damage_type=DamageType.Bludgeoning
            ),
        ),
        base_attack_damage=attack_damage,
    )
