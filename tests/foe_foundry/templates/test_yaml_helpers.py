"""
Tests for YAML template parsing helper functions.
"""

import pytest
from unittest.mock import Mock
from foe_foundry.creatures._yaml_template import (
    merge_template_data,
    parse_stat_scaling,
    parse_abilities_from_yaml,
    parse_creature_types_from_yaml,
    parse_roles_from_yaml,
    parse_movement_from_yaml,
    parse_senses_from_yaml,
    parse_damage_immunities_from_yaml,
    parse_damage_resistances_from_yaml,
    parse_skills_from_yaml,
    parse_saving_throws_from_yaml,
    parse_secondary_damage_type_from_yaml,
    parse_single_attack_from_yaml,
)


class TestMergeTemplateData:
    """Test merge_template_data function."""
    
    def test_simple_merge(self):
        """Test simple key-value merging."""
        common = {"a": 1, "b": 2}
        monster = {"c": 3}
        
        result = merge_template_data(common, monster)
        
        assert result == {"a": 1, "b": 2, "c": 3}
    
    def test_override_values(self):
        """Test that monster data overrides common data."""
        common = {"a": 1, "b": 2}
        monster = {"b": 99}
        
        result = merge_template_data(common, monster)
        
        assert result == {"a": 1, "b": 99}
    
    def test_deep_merge_dicts(self):
        """Test deep merging of nested dictionaries."""
        common = {"attacks": {"main": {"base": "Sword"}}}
        monster = {"attacks": {"main": {"damage_multiplier": 1.5}}}
        
        result = merge_template_data(common, monster)
        
        expected = {
            "attacks": {
                "main": {
                    "base": "Sword", 
                    "damage_multiplier": 1.5
                }
            }
        }
        assert result == expected
    
    def test_list_replacement(self):
        """Test that lists are replaced entirely, not merged."""
        common = {"skills": {"proficiency": ["Athletics", "Perception"]}}
        monster = {"skills": {"proficiency": ["Stealth"]}}
        
        result = merge_template_data(common, monster)
        
        expected = {"skills": {"proficiency": ["Stealth"]}}
        assert result == expected
    
    def test_skip_yaml_anchor(self):
        """Test that YAML anchor references are skipped."""
        common = {"a": 1}
        monster = {"<<": "*common", "b": 2}
        
        result = merge_template_data(common, monster)
        
        assert result == {"a": 1, "b": 2}
        assert "<<" not in result


class TestParseStatScaling:
    """Test parse_stat_scaling function."""
    
    def test_simple_string(self):
        """Test parsing simple string scaling."""
        # Mock StatScaling enum
        import foe_foundry.creatures._yaml_template as yaml_template
        mock_stat_scaling = Mock()
        mock_stat_scaling.Primary = "PRIMARY"
        mock_stat_scaling.Default = "DEFAULT"
        yaml_template.StatScaling = mock_stat_scaling
        
        result = parse_stat_scaling("Primary")
        assert result == "PRIMARY"
    
    def test_list_format(self):
        """Test parsing list format [scaling_type, modifier]."""
        import foe_foundry.creatures._yaml_template as yaml_template
        mock_stat_scaling = Mock()
        mock_stat_scaling.Medium = "MEDIUM"
        mock_stat_scaling.Default = "DEFAULT"
        yaml_template.StatScaling = mock_stat_scaling
        
        result = parse_stat_scaling(["Medium", 2])
        assert result == ("MEDIUM", 2)
    
    def test_invalid_input(self):
        """Test parsing invalid input returns default."""
        import foe_foundry.creatures._yaml_template as yaml_template
        mock_stat_scaling = Mock()
        mock_stat_scaling.Default = "DEFAULT"
        yaml_template.StatScaling = mock_stat_scaling
        
        result = parse_stat_scaling(42)
        assert result == "DEFAULT"


