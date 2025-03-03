from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, berserker


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize(
    "settings", berserker.BerserkerTemplate.generate_settings(), ids=_ids
)
def test_berserker_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "berserkers"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats = berserker.BerserkerTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
