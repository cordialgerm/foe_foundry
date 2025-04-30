from foe_foundry.spells.transmutation import EnlargeReduce


def test_override_concentration():
    spell = EnlargeReduce.copy(concentration=False)
    spell_for_statblock = spell.for_statblock()
    assert spell_for_statblock.concentration_overriden
    assert "\u023b" in spell_for_statblock.caption_md


def test_equality_based_on_name():
    spell1 = EnlargeReduce.copy()
    spell2 = EnlargeReduce.copy()
    spell3 = EnlargeReduce.copy(concentration=False)

    assert spell1 == spell2
    assert spell1 == spell3
    assert spell2 == spell3


def test_statblock_spell_equality_based_on_name():
    spell1 = EnlargeReduce.copy().for_statblock(concentration=False)
    spell2 = EnlargeReduce.copy().for_statblock()

    assert spell1 == spell2