class TestParseAbilitiesFromYaml:
    """Test parse_abilities_from_yaml function."""
    
    def test_parse_abilities(self):
        """Test parsing abilities section."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        # Mock AbilityScore and StatScaling
        mock_ability_score = Mock()
        mock_ability_score.STR = "STR"
        mock_ability_score.DEX = "DEX"
        mock_stat_scaling = Mock()
        mock_stat_scaling.Primary = "PRIMARY"
        mock_stat_scaling.Default = "DEFAULT"
        
        yaml_template.AbilityScore = mock_ability_score
        yaml_template.StatScaling = mock_stat_scaling
        
        data = {
            "abilities": {
                "STR": "Primary",
                "DEX": ["Medium", 2]
            }
        }
        
        result = parse_abilities_from_yaml(data)
        
        assert "STR" in result
        assert "DEX" in result
        assert result["STR"] == "PRIMARY"
        assert result["DEX"] == ("DEFAULT", 2)  # Medium not defined in mock
    
    def test_no_abilities_section(self):
        """Test parsing when no abilities section exists."""
        data = {"other": "stuff"}
        
        result = parse_abilities_from_yaml(data)
        
        assert result == {}


class TestParseMovementFromYaml:
    """Test parse_movement_from_yaml function."""
    
    def test_parse_movement(self):
        """Test parsing movement data."""
        data = {
            "movement": {
                "walk": 30,
                "fly": 60,
                "swim": 20
            }
        }
        
        result = parse_movement_from_yaml(data)
        
        assert result == {"walk": 30, "fly": 60, "swim": 20}
    
    def test_no_movement_section(self):
        """Test when no movement section exists."""
        data = {"other": "stuff"}
        
        result = parse_movement_from_yaml(data)
        
        assert result is None
    
    def test_empty_movement_section(self):
        """Test when movement section is empty."""
        data = {"movement": {}}
        
        result = parse_movement_from_yaml(data)
        
        assert result is None


class TestParseSensesFromYaml:
    """Test parse_senses_from_yaml function."""
    
    def test_parse_senses(self):
        """Test parsing senses data."""
        data = {
            "senses": {
                "darkvision": 60,
                "blindsight": 10
            }
        }
        
        result = parse_senses_from_yaml(data)
        
        assert result == {"darkvision": 60, "blindsight": 10}
    
    def test_no_senses_section(self):
        """Test when no senses section exists."""
        data = {"other": "stuff"}
        
        result = parse_senses_from_yaml(data)
        
        assert result is None


class TestParseDamageImmunitiesFromYaml:
    """Test parse_damage_immunities_from_yaml function."""
    
    def test_parse_nested_immunities(self):
        """Test parsing nested immunities structure."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        # Mock DamageType and Condition
        mock_damage_type = Mock()
        mock_damage_type.Fire = "FIRE"
        mock_damage_type.Cold = "COLD"
        mock_condition = Mock()
        mock_condition.Frightened = "FRIGHTENED"
        mock_condition.Charmed = "CHARMED"
        
        yaml_template.DamageType = mock_damage_type
        yaml_template.Condition = mock_condition
        
        data = {
            "immunities": {
                "damage_types": ["Fire", "Cold"],
                "conditions": ["Frightened"]
            },
            "condition_immunities": ["Charmed"]
        }
        
        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(data)
        
        assert "FIRE" in damage_immunities
        assert "COLD" in damage_immunities
        assert "FRIGHTENED" in condition_immunities
        assert "CHARMED" in condition_immunities
    
    def test_legacy_condition_immunities_only(self):
        """Test parsing legacy condition_immunities only."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        mock_condition = Mock()
        mock_condition.Frightened = "FRIGHTENED"
        yaml_template.Condition = mock_condition
        
        data = {
            "condition_immunities": ["Frightened"]
        }
        
        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(data)
        
        assert len(damage_immunities) == 0
        assert "FRIGHTENED" in condition_immunities


class TestParseSecondaryDamageTypeFromYaml:
    """Test parse_secondary_damage_type_from_yaml function."""
    
    def test_single_damage_type(self):
        """Test parsing single damage type."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        mock_damage_type = Mock()
        mock_damage_type.Fire = "FIRE"
        yaml_template.DamageType = mock_damage_type
        
        result = parse_secondary_damage_type_from_yaml("Fire")
        
        assert result == "FIRE"
    
    def test_multiple_damage_types(self):
        """Test parsing list of damage types."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        mock_damage_type = Mock()
        mock_damage_type.Fire = "FIRE"
        mock_damage_type.Cold = "COLD"
        yaml_template.DamageType = mock_damage_type
        
        result = parse_secondary_damage_type_from_yaml(["Fire", "Cold"])
        
        assert result == ["FIRE", "COLD"]
    
    def test_none_input(self):
        """Test parsing None input."""
        result = parse_secondary_damage_type_from_yaml(None)
        
        assert result is None


class TestParseSingleAttackFromYaml:
    """Test parse_single_attack_from_yaml function."""
    
    def test_parse_basic_attack(self):
        """Test parsing basic attack data."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        # Mock weapon module and attack template
        mock_weapon = Mock()
        mock_attack_template = Mock()
        mock_weapon.Sword = mock_attack_template
        yaml_template.weapon = mock_weapon
        
        attack_data = {
            "base": "Sword"
        }
        
        result = parse_single_attack_from_yaml(attack_data)
        
        assert result == mock_attack_template
    
    def test_parse_attack_with_display_name(self):
        """Test parsing attack with display name."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        mock_weapon = Mock()
        mock_attack_template = Mock()
        mock_enhanced_attack = Mock()
        mock_attack_template.with_display_name.return_value = mock_enhanced_attack
        mock_weapon.Sword = mock_attack_template
        yaml_template.weapon = mock_weapon
        
        attack_data = {
            "base": "Sword",
            "display_name": "Flame Sword"
        }
        
        result = parse_single_attack_from_yaml(attack_data)
        
        mock_attack_template.with_display_name.assert_called_once_with("Flame Sword")
        assert result == mock_enhanced_attack
    
    def test_missing_base_attack(self):
        """Test when base attack is missing."""
        attack_data = {}
        
        result = parse_single_attack_from_yaml(attack_data)
        
        assert result is None
    
    def test_unknown_base_attack(self):
        """Test when base attack is not found."""
        import foe_foundry.creatures._yaml_template as yaml_template
        
        mock_weapon = Mock()
        mock_natural = Mock()
        mock_spell = Mock()
        
        # Set up mocks to return None for Unknown attack
        mock_weapon.Unknown = None
        mock_natural.Unknown = None
        mock_spell.Unknown = None
        
        yaml_template.weapon = mock_weapon
        yaml_template.natural = mock_natural
        yaml_template.spell = mock_spell
        
        attack_data = {
            "base": "Unknown"
        }
        
        result = parse_single_attack_from_yaml(attack_data)
        
        assert result is None


if __name__ == "__main__":
    # Run a simple test
    test_merge = TestMergeTemplateData()
    test_merge.test_simple_merge()
    test_merge.test_override_values()
    print("Basic merge tests passed!")
    
    test_movement = TestParseMovementFromYaml()
    test_movement.test_parse_movement()
    test_movement.test_no_movement_section()
    print("Movement parsing tests passed!")
    
    print("All standalone tests passed!")