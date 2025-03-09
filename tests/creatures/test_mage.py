from pathlib import Path

import numpy as np
import pytest

from foe_foundry import templates
from foe_foundry.creatures import GenerationSettings, SelectionSettings, mage


def _ids(settings: GenerationSettings) -> str:
    return settings.id


@pytest.mark.parametrize("settings", mage.MageTemplate.generate_settings(), ids=_ids)
def test_mage_statblocks(settings: GenerationSettings):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "mages"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats = mage.MageTemplate.generate(settings).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")


def test_elementalist():
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "mages"
    examples_dir.mkdir(exist_ok=True, parents=True)
    stats_wip = mage.MageTemplate.generate(
        settings=GenerationSettings(
            creature_name="Test Pyromancer",
            cr=4,
            variant=mage.MageVariant,
            rng=np.random.default_rng(),
            is_legendary=False,
            selection_settings=SelectionSettings(
                boost_powers={"Pyromancer": 10},
            ),
        )
    )
    assert "Pyromancer" in {p.name for p in stats_wip.powers.selection.selected_powers}
    stats = stats_wip.finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
