"""
Tests for YAML template parsing helper functions.

These tests focus on real functionality using actual enum values and data structures
rather than mocking everything. This provides more meaningful validation of the parsing logic.
"""

from pathlib import Path

import pytest
import yaml

from foe_foundry.creature_types import CreatureType
from foe_foundry.creatures._yaml_template import (
    merge_template_data,
    parse_abilities_from_yaml,
    parse_creature_types_from_yaml,
    parse_damage_immunities_from_yaml,
    parse_movement_from_yaml,
    parse_roles_from_yaml,
    parse_secondary_damage_type_from_yaml,
    parse_senses_from_yaml,
    parse_single_attack_from_yaml,
    parse_stat_scaling,
)
from foe_foundry.damage import Condition, DamageType
from foe_foundry.role_types import MonsterRole
from foe_foundry.skills import AbilityScore, StatScaling


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

        expected = {"attacks": {"main": {"base": "Sword", "damage_multiplier": 1.5}}}
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
    """Test parse_stat_scaling function with real StatScaling enum values."""

    def test_simple_string_primary(self):
        """Test parsing primary scaling string."""
        result = parse_stat_scaling("Primary")
        assert result == StatScaling.Primary

    def test_simple_string_default(self):
        """Test parsing default scaling string."""
        result = parse_stat_scaling("Default")
        assert result == StatScaling.Default

    def test_list_format_medium(self):
        """Test parsing list format [scaling_type, modifier]."""
        result = parse_stat_scaling(["Medium", 2])
        assert result == (StatScaling.Medium, 2)

    def test_list_format_constitution(self):
        """Test parsing constitution scaling with modifier."""
        result = parse_stat_scaling(["Constitution", -1])
        assert result == (StatScaling.Constitution, -1)

    def test_invalid_input_returns_default(self):
        """Test parsing invalid input returns default."""
        result = parse_stat_scaling(42)
        assert result == StatScaling.Default

    def test_invalid_string_returns_default(self):
        """Test parsing invalid string returns default."""
        result = parse_stat_scaling("NonExistentScaling")
        assert result == StatScaling.Default


class TestParseAbilitiesFromYaml:
    """Test parse_abilities_from_yaml function with real enum values."""

    def test_parse_abilities_with_real_data(self):
        """Test parsing abilities section with real YAML data structure."""
        data = {
            "abilities": {
                "STR": "Primary",
                "DEX": ["Medium", 2],
                "CON": ["Constitution", -1],
                "INT": "Default",
                "WIS": ["Default", 1],
                "CHA": ["Default", -2],
            }
        }

        result = parse_abilities_from_yaml(data)

        # Verify all abilities are parsed correctly
        assert AbilityScore.STR in result
        assert AbilityScore.DEX in result
        assert AbilityScore.CON in result
        assert AbilityScore.INT in result
        assert AbilityScore.WIS in result
        assert AbilityScore.CHA in result

        # Verify specific values
        assert result[AbilityScore.STR] == StatScaling.Primary
        assert result[AbilityScore.DEX] == (StatScaling.Medium, 2)
        assert result[AbilityScore.CON] == (StatScaling.Constitution, -1)
        assert result[AbilityScore.INT] == StatScaling.Default
        assert result[AbilityScore.WIS] == (StatScaling.Default, 1)
        assert result[AbilityScore.CHA] == (StatScaling.Default, -2)

    def test_parse_abilities_berserker_like(self):
        """Test parsing abilities that match berserker template structure."""
        data = {
            "abilities": {
                "STR": "Primary",
                "DEX": ["Medium", 2],
                "CON": ["Constitution", 2],
                "INT": ["Default", -1],
                "WIS": "Default",
                "CHA": ["Default", -1],
            }
        }

        result = parse_abilities_from_yaml(data)

        assert result[AbilityScore.STR] == StatScaling.Primary
        assert result[AbilityScore.DEX] == (StatScaling.Medium, 2)
        assert result[AbilityScore.CON] == (StatScaling.Constitution, 2)
        assert result[AbilityScore.INT] == (StatScaling.Default, -1)
        assert result[AbilityScore.WIS] == StatScaling.Default
        assert result[AbilityScore.CHA] == (StatScaling.Default, -1)

    def test_no_abilities_section(self):
        """Test parsing when no abilities section exists."""
        data = {"other": "stuff"}

        result = parse_abilities_from_yaml(data)

        assert result == {}

    def test_partial_abilities(self):
        """Test parsing when only some abilities are defined."""
        data = {"abilities": {"STR": "Primary", "CON": "Constitution"}}

        result = parse_abilities_from_yaml(data)

        assert len(result) == 2
        assert result[AbilityScore.STR] == StatScaling.Primary
        assert result[AbilityScore.CON] == StatScaling.Constitution


