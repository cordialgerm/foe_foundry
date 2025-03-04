from pathlib import Path

import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, SelectionSettings, assassin


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize(
    "settings", assassin.AssassinTemplate.generate_settings(), ids=_ids
)
def test_assassin_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "assassins"
    examples_dir.mkdir(exist_ok=True, parents=True)

    settings = settings.copy(
        selection_settings=SelectionSettings(boost_powers={"overchannel": 5})
    )

    stats = assassin.AssassinTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
