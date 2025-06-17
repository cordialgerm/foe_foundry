from pathlib import Path

import numpy as np
from PIL import Image


def has_transparent_edges(image_path: str | Path, threshold: float = 0.1) -> bool:
    """Check if an image has transparent edges."""

    img = Image.open(image_path).convert("RGBA")
    alpha = np.array(img)[:, :, 3]

    # Define edge width (pixels to check from each side)
    edge_margin = 20

    # Extract edges
    top = alpha[:edge_margin, :]
    bottom = alpha[-edge_margin:, :]
    left = alpha[:, :edge_margin]
    right = alpha[:, -edge_margin:]

    # Combine all edges
    edge_pixels = np.concatenate(
        [top.flatten(), bottom.flatten(), left.flatten(), right.flatten()]
    )

    # Count how many are "transparent enough"
    transparent_ratio = np.sum(edge_pixels < 30) / len(edge_pixels)

    return bool(transparent_ratio > threshold)
