from pathlib import Path

import numpy as np


class _RandomMask:
    """
    A class to handle random mask selection for homepage elements.
    """

    def __init__(self, mask_count: int):
        self.mask_count = mask_count
        self.last_index = -1
        self.rng = np.random.default_rng()

    def random_mask_css(self) -> str:
        n = self.rng.choice(self.mask_count) + 1
        if n == self.last_index:
            n = (n + 1) % self.mask_count
        self.last_index = n
        return f"masked v{n}"


def _get_mask_count() -> int:
    mask_dir = Path.cwd() / "docs" / "img" / "backgrounds" / "masks"
    # check for webp or png
    mask_count = len(list(mask_dir.glob("*.webp"))) + len(list(mask_dir.glob("*.png")))
    return mask_count


random_mask = _RandomMask(_get_mask_count())  # Default to 10 masks if not specified
