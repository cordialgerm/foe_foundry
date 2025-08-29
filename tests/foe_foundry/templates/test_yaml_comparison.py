from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from foe_foundry.creatures import AllTemplates, MonsterTemplate, YamlMonsterTemplate
from foe_foundry.statblocks import BaseStatblock


def yaml_templates() -> list[Path]:
    """
    Fixture to get all YAML template files.
    """
    templates_dir = (
        Path(__file__).parent.parent.parent.parent
        / "foe_foundry"
        / "creatures"
        / "templates"
    )
    if not templates_dir.exists():
        templates_dir = Path(
            "/home/runner/work/foe_foundry/foe_foundry/foe_foundry/creatures/templates"
        )
    return list(templates_dir.glob("*.yml"))


def load_yaml_template_data(yaml_path: Path) -> Dict[str, Any]:
    """Load YAML template data from file."""
    with open(yaml_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def base_templates() -> list[MonsterTemplate]:
    return AllTemplates


@pytest.mark.parametrize("template", base_templates(), ids=lambda t: t.key)
def test_yaml_template_exact_comparison(template: MonsterTemplate):
    """
    Test that YAML templates produce exactly equivalent statblocks to original Python templates.

    This test ensures complete parity between Python imperative templates and YAML declarative templates:
    - Verifies that a YAML template file exists for each Python template
    - Compares all generated statblocks for exact field-by-field equality
    - Provides detailed failure information for any mismatches
    """
    key = template.key
    template_path = (
        Path.cwd() / "foe_foundry" / "creatures" / "templates" / f"{key}.yml"
    )
    if not template_path.exists():
        pytest.skip(f"Template file not found: {template_path}")

    template_data = load_yaml_template_data(template_path)
    yaml_template = YamlMonsterTemplate(template_data)

    base_stats = {}
    for _, _, _, generated_stats in template.generate_all():
        base_stat = generated_stats.stats
        base_stats[base_stat.key] = base_stat

    new_stats = {}
    for _, _, _, generated_stats in yaml_template.generate_all():
        new_stat = generated_stats.stats
        new_stats[new_stat.key] = new_stat

    # Check that we have the same set of stats keys
    assert set(base_stats.keys()) == set(new_stats.keys()), (
        f"Mismatched stat keys for template {key}"
    )

    # Check exact equality for each statblock
    for stat_key, base_stat in base_stats.items():
        assert stat_key in new_stats, (
            f"Missing stats for key {stat_key} in YAML template"
        )
        new_stat = new_stats[stat_key]

        # Use exact equality comparison with detailed error message
        mismatch_reason = compare_stats(base_stat, new_stat)
        assert mismatch_reason is None, (
            f"Stats mismatch for key {stat_key}: {mismatch_reason}"
        )


def compare_stats(stats1: BaseStatblock, stats2: BaseStatblock) -> str | None:
    """
    Compare two statblocks for exact equivalence.

    This function checks that ALL fields match exactly between the two statblocks.
    Provides detailed breakdown of differences for complex objects.

    Returns:
        None if the statblocks are exactly equivalent, otherwise a string describing the mismatch
    """
    
    def _detailed_attributes_diff(attr1, attr2):
        """Compare Attributes objects and highlight specific differences."""
        diffs = []
        if attr1.STR != attr2.STR:
            diffs.append(f"STR: {attr1.STR} vs {attr2.STR}")
        if attr1.DEX != attr2.DEX:
            diffs.append(f"DEX: {attr1.DEX} vs {attr2.DEX}")
        if attr1.CON != attr2.CON:
            diffs.append(f"CON: {attr1.CON} vs {attr2.CON}")
        if attr1.INT != attr2.INT:
            diffs.append(f"INT: {attr1.INT} vs {attr2.INT}")
        if attr1.WIS != attr2.WIS:
            diffs.append(f"WIS: {attr1.WIS} vs {attr2.WIS}")
        if attr1.CHA != attr2.CHA:
            diffs.append(f"CHA: {attr1.CHA} vs {attr2.CHA}")
        if attr1.proficiency != attr2.proficiency:
            diffs.append(f"proficiency: {attr1.proficiency} vs {attr2.proficiency}")
        if attr1.proficient_saves != attr2.proficient_saves:
            diffs.append(f"proficient_saves: {_set_diff_details(attr1.proficient_saves, attr2.proficient_saves)}")
        if attr1.proficient_skills != attr2.proficient_skills:
            diffs.append(f"proficient_skills: {_set_diff_details(attr1.proficient_skills, attr2.proficient_skills)}")
        if attr1.expertise_skills != attr2.expertise_skills:
            diffs.append(f"expertise_skills: {_set_diff_details(attr1.expertise_skills, attr2.expertise_skills)}")
        
        return " | ".join(diffs) if diffs else "unknown difference"
    
    def _set_diff_details(set1, set2):
        """Show detailed differences between two sets."""
        if set1 == set2:
            return "identical"
        
        added = set2 - set1
        removed = set1 - set2
        parts = []
        if added:
            parts.append(f"added: {added}")
        if removed:
            parts.append(f"removed: {removed}")
        return f"({', '.join(parts)})"
    # Core identity fields
    if stats1.name != stats2.name:
        return f"name mismatch: '{stats1.name}' != '{stats2.name}'"
    if stats1.template_key != stats2.template_key:
        return (
            f"template_key mismatch: '{stats1.template_key}' != '{stats2.template_key}'"
        )
    if stats1.variant_key != stats2.variant_key:
        return f"variant_key mismatch: '{stats1.variant_key}' != '{stats2.variant_key}'"
    if stats1.monster_key != stats2.monster_key:
        return f"monster_key mismatch: '{stats1.monster_key}' != '{stats2.monster_key}'"
    if stats1.species_key != stats2.species_key:
        return f"species_key mismatch: '{stats1.species_key}' != '{stats2.species_key}'"

    # Challenge rating and hit points
    if stats1.cr != stats2.cr:
        return f"cr mismatch: {stats1.cr} != {stats2.cr}"
    if stats1.hp != stats2.hp:
        return f"hp mismatch: {stats1.hp} != {stats2.hp}"

    # Creature type information
    if stats1.creature_type != stats2.creature_type:
        return (
            f"creature_type mismatch: {stats1.creature_type} != {stats2.creature_type}"
        )
    if stats1.creature_subtype != stats2.creature_subtype:
        return f"creature_subtype mismatch: '{stats1.creature_subtype}' != '{stats2.creature_subtype}'"
    if stats1.creature_class != stats2.creature_class:
        return f"creature_class mismatch: '{stats1.creature_class}' != '{stats2.creature_class}'"
    if stats1.additional_types != stats2.additional_types:
        return f"additional_types mismatch: {_set_diff_details(stats1.additional_types, stats2.additional_types)}"

    # Role information
    if stats1.role != stats2.role:
        return f"role mismatch: {stats1.role} != {stats2.role}"
    if stats1.additional_roles != stats2.additional_roles:
        return f"additional_roles mismatch: {_set_diff_details(stats1.additional_roles, stats2.additional_roles)}"

    # Speed, size, senses, languages
    if stats1.speed != stats2.speed:
        return f"speed mismatch: {stats1.speed} != {stats2.speed}"
    if (
        stats1.has_unique_movement_manipulation
        != stats2.has_unique_movement_manipulation
    ):
        return f"has_unique_movement_manipulation mismatch: {stats1.has_unique_movement_manipulation} != {stats2.has_unique_movement_manipulation}"
    if stats1.size != stats2.size:
        return f"size mismatch: {stats1.size} != {stats2.size}"
    if stats1.senses != stats2.senses:
        return f"senses mismatch: {stats1.senses} != {stats2.senses}"
    if stats1.languages != stats2.languages:
        return f"languages mismatch: {stats1.languages} != {stats2.languages}"

    # Armor class
    if stats1.ac_templates != stats2.ac_templates:
        return f"ac_templates mismatch: {stats1.ac_templates} != {stats2.ac_templates}"
    if stats1.ac_boost != stats2.ac_boost:
        return f"ac_boost mismatch: {stats1.ac_boost} != {stats2.ac_boost}"
    if stats1.uses_shield != stats2.uses_shield:
        return f"uses_shield mismatch: {stats1.uses_shield} != {stats2.uses_shield}"

    # Damage vulnerabilities, resistances, immunities
    if stats1.damage_vulnerabilities != stats2.damage_vulnerabilities:
        return f"damage_vulnerabilities mismatch: {_set_diff_details(stats1.damage_vulnerabilities, stats2.damage_vulnerabilities)}"
    if stats1.damage_resistances != stats2.damage_resistances:
        return f"damage_resistances mismatch: {_set_diff_details(stats1.damage_resistances, stats2.damage_resistances)}"
    if stats1.damage_immunities != stats2.damage_immunities:
        return f"damage_immunities mismatch: {_set_diff_details(stats1.damage_immunities, stats2.damage_immunities)}"
    if stats1.condition_immunities != stats2.condition_immunities:
        return f"condition_immunities mismatch: {_set_diff_details(stats1.condition_immunities, stats2.condition_immunities)}"
    if stats1.nonmagical_resistance != stats2.nonmagical_resistance:
        return f"nonmagical_resistance mismatch: {stats1.nonmagical_resistance} != {stats2.nonmagical_resistance}"
    if stats1.nonmagical_immunity != stats2.nonmagical_immunity:
        return f"nonmagical_immunity mismatch: {stats1.nonmagical_immunity} != {stats2.nonmagical_immunity}"

    # Attributes and ability scores
    if stats1.primary_attribute_score != stats2.primary_attribute_score:
        return f"primary_attribute_score mismatch: {stats1.primary_attribute_score} != {stats2.primary_attribute_score}"
    if stats1.attributes != stats2.attributes:
        return f"attributes mismatch: {_detailed_attributes_diff(stats1.attributes, stats2.attributes)}"
    if stats1.difficulty_class_modifier != stats2.difficulty_class_modifier:
        return f"difficulty_class_modifier mismatch: {stats1.difficulty_class_modifier} != {stats2.difficulty_class_modifier}"

    # Attack information
    if stats1.attack != stats2.attack:
        return f"attack mismatch: {stats1.attack} != {stats2.attack}"
    if stats1.additional_attacks != stats2.additional_attacks:
        return f"additional_attacks mismatch: {stats1.additional_attacks} != {stats2.additional_attacks}"
    if stats1.damage_modifier != stats2.damage_modifier:
        return f"damage_modifier mismatch: {stats1.damage_modifier} != {stats2.damage_modifier}"
    if stats1.base_attack_damage != stats2.base_attack_damage:
        return f"base_attack_damage mismatch: {stats1.base_attack_damage} != {stats2.base_attack_damage}"
    if stats1.multiattack != stats2.multiattack:
        return f"multiattack mismatch: {stats1.multiattack} != {stats2.multiattack}"
    if stats1.multiattack_benchmark != stats2.multiattack_benchmark:
        return f"multiattack_benchmark mismatch: {stats1.multiattack_benchmark} != {stats2.multiattack_benchmark}"
    if stats1.multiattack_custom_text != stats2.multiattack_custom_text:
        return f"multiattack_custom_text mismatch: '{stats1.multiattack_custom_text}' != '{stats2.multiattack_custom_text}'"
    if stats1.primary_damage_type != stats2.primary_damage_type:
        return f"primary_damage_type mismatch: {stats1.primary_damage_type} != {stats2.primary_damage_type}"
    if stats1.secondary_damage_type != stats2.secondary_damage_type:
        return f"secondary_damage_type mismatch: {stats1.secondary_damage_type} != {stats2.secondary_damage_type}"

    # Reactions
    if stats1.reaction_count != stats2.reaction_count:
        return f"reaction_count mismatch: {stats1.reaction_count} != {stats2.reaction_count}"

    # Powers and selection
    if stats1.recommended_powers_modifier != stats2.recommended_powers_modifier:
        return f"recommended_powers_modifier mismatch: {stats1.recommended_powers_modifier} != {stats2.recommended_powers_modifier}"
    if stats1.selection_target_args != stats2.selection_target_args:
        return f"selection_target_args mismatch: {stats1.selection_target_args} != {stats2.selection_target_args}"
    if stats1.flags != stats2.flags:
        return f"flags mismatch: {_set_diff_details(stats1.flags, stats2.flags)}"

    # Spellcasting
    if stats1.caster_type != stats2.caster_type:
        return f"caster_type mismatch: {stats1.caster_type} != {stats2.caster_type}"
    if stats1.spells != stats2.spells:
        return f"spells mismatch: {stats1.spells} != {stats2.spells}"

    # Legendary creature features
    if stats1.is_legendary != stats2.is_legendary:
        return f"is_legendary mismatch: {stats1.is_legendary} != {stats2.is_legendary}"
    if stats1.has_lair != stats2.has_lair:
        return f"has_lair mismatch: {stats1.has_lair} != {stats2.has_lair}"
    if stats1.legendary_actions != stats2.legendary_actions:
        return f"legendary_actions mismatch: {stats1.legendary_actions} != {stats2.legendary_actions}"
    if stats1.legendary_resistances != stats2.legendary_resistances:
        return f"legendary_resistances mismatch: {stats1.legendary_resistances} != {stats2.legendary_resistances}"
    if (
        stats1.legendary_resistance_damage_taken
        != stats2.legendary_resistance_damage_taken
    ):
        return f"legendary_resistance_damage_taken mismatch: {stats1.legendary_resistance_damage_taken} != {stats2.legendary_resistance_damage_taken}"

    return None


def test_template_coverage():
    """
    Verify that YAML and Python templates have complete bidirectional coverage.

    This test ensures:
    - Every Python template has a corresponding YAML template file
    - Every YAML template file has a corresponding Python template
    """
    # Get all Python templates
    python_templates = {t.key for t in base_templates()}

    # Get all YAML template files
    yaml_files = yaml_templates()
    yaml_template_keys = {path.stem for path in yaml_files}

    # Check Python -> YAML coverage
    missing_yaml = python_templates - yaml_template_keys
    if missing_yaml:
        pytest.fail(f"Python templates missing YAML files: {sorted(missing_yaml)}")

    # Check YAML -> Python coverage
    missing_python = yaml_template_keys - python_templates
    if missing_python:
        pytest.fail(
            f"YAML template files missing Python templates: {sorted(missing_python)}"
        )

    # All templates should have bidirectional coverage
    assert python_templates == yaml_template_keys, (
        "Template coverage mismatch between Python and YAML implementations"
    )
