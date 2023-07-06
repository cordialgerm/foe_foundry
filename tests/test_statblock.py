from foundry_of_foes.attributes import Attributes, Stats
from foundry_of_foes.damage import Attack, Damage, DamageType
from foundry_of_foes.die import DieFormula
from foundry_of_foes.statblock import ArmorClass, BaseStatblock, MonsterDials, Movement


def test_minion():
    minion = BaseStatblock(
        name="Minion",
        cr=1 / 8,
        ac=ArmorClass(value=11),
        hp=DieFormula.from_expression("2d8"),
        speed=Movement(walk=30),
        primary_attribute_score=12,
        primary_attribute=Stats.DEX,
        attributes=Attributes(proficiency=2, STR=10, DEX=12, CON=10, INT=10, WIS=12, CHA=10),
        multiattack=1,
        primary_damage_type=DamageType.Piercing,
        attack=Attack(
            name="Attack",
            hit=3,
            damage=Damage.from_expression("1d6 + 1", damage_type=DamageType.Piercing),
        ),
    )

    ## as ambusher
    dials = [MonsterDials(ac_modifier=-2), MonsterDials(hp_multiplier=0.8)]
    ambusher1 = minion.apply_monster_dials(dials[0])
    ambusher2 = minion.apply_monster_dials(dials[1])

    ## as artillery
    dials = [
        MonsterDials(attack_hit_modifier=2, ac_modifier=-2),
        MonsterDials(attack_hit_modifier=2, hp_multiplier=0.8),
        MonsterDials(attack_hit_modifier=1, attack_damage_dice_modifier=1, ac_modifier=-2),
        MonsterDials(attack_hit_modifier=1, attack_damage_dice_modifier=1, hp_multiplier=0.8),
    ]
    artillery1 = minion.apply_monster_dials(dials[0])
    artillery2 = minion.apply_monster_dials(dials[1])
    artillery3 = minion.apply_monster_dials(dials[2])
    artillery4 = minion.apply_monster_dials(dials[3])
