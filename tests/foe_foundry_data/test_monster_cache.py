import json
import tempfile
from pathlib import Path
from unittest.mock import patch

from foe_foundry_data.monsters.all import _MonsterCache


def test_cache_directory_creation():
    """Test that cache directory is created properly."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        assert cache.cache_dir.exists()
        assert cache.cache_dir.is_dir()


def test_generate_cache_creates_json_files():
    """Test that generate_cache creates individual JSON files."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
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
                assert "cr" in data


def test_load_from_cache_when_cache_exists():
    """Test loading monsters from cache when cache exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        # Generate cache first
        cache.generate_cache()

        # Create a new cache instance to test loading
        new_cache = _MonsterCache()
        new_cache.cache_dir = cache.cache_dir

        monsters = new_cache.one_of_each_monster
        assert len(monsters) > 0

        # Verify monsters are sorted by key
        sorted_keys = [m.key for m in monsters]
        assert sorted_keys == sorted(sorted_keys)


def test_fallback_to_generation_when_no_cache():
    """Test that monsters are generated when no cache exists."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "nonexistent_cache"

        monsters = cache.one_of_each_monster
        assert len(monsters) > 0

        # Verify we get actual MonsterModel instances
        for monster in monsters[:3]:  # Test first 3
            assert hasattr(monster, "key")
            assert hasattr(monster, "name")
            assert hasattr(monster, "cr")


def test_fallback_when_cache_loading_fails():
    """Test fallback to generation when cache loading fails."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"
        cache.cache_dir.mkdir(parents=True)

        # Create an invalid JSON file
        invalid_file = cache.cache_dir / "invalid.json"
        with invalid_file.open("w") as f:
            f.write("{ invalid json")

        monsters = cache.one_of_each_monster
        assert len(monsters) > 0


def test_cache_clears_existing_files():
    """Test that generate_cache clears existing files before generating new ones."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"
        cache.cache_dir.mkdir(parents=True)

        # Create a dummy file
        dummy_file = cache.cache_dir / "dummy.json"
        with dummy_file.open("w") as f:
            json.dump({"test": "data"}, f)

        cache.generate_cache()

        # Dummy file should be gone
        assert not dummy_file.exists()

        # Should have real monster files now
        json_files = list(cache.cache_dir.glob("*.json"))
        assert len(json_files) > 0
        assert all("dummy" not in f.name for f in json_files)


def test_lookup_property():
    """Test that lookup property creates correct dictionary mapping."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        # Create new instance to test loading from cache
        new_cache = _MonsterCache()
        new_cache.cache_dir = cache.cache_dir

        lookup = new_cache.lookup
        monsters = new_cache.one_of_each_monster

        assert len(lookup) == len(monsters)

        for monster in monsters[:5]:  # Test first 5
            assert monster.key in lookup
            assert lookup[monster.key] == monster


@patch("foe_foundry_data.monsters.all.AllTemplates", [])
def test_generate_cache_with_no_templates():
    """Test generate_cache handles empty template list gracefully."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        assert cache.cache_dir.exists()
        json_files = list(cache.cache_dir.glob("*.json"))
        assert len(json_files) == 0


def test_cached_property_behavior():
    """Test that one_of_each_monster behaves as a cached property."""
    with tempfile.TemporaryDirectory() as tmp_dir:
        cache = _MonsterCache()
        cache.cache_dir = Path(tmp_dir) / "test_cache"

        cache.generate_cache()

        # Create new instance
        new_cache = _MonsterCache()
        new_cache.cache_dir = cache.cache_dir

        # First access
        monsters1 = new_cache.one_of_each_monster

        # Second access should return the same object (cached)
        monsters2 = new_cache.one_of_each_monster

        assert monsters1 is monsters2
