"""Tests for monster content extraction functions."""

import glob
import os
from pathlib import Path

import pytest

from foe_foundry.utils.monster_content import (
    extract_encounters_content,
    extract_monster_hyperlinks,
    extract_overview_content,
)


def get_monster_files():
    """Get all monster markdown files, excluding index.md."""
    monster_files = glob.glob(
        os.path.join(os.path.dirname(__file__), "../../docs/monsters/*.md")
    )
    # Filter out index.md as it's not a monster file
    return [f for f in monster_files if not f.endswith("index.md")]


@pytest.mark.parametrize("monster_file", get_monster_files())
def test_monster_has_lore_content(monster_file):
    """Test that all monster files have extractable lore content."""
    with open(monster_file, "r", encoding="utf-8") as f:
        content = f.read()

    lore = extract_overview_content(content)

    # Assert that lore content exists and is not empty
    assert lore is not None, (
        f"No lore content found in {os.path.basename(monster_file)}"
    )
    assert len(lore.strip()) > 0, (
        f"Empty lore content in {os.path.basename(monster_file)}"
    )

    # Check that lore content has substantial content (more than just a header or single line)
    lines = [line.strip() for line in lore.strip().splitlines() if line.strip()]
    assert len(lines) > 1, f"Lore content too short in {os.path.basename(monster_file)}"


@pytest.mark.parametrize("monster_file", get_monster_files())
def test_monster_has_encounters_content(monster_file):
    """Test that all monster files have extractable encounters content."""
    with open(monster_file, "r", encoding="utf-8") as f:
        content = f.read()

    encounters = extract_encounters_content(content)

    # Assert that encounters content exists and is not empty
    assert encounters is not None, (
        f"No encounters content found in {os.path.basename(monster_file)}"
    )
    assert len(encounters.strip()) > 0, (
        f"Empty encounters content in {os.path.basename(monster_file)}"
    )

    # Check that encounters content has substantial content
    lines = [line.strip() for line in encounters.strip().splitlines() if line.strip()]
    assert len(lines) > 2, (
        f"Encounters content too short in {os.path.basename(monster_file)}"
    )

    # Check that it contains at least one encounter or adventure section header
    has_encounter_header = any(
        ("encounter" in line.lower() and line.startswith("##"))
        or ("adventure" in line.lower() and line.startswith("##"))
        for line in encounters.splitlines()
    )
    assert has_encounter_header, (
        f"No encounter/adventure headers found in {os.path.basename(monster_file)}"
    )


@pytest.mark.parametrize("monster_file", get_monster_files())
def test_lore_content_quality(monster_file):
    """Test the quality of extracted lore content."""
    with open(monster_file, "r", encoding="utf-8") as f:
        content = f.read()

    lore = extract_overview_content(content)
    assert lore is not None

    # Lore should not contain image directives
    assert "![" not in lore, (
        f"Lore contains image directives in {os.path.basename(monster_file)}"
    )

    # Lore should not contain info-style directives
    assert "!!!" not in lore, (
        f"Lore contains info directives in {os.path.basename(monster_file)}"
    )

    # Lore should contain actual descriptive content (not just headers)
    non_header_lines = [
        line.strip()
        for line in lore.splitlines()
        if line.strip() and not line.strip().startswith("#")
    ]
    assert len(non_header_lines) > 0, (
        f"Lore contains only headers in {os.path.basename(monster_file)}"
    )


@pytest.mark.parametrize("monster_file", get_monster_files())
def test_encounters_content_quality(monster_file):
    """Test the quality of extracted encounters content."""
    with open(monster_file, "r", encoding="utf-8") as f:
        content = f.read()

    encounters = extract_encounters_content(content)
    assert encounters is not None

    # Encounters should contain encounter ideas (bullet points or paragraphs)
    has_content_lines = any(
        line.strip() and not line.strip().startswith("#")
        for line in encounters.splitlines()
    )
    assert has_content_lines, (
        f"Encounters contains only headers in {os.path.basename(monster_file)}"
    )


