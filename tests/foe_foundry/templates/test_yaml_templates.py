"""
Integration tests for YAML template functionality and structure validation.

These tests focus on verifying that YAML templates can be loaded, parsed, and
used to generate meaningful monster data. While full comparison with Python
implementations is the ultimate goal, these tests provide meaningful validation
of the YAML parsing system.
"""

from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from foe_foundry.creatures._yaml_template import (
    merge_template_data,
)


class TestYamlTemplateIntegration:
    """Test YAML template integration and functionality."""

    @pytest.fixture
    def yaml_template_files(self):
        """
        Fixture to get all YAML template files.
        """
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
        return list(templates_dir.glob("*.yml"))

    @pytest.fixture
    def sample_yaml_templates(self, yaml_template_files):
        """Get a few sample YAML templates for detailed testing."""
        return yaml_template_files[:5]  # Test with first 5 templates

    def load_yaml_template_data(self, yaml_path: Path) -> Dict[str, Any]:
        """Load YAML template data from file."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            return yaml.safe_load(f)

    def test_yaml_template_data_merging(self, sample_yaml_templates):
        """Test that template data merging works correctly."""
        for yaml_path in sample_yaml_templates:
            yaml_data = self.load_yaml_template_data(yaml_path)

            # Get common sections
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            if not common_sections:
                continue

            common_data = yaml_data[common_sections[0]]

            # Test merging with each monster
            template_section = yaml_data.get("template", {})
            monsters = template_section.get("monsters", [])

            for monster in monsters:
                monster_key = monster["key"]
                monster_data = yaml_data.get(monster_key, {})

                # Merge data
                merged_data = merge_template_data(common_data, monster_data)

                # Should have essential fields
                assert "creature_type" in merged_data
                assert "abilities" in merged_data

                # Should preserve monster-specific overrides
                if monster_data:
                    for key, value in monster_data.items():
                        if key != "<<":  # Skip YAML anchor references
                            assert key in merged_data

    def test_template_environments_parsing(self, sample_yaml_templates):
        """Test that environment parsing works correctly."""
        for yaml_path in sample_yaml_templates:
            yaml_data = self.load_yaml_template_data(yaml_path)

            template_section = yaml_data.get("template", {})
            environments = template_section.get("environments", [])

            if not environments:
                continue

            # Each environment should have valid structure
            for env in environments:
                if isinstance(env, dict):
                    # Can be structured like {"development": "native", "affinity": "common"}
                    # OR like {"Urban": "High"} - shorthand format
                    assert len(env) > 0, "Environment dict should not be empty"

                    # Validate that values are strings
                    for key, value in env.items():
                        assert isinstance(key, str), (
                            f"Environment key should be string, got {type(key)}"
                        )
                        assert isinstance(value, str), (
                            f"Environment value should be string, got {type(value)}"
                        )

                elif isinstance(env, str):
                    # Simple string environments are also valid
                    assert len(env) > 0
                else:
                    # Should be either dict or string
                    assert False, (
                        f"Environment should be dict or string, got {type(env)}"
                    )

    def test_template_species_support(self, sample_yaml_templates):
        """Test that species support is correctly specified."""
        for yaml_path in sample_yaml_templates:
            yaml_data = self.load_yaml_template_data(yaml_path)

            template_section = yaml_data.get("template", {})
            species = template_section.get("species", "all")

            # Should be either "all" or a list of specific species
            assert species == "all" or isinstance(species, list)

            if isinstance(species, list):
                # Each species should be a string
                for spec in species:
                    assert isinstance(spec, str)
                    assert len(spec) > 0


class TestYamlTemplateFunctionalValidation:
    """Test functional validation of YAML templates with comprehensive checks."""

    @pytest.fixture
    def yaml_template_files(self):
        """Get all YAML template files."""
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
        return list(templates_dir.glob("*.yml"))

    def test_all_yaml_templates_have_required_sections(self, yaml_template_files):
        """
        Test that all YAML templates have the required sections for monster generation.
        """
        required_template_fields = ["key", "name", "monsters"]
        required_common_fields = ["creature_type", "abilities"]

        for yaml_path in yaml_template_files:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            # Check template section
            template_section = yaml_data.get("template", {})
            for field in required_template_fields:
                assert field in template_section, (
                    f"Missing required template field '{field}' in {yaml_path.name}"
                )

            # Check common sections
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            assert len(common_sections) > 0, (
                f"No common section found in {yaml_path.name}"
            )

            # Check first common section has required fields
            common_data = yaml_data[common_sections[0]]
            for field in required_common_fields:
                assert field in common_data, (
                    f"Missing required common field '{field}' in {yaml_path.name}"
                )

            # Verify that each monster has a data section and essential fields
            template_data = yaml_data["template"]
            for monster in template_data.get("monsters", []):
                monster_key = monster["key"]
                assert monster_key in yaml_data, (
                    f"Missing data section for monster '{monster_key}' in {yaml_path.name}"
                )

                # Get merged data for this monster to check essential fields
                monster_data = yaml_data[monster_key]
                merged_data = {**common_data}
                for key, value in monster_data.items():
                    if key != "<<":
                        merged_data[key] = value

                # Check that essential fields exist either in common or monster-specific data
                essential_fields = ["creature_type", "abilities"]
                for field in essential_fields:
                    assert field in merged_data, (
                        f"Missing essential field '{field}' for monster '{monster_key}' in {yaml_path.name}"
                    )

    def test_yaml_template_basic_structure(self, yaml_template_files):
        """
        Test basic structure validation of YAML templates.
        """
        for yaml_path in yaml_template_files:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            # Basic structure validation
            assert "template" in yaml_data
            assert "key" in yaml_data["template"]
            assert "name" in yaml_data["template"]
            assert "monsters" in yaml_data["template"]

            # Validate each monster entry
            for monster in yaml_data["template"]["monsters"]:
                assert "key" in monster
                assert "name" in monster
                assert "cr" in monster
                assert isinstance(monster["cr"], (int, float))

                # Ensure monster data section exists
                assert monster["key"] in yaml_data

            # Validate common sections exist
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            assert len(common_sections) > 0, (
                f"No common section found in {yaml_path.name}"
            )

    def test_ability_score_consistency(self, yaml_template_files):
        """Test that ability scores are consistently defined across templates."""
        ability_names = {"STR", "DEX", "CON", "INT", "WIS", "CHA"}

        for yaml_path in yaml_template_files:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            # Get common sections
            common_sections = [
                k for k in yaml_data.keys() if k == "common" or k.endswith("_common")
            ]
            if not common_sections:
                continue

            common_data = yaml_data[common_sections[0]]
            abilities = common_data.get("abilities", {})

            # Check that all defined abilities are valid
            for ability_name in abilities.keys():
                assert ability_name in ability_names, (
                    f"Invalid ability '{ability_name}' in {yaml_path.name}"
                )

    def test_cr_values_are_valid(self, yaml_template_files):
        """Test that CR values are valid D&D 5e CR values."""
        valid_crs = {
            0,
            0.125,
            0.25,
            0.5,
            1,
            2,
            3,
            4,
            5,
            6,
            7,
            8,
            9,
            10,
            11,
            12,
            13,
            14,
            15,
            16,
            17,
            18,
            19,
            20,
            21,
            22,
            23,
            24,
            25,
            26,
            27,
            28,
            29,
            30,
        }

        for yaml_path in yaml_template_files:
            with open(yaml_path, "r", encoding="utf-8") as f:
                yaml_data = yaml.safe_load(f)

            template_section = yaml_data["template"]
            for monster in template_section["monsters"]:
                cr = monster["cr"]
                assert cr in valid_crs, (
                    f"Invalid CR {cr} for monster '{monster['key']}' in {yaml_path.name}"
                )
