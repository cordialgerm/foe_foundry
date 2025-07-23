from foe_foundry import AbilityScore, Skills


def test_all_stats():
    assert len(AbilityScore.All()) == 6


def test_all_skills():
    assert len(Skills.All()) == 19


def test_get_stat_from_skill():
    for skill in Skills.All():
        assert skill.stat is not None
