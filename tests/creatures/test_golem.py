from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, golem


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize("settings", golem.GolemTemplate.generate_settings(), ids=_ids)
def test_golem_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "golems"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats = golem.GolemTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
