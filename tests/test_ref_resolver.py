import numpy as np

from foe_foundry_data.refs import MonsterRefResolver


def test_ref_equality():
    resolver = MonsterRefResolver()
    key = "guard"
    ref1 = resolver.resolve_monster_ref(key)
    ref2 = resolver.resolve_monster_ref(key)
    assert ref1 == ref2


def test_keys_resolve():
    resolver = MonsterRefResolver()
    keys = [
        "berserker",
        "archpriest",
        "Necromancer Mage",
        "orc-hardened-one",
        "orc-berserker",
        "berserker",
        "dwarf-berserker",
    ]
    for key in keys:
        ref = resolver.resolve_monster_ref(key)
        assert ref is not None, f"Failed to resolve key: {key}"


def test_resolve_orc_key():
    resolver = MonsterRefResolver()
    key = "orc-druid"
    ref = resolver.resolve_monster_ref(key)
    assert ref is not None
    assert ref.monster is not None
    assert ref.monster.name == "Druid"


def test_resolve_overloaded_alias():
    alias = "mage"
    resolver = MonsterRefResolver()
    ref1 = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(42))
    ref1b = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(42))
    ref2 = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(43))

    assert ref1 == ref1b
    assert ref1 != ref2, "Different RNGs should resolve to different refs"


def test_resolve_overloaded_alias_with_species():
    alias = "orc-veteran"
    resolver = MonsterRefResolver()
    ref1 = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(42))
    ref1b = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(42))
    ref2 = resolver.resolve_monster_ref(alias, rng=np.random.default_rng(43))

    assert ref1 is not None
    assert ref1.species is not None
    assert ref1 == ref1b
    assert ref1 != ref2, "Different RNGs should resolve to different refs"
