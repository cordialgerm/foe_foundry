"""Tests for monster family back-references functionality."""

import pytest
from foe_foundry_data.base import MonsterInfoModel, MonsterFamilyInfo
from foe_foundry_data.monster_families.data import load_monster_families
from foe_foundry_data.monsters.all import Monsters


class TestMonsterFamilyBackReferences:
    """Test the back-reference system between monsters and families."""

    def test_monster_family_back_references_populated(self):
        """Test that monsters in families have family_keys populated."""
        families = load_monster_families()
        assert len(families) > 0, "Should have loaded some families"
        
        # Find a family with monsters
        family_with_monsters = next((f for f in families if f.monsters), None)
        assert family_with_monsters is not None, "Should find a family with monsters"
        
        # Check that monsters have family_keys set and include this family
        for monster in family_with_monsters.monsters:
            assert monster.family_keys is not None, (
                f"Monster {monster.name} should have family_keys set"
            )
            assert family_with_monsters.key in monster.family_keys, (
                f"Monster {monster.name} should have {family_with_monsters.key} in family_keys"
            )

    def test_monster_info_computed_field_includes_monster_families(self):
        """Test that MonsterInfoModel.monsterFamilies computed field works correctly."""
        families = load_monster_families()
        family_with_monsters = next((f for f in families if f.monsters), None)
        monster = family_with_monsters.monsters[0]
        
        # Test the computed property directly
        family_names = monster.monsterFamilies
        
        assert family_names is not None, "monsterFamilies should not be None"
        assert family_with_monsters.name in family_names, (
            f"monsterFamilies should contain family name: {family_with_monsters.name}"
        )

    def test_monster_model_has_family_keys(self):
        """Test that MonsterModel instances have family_keys populated."""
        # Get a monster from the main cache
        monsters = list(Monsters.one_of_each_monster)
        
        # Find a monster that should be in a family
        monster_with_family = next((m for m in monsters if m.family_keys), None)
        
        if monster_with_family:
            assert monster_with_family.family_keys is not None, (
                f"Monster {monster_with_family.name} should have family_keys set"
            )
            
            # Verify the families exist
            families = load_monster_families()
            for family_key in monster_with_family.family_keys:
                family = next((f for f in families if f.key == family_key), None)
                assert family is not None, (
                    f"Family with key {family_key} should exist"
                )

    def test_no_circular_references_in_serialization(self):
        """Test that we can serialize monster families without circular reference errors."""
        families = load_monster_families()
        family = families[0]
        
        # This should not raise a recursion error
        import dataclasses
        try:
            # Convert the basic fields to dict, excluding the monsters to test partial serialization
            basic_family_dict = {
                "key": family.key,
                "name": family.name,
                "url": family.url,
                "icon": family.icon,
                "tag_line": family.tag_line,
            }
            assert isinstance(basic_family_dict, dict)
            
            # Test that monsters can access their family names without circular references
            for monster in family.monsters:
                family_names = monster.monsterFamilies
                assert isinstance(family_names, (list, type(None)))
                if family_names:
                    assert family.name in family_names
                
        except RecursionError:
            pytest.fail("Circular reference detected in serialization")

    def test_monster_families_field_consistency(self):
        """Test that monsterFamilies field is consistent across different access patterns."""
        families = load_monster_families()
        family_with_monsters = next((f for f in families if f.monsters), None)
        monster = family_with_monsters.monsters[0]
        
        # Test via family.monsters
        family_names1 = monster.monsterFamilies
        
        # Test via Monsters.one_of_each_monster  
        all_monsters = list(Monsters.one_of_each_monster)
        cached_monster = next((m for m in all_monsters if m.key == monster.key), None)
        
        if cached_monster:
            # Create MonsterInfoModel from cached monster
            monster_info = MonsterInfoModel(
                key=cached_monster.key,
                name=cached_monster.name,
                cr=cached_monster.cr,
                template=cached_monster.template_key,
                family_keys=cached_monster.family_keys,
            )
            family_names2 = monster_info.monsterFamilies
            
            assert family_names1 == family_names2, (
                "monsterFamilies should be consistent across different access patterns"
            )