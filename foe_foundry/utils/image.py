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


def is_grayscaleish(image_path, grayscale_tolerance=10, grayscale_ratio=0.95):
    """
    Determines whether an image is mostly grayscale by checking if R ≈ G ≈ B
    for the majority of pixels.

    Parameters:
        image_path (str): Path to the image file.
        grayscale_tolerance (int): Max allowed difference between RGB channels per pixel.
        grayscale_ratio (float): Proportion of pixels that must be grayscale-like.

    Returns:
        bool: True if the image is mostly grayscale, False otherwise.
    """
    # Load image as RGB and convert to numpy array
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img)

    # Split into R, G, B channels
    r, g, b = arr[..., 0], arr[..., 1], arr[..., 2]

    # Compute max channel difference for each pixel
    # A pixel is grayscale if all its channels are nearly equal (R ≈ G ≈ B)
    max_diff = np.maximum.reduce([np.abs(r - g), np.abs(r - b), np.abs(g - b)])

    # Count the proportion of pixels that are "close enough" to grayscale
    grayscale_pixel_ratio = np.mean(max_diff < grayscale_tolerance)

    # If enough pixels are grayscale-ish, return True
    return grayscale_pixel_ratio > grayscale_ratio
