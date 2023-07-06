from foundry_of_foes.damage import Attack, Damage


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
