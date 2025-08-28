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
        Path(__file__).parent.parent.parent / "foe_foundry" / "creatures" / "templates"
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
def test_yaml_template_comparison(template: MonsterTemplate):
    """Test that YAML templates produce exactly equivalent statblocks to original templates."""
    key = template.key
    template_path = (
        Path.cwd() / "foe_foundry" / "creatures" / "templates" / f"{key}.yml"
    )
    if not template_path.exists():
        pytest.skip(f"Template file not found: {template_path}")

    template_data = load_yaml_template_data(template_path)
    yaml_template = YamlMonsterTemplate(template_data)

    base_stats = {}
    for _, _, _, stats in template.generate_all():
        base_stats[stats.stats.key] = stats.stats

    new_stats = {}
    for _, _, _, stats in yaml_template.generate_all():
        new_stats[stats.stats.key] = stats.stats

    # Check that we have the same set of stats keys
    assert set(base_stats.keys()) == set(new_stats.keys()), f"Mismatched stat keys for template {key}"

    # Check exact equality for each statblock
    for key, base_stat in base_stats.items():
        assert key in new_stats, f"Missing stats for key {key} in YAML template"
        new_stat = new_stats[key]
        
        # Use exact equality comparison
        assert compare_stats(base_stat, new_stat), f"Stats mismatch for key {key} - statblocks are not exactly equivalent"


