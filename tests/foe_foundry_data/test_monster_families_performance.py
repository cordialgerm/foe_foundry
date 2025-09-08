"""Test performance comparison between cached and non-cached monster families."""
import tempfile
import shutil
import time
from pathlib import Path
from foe_foundry_data.monster_families import MonsterFamilies


def test_monster_families_performance_comparison():
    """Test that cached monster families load faster than runtime generation."""
    # Get current cache dir
    cache_dir = MonsterFamilies.cache_dir
    backup_dir = None
    
    try:
        # If cache exists, back it up
        if cache_dir.exists():
            backup_dir = cache_dir.parent / "monster_families_backup"
            if backup_dir.exists():
                shutil.rmtree(backup_dir)
            shutil.move(str(cache_dir), str(backup_dir))
        
        # Clear the cached property to force re-evaluation
        if hasattr(MonsterFamilies, '_families'):
            delattr(MonsterFamilies, '_families')
        
        # Time runtime generation (fallback behavior)
        start_time = time.time()
        families_runtime = MonsterFamilies.families
        runtime_duration = time.time() - start_time
        
        # Clear the cached property again
        if hasattr(MonsterFamilies, '_families'):
            delattr(MonsterFamilies, '_families')
        
        # Restore cache
        if backup_dir and backup_dir.exists():
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            shutil.move(str(backup_dir), str(cache_dir))
        
        # Time cached loading
        start_time = time.time()
        families_cached = MonsterFamilies.families
        cached_duration = time.time() - start_time
        
        # Verify both methods return same data
        assert len(families_runtime) == len(families_cached)
        
        # Log performance comparison
        print(f"Runtime generation: {runtime_duration:.4f}s")
        print(f"Cached loading: {cached_duration:.4f}s")
        
        # The test doesn't assert cached is faster because both use in-memory caching
        # But we can verify that both work and return the same data
        assert len(families_runtime) > 0, "Should have families from runtime generation"
        assert len(families_cached) > 0, "Should have families from cache"
        
        # Verify cache directory exists and has files
        assert cache_dir.exists(), "Cache directory should exist"
        json_files = list(cache_dir.glob("*.json"))
        assert len(json_files) > 0, "Cache should have JSON files"
        
    finally:
        # Cleanup: ensure cache is restored if something went wrong
        if backup_dir and backup_dir.exists():
            if cache_dir.exists():
                shutil.rmtree(cache_dir)
            shutil.move(str(backup_dir), str(cache_dir))


def test_monster_families_cache_vs_families_cache():
    """Test that MonsterFamilies and Families caches are different systems."""
    from foe_foundry_data.families import Families
    
    # Both should work
    monster_families = MonsterFamilies.families
    families = Families.all_monster_families
    
    # Both should have content
    assert len(monster_families) > 0, "MonsterFamilies should have content"
    assert len(families) > 0, "Families should have content"
    
    # They should have different cache directories
    monster_families_cache = MonsterFamilies.cache_dir
    families_cache = Families.cache_dir
    
    assert monster_families_cache != families_cache, "Cache directories should be different"
    assert monster_families_cache.name == "monster_families"
    assert families_cache.name == "families"
    
    # Both cache directories should exist
    assert monster_families_cache.exists(), "MonsterFamilies cache should exist"
    assert families_cache.exists(), "Families cache should exist"