def test_extract_lore_content_gelatinous_cube():
    """Test lore extraction with a specific known example."""
    test_content = """---
title: Test
---
# Gelatinous Cubes

*Acidic, Nigh-Invisible Dungeon Cleaner*

A Gelatinous Cube is a silent, quivering mass of acidic goo.

Unless it's recently dined, a gelatinous cube is nearly invisible.

## Gelatinous Cube Lore

- Gelatinous Cubes glide toward their prey without hesitation.
- Once engulfed, escape is rare.

## Gelatinous Cube Tactics

Gelatinous Cubes are mindless entities.
"""

    lore = extract_overview_content(test_content)

    assert lore is not None
    assert "A Gelatinous Cube is a silent, quivering mass" in lore
    assert "## Gelatinous Cube Lore" in lore
    assert "Gelatinous Cubes glide toward their prey" in lore
    assert "## Gelatinous Cube Tactics" not in lore
    assert "Gelatinous Cubes are mindless entities" not in lore


def test_extract_encounters_content_gelatinous_cube():
    """Test encounters extraction with a specific known example."""
    test_content = """---
title: Test
---
# Gelatinous Cubes

*Acidic, Nigh-Invisible Dungeon Cleaner*

Some lore content here.

## Gelatinous Cube Tactics

Tactics content here.

## Gelatinous Cube Encounter Ideas

- A panicked NPC barrels past the party.
- A gleaming sword glows softly.

## Gelatinous Cube Adventure Ideas

- A fast-talking Mage hires the party.
- A wealthy Noble hires the party.

## Other Section

This should not be included.
"""

    encounters = extract_encounters_content(test_content)

    assert encounters is not None
    assert "## Gelatinous Cube Encounter Ideas" in encounters
    assert "A panicked NPC barrels past" in encounters
    assert "## Gelatinous Cube Adventure Ideas" in encounters
    assert "A fast-talking Mage hires" in encounters
    assert "## Other Section" not in encounters
    assert "This should not be included" not in encounters


def test_lore_filters_image_directives():
    """Test that lore extraction filters out image directives."""
    test_content = """---
title: Test
---
# Monster

*Tagline*

Some lore content.

![Image description](../img/test.webp){.monster-image}

More lore content.

## Monster Lore

- Lore bullet point.

![Another image](test.jpg)

## Monster Tactics

Tactics content.
"""

    lore = extract_overview_content(test_content)

    assert lore is not None
    assert "Some lore content" in lore
    assert "More lore content" in lore
    assert "Lore bullet point" in lore
    assert "![Image description]" not in lore
    assert "![Another image]" not in lore


def test_lore_filters_info_directives():
    """Test that lore extraction filters out info-style directives."""
    test_content = """---
title: Test
---
# Monster

*Tagline*

Some lore content.

!!! info "Important Note"
    This should be filtered out.

More lore content.

## Monster Tactics

Tactics content.
"""

    lore = extract_overview_content(test_content)

    assert lore is not None
    assert "Some lore content" in lore
    assert "More lore content" in lore
    assert "!!! info" not in lore
    assert "This should be filtered out" not in lore


def test_monster_content_functions_with_index_file():
    """Test that functions handle non-monster files gracefully."""
    test_content = """---
title: All 5E Monsters
---
# Foe Foundry Monsters

This is an index page, not a monster file.

## All Monsters

List of monsters here.
"""

    lore = extract_overview_content(test_content)
    encounters = extract_encounters_content(test_content)

    # Index files should not have monster-style content
    assert lore is None
    assert encounters is None


def test_extract_monster_hyperlinks():
    path = Path.cwd() / "docs" / "families" / "soldiers_and_fighters.md"
    content = path.read_text(encoding="utf-8")
    links = extract_monster_hyperlinks(content)
    assert len(links) > 0, "No monster links found in the content"
