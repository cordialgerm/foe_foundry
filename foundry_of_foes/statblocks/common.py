from ..ac import ArmorClass
from ..attributes import Attributes, Stats
from ..damage import Attack, Damage, DamageType
from ..die import DieFormula
from ..movement import Movement
from .statblock import BaseStatblock

Minion = BaseStatblock(
    name="Minion",
    cr=1 / 8,
    ac=ArmorClass(value=11),
    hp=DieFormula.from_expression("2d8"),
    speed=Movement(walk=30),
    primary_attribute_score=12,
    attribute_backup_score=10,
    primary_attribute=Stats.DEX,
    attributes=Attributes(
        proficiency=2,
        primary_attribute=Stats.DEX,
        STR=10,
        DEX=12,
        CON=10,
        INT=10,
        WIS=12,
        CHA=10,
    ),
    multiattack=1,
    primary_damage_type=DamageType.Piercing,
    attack=Attack(
        name="Attack",
        hit=3,
        damage=Damage.from_expression("1d6 + 1", damage_type=DamageType.Piercing),
    ),
)

Soldier = BaseStatblock(
    name="Soldier",
    cr=1 / 2,
    ac=ArmorClass(value=12, description="leather armor or natural armor"),
    hp=DieFormula.from_expression("4d8 + 4"),
    speed=Movement(walk=30),
    primary_attribute_score=14,
    attribute_backup_score=10,
    primary_attribute=Stats.STR,
    attributes=Attributes(
        proficiency=2,
        primary_attribute=Stats.STR,
        STR=14,
        DEX=12,
        CON=12,
        INT=10,
        WIS=10,
        CHA=10,
    ),
    multiattack=1,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=4,
        damage=Damage.from_expression("1d12 + 2", damage_type=DamageType.Slashing),
    ),
)

Brute = BaseStatblock(
    name="Brute",
    cr=2,
    ac=ArmorClass(value=13, description="studded leather or natural armor"),
    hp=DieFormula.from_expression("7d8 + 14"),
    speed=Movement(walk=30),
    primary_attribute_score=16,
    attribute_backup_score=12,
    primary_attribute=Stats.STR,
    attributes=Attributes(
        proficiency=2,
        primary_attribute=Stats.STR,
        STR=16,
        DEX=12,
        CON=14,
        INT=10,
        WIS=10,
        CHA=8,
    ),
    multiattack=2,
    primary_damage_type=DamageType.Bludgeoning,
    attack=Attack(
        name="Attack",
        hit=5,
        damage=Damage.from_expression("1d12 + 3", damage_type=DamageType.Bludgeoning),
    ),
)


All = [Minion, Soldier, Brute]
AllNamed = [(Minion.name, Minion), (Soldier.name, Soldier), (Brute.name, Brute)]
