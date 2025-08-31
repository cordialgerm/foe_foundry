import numpy as np
import pytest

from foe_foundry_data.generate import generate_monster
from foe_foundry_data.jinja import render_statblock_markdown
from foe_foundry_data.refs import MonsterRefResolver


def _generate_fixed_monster(monster_key: str, seed: int = 12345):
    """Generate a monster with fixed parameters for reproducible tests"""
    ref_resolver = MonsterRefResolver()
    rng = np.random.default_rng(seed)
    ref, stats = generate_monster(monster_key, ref_resolver=ref_resolver, rng=rng)
    return ref, stats


def test_render_statblock_markdown_5esrd_knight():
    """Test 5E SRD markdown rendering with Knight"""
    ref, stats = _generate_fixed_monster("knight")
    markdown = render_statblock_markdown(stats, "5esrd")
    
    # Validate basic structure
    assert markdown.startswith("# ")
    assert "Knight" in markdown
    assert "**Armor Class**" in markdown
    assert "**Hit Points**" in markdown
    assert "**Speed**" in markdown
    assert "| STR | DEX | CON | INT | WIS | CHA |" in markdown
    assert "**Challenge**" in markdown


def test_render_statblock_markdown_5esrd_priest():
    """Test 5E SRD markdown rendering with Priest"""
    ref, stats = _generate_fixed_monster("priest")
    markdown = render_statblock_markdown(stats, "5esrd")
    
    # Validate basic structure
    assert markdown.startswith("# ")
    assert "Priest" in markdown
    assert "**Armor Class**" in markdown
    assert "**Hit Points**" in markdown
    assert "**Speed**" in markdown
    assert "| STR | DEX | CON | INT | WIS | CHA |" in markdown
    assert "**Challenge**" in markdown


def test_render_statblock_markdown_5esrd_spy():
    """Test 5E SRD markdown rendering with Spy"""
    ref, stats = _generate_fixed_monster("spy")
    markdown = render_statblock_markdown(stats, "5esrd")
    
    # Validate basic structure
    assert markdown.startswith("# ")
    assert "Spy" in markdown
    assert "**Armor Class**" in markdown
    assert "**Hit Points**" in markdown
    assert "**Speed**" in markdown
    assert "| STR | DEX | CON | INT | WIS | CHA |" in markdown
    assert "**Challenge**" in markdown


def test_render_statblock_markdown_invalid_format():
    """Test that invalid format raises ValueError"""
    ref, stats = _generate_fixed_monster("knight")
    
    with pytest.raises(ValueError, match="Unknown format 'invalid'"):
        render_statblock_markdown(stats, "invalid")


def test_render_statblock_markdown_default_format():
    """Test that default format is 5esrd"""
    ref, stats = _generate_fixed_monster("knight")
    
    markdown_default = render_statblock_markdown(stats)
    markdown_5esrd = render_statblock_markdown(stats, "5esrd")
    
    assert markdown_default == markdown_5esrd


def test_statblock_markdown_has_sections():
    """Test that the markdown includes expected sections"""
    ref, stats = _generate_fixed_monster("knight")
    markdown = render_statblock_markdown(stats, "5esrd")
    
    # Should contain ability score table
    assert "| STR | DEX | CON | INT | WIS | CHA |" in markdown
    
    # Check for traits (all creatures should have some)
    assert "***" in markdown  # trait formatting
    
    # Actions section should be present
    assert "###### Actions" in markdown or "Actions" in markdown