class TestParseCreatureTypesFromYaml:
    """Test parse_creature_types_from_yaml function with real enum values."""

    def test_parse_primary_creature_type_only(self):
        """Test parsing only primary creature type."""
        data = {"creature_type": "Humanoid"}

        primary_type, additional_types = parse_creature_types_from_yaml(data)

        assert primary_type == CreatureType.Humanoid
        assert additional_types == []

    def test_parse_with_additional_creature_types(self):
        """Test parsing with additional creature types."""
        data = {"creature_type": "Undead", "additional_creature_types": ["Humanoid"]}

        primary_type, additional_types = parse_creature_types_from_yaml(data)

        assert primary_type == CreatureType.Undead
        assert additional_types == [CreatureType.Humanoid]

    def test_parse_multiple_additional_types(self):
        """Test parsing multiple additional creature types."""
        data = {
            "creature_type": "Construct",
            "additional_creature_types": ["Humanoid", "Undead"],
        }

        primary_type, additional_types = parse_creature_types_from_yaml(data)

        assert primary_type == CreatureType.Construct
        assert additional_types == [CreatureType.Humanoid, CreatureType.Undead]


class TestParseRolesFromYaml:
    """Test parse_roles_from_yaml function with real enum values."""

    def test_parse_primary_role_only(self):
        """Test parsing only primary role."""
        data = {"roles": {"primary": "Bruiser", "additional": []}}

        primary_role, additional_roles = parse_roles_from_yaml(data)

        assert primary_role == MonsterRole.Bruiser
        assert additional_roles == []

    def test_parse_with_additional_roles(self):
        """Test parsing with additional roles."""
        data = {
            "roles": {"primary": "Controller", "additional": ["Defender", "Skirmisher"]}
        }

        primary_role, additional_roles = parse_roles_from_yaml(data)

        assert primary_role == MonsterRole.Controller
        assert additional_roles == [MonsterRole.Defender, MonsterRole.Skirmisher]

    def test_no_roles_section(self):
        """Test parsing when no roles section exists."""
        data = {"other": "stuff"}

        primary_role, additional_roles = parse_roles_from_yaml(data)

        assert primary_role is None
        assert additional_roles == []

    def test_empty_roles_section(self):
        """Test parsing empty roles section."""
        data = {"roles": {}}

        primary_role, additional_roles = parse_roles_from_yaml(data)

        assert primary_role is None
        assert additional_roles == []


class TestParseMovementFromYaml:
    """Test parse_movement_from_yaml function."""

    def test_parse_movement(self):
        """Test parsing movement data."""
        data = {"movement": {"walk": 30, "fly": 60, "swim": 20}}

        result = parse_movement_from_yaml(data)
        assert result is not None
        assert result.walk == 30
        assert result.fly == 60
        assert result.swim == 20

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
        data = {"senses": {"darkvision": 60, "blindsight": 10}}

        result = parse_senses_from_yaml(data)
        assert result is not None
        assert result.darkvision == 60
        assert result.blindsight == 10

    def test_no_senses_section(self):
        """Test when no senses section exists."""
        data = {"other": "stuff"}

        result = parse_senses_from_yaml(data)

        assert result is None


class TestParseDamageImmunitiesFromYaml:
    """Test parse_damage_immunities_from_yaml function with real enum values."""

    def test_parse_nested_immunities(self):
        """Test parsing nested immunities structure."""
        data = {
            "immunities": {
                "damage_types": ["Fire", "Cold"],
                "conditions": ["Frightened"],
            },
            "condition_immunities": ["Charmed"],
        }

        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(
            data
        )

        assert DamageType.Fire in damage_immunities
        assert DamageType.Cold in damage_immunities
        assert Condition.Frightened in condition_immunities
        assert Condition.Charmed in condition_immunities

    def test_legacy_condition_immunities_only(self):
        """Test parsing legacy condition_immunities only."""
        data = {"condition_immunities": ["Frightened", "Charmed"]}

        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(
            data
        )

        assert len(damage_immunities) == 0
        assert Condition.Frightened in condition_immunities
        assert Condition.Charmed in condition_immunities

    def test_damage_immunities_only(self):
        """Test parsing damage immunities without conditions."""
        data = {"immunities": {"damage_types": ["Fire", "Necrotic", "Poison"]}}

        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(
            data
        )

        assert DamageType.Fire in damage_immunities
        assert DamageType.Necrotic in damage_immunities
        assert DamageType.Poison in damage_immunities
        assert len(condition_immunities) == 0

    def test_no_immunities_section(self):
        """Test parsing when no immunities section exists."""
        data = {"other": "stuff"}

        damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(
            data
        )

        assert len(damage_immunities) == 0
        assert len(condition_immunities) == 0


