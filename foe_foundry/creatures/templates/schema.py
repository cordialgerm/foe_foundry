"""
YAML Template Schema Definition and Validation

This module defines the schema for YAML monster templates and provides validation functionality.
"""

from pathlib import Path
from typing import Any, Dict, List

import yaml

# Define the schema as a dictionary structure that can be used for validation
YAML_TEMPLATE_SCHEMA = {
    "type": "object",
    "definitions": {
        "monster_properties": {
            "type": "object",
            "properties": {
                "creature_type": {"type": "string"},
                "additional_creature_types": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "creature_subtype": {"type": "string"},
                "size": {"type": "string"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "creature_class": {"type": "string"},
                "hp_multiplier": {"type": "number"},
                "damage_multiplier": {"type": "number"},
                "darkvision": {"type": "number"},
                "roles": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "additional": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "abilities": {
                    "type": "object",
                    "properties": {
                        "STR": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "DEX": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CON": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "INT": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "WIS": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CHA": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                    },
                    "additionalProperties": False,
                },
                "ac_templates": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "template": {"type": "string"},
                                    "modifier": {"type": "number"},
                                },
                                "required": ["template"],
                                "additionalProperties": False,
                            },
                        },
                    ]
                },
                "attacks": {
                    "type": "object",
                    "properties": {
                        "main": {
                            "type": "object",
                            "properties": {
                                "base": {"type": "string"},
                                "display_name": {"type": "string"},
                                "damage_multiplier": {"type": "number"},
                                "damage_scalar": {"type": "number"},
                                "reach": {"type": "number"},
                                "damage_type": {"type": "string"},
                                "secondary_damage_type": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}},
                                        {"type": "null"},
                                    ]
                                },
                            },
                            "additionalProperties": False,
                        },
                        "secondary": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "base": {"type": "string"},
                                        "display_name": {"type": "string"},
                                        "damage_multiplier": {"type": "number"},
                                        "damage_scalar": {"type": "number"},
                                        "reach": {"type": "number"},
                                        "damage_type": {"type": "string"},
                                        "secondary_damage_type": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                {"type": "null"},
                                            ]
                                        },
                                    },
                                    "additionalProperties": False,
                                },
                                {"type": "array", "items": {"type": "string"}},
                            ]
                        },
                    },
                    "additionalProperties": False,
                },
                "armor_class": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "object",
                            "properties": {
                                "base": {"type": "string"},
                                "modifier": {"type": "number"},
                            },
                            "required": ["base"],
                            "additionalProperties": False,
                        },
                        {"type": "null"},
                    ]
                },
                "speed": {
                    "type": "object",
                    "properties": {
                        "walk": {"type": "number"},
                        "fly": {"type": "number"},
                        "swim": {"type": "number"},
                        "climb": {"type": "number"},
                        "burrow": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "senses": {
                    "type": "object",
                    "properties": {
                        "darkvision": {"type": "number"},
                        "blindsight": {"type": "number"},
                        "tremorsense": {"type": "number"},
                        "truesight": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "proficiency": {"type": "array", "items": {"type": "string"}},
                        "expertise": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "saves": {"type": "array", "items": {"type": "string"}},
                "immunities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "resistances": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "vulnerabilities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "additionalProperties": False,
                },
                "attack_reduction": {"type": "number"},
                # Legacy support fields
                "damage_immunities": {"type": "array", "items": {"type": "string"}},
                "damage_resistances": {"type": "array", "items": {"type": "string"}},
                "damage_vulnerabilities": {"type": "array", "items": {"type": "string"}},
                # Additional fields found in templates
                "additional_types": {"type": "array", "items": {"type": "string"}},
                "caster_type": {"type": "string"},
                "flags": {"type": "object"},
                "has_unique_movement_manipulation": {"type": "boolean"},
                "legendary_boost_ac": {"type": "boolean"},
                "min_attacks": {"type": "number"},
                "multiattack_custom_text": {"type": "string"},
                "primary_damage_type": {"type": "string"},
                "reaction_count": {"type": "number"},
                "reduce_attacks": {"type": "number"},
                "secondary_damage_type": {"type": "string"},
                "set_attacks": {"type": "number"},
                "uses_shield": {"type": "boolean"},
            },
            "additionalProperties": False,
        }
    },
    "properties": {
        "template": {
            "type": "object",
            "properties": {
                "key": {"type": "string"},
                "name": {"type": "string"},
                "monsters": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "key": {"type": "string"},
                            "name": {"type": "string"},
                            "cr": {"type": "number"},
                            "legendary": {"type": "boolean"},
                        },
                        "required": ["key", "name", "cr"],
                        "additionalProperties": False,
                    },
                },
                "environments": {
                    "oneOf": [
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "development": {"type": "string"},
                                    "biome": {"type": "string"},
                                    "terrain": {"type": "string"},
                                    "region": {"type": "string"},
                                    "extraplanar": {"type": "string"},
                                    "affinity": {
                                        "type": "string",
                                        "enum": [
                                            "native",
                                            "common",
                                            "uncommon",
                                            "rare",
                                        ],
                                    },
                                },
                                "additionalProperties": False,
                            },
                        },
                        {
                            "type": "object",
                            "patternProperties": {
                                "^[a-zA-Z0-9_-]+$": {
                                    "type": "string",
                                    "enum": ["native", "common", "uncommon", "rare"],
                                }
                            },
                        },
                    ]
                },
                "species": {
                    "oneOf": [{"type": "string", "enum": ["all"]}, {"type": "null"}]
                },
                "is_sentient_species": {"type": "boolean"},
            },
            "required": ["key", "name", "monsters"],
            "additionalProperties": False,
        },
        "common": {
            "type": "object",
            "properties": {
                "creature_type": {"type": "string"},
                "additional_creature_types": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "creature_subtype": {"type": "string"},
                "size": {"type": "string"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "creature_class": {"type": "string"},
                "hp_multiplier": {"type": "number"},
                "damage_multiplier": {"type": "number"},
                "darkvision": {"type": "number"},
                "roles": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "additional": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "abilities": {
                    "type": "object",
                    "properties": {
                        "STR": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "DEX": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CON": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "INT": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "WIS": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CHA": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                    },
                    "additionalProperties": False,
                },
                "ac_templates": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "template": {"type": "string"},
                                    "modifier": {"type": "number"},
                                },
                                "required": ["template"],
                                "additionalProperties": False,
                            },
                        },
                    ]
                },
                "attacks": {
                    "type": "object",
                    "properties": {
                        "main": {
                            "type": "object",
                            "properties": {
                                "base": {"type": "string"},
                                "display_name": {"type": "string"},
                                "damage_multiplier": {"type": "number"},
                                "damage_scalar": {"type": "number"},
                                "reach": {"type": "number"},
                                "damage_type": {"type": "string"},
                                "secondary_damage_type": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}},
                                        {"type": "null"},
                                    ]
                                },
                            },
                            "additionalProperties": False,
                        },
                        "secondary": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "base": {"type": "string"},
                                        "display_name": {"type": "string"},
                                        "damage_multiplier": {"type": "number"},
                                        "damage_scalar": {"type": "number"},
                                        "reach": {"type": "number"},
                                        "damage_type": {"type": "string"},
                                        "secondary_damage_type": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                {"type": "null"},
                                            ]
                                        },
                                    },
                                    "additionalProperties": False,
                                },
                                {"type": "null"},
                            ]
                        },
                        "set_attacks": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "proficiency": {"type": "array", "items": {"type": "string"}},
                        "expertise": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "saves": {"type": "array", "items": {"type": "string"}},
                "condition_immunities": {"type": "array", "items": {"type": "string"}},
                "immunities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "resistances": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "additionalProperties": False,
                },
                "spellcasting": {
                    "type": "object",
                    "properties": {"caster_type": {"type": "string"}},
                    "additionalProperties": False,
                },
                "movement": {
                    "type": "object",
                    "properties": {
                        "walk": {"type": "number"},
                        "climb": {"type": "number"},
                        "fly": {"type": "number"},
                        "swim": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "senses": {
                    "type": "object",
                    "properties": {
                        "darkvision": {"type": "number"},
                        "blindsight": {"type": "number"},
                        "tremorsense": {"type": "number"},
                        "truesight": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "legendary": {
                    "type": "object",
                    "properties": {
                        "actions": {"type": "number"},
                        "resistances": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "attack_reduction": {"type": "number"},
                # Legacy support fields
                "damage_immunities": {"type": "array", "items": {"type": "string"}},
                "damage_resistances": {"type": "array", "items": {"type": "string"}},
                "damage_vulnerabilities": {"type": "array", "items": {"type": "string"}},
                # Additional fields found in templates
                "additional_types": {"type": "array", "items": {"type": "string"}},
                "caster_type": {"type": "string"},
                "flags": {"type": "object"},
                "has_unique_movement_manipulation": {"type": "boolean"},
                "legendary_boost_ac": {"type": "boolean"},
                "min_attacks": {"type": "number"},
                "multiattack_custom_text": {"type": "string"},
                "primary_damage_type": {"type": "string"},
                "reaction_count": {"type": "number"},
                "reduce_attacks": {"type": "number"},
                "secondary_damage_type": {"type": "string"},
                "set_attacks": {"type": "number"},
                "uses_shield": {"type": "boolean"},
                "vulnerabilities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "additionalProperties": False,
                },
            },
            "additionalProperties": False,
        },
    },
    "required": ["template", "common"],
    "patternProperties": {
        "^[a-zA-Z0-9_-]+$": {
            # Individual monster configurations (can inherit from common)
            # Must use the same structure as common section
            "type": "object",
            "properties": {
                # Allow all properties that can be in common
                "creature_type": {"type": "string"},
                "additional_creature_types": {
                    "type": "array",
                    "items": {"type": "string"},
                },
                "creature_subtype": {"type": "string"},
                "size": {"type": "string"},
                "languages": {"type": "array", "items": {"type": "string"}},
                "creature_class": {"type": "string"},
                "hp_multiplier": {"type": "number"},
                "damage_multiplier": {"type": "number"},
                "roles": {
                    "type": "object",
                    "properties": {
                        "primary": {"type": "string"},
                        "additional": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "abilities": {
                    "type": "object",
                    "properties": {
                        "STR": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "DEX": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CON": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "INT": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "WIS": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                        "CHA": {"oneOf": [{"type": "string"}, {"type": "array"}]},
                    },
                    "additionalProperties": False,
                },
                "ac_templates": {
                    "oneOf": [
                        {"type": "string"},
                        {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "template": {"type": "string"},
                                    "modifier": {"type": "number"},
                                },
                                "required": ["template"],
                                "additionalProperties": False,
                            },
                        },
                    ]
                },
                "attacks": {
                    "type": "object",
                    "properties": {
                        "main": {
                            "type": "object",
                            "properties": {
                                "base": {"type": "string"},
                                "display_name": {"type": "string"},
                                "damage_multiplier": {"type": "number"},
                                "damage_scalar": {"type": "number"},
                                "reach": {"type": "number"},
                                "damage_type": {"type": "string"},
                                "secondary_damage_type": {
                                    "oneOf": [
                                        {"type": "string"},
                                        {"type": "array", "items": {"type": "string"}},
                                        {"type": "null"},
                                    ]
                                },
                            },
                            "additionalProperties": False,
                        },
                        "secondary": {
                            "oneOf": [
                                {
                                    "type": "object",
                                    "properties": {
                                        "base": {"type": "string"},
                                        "display_name": {"type": "string"},
                                        "damage_multiplier": {"type": "number"},
                                        "damage_scalar": {"type": "number"},
                                        "reach": {"type": "number"},
                                        "damage_type": {"type": "string"},
                                        "secondary_damage_type": {
                                            "oneOf": [
                                                {"type": "string"},
                                                {
                                                    "type": "array",
                                                    "items": {"type": "string"},
                                                },
                                                {"type": "null"},
                                            ]
                                        },
                                    },
                                    "additionalProperties": False,
                                },
                                {"type": "null"},
                            ]
                        },
                        "set_attacks": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "skills": {
                    "type": "object",
                    "properties": {
                        "proficiency": {"type": "array", "items": {"type": "string"}},
                        "expertise": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "saves": {"type": "array", "items": {"type": "string"}},
                "condition_immunities": {"type": "array", "items": {"type": "string"}},
                "immunities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}},
                        "conditions": {"type": "array", "items": {"type": "string"}},
                    },
                    "additionalProperties": False,
                },
                "resistances": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "additionalProperties": False,
                },
                "vulnerabilities": {
                    "type": "object",
                    "properties": {
                        "damage_types": {"type": "array", "items": {"type": "string"}}
                    },
                    "additionalProperties": False,
                },
                "spellcasting": {
                    "type": "object",
                    "properties": {"caster_type": {"type": "string"}},
                    "additionalProperties": False,
                },
                "movement": {
                    "type": "object",
                    "properties": {
                        "walk": {"type": "number"},
                        "climb": {"type": "number"},
                        "fly": {"type": "number"},
                        "swim": {"type": "number"},
                        "burrow": {"type": "number"},
                        "hover": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
                "speed": {
                    "type": "object",
                    "properties": {
                        "walk": {"type": "number"},
                        "climb": {"type": "number"},
                        "fly": {"type": "number"},
                        "swim": {"type": "number"},
                        "burrow": {"type": "number"},
                        "hover": {"type": "boolean"},
                    },
                    "additionalProperties": False,
                },
                "senses": {
                    "type": "object",
                    "properties": {
                        "darkvision": {"type": "number"},
                        "blindsight": {"type": "number"},
                        "tremorsense": {"type": "number"},
                        "truesight": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "legendary": {
                    "type": "object",
                    "properties": {
                        "actions": {"type": "number"},
                        "resistances": {"type": "number"},
                    },
                    "additionalProperties": False,
                },
                "attack_reduction": {"type": "number"},
                # Legacy support fields
                "damage_immunities": {"type": "array", "items": {"type": "string"}},
                "damage_resistances": {"type": "array", "items": {"type": "string"}},
                "damage_vulnerabilities": {"type": "array", "items": {"type": "string"}},
                # YAML anchor support
                "<<": {},  # Allow YAML anchors
            },
            "additionalProperties": False,
        }
    },
    "additionalProperties": False,
}


def validate_yaml_template(template_data: Dict[str, Any]) -> List[str]:
    """
    Validate a YAML template against the schema.

    Args:
        template_data: The parsed YAML template data

    Returns:
        List of validation error messages (empty if valid)
    """
    errors = []

    # Basic structure validation
    if not isinstance(template_data, dict):
        return ["Template must be a dictionary"]

    # Required sections
    if "template" not in template_data:
        errors.append("Missing required 'template' section")

    # Check for common section
    common_section = template_data.get("common")
    if not common_section:
        errors.append("Missing required 'common' section")

    # Validate template section
    if "template" in template_data:
        template_section = template_data["template"]
        if not isinstance(template_section, dict):
            errors.append("'template' section must be a dictionary")
        else:
            # Required fields in template
            for field in ["key", "name", "monsters"]:
                if field not in template_section:
                    errors.append(f"Missing required field 'template.{field}'")

            # Validate monsters array
            if "monsters" in template_section:
                monsters = template_section["monsters"]
                if not isinstance(monsters, list):
                    errors.append("'template.monsters' must be an array")
                else:
                    for i, monster in enumerate(monsters):
                        if not isinstance(monster, dict):
                            errors.append(f"Monster {i} must be a dictionary")
                            continue

                        for field in ["key", "name", "cr"]:
                            if field not in monster:
                                errors.append(
                                    f"Missing required field 'template.monsters[{i}].{field}'"
                                )

                        if "cr" in monster and not isinstance(
                            monster["cr"], (int, float)
                        ):
                            errors.append(
                                f"'template.monsters[{i}].cr' must be a number"
                            )

    # Validate individual monster sections exist
    if "template" in template_data and "monsters" in template_data["template"]:
        for monster in template_data["template"]["monsters"]:
            if isinstance(monster, dict) and "key" in monster:
                monster_key = monster["key"]
                if monster_key not in template_data:
                    errors.append(f"Missing monster section '{monster_key}'")

    return errors


def validate_yaml_template_file(yaml_path: Path) -> List[str]:
    """
    Validate a YAML template file against the schema.

    Args:
        yaml_path: Path to the YAML template file

    Returns:
        List of validation error messages (empty if valid)
    """
    try:
        with open(yaml_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)

        if template_data is None:
            return ["Empty or invalid YAML file"]

        return validate_yaml_template(template_data)

    except yaml.YAMLError as e:
        return [f"YAML parsing error: {e}"]
    except FileNotFoundError:
        return [f"File not found: {yaml_path}"]
    except Exception as e:
        return [f"Unexpected error: {e}"]


def get_all_template_files() -> List[Path]:
    """
    Get all YAML template files in the templates directory.

    Returns:
        List of Path objects for template files
    """
    templates_dir = Path(__file__).parent
    return list(templates_dir.glob("*.yml"))


def validate_all_templates() -> Dict[str, List[str]]:
    """
    Validate all YAML templates in the templates directory.

    Returns:
        Dictionary mapping template names to their validation errors
    """
    results = {}

    for template_path in get_all_template_files():
        errors = validate_yaml_template_file(template_path)
        results[template_path.name] = errors

    return results
