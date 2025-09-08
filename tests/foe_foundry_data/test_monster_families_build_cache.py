"""Test that monster families caching works during build process."""
import tempfile
import subprocess
import os
from pathlib import Path


def test_monster_families_cache_generated_during_build():
    """Test that running foe_foundry_data.__main__ generates monster families cache."""
    with tempfile.TemporaryDirectory() as temp_dir:
        # Set up environment to use temp directory for cache
        env = os.environ.copy()
        env['PYTHONPATH'] = str(Path(__file__).parent.parent.parent)
        
        # Change to temp directory to ensure cache is created there
        original_cwd = os.getcwd()
        os.chdir(temp_dir)
        
        try:
            # Run the main module
            result = subprocess.run(
                ['python', '-m', 'foe_foundry_data'],
                env=env,
                capture_output=True,
                text=True,
                timeout=120
            )
            
            # Check that command succeeded
            assert result.returncode == 0, f"Command failed: {result.stderr}"
            
            # Check that output includes monster families caching message
            assert "Caching monster families..." in result.stdout
            assert "Monster families cached." in result.stdout
            
            # Check that monster_families cache directory was created
            cache_dir = Path(temp_dir) / "cache" / "monster_families"
            assert cache_dir.exists(), "Monster families cache directory was not created"
            
            # Check that JSON files were created
            json_files = list(cache_dir.glob("*.json"))
            assert len(json_files) > 0, "No JSON cache files were created"
            
            # Check that expected family files exist
            expected_families = {"undead", "soldiers-and-fighters", "monstrosities"}
            actual_families = {f.stem for f in json_files}
            assert expected_families.issubset(actual_families), f"Expected families not found. Got: {actual_families}"
            
        finally:
            os.chdir(original_cwd)


def test_monster_families_cache_content():
    """Test that monster families cache contains valid JSON data."""
    # This test assumes cache is already generated
    cache_dir = Path.cwd() / "cache" / "monster_families"
    
    if not cache_dir.exists():
        # Generate cache first
        subprocess.run(['python', '-m', 'foe_foundry_data'], check=True)
    
    # Check that cache has content
    json_files = list(cache_dir.glob("*.json"))
    assert len(json_files) > 0, "No JSON cache files found"
    
    # Validate one of the cache files has correct structure
    import json
    test_file = json_files[0]
    with open(test_file, 'r') as f:
        family_data = json.load(f)
    
    # Check required fields
    required_fields = ["key", "name", "tag_line", "icon", "templates"]
    for field in required_fields:
        assert field in family_data, f"Required field '{field}' missing from family data"
    
    # Check templates structure
    assert isinstance(family_data["templates"], list), "Templates should be a list"
    if family_data["templates"]:  # If there are templates
        template = family_data["templates"][0]
        template_fields = ["key", "name", "url", "tagline"]
        for field in template_fields:
            assert field in template, f"Required template field '{field}' missing"