"""Tests for monster family back-references functionality."""

import pytest
from foe_foundry_data.base import MonsterInfoModel, MonsterFamilyInfo
from foe_foundry_data.monster_families.data import load_monster_families
from foe_foundry_data.monsters.all import Monsters
from foe_foundry_site.routes.search import _monster_info_to_dict


class TestMonsterFamilyBackReferences:
    """Test the back-reference system between monsters and families."""

    def test_monster_family_back_references_populated(self):
        """Test that monsters in families have family_key populated."""
        families = load_monster_families()
        assert len(families) > 0, "Should have loaded some families"
        
        # Find a family with monsters
        family_with_monsters = next((f for f in families if f.monsters), None)
        assert family_with_monsters is not None, "Should find a family with monsters"
        
        # Check that monsters have family_key set
        for monster in family_with_monsters.monsters:
            assert monster.family_key == family_with_monsters.key, (
                f"Monster {monster.name} should have family_key set to {family_with_monsters.key}"
            )

    def test_monster_info_to_dict_includes_monster_families(self):
        """Test that _monster_info_to_dict includes monsterFamilies field."""
        families = load_monster_families()
        family_with_monsters = next((f for f in families if f.monsters), None)
        monster = family_with_monsters.monsters[0]
        
        result = _monster_info_to_dict(monster)
        
        assert "monsterFamilies" in result, "Result should include monsterFamilies field"
        assert result["monsterFamilies"] == [family_with_monsters.name], (
            f"monsterFamilies should contain family name: {family_with_monsters.name}"
        )

    def test_monster_model_has_family_key(self):
        """Test that MonsterModel instances have family_key populated."""
        # Get a monster from the main cache
        monsters = list(Monsters.one_of_each_monster)
        
        # Find a monster that should be in a family
        monster_with_family = next((m for m in monsters if m.family_key), None)
        
        if monster_with_family:
            assert monster_with_family.family_key is not None, (
                f"Monster {monster_with_family.name} should have family_key set"
            )
            
            # Verify the family exists
            families = load_monster_families()
            family = next((f for f in families if f.key == monster_with_family.family_key), None)
            assert family is not None, (
                f"Family with key {monster_with_family.family_key} should exist"
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
            
            # Test that monsters can be converted to dict
            for monster in family.monsters:
                monster_dict = _monster_info_to_dict(monster)
                assert isinstance(monster_dict, dict)
                assert "monsterFamilies" in monster_dict
                
        except RecursionError:
            pytest.fail("Circular reference detected in serialization")

    def test_monster_families_field_consistency(self):
        """Test that monsterFamilies field is consistent across different access patterns."""
        families = load_monster_families()
        family_with_monsters = next((f for f in families if f.monsters), None)
        monster = family_with_monsters.monsters[0]
        
        # Test via family.monsters
        dict1 = _monster_info_to_dict(monster)
        
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
                family_key=cached_monster.family_key,
            )
            dict2 = _monster_info_to_dict(monster_info)
            
            assert dict1["monsterFamilies"] == dict2["monsterFamilies"], (
                "monsterFamilies should be consistent across different access patterns"
            )