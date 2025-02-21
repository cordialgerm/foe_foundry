import hashlib
from pathlib import Path

import numpy as np
import pytest

from foe_foundry import templates
from foe_foundry.creatures import zombie


def _ids(args: dict) -> str:
    return f"{args['name']}-{args['species_name']}"


@pytest.mark.parametrize("args", zombie.ZombieTemplate.generate_options(), ids=_ids)
def test_zombie_statblocks(args: dict):
    examples_dir = Path(__file__).parent.parent.parent / "examples" / "zombies"
    examples_dir.mkdir(exist_ok=True, parents=True)

    hash_key = _ids(args)

    def rng_factory() -> np.random.Generator:
        bytes = hashlib.sha256(hash_key.encode("utf-8")).digest()
        random_state = int.from_bytes(bytes, byteorder="little")
        return np.random.default_rng(seed=random_state)

    stats = zombie.ZombieTemplate.generate(**args, rng_factory=rng_factory).finalize()
    templates.render_html_inline_page_to_path(stats, examples_dir / f"{stats.key}.html")
