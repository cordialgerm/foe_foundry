from pathlib import Path

import pytest

from foe_foundry import templates2
from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
    all_templates_and_settings,
)


def templates_with_lore() -> list[CreatureTemplate]:
    templates = {
        template
        for template, settings in all_templates_and_settings()
        if template.lore_md.strip() != ""
    }
    templates = list(templates)
    templates.sort(key=lambda t: t.key)
    return templates


def theme_templates() -> list[str]:
    dir = Path(__file__).parent.parent / "content" / "themes"
    return [f.stem for f in dir.glob("*.md")]


def _ids(t: CreatureTemplate) -> str:
    return t.key


def _ids2(obj: tuple[CreatureTemplate, GenerationSettings]) -> str:
    template, settings = obj
    return f"{template.key}/{settings.id}"


@pytest.mark.parametrize("template", templates_with_lore(), ids=_ids)
def test_all_monster_pamphlets(template: CreatureTemplate):
    pamphlets_dir = Path(__file__).parent.parent / "examples" / "monsters"
    pamphlets_dir.mkdir(exist_ok=True, parents=True)
    path = pamphlets_dir / f"{template.key}.html"
    templates2.render_creature_template_pamphlet(template, path)


@pytest.mark.parametrize("theme", theme_templates())
def test_all_theme_pamphlets(theme: str):
    pamphlets_dir = Path(__file__).parent.parent / "examples" / "themes"
    pamphlets_dir.mkdir(exist_ok=True, parents=True)
    path = pamphlets_dir / f"{theme}.html"
    templates2.render_theme_pamphlet(theme, path)


@pytest.mark.parametrize(
    "template_and_setting", all_templates_and_settings(), ids=_ids2
)
def test_all_statblocks(
    template_and_setting: tuple[CreatureTemplate, GenerationSettings],
):
    template, settings = template_and_setting
    stats = template.generate(settings).finalize()

    pamphlets_dir = Path(__file__).parent.parent / "examples" / "statblocks"
    pamphlets_dir.mkdir(exist_ok=True, parents=True)
    path = pamphlets_dir / f"{stats.key}.html"

    templates2.render_statblock_pamphlet(stats, path)
