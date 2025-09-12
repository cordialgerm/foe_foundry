"""
Unit tests for tag icon validation.

This module tests that all defined tags have corresponding icons in the docs/img/icons directory.
"""

from pathlib import Path

import numpy as np
import pytest

from foe_foundry.tags.definitions import ALL_TAG_DEFINITIONS
from foe_foundry_data.generate import generate_monster
from foe_foundry_data.refs import MonsterRefResolver


def get_icons_directory():
    """Get the path to the icons directory"""
    # Start from the test file location and navigate to docs/img/icons
    test_dir = Path(__file__).parent
    repo_root = test_dir.parent.parent  # Go up to repo root
    icons_dir = repo_root / "docs" / "img" / "icons"
    return icons_dir


def get_available_icons():
    """Get a set of all available icon files"""
    icons_dir = get_icons_directory()
    if not icons_dir.exists():
        return set()

    available_icons = set()
    for icon_file in icons_dir.iterdir():
        if icon_file.is_file() and icon_file.suffix.lower() == ".svg":
            available_icons.add(icon_file.name)
    return available_icons


class TestTags:
    def test_species_tags(self):
        ref_resolver = MonsterRefResolver()
        rng = np.random.default_rng()
        ref, stats = generate_monster("orc-knight", ref_resolver, rng)
        assert stats is not None
        assert any(t for t in stats.tags if t.key == "orc")


class TestTagIcons:
    """Test cases for tag icon validation"""

    def test_icons_directory_exists(self):
        """Test that the icons directory exists"""
        icons_dir = get_icons_directory()
        assert icons_dir.exists(), f"Icons directory does not exist: {icons_dir}"
        assert icons_dir.is_dir(), f"Icons path is not a directory: {icons_dir}"

    def test_all_tags_have_icons(self):
        """Test that all defined tags have corresponding icon files"""
        available_icons = get_available_icons()
        missing_icons = []

        for tag_def in ALL_TAG_DEFINITIONS:
            icon = tag_def.icon
            if not icon.endswith(".svg"):
                icon += ".svg"
            if icon not in available_icons:
                missing_icons.append(
                    {
                        "tag": tag_def.name,
                        "key": tag_def.key,
                        "category": tag_def.category,
                        "icon": tag_def.icon,
                        "description": tag_def.description,
                    }
                )

        if missing_icons:
            error_message = "The following tags have missing icon files:\n"
            for missing in missing_icons:
                error_message += f"  - {missing['tag']} ({missing['category']}): {missing['icon']} - {missing['description']}\n"

            # Also provide available similar icons for troubleshooting
            error_message += f"\nTotal available icons: {len(available_icons)}\n"

            pytest.fail(error_message)

    def test_no_duplicate_tag_keys(self):
        """Test that all tag keys are unique"""
        seen_keys = set()
        duplicates = []

        for tag_def in ALL_TAG_DEFINITIONS:
            if tag_def.key in seen_keys:
                duplicates.append(tag_def.key)
            seen_keys.add(tag_def.key)

        assert not duplicates, f"Duplicate tag keys found: {duplicates}"


def print_tag_icon_report():
    """Print a detailed report of tag icons for manual review"""
    available_icons = get_available_icons()
    print("\n=== TAG ICON REPORT ===")
    print(f"Total tags defined: {len(ALL_TAG_DEFINITIONS)}")
    print(f"Total available icons: {len(available_icons)}")

    missing_count = 0
    for tag_def in ALL_TAG_DEFINITIONS:
        if tag_def.icon not in available_icons:
            missing_count += 1
            print(f"MISSING: {tag_def.name} ({tag_def.category}) -> {tag_def.icon}")

    print(f"Missing icons: {missing_count}")

    if missing_count == 0:
        print("✅ All tags have icons!")


if __name__ == "__main__":
    # Allow running this file directly to see the report
    print_tag_icon_report()
