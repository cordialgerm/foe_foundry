from foe_foundry_data.markdown import markdown


def test_markdown():
    text = "This is a **Wight** and these are [[Zombies]] and this is a button [[$Lich]] and this is **NOTHING IMPORTANT** and this is a statblock [[!Bandit]]"
    result = markdown(text)
    assert len(result.references) == 4


def test_necromancer_primagus():
    text = "This is a **Necromancer Primagus** and this is [[$Necromancer Primagus]] and [[!Necromancer Primagus]]"
    result = markdown(text)
    assert len(result.references) == 3


def test_cultist_fanatic():
    text = "This is a **Cultist Fanatic** and this is [[$Cultist-Fanatic]] and [[!Cultist_Fanatic]]"
    result = markdown(text)
    assert len(result.references) == 3


def test_aliases():
    text = "This is a **Cult Fanatic** and these are **Cult Fanatics**"
    result = markdown(text)
    assert len(result.references) == 2


def test_reference_power():
    text = "This is [[Pack Tactics]] and this is [[!Pack Tactics]]"
    result = markdown(text)
    assert len(result.references) == 2


def test_embed_power():
    text = "This is [[!Pack Tactics]]"
    result = markdown(text)
    assert len(result.references) == 1


def test_reference_statblock_with_species():
    text = "This is an [[Orc Bandit]]"
    result = markdown(text)
    assert len(result.references) == 1


def test_embed_statblock_with_species():
    text = "This is [[!Orc Berserker]]"
    result = markdown(text)
    assert len(result.references) == 1
    assert "Orc Berserker" in result.html
    assert 'data-monster="orc-berserker"' in result.html
    assert 'data-species="orc"' in result.html


def test_statblock_starts_with_species_name_but_isnt_species_templated():
    text = "This is an [[Orc Hardened One]]"
    result = markdown(text)
    assert len(result.references) == 1
    assert "orc-hardened-one" in result.html


def test_monster_key_works_as_well():
    text = "This is an [[orc-hardened-one]]"
    result = markdown(text)
    assert len(result.references) == 1
    assert "orc-hardened-one" in result.html


def test_monster_key_works_for_npcs():
    text = "This is an [[orc-berserker]]"
    result = markdown(text)
    assert len(result.references) == 1
    assert "orc-berserker" in result.html
