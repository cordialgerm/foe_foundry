from foe_foundry import Attack, Damage, DamageType


def test_attack_delta():
    a = Attack(name="Attack", hit=3, damage=Damage.from_expression("1d6 + 1"))

    a2 = a.delta(hit_delta=1)
    assert a2.hit == 4

    a3 = a.delta(dice_delta=1)
    assert a3.damage.formula.dice_formula() == "2d6 + 1"

    a4 = a.delta(damage_delta=1)
    assert a4.damage.formula.dice_formula() == "1d6 + 2"

    a5 = a.delta(dice_delta=3, damage_delta=-1)
    assert a5.damage.formula.dice_formula() == "4d6 - 3"  # 1d6 + 1 + 3d6 + -1 *4


def test_attack_split_damage_one_die_too_small():
    a = Attack(name="Attack", hit=3, damage=Damage.from_expression("1d4 + 2"))
    a2 = a.split_damage(secondary_damage_type=DamageType.Poison)
    assert a2.description == a.description  # no change because die is too small to split


def test_attack_split_damage_one_die():
    a = Attack(name="Attack", hit=3, damage=Damage.from_expression("1d6 + 2"))
    a2 = a.split_damage(secondary_damage_type=DamageType.Poison)
    assert a2.average_damage == 7  # 1d4 + 2 bludgeoning and 1d4 poison = 2.5 + 2 + 2.5 = 7


def test_attack_split_damage_many_die():
    a = Attack(name="Attack", hit=7, damage=Damage.from_expression("3d6 + 8"))
    a2 = a.split_damage(DamageType.Necrotic)
    assert (
        a2.average_damage == 18.5
    )  # 2d6 + 8 bludgeoning and 1d6 necrotic = 2 * 3.5 + 8 + 3.5 = 18.5
