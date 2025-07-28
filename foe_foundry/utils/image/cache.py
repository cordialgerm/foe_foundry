import hashlib
import json
from pathlib import Path
from typing import Any, Dict

from .helpers import get_dominant_edge_color as edge_color_core
from .helpers import has_transparent_edges as transparent_edge_core
from .helpers import is_grayscaleish as grayscaleish_core


class ImageMetadataCache:
    def __init__(self, cache_dir: Path | None = None):
        self.cache_dir = cache_dir or (Path.cwd() / "cache" / "image_metadata")
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _hash_image(self, image_path: Path) -> str:
        hasher = hashlib.md5()
        with open(image_path, "rb") as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_metadata(self, image_path: str | Path) -> Dict[str, Any]:
        image_path = Path(image_path)
        img_hash = self._hash_image(image_path)
        meta_path = self.cache_dir / f"{img_hash}.json"
        if meta_path.exists():
            with open(meta_path, "r") as f:
                return json.load(f)
        # Compute metadata
        metadata = {
            "has_transparent_edges": transparent_edge_core(image_path),
            "is_grayscaleish": grayscaleish_core(image_path),
            "dominant_edge_color": edge_color_core(image_path),
        }
        with open(meta_path, "w") as f:
            json.dump(metadata, f, indent=2)
        return metadata


_cache = ImageMetadataCache()


def get_dominant_edge_color(image_path: str | Path) -> str | None:
    """Returns the cached dominant edge color for an image, or computes it if not cached."""
    return _cache.get_metadata(image_path).get("dominant_edge_color")


def has_transparent_edges(image_path: str | Path) -> bool:
    """Returns whether the image has transparent edges, using cached metadata."""
    return _cache.get_metadata(image_path).get("has_transparent_edges", False)


def is_grayscaleish(image_path: str | Path) -> bool:
    """Returns whether the image is mostly grayscale, using cached metadata."""
    return _cache.get_metadata(image_path).get("is_grayscaleish", False)
