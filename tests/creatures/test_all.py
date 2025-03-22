from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import (
    CreatureTemplate,
    GenerationSettings,
    all_templates_and_settings,
)


def _ids(obj: tuple[CreatureTemplate, GenerationSettings]) -> str:
    template, settings = obj
    return f"{template.key}/{settings.id}"


@pytest.mark.parametrize("template_and_setting", all_templates_and_settings(), ids=_ids)
def test_all_statblocks(
    template_and_setting: tuple[CreatureTemplate, GenerationSettings],
):
    template, settings = template_and_setting

    examples_dir = (
        Path(__file__).parent.parent.parent / "examples" / settings.creature_template
    )
    examples_dir.mkdir(exist_ok=True, parents=True)

    stats = template.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
