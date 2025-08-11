from foe_foundry import AbilityScore, Attributes, Skills


def test_attribute_modifiers():
    a = Attributes(
        STR=10,
        DEX=13,
        CON=16,
        WIS=20,
        CHA=8,
        INT=10,
        proficiency=2,
    )
    assert a.stat_mod(AbilityScore.STR) == 0
    assert a.stat_mod(AbilityScore.DEX) == 1
    assert a.stat_mod(AbilityScore.CON) == 3
    assert a.stat_mod(AbilityScore.WIS) == 5
    assert a.stat_mod(AbilityScore.CHA) == -1
    assert a.stat_mod(AbilityScore.INT) == 0


def test_attributes_generate_saves():
    a = Attributes(
        STR=10,
        DEX=13,
        CON=16,
        WIS=20,
        CHA=8,
        INT=10,
        proficiency=2,
        proficient_saves={AbilityScore.WIS, AbilityScore.CHA},
    )

    assert a.save_mod(AbilityScore.STR) is None
    assert a.save_mod(AbilityScore.WIS) == 7
    assert a.save_mod(AbilityScore.CHA) == 1

    assert {AbilityScore.WIS: 7, AbilityScore.CHA: 1} == a.saves


def test_attributes_generate_skills():
    a = Attributes(
        STR=10,
        DEX=13,
        CON=16,
        WIS=20,
        CHA=8,
        INT=10,
        proficiency=2,
        proficient_skills={
            Skills.Perception,
            Skills.Religion,
            Skills.Persuasion,
            Skills.Initiative,
        },
    )

    assert a.skill_mod(Skills.Perception) == 7
    assert a.skill_mod(Skills.Religion) == 2
    assert a.skill_mod(Skills.Persuasion) == 1
    assert a.skill_mod(Skills.Deception) is None
    assert a.skill_mod(Skills.Initiative) == 3

    assert {
        Skills.Perception: 7,
        Skills.Religion: 2,
        Skills.Persuasion: 1,
        Skills.Initiative: 3,
    } == a.skills


def test_attributes_infers_primary():
    a = Attributes(
        STR=10,
        DEX=13,
        CON=16,
        WIS=20,
        CHA=8,
        INT=10,
        proficiency=2,
        proficient_skills={Skills.Perception, Skills.Religion, Skills.Persuasion},
    )

    assert a.primary_attribute == AbilityScore.WIS
