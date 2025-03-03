from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, priest


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize(
    "settings", priest.PriestTemplate.generate_settings(), ids=_ids
)
def test_priest_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "priests"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats = priest.PriestTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