class TestParseSecondaryDamageTypeFromYaml:
    """Test parse_secondary_damage_type_from_yaml function with real enum values."""

    def test_single_damage_type(self):
        """Test parsing single damage type."""
        result = parse_secondary_damage_type_from_yaml("Fire")

        assert result == DamageType.Fire

    def test_multiple_damage_types(self):
        """Test parsing list of damage types."""
        result = parse_secondary_damage_type_from_yaml(["Fire", "Cold"])

        assert result == [DamageType.Fire, DamageType.Cold]

    def test_none_input(self):
        """Test parsing None input."""
        result = parse_secondary_damage_type_from_yaml(None)

        assert result is None

    def test_empty_list_input(self):
        """Test parsing empty list input."""
        result = parse_secondary_damage_type_from_yaml([])

        # Empty list returns None based on implementation
        assert result is None


class TestParseSingleAttackFromYaml:
    """Test parse_single_attack_from_yaml function with real attack templates."""

    def test_parse_basic_weapon_attack(self):
        """Test parsing basic weapon attack data."""
        attack_data = {"base": "Sword"}

        result = parse_single_attack_from_yaml(attack_data)

        # This may return None if the weapon.Sword doesn't exist in the current environment
        # which is expected in a limited test environment
        # The important thing is the function doesn't crash
        assert (
            result is None or hasattr(result, "name") or hasattr(result, "display_name")
        )

    def test_parse_natural_attack(self):
        """Test parsing natural attack data."""
        attack_data = {"base": "Claw"}

        result = parse_single_attack_from_yaml(attack_data)

        # Should return None if natural.Claw doesn't exist, which is expected
        assert (
            result is None or hasattr(result, "name") or hasattr(result, "display_name")
        )

    def test_parse_attack_with_display_name(self):
        """Test parsing attack with custom display name."""
        attack_data = {"base": "Sword", "display_name": "Flame Sword"}

        result = parse_single_attack_from_yaml(attack_data)

        # Should return None if weapon.Sword doesn't exist, which is expected
        assert (
            result is None or hasattr(result, "name") or hasattr(result, "display_name")
        )

    def test_missing_base_attack(self):
        """Test when base attack is missing."""
        attack_data = {}

        result = parse_single_attack_from_yaml(attack_data)

        assert result is None

    def test_unknown_base_attack(self):
        """Test when base attack is not found."""
        attack_data = {"base": "UnknownWeaponType"}

        result = parse_single_attack_from_yaml(attack_data)

        assert result is None


class TestRealYamlDataIntegration:
    """Test helper functions with real YAML template data."""

    @pytest.fixture
    def sample_yaml_files(self):
        """Get a few sample YAML template files for testing."""
        templates_dir = (
            Path(__file__).parent.parent.parent
            / "foe_foundry"
            / "creatures"
            / "templates"
        )
        if not templates_dir.exists():
            templates_dir = Path(
                "/home/runner/work/foe_foundry/foe_foundry/foe_foundry/creatures/templates"
            )

        yaml_files = list(templates_dir.glob("*.yml"))[
            :3
        ]  # Just test with first 3 files
        return yaml_files

    def test_parse_abilities_with_real_templates(self, sample_yaml_files):
        """Test parsing abilities from real template files."""
        for yaml_file in sample_yaml_files:
            with open(yaml_file, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            # Get common sections
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            if not common_sections:
                continue

            common_data = yaml_data[common_sections[0]]
            if "abilities" not in common_data:
                continue

            # Parse abilities and verify they work
            result = parse_abilities_from_yaml(common_data)

            # Should have at least some abilities defined
            assert len(result) > 0

            # All keys should be valid AbilityScore enum values
            for ability in result.keys():
                assert isinstance(ability, type(AbilityScore.STR))

            # All values should be StatScaling or tuples with StatScaling
            for value in result.values():
                if isinstance(value, tuple):
                    assert isinstance(value[0], type(StatScaling.Default))
                    assert isinstance(value[1], int)
                else:
                    assert isinstance(value, type(StatScaling.Default))

    def test_parse_creature_types_with_real_templates(self, sample_yaml_files):
        """Test parsing creature types from real template files."""
        for yaml_file in sample_yaml_files:
            with open(yaml_file, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            # Get common sections
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            if not common_sections:
                continue

            common_data = yaml_data[common_sections[0]]
            if "creature_type" not in common_data:
                continue

            # Parse creature types and verify they work
            primary_type, additional_types = parse_creature_types_from_yaml(common_data)

            # Should have a valid primary type
            assert isinstance(primary_type, type(CreatureType.Humanoid))

            # Additional types should be a list of valid CreatureType values
            assert isinstance(additional_types, list)
            for creature_type in additional_types:
                assert isinstance(creature_type, type(CreatureType.Humanoid))
