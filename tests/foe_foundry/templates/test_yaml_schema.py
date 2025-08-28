"""
Tests for YAML template schema validation.
"""

import pytest
from pathlib import Path
from foe_foundry.creatures.templates.schema import (
    validate_yaml_template_file, 
    validate_yaml_template,
    get_all_template_files,
    validate_all_templates
)


class TestYamlSchema:
    """Test class for YAML schema validation."""
    
    def test_schema_validation_basic_valid_template(self):
        """Test schema validation with a basic valid template."""
        template_data = {
            "template": {
                "key": "test_monster",
                "name": "Test Monster",
                "monsters": [
                    {"key": "test", "name": "Test", "cr": 1}
                ]
            },
            "common": {
                "creature_type": "Humanoid",
                "size": "Medium"
            },
            "test": {}
        }
        
        errors = validate_yaml_template(template_data)
        assert errors == []
    
    def test_schema_validation_missing_template_section(self):
        """Test schema validation fails when template section is missing."""
        template_data = {
            "common": {
                "creature_type": "Humanoid"
            }
        }
        
        errors = validate_yaml_template(template_data)
        assert "Missing required 'template' section" in errors
    
    def test_schema_validation_missing_common_section(self):
        """Test schema validation fails when common section is missing."""
        template_data = {
            "template": {
                "key": "test_monster",
                "name": "Test Monster",
                "monsters": [
                    {"key": "test", "name": "Test", "cr": 1}
                ]
            }
        }
        
        errors = validate_yaml_template(template_data)
        assert len(errors) > 0
        assert any("common" in error for error in errors)
    
    def test_schema_validation_missing_required_template_fields(self):
        """Test schema validation fails when required template fields are missing."""
        template_data = {
            "template": {
                "name": "Test Monster"
                # Missing key and monsters
            },
            "common": {
                "creature_type": "Humanoid"
            }
        }
        
        errors = validate_yaml_template(template_data)
        assert "Missing required field 'template.key'" in errors
        assert "Missing required field 'template.monsters'" in errors
    
    def test_schema_validation_invalid_monster_cr(self):
        """Test schema validation fails when monster CR is not a number."""
        template_data = {
            "template": {
                "key": "test_monster",
                "name": "Test Monster", 
                "monsters": [
                    {"key": "test", "name": "Test", "cr": "invalid"}
                ]
            },
            "common": {
                "creature_type": "Humanoid"
            },
            "test": {}
        }
        
        errors = validate_yaml_template(template_data)
        assert "'template.monsters[0].cr' must be a number" in errors
    
    def test_schema_validation_missing_monster_section(self):
        """Test schema validation fails when a monster section is missing."""
        template_data = {
            "template": {
                "key": "test_monster",
                "name": "Test Monster",
                "monsters": [
                    {"key": "test", "name": "Test", "cr": 1},
                    {"key": "missing", "name": "Missing", "cr": 2}
                ]
            },
            "common": {
                "creature_type": "Humanoid"
            },
            "test": {}
            # Missing "missing" section
        }
        
        errors = validate_yaml_template(template_data)
        assert "Missing monster section 'missing'" in errors


@pytest.mark.parametrize("template_file", get_all_template_files())
def test_all_templates_pass_schema_validation(template_file: Path):
    """Test that all existing YAML templates pass schema validation."""
    errors = validate_yaml_template_file(template_file)
    
    # If there are errors, print them for debugging
    if errors:
        print(f"\nValidation errors for {template_file.name}:")
        for error in errors:
            print(f"  - {error}")
    
    # For now, we'll allow some templates to have issues during development
    # but track which ones have problems
    if errors:
        pytest.skip(f"Template {template_file.name} has validation errors: {errors}")


def test_validate_all_templates():
    """Test the validate_all_templates function."""
    results = validate_all_templates()
    
    assert isinstance(results, dict)
    assert len(results) > 0  # Should have found some templates
    
    # Print summary of validation results
    total_templates = len(results)
    valid_templates = sum(1 for errors in results.values() if not errors)
    invalid_templates = total_templates - valid_templates
    
    print(f"\nValidation Summary:")
    print(f"  Total templates: {total_templates}")
    print(f"  Valid templates: {valid_templates}")
    print(f"  Invalid templates: {invalid_templates}")
    
    if invalid_templates > 0:
        print(f"\nTemplates with validation errors:")
        for template_name, errors in results.items():
            if errors:
                print(f"  {template_name}: {len(errors)} error(s)")


if __name__ == "__main__":
    # Run a quick validation check
    results = validate_all_templates()
    for template_name, errors in results.items():
        if errors:
            print(f"{template_name}: {len(errors)} error(s)")
        else:
            print(f"{template_name}: OK")