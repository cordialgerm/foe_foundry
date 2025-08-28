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


def compare_stats(stats1: BaseStatblock, stats2: BaseStatblock):
    # TODO - implement this properly
    pytest.fail("Implement this!")
