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
    return bool(grayscale_pixel_ratio > grayscale_ratio)


def get_dominant_edge_color(
    image_path: str | Path,
    edge_thickness: float = 0.05,
    threshold: float = 0.1,
    quant_level: int = 8,
    ignore_white: bool = True,
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

    # Vectorized quantization of all edge pixels
    quantized = (edge_pixels // quant_level) * quant_level
    # Find unique quantized colors and their counts
    q_colors, q_counts = np.unique(quantized, axis=0, return_counts=True)
    dominant_idx = np.argmax(q_counts)
    dominant_bucket = q_colors[dominant_idx]
    count = q_counts[dominant_idx]

    if count / edge_pixels.shape[0] < threshold:
        return None  # no dominant color

    # Find all pixels in the dominant bucket
    mask = np.all(quantized == dominant_bucket, axis=1)
    bucket_pixels = edge_pixels[mask]
    # Find the mode (most common pixel) in the dominant bucket
    if len(bucket_pixels) == 0:
        return None
    # Use np.unique to find the most common pixel
    uniq_pix, pix_counts = np.unique(bucket_pixels, axis=0, return_counts=True)
    rgb = uniq_pix[np.argmax(pix_counts)]

    # Ignore if the dominant color is very close to pure white
    if ignore_white and np.all(rgb >= 252):
        return None

    return "#{:02x}{:02x}{:02x}".format(*rgb)
