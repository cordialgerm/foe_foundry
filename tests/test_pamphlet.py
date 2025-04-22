from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import CreatureTemplate, all_templates_and_settings


def templates_with_lore() -> list[CreatureTemplate]:
    templates = {
        template
        for template, settings in all_templates_and_settings()
        if template.lore_md.strip() != ""
    }
    templates = list(templates)
    templates.sort(key=lambda t: t.key)
    return templates


def _ids(t: CreatureTemplate) -> str:
    return t.key


@pytest.mark.parametrize("template", templates_with_lore(), ids=_ids)
def test_all_pamphlets(template: CreatureTemplate):
    pamphlets_dir = Path(__file__).parent.parent / "examples" / "pamphlets"
    pamphlets_dir.mkdir(exist_ok=True, parents=True)
    path = pamphlets_dir / f"{template.key}.html"
    templates.render_pamphlet(template, path)
