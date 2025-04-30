from foe_foundry import Skills, Stats


def test_all_stats():
    assert len(Stats.All()) == 6


def test_all_skills():
    assert len(Skills.All()) == 19


def test_get_stat_from_skill():
    for skill in Skills.All():
        assert skill.stat is not None
