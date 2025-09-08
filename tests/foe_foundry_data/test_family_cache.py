import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from foe_foundry_data.monster_families.all import _MonsterFamilyCache


def test_cache_directory_creation():
    """Test that cache directory is created properly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()


def test_generate_cache_creates_json_files():
    """Test that generate_cache creates individual JSON files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        json_files = list(cache.cache_dir.glob("*.json"))
        assert len(json_files) > 0

        # Check that each file contains valid JSON
        for json_file in json_files[:5]:  # Test first 5 files
            with json_file.open("r") as f:
                data = json.load(f)
                assert isinstance(data, dict)
                assert "name" in data
                assert "key" in data
                assert "tag_line" in data
                assert "monsters" in data


def test_load_from_cache_when_cache_exists():
    """Test loading families from cache when cache exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        # Generate cache first
        cache.generate_cache()

        # Create a new cache instance to test loading
        cache2 = _MonsterFamilyCache()
        cache2.cache_dir = Path(tmp_dir) / "test_cache"

        families = cache2._load_from_cache()
        assert families is not None
        assert len(families) > 0
        assert all(hasattr(family, "key") for family in families)
        assert all(hasattr(family, "name") for family in families)


def test_fallback_to_generation_when_no_cache():
    """Test that families are generated when no cache exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "nonexistent_cache"

        # Should not crash and should return families
        families = cache.families
        assert isinstance(families, list)
        # Note: families might be empty if no actual family files exist


def test_fallback_when_cache_loading_fails():
    """Test fallback to generation when cache loading fails."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"
        cache.cache_dir.mkdir(parents=True)

        # Create an invalid JSON file
        bad_file = cache.cache_dir / "bad.json"
        with bad_file.open("w") as f:
            f.write("invalid json content")

        # Should fall back to generation instead of crashing
        families = cache._load_from_cache()
        assert families is None  # Should return None when loading fails


def test_cache_clears_existing_files():
    """Test that generate_cache clears existing files before generating new ones."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"
        cache.cache_dir.mkdir(parents=True)

        # Create a dummy file
        dummy_file = cache.cache_dir / "dummy.json"
        with dummy_file.open("w") as f:
            json.dump({"test": "data"}, f)

        cache.generate_cache()

        # Dummy file should be gone
        assert not dummy_file.exists()

        # Should have real family files now
        json_files = list(cache.cache_dir.glob("*.json"))
        assert all("dummy" not in f.name for f in json_files)


def test_lookup_property():
    """Test that lookup property creates correct dictionary mapping."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        # Generate cache
        cache.generate_cache()

        # Test lookup property
        lookup = cache.lookup
        assert isinstance(lookup, dict)

        # Check that all families in the list are also in the lookup
        families = cache.families
        for family in families:
            assert family.key in lookup
            assert lookup[family.key] == family


@patch("foe_foundry_data.monster_families.all.load_monster_families")
def test_generate_cache_with_no_families(mock_load_monster_families):
    """Test generate_cache handles empty family list gracefully."""
    mock_load_monster_families.return_value = []

    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterFamilyCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        # Should not crash with empty family list
        cache.generate_cache()

        # Should create cache directory but no JSON files
        assert cache.cache_dir.exists()
        json_files = list(cache.cache_dir.glob("*.json"))
        assert len(json_files) == 0