import numpy as np

from foe_foundry.powers.species import powers_for_role
from foe_foundry.role_types import MonsterRole
from foe_foundry_data.generate import generate_monster
from foe_foundry_data.refs import MonsterRefResolver


def test_orc_powers():
    powers_for_role("orc", MonsterRole.Support)


def test_generate_orc_npc():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("orc-priest", ref_resolver, rng)
    assert ref is not None
    assert stats is not None
    assert ref.species is not None
    assert ref.species.key == "orc"
    assert stats.key == "orc-priest"
    assert stats.name == "Orc Priest"


def test_generate_human_npc_implied():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("priest", ref_resolver, rng)
    assert ref is not None
    assert stats is not None
    assert ref.species is None
    assert stats.key == "priest"
    assert stats.name == "Priest"


def test_generate_human_npc_explicit():
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng()
    ref, stats = generate_monster("human-priest", ref_resolver, rng)
    assert ref is not None
    assert stats is not None
    assert ref.species is not None
    assert ref.species.key == "human"
    assert stats.key == "priest"
    assert stats.name == "Priest"
