from ..attributes import Attributes
from ..damage import Attack, Damage, DamageType
from ..die import DieFormula
from ..movement import Movement
from .base import BaseStatblock

Minion = BaseStatblock(
    name="Minion",
    cr=1 / 8,
    hp=DieFormula.from_expression("2d8"),
    speed=Movement(walk=30),
    primary_attribute_score=12,
    attributes=Attributes(
        proficiency=2,
        STR=10,
        DEX=12,
        CON=10,
        INT=10,
        WIS=12,
        CHA=10,
    ),
    multiattack=1,
    multiattack_benchmark=1,
    primary_damage_type=DamageType.Piercing,
    attack=Attack(
        name="Attack",
        hit=3,
        damage=Damage.from_expression("4", damage_type=DamageType.Piercing),
    ),
    base_attack_damage=4,
)

Soldier = BaseStatblock(
    name="Soldier",
    cr=1 / 2,
    hp=DieFormula.from_expression("4d8 + 4"),
    speed=Movement(walk=30),
    primary_attribute_score=14,
    attributes=Attributes(
        proficiency=2,
        STR=14,
        DEX=12,
        CON=12,
        INT=10,
        WIS=10,
        CHA=10,
    ),
    multiattack=1,
    multiattack_benchmark=1,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=4,
        damage=Damage.from_expression("8", damage_type=DamageType.Slashing),
    ),
    base_attack_damage=8,
)

Brute = BaseStatblock(
    name="Brute",
    cr=2,
    hp=DieFormula.from_expression("7d8 + 14"),
    speed=Movement(walk=30),
    primary_attribute_score=16,
    attributes=Attributes(
        proficiency=2,
        STR=16,
        DEX=12,
        CON=14,
        INT=10,
        WIS=10,
        CHA=8,
    ),
    multiattack=2,
    multiattack_benchmark=2,
    primary_damage_type=DamageType.Bludgeoning,
    attack=Attack(
        name="Attack",
        hit=5,
        damage=Damage.from_expression("9", damage_type=DamageType.Bludgeoning),
    ),
    base_attack_damage=9,
)

Specialist = BaseStatblock(
    name="Specialist",
    cr=4,
    hp=DieFormula.from_expression("13d8 + 26"),
    speed=Movement(walk=30),
    primary_attribute_score=18,
    attributes=Attributes(
        proficiency=2,
        STR=12,
        DEX=18,
        CON=14,
        INT=10,
        WIS=14,
        CHA=12,
    ),
    multiattack=2,
    multiattack_benchmark=2,
    primary_damage_type=DamageType.Piercing,
    attack=Attack(
        name="Attack",
        hit=6,
        damage=Damage.from_expression("14", damage_type=DamageType.Piercing),
    ),
    base_attack_damage=14,
)

Myrmidon = BaseStatblock(
    name="Myrmidon",
    cr=7,
    hp=DieFormula.from_expression("20d8 + 40"),
    speed=Movement(walk=30),
    primary_attribute_score=18,
    attributes=Attributes(
        proficiency=3,
        STR=10,
        DEX=14,
        CON=14,
        INT=18,
        WIS=14,
        CHA=10,
    ),
    multiattack=3,
    multiattack_benchmark=3,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=7,
        damage=Damage.from_expression("17", damage_type=DamageType.Slashing),
    ),
    base_attack_damage=17,
)

Sentinel = BaseStatblock(
    name="Sentinel",
    cr=11,
    ac_boost=1,
    hp=DieFormula.from_expression("22d8 + 66"),
    speed=Movement(walk=30),
    primary_attribute_score=20,
    attributes=Attributes(
        proficiency=4,
        STR=20,
        DEX=16,
        CON=16,
        INT=10,
        WIS=14,
        CHA=10,
    ),
    multiattack=4,
    multiattack_benchmark=4,
    primary_damage_type=DamageType.Bludgeoning,
    attack=Attack(
        name="Attack",
        hit=9,
        damage=Damage.from_expression("18", damage_type=DamageType.Bludgeoning),
    ),
    base_attack_damage=18,
)

Champion = BaseStatblock(
    name="Champion",
    cr=15,
    ac_boost=2,
    hp=DieFormula.from_expression("25d8 + 100"),
    speed=Movement(walk=30),
    primary_attribute_score=22,
    attributes=Attributes(
        proficiency=5,
        STR=10,
        DEX=12,
        CON=18,
        INT=12,
        WIS=16,
        CHA=22,
    ),
    multiattack=4,
    multiattack_benchmark=4,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=11,
        damage=Damage.from_expression("24", damage_type=DamageType.Slashing),
    ),
    base_attack_damage=24,
)


All = [
    Minion,
    Soldier,
    Brute,
    Specialist,
    Myrmidon,
    Sentinel,
    Champion,
]
Names = [s.name for s in All]
Named = {s.name.lower(): s for s in All}


def get_named_stats(name: str) -> BaseStatblock:
    s = Named.get(name.lower(), None)
    if s is None:
        raise ValueError(f"No commmon statblock named '{name}'")
    return s


def get_stats_by_cr(cr: float | int) -> BaseStatblock:
    return next((s for s in All if s.cr >= cr), All[-1])


def get_common_stats(name_or_cr: str | float | int) -> BaseStatblock:
    if isinstance(name_or_cr, (float, int)):
        return get_stats_by_cr(cr=name_or_cr)
    else:
        try:
            cr = float(name_or_cr)
            return get_common_stats(name_or_cr=cr)
        except ValueError:
            return get_named_stats(name_or_cr)
