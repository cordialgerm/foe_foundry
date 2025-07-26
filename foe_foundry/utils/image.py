from collections import Counter, defaultdict
from pathlib import Path
from typing import Optional

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


def get_dominant_edge_color(
    image_path: str | Path,
    edge_thickness: float = 0.05,
    threshold: float = 0.1,
    quant_level: int = 8,
) -> Optional[str]:
    """
    Finds the most common edge color by quantizing into bins, then returning
    the mode of the most common bin.

    Args:
        image_path (str | Path): Path to image.
        edge_thickness (float): % of width/height to use as edge.
        threshold (float): Minimum fraction to consider a color dominant.
        quant_level (int): Quantization level (e.g., 8 -> RGB values rounded to nearest 8).

    Returns:
        Hex string (e.g., '#aabbcc') of the dominant color, or None if no dominant color found.
    """

    if has_transparent_edges(image_path):
        return None

    img = Image.open(image_path).convert("RGB")
    np_img = np.array(img)
    h, w, _ = np_img.shape

    # Use separate thickness for each axis
    t_h = max(1, int(h * edge_thickness))
    t_w = max(1, int(w * edge_thickness))

    # Top and bottom edges (full width)
    top = np_img[:t_h, :, :]
    bottom = np_img[-t_h:, :, :]

    # Left and right edges (excluding corners already in top/bottom)
    left = (
        np_img[t_h:-t_h, :t_w, :]
        if h > 2 * t_h
        else np.empty((0, t_w, 3), dtype=np_img.dtype)
    )
    right = (
        np_img[t_h:-t_h, -t_w:, :]
        if h > 2 * t_h
        else np.empty((0, t_w, 3), dtype=np_img.dtype)
    )

    edge_pixels = np.concatenate(
        [
            top.reshape(-1, 3),
            bottom.reshape(-1, 3),
            left.reshape(-1, 3),
            right.reshape(-1, 3),
        ],
        axis=0,
    )

    # Group into quantized buckets
    buckets = defaultdict(list)
    for pixel in edge_pixels:
        q = tuple((pixel // quant_level) * quant_level)
        buckets[q].append(tuple(pixel))

    # Find the dominant bucket
    bucket_counts = {k: len(v) for k, v in buckets.items()}
    dominant_bucket, count = max(bucket_counts.items(), key=lambda x: x[1])

    if count / edge_pixels.shape[0] < threshold:
        return None  # no dominant color

    # Return the mode of the dominant bucket as a hex string
    pixel_counts = Counter(buckets[dominant_bucket])
    rgb = pixel_counts.most_common(1)[0][0]
    return "#{:02x}{:02x}{:02x}".format(*rgb)
