from ..ac import ArmorClass
from ..attributes import Attributes, Skills, Stats
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

Specialist = BaseStatblock(
    name="Specialist",
    cr=4,
    ac=ArmorClass(value=14),
    hp=DieFormula.from_expression("13d8 + 26"),
    speed=Movement(walk=30),
    primary_attribute_score=18,
    attribute_backup_score=14,
    primary_attribute=Stats.DEX,
    attributes=Attributes(
        proficiency=2,
        primary_attribute=Stats.DEX,
        STR=12,
        DEX=18,
        CON=14,
        INT=10,
        WIS=14,
        CHA=12,
        proficient_skills={Skills.Acrobatics, Skills.Perception, Skills.Stealth},
        proficient_saves={Stats.DEX, Stats.WIS},
    ),
    multiattack=3,
    primary_damage_type=DamageType.Piercing,
    attack=Attack(
        name="Attack",
        hit=6,
        damage=Damage.from_expression("3d6 + 4", damage_type=DamageType.Piercing),
    ),
)

Myrmidon = BaseStatblock(
    name="Myrmidon",
    cr=7,
    ac=ArmorClass(value=15, description="chain shirt or natural armor"),
    hp=DieFormula.from_expression("20d8 + 40"),
    speed=Movement(walk=30),
    primary_attribute_score=18,
    attribute_backup_score=14,
    primary_attribute=Stats.INT,
    attributes=Attributes(
        proficiency=3,
        primary_attribute=Stats.INT,
        STR=10,
        DEX=14,
        CON=14,
        INT=18,
        WIS=14,
        CHA=10,
        proficient_saves={Stats.DEX, Stats.WIS},
        proficient_skills={Skills.Perception},
    ),
    multiattack=3,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=7,
        damage=Damage.from_expression("3d8 + 4", damage_type=DamageType.Slashing),
    ),
)

Sentinel = BaseStatblock(
    name="Sentinel",
    cr=11,
    ac=ArmorClass(value=17, description="natural armor or magical protection"),
    hp=DieFormula.from_expression("22d8 + 66"),
    speed=Movement(walk=30),
    primary_attribute_score=20,
    attribute_backup_score=16,
    primary_attribute=Stats.STR,
    attributes=Attributes(
        proficiency=4,
        primary_attribute=Stats.STR,
        STR=20,
        DEX=16,
        CON=16,
        INT=10,
        WIS=14,
        CHA=10,
    ),
    multiattack=4,
    primary_damage_type=DamageType.Bludgeoning,
    attack=Attack(
        name="Attack",
        hit=9,
        damage=Damage.from_expression("3d8 + 5", damage_type=DamageType.Bludgeoning),
    ),
)

Champion = BaseStatblock(
    name="Champion",
    cr=15,
    ac=ArmorClass(value=19, description="natural armor or magical protection"),
    hp=DieFormula.from_expression("25d8 + 100"),
    speed=Movement(walk=30),
    primary_attribute_score=22,
    attribute_backup_score=16,
    primary_attribute=Stats.CHA,
    attributes=Attributes(
        proficiency=5,
        primary_attribute=Stats.CHA,
        STR=10,
        DEX=12,
        CON=18,
        INT=12,
        WIS=16,
        CHA=22,
    ),
    multiattack=4,
    primary_damage_type=DamageType.Slashing,
    attack=Attack(
        name="Attack",
        hit=11,
        damage=Damage.from_expression("4d8 + 6", damage_type=DamageType.Slashing),
    ),
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
Named = {s.name: s for s in All}


def get_named_stats(name: str) -> BaseStatblock:
    return Named[name]