def compare_stats(stats1: BaseStatblock, stats2: BaseStatblock) -> bool:
    """
    Compare two statblocks for exact equivalence.
    
    This function checks that ALL fields match exactly between the two statblocks.
    
    Returns:
        True if the statblocks are exactly equivalent
    """
    # Core identity fields
    if stats1.name != stats2.name:
        print(f"Name mismatch: {stats1.name} != {stats2.name}")
        return False
    if stats1.template_key != stats2.template_key:
        print(f"Template key mismatch: {stats1.template_key} != {stats2.template_key}")
        return False
    if stats1.variant_key != stats2.variant_key:
        print(f"Variant key mismatch: {stats1.variant_key} != {stats2.variant_key}")
        return False
    if stats1.monster_key != stats2.monster_key:
        print(f"Monster key mismatch: {stats1.monster_key} != {stats2.monster_key}")
        return False
    if stats1.species_key != stats2.species_key:
        print(f"Species key mismatch: {stats1.species_key} != {stats2.species_key}")
        return False
    
    # Challenge rating and hit points
    if stats1.cr != stats2.cr:
        print(f"CR mismatch: {stats1.cr} != {stats2.cr}")
        return False
    if stats1.hp != stats2.hp:
        print(f"HP mismatch: {stats1.hp} != {stats2.hp}")
        return False
    
    # Creature type information
    if stats1.creature_type != stats2.creature_type:
        print(f"Creature type mismatch: {stats1.creature_type} != {stats2.creature_type}")
        return False
    if stats1.creature_subtype != stats2.creature_subtype:
        print(f"Creature subtype mismatch: {stats1.creature_subtype} != {stats2.creature_subtype}")
        return False
    if stats1.creature_class != stats2.creature_class:
        print(f"Creature class mismatch: {stats1.creature_class} != {stats2.creature_class}")
        return False
    if stats1.additional_types != stats2.additional_types:
        print(f"Additional types mismatch: {stats1.additional_types} != {stats2.additional_types}")
        return False
    
    # Role information
    if stats1.role != stats2.role:
        print(f"Role mismatch: {stats1.role} != {stats2.role}")
        return False
    if stats1.additional_roles != stats2.additional_roles:
        print(f"Additional roles mismatch: {stats1.additional_roles} != {stats2.additional_roles}")
        return False
    
    # Speed, size, senses, languages
    if stats1.speed != stats2.speed:
        print(f"Speed mismatch: {stats1.speed} != {stats2.speed}")
        return False
    if stats1.has_unique_movement_manipulation != stats2.has_unique_movement_manipulation:
        print(f"Movement manipulation mismatch: {stats1.has_unique_movement_manipulation} != {stats2.has_unique_movement_manipulation}")
        return False
    if stats1.size != stats2.size:
        print(f"Size mismatch: {stats1.size} != {stats2.size}")
        return False
    if stats1.senses != stats2.senses:
        print(f"Senses mismatch: {stats1.senses} != {stats2.senses}")
        return False
    if stats1.languages != stats2.languages:
        print(f"Languages mismatch: {stats1.languages} != {stats2.languages}")
        return False
    
    # Armor class
    if stats1.ac_templates != stats2.ac_templates:
        print(f"AC templates mismatch: {stats1.ac_templates} != {stats2.ac_templates}")
        return False
    if stats1.ac_boost != stats2.ac_boost:
        print(f"AC boost mismatch: {stats1.ac_boost} != {stats2.ac_boost}")
        return False
    if stats1.uses_shield != stats2.uses_shield:
        print(f"Uses shield mismatch: {stats1.uses_shield} != {stats2.uses_shield}")
        return False
    
    # Damage vulnerabilities, resistances, immunities
    if stats1.damage_vulnerabilities != stats2.damage_vulnerabilities:
        print(f"Damage vulnerabilities mismatch: {stats1.damage_vulnerabilities} != {stats2.damage_vulnerabilities}")
        return False
    if stats1.damage_resistances != stats2.damage_resistances:
        print(f"Damage resistances mismatch: {stats1.damage_resistances} != {stats2.damage_resistances}")
        return False
    if stats1.damage_immunities != stats2.damage_immunities:
        print(f"Damage immunities mismatch: {stats1.damage_immunities} != {stats2.damage_immunities}")
        return False
    if stats1.condition_immunities != stats2.condition_immunities:
        print(f"Condition immunities mismatch: {stats1.condition_immunities} != {stats2.condition_immunities}")
        return False
    if stats1.nonmagical_resistance != stats2.nonmagical_resistance:
        print(f"Nonmagical resistance mismatch: {stats1.nonmagical_resistance} != {stats2.nonmagical_resistance}")
        return False
    if stats1.nonmagical_immunity != stats2.nonmagical_immunity:
        print(f"Nonmagical immunity mismatch: {stats1.nonmagical_immunity} != {stats2.nonmagical_immunity}")
        return False
    
    # Attributes and ability scores
    if stats1.primary_attribute_score != stats2.primary_attribute_score:
        print(f"Primary attribute score mismatch: {stats1.primary_attribute_score} != {stats2.primary_attribute_score}")
        return False
    if stats1.attributes != stats2.attributes:
        print(f"Attributes mismatch: {stats1.attributes} != {stats2.attributes}")
        return False
    if stats1.difficulty_class_modifier != stats2.difficulty_class_modifier:
        print(f"DC modifier mismatch: {stats1.difficulty_class_modifier} != {stats2.difficulty_class_modifier}")
        return False
    
    # Attack information
    if stats1.attack != stats2.attack:
        print(f"Attack mismatch: {stats1.attack} != {stats2.attack}")
        return False
    if stats1.additional_attacks != stats2.additional_attacks:
        print(f"Additional attacks mismatch: {stats1.additional_attacks} != {stats2.additional_attacks}")
        return False
    if stats1.damage_modifier != stats2.damage_modifier:
        print(f"Damage modifier mismatch: {stats1.damage_modifier} != {stats2.damage_modifier}")
        return False
    if stats1.base_attack_damage != stats2.base_attack_damage:
        print(f"Base attack damage mismatch: {stats1.base_attack_damage} != {stats2.base_attack_damage}")
        return False
    if stats1.multiattack != stats2.multiattack:
        print(f"Multiattack mismatch: {stats1.multiattack} != {stats2.multiattack}")
        return False
    if stats1.multiattack_benchmark != stats2.multiattack_benchmark:
        print(f"Multiattack benchmark mismatch: {stats1.multiattack_benchmark} != {stats2.multiattack_benchmark}")
        return False
    if stats1.multiattack_custom_text != stats2.multiattack_custom_text:
        print(f"Multiattack custom text mismatch: {stats1.multiattack_custom_text} != {stats2.multiattack_custom_text}")
        return False
    if stats1.primary_damage_type != stats2.primary_damage_type:
        print(f"Primary damage type mismatch: {stats1.primary_damage_type} != {stats2.primary_damage_type}")
        return False
    if stats1.secondary_damage_type != stats2.secondary_damage_type:
        print(f"Secondary damage type mismatch: {stats1.secondary_damage_type} != {stats2.secondary_damage_type}")
        return False
    
    # Reactions
    if stats1.reaction_count != stats2.reaction_count:
        print(f"Reaction count mismatch: {stats1.reaction_count} != {stats2.reaction_count}")
        return False
    
    # Powers and selection
    if stats1.recommended_powers_modifier != stats2.recommended_powers_modifier:
        print(f"Recommended powers modifier mismatch: {stats1.recommended_powers_modifier} != {stats2.recommended_powers_modifier}")
        return False
    if stats1.selection_target_args != stats2.selection_target_args:
        print(f"Selection target args mismatch: {stats1.selection_target_args} != {stats2.selection_target_args}")
        return False
    if stats1.flags != stats2.flags:
        print(f"Flags mismatch: {stats1.flags} != {stats2.flags}")
        return False
    
    # Spellcasting
    if stats1.caster_type != stats2.caster_type:
        print(f"Caster type mismatch: {stats1.caster_type} != {stats2.caster_type}")
        return False
    if stats1.spells != stats2.spells:
        print(f"Spells mismatch: {stats1.spells} != {stats2.spells}")
        return False
    
    # Legendary creature features
    if stats1.is_legendary != stats2.is_legendary:
        print(f"Is legendary mismatch: {stats1.is_legendary} != {stats2.is_legendary}")
        return False
    if stats1.has_lair != stats2.has_lair:
        print(f"Has lair mismatch: {stats1.has_lair} != {stats2.has_lair}")
        return False
    if stats1.legendary_actions != stats2.legendary_actions:
        print(f"Legendary actions mismatch: {stats1.legendary_actions} != {stats2.legendary_actions}")
        return False
    if stats1.legendary_resistances != stats2.legendary_resistances:
        print(f"Legendary resistances mismatch: {stats1.legendary_resistances} != {stats2.legendary_resistances}")
        return False
    if stats1.legendary_resistance_damage_taken != stats2.legendary_resistance_damage_taken:
        print(f"Legendary resistance damage taken mismatch: {stats1.legendary_resistance_damage_taken} != {stats2.legendary_resistance_damage_taken}")
        return False
    
    return True


