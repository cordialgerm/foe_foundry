from pathlib import Path

from foe_foundry import templates
from foe_foundry.creatures.mimic import MimicTemplate


def test_mimics():
    pamphlets_dir = Path(__file__).parent.parent / "examples" / "pamphlets"
    pamphlets_dir.mkdir(exist_ok=True, parents=True)

    path = pamphlets_dir / f"{MimicTemplate.key}.html"

    templates.render_pamphlet(MimicTemplate, path)
