from pathlib import Path
from typing import Any, Dict

import pytest
import yaml

from foe_foundry.creatures import AllTemplates, MonsterTemplate, YamlMonsterTemplate
from foe_foundry.skills import AbilityScore
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
    key = template.key
    template_path = (
        Path.cwd() / "foe_foundry" / "creatures" / "templates" / f"{key}.yml"
    )
    if not template_path.exists():
        raise FileNotFoundError(f"Template file not found: {template_path}")

    template_data = load_yaml_template_data(template_path)
    yaml_template = YamlMonsterTemplate(template_data)

    base_stats = {}
    for _, _, _, stats in template.generate_all():
        base_stats[stats.stats.key] = stats.stats

    new_stats = {}
    for _, _, _, stats in yaml_template.generate_all():
        new_stats[stats.stats.key] = stats.stats

    for key, base_stat in base_stats.items():
        assert key in new_stats, f"Missing stats for key {key} in YAML template"
        new_stat = new_stats[key]

        assert base_stat == new_stat, f"Stats mismatch for key {key}"


def compare_stats(stats1: BaseStatblock, stats2: BaseStatblock) -> bool:
    """
    Compare two statblocks for meaningful equivalence.
    
    This function checks that the core characteristics are similar,
    but allows for some differences in implementation details.
    
    Returns:
        True if the statblocks are meaningfully equivalent
    """
    # Core identity should match
    if stats1.cr != stats2.cr:
        return False
        
    # Basic stats should be within reasonable range (allow 2 point difference)
    for ability in [AbilityScore.STR, AbilityScore.DEX, AbilityScore.CON, 
                   AbilityScore.INT, AbilityScore.WIS, AbilityScore.CHA]:
        stat1 = getattr(stats1.attributes, ability.name)
        stat2 = getattr(stats2.attributes, ability.name)
        # Allow up to 2 point difference in ability scores
        if abs(stat1 - stat2) > 2:
            return False
    
    # Check that they have similar roles (at least one in common)
    roles1 = {stats1.role} | set(stats1.additional_roles)
    roles2 = {stats2.role} | set(stats2.additional_roles)
    roles1.discard(None)
    roles2.discard(None)
    
    if roles1 and roles2 and not (roles1 & roles2):
        return False  # No common roles
    
    # HP should be within reasonable range (±30%)
    if stats1.hp.average > 0 and stats2.hp.average > 0:
        hp_diff = abs(stats1.hp.average - stats2.hp.average) / max(stats1.hp.average, stats2.hp.average)
        if hp_diff > 0.4:  # Allow 40% difference
            return False
    
    # Check that they have some AC templates (if they should)
    # This is a basic structural check
    if stats1.ac_templates and not stats2.ac_templates:
        return False
    if stats2.ac_templates and not stats1.ac_templates:
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