@pytest.mark.parametrize("template", base_templates(), ids=lambda t: t.key)
def test_yaml_template_meaningful_comparison(template: MonsterTemplate):
    """Test that YAML templates produce meaningfully equivalent statblocks to original templates."""
    key = template.key
    template_path = (
        Path.cwd() / "foe_foundry" / "creatures" / "templates" / f"{key}.yml"
    )
    if not template_path.exists():
        pytest.skip(f"Template file not found: {template_path}")

    template_data = load_yaml_template_data(template_path)
    yaml_template = YamlMonsterTemplate(template_data)

    base_stats = {}
    for _, _, _, stats in template.generate_all():
        base_stats[stats.stats.key] = stats.stats

    new_stats = {}
    for _, _, _, stats in yaml_template.generate_all():
        new_stats[stats.stats.key] = stats.stats

    # Check that we have reasonable coverage
    assert len(new_stats) > 0, f"No stats generated for YAML template {key}"
    
    # For each YAML-generated stat, try to find a reasonable match in the base stats
    for yaml_key, yaml_stat in new_stats.items():
        found_match = False
        for base_key, base_stat in base_stats.items():
            if compare_stats(base_stat, yaml_stat):
                found_match = True
                break
        
        if not found_match:
            # Try to provide helpful information about what didn't match
            similar_cr_stats = [s for s in base_stats.values() if s.cr == yaml_stat.cr]
            if similar_cr_stats:
                pytest.fail(f"No meaningful match found for YAML stat {yaml_key} (CR {yaml_stat.cr}). "
                          f"Found {len(similar_cr_stats)} base stats with same CR but none matched meaningfully.")
            else:
                pytest.fail(f"No meaningful match found for YAML stat {yaml_key} (CR {yaml_stat.cr}). "
                          f"No base stats found with matching CR.")
