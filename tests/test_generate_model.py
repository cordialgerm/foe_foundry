import numpy as np

from foe_foundry_data.generate import generate_monster
from foe_foundry_data.refs import MonsterRefResolver


def test_generate_orc():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("orc-druid", ref_resolver=ref_resolver, rng=rng)
    assert ref is not None
    assert stats is not None
    assert stats.name == "Orc Druid"


def test_generate_dwarf():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("dwarf-guard", ref_resolver=ref_resolver, rng=rng)
    assert ref is not None
    assert stats is not None
    assert stats.name == "Dwarf Guard"


def test_generate_gnome():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("gnome-priest", ref_resolver=ref_resolver, rng=rng)
    assert ref is not None
    assert stats is not None
    assert stats.name == "Gnome Priest"


def test_generate_halfling():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("halfling-thug", ref_resolver=ref_resolver, rng=rng)
    assert ref is not None
    assert stats is not None
    assert stats.name == "Halfling Thug"


def test_generate_legendary():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("lich", ref_resolver=ref_resolver, rng=rng)
    assert stats is not None
    recharge_count = sum(1 if f.recharge is not None else 0 for f in stats.features)
    assert recharge_count <= 1
