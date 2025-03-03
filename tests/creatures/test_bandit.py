from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, bandit


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize(
    "settings", bandit.BanditTemplate.generate_settings(), ids=_ids
)
def test_bandit_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "bandits"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats = bandit.BanditTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
