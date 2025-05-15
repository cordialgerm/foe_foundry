from foe_foundry_data.refs import MonsterRefResolver


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
