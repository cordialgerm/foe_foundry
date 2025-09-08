from pathlib import Path
from unittest.mock import patch
from datetime import datetime

import pytest

from foe_foundry.utils.monster_content import (
    extract_monster_hyperlinks,
    extract_tagline,
    extract_yaml_frontmatter,
    strip_yaml_frontmatter,
)
from foe_foundry_data.monster_families import MonsterFamilies
from foe_foundry_data.monster_families.data import load_monster_families


class TestMonsterContentUtilities:
    """Test the utility functions used by monster family loading."""

    def test_extract_monster_hyperlinks_basic(self):
        """Test extraction of monster hyperlinks from markdown content."""
        markdown_content = """
        | [Berserkers](../monsters/berserker.md) | *Battle-Frenzied Warriors* |
        | [Guards](../monsters/guard.md) | *Watchful Sentries* |

        [Warriors](../monsters/warrior.md) are disciplined soldiers.

        Also check [Monster Catalog](../monsters/index.md) for more.
        """

        result = extract_monster_hyperlinks(markdown_content)

        # Should extract unique monster names, excluding 'index'
        assert result == ["berserker", "guard", "warrior"]

    def test_extract_monster_hyperlinks_absolute_paths(self):
        """Test extraction works with absolute paths."""
        markdown_content = """
        [Knights](/monsters/knight.md) are noble warriors.
        [Rogues](/monsters/rogue.md) strike from shadows.
        """

        result = extract_monster_hyperlinks(markdown_content)
        assert result == ["knight", "rogue"]

    def test_extract_monster_hyperlinks_deduplication(self):
        """Test that duplicate monster links are deduplicated."""
        markdown_content = """
        [Berserkers](../monsters/berserker.md) are warriors.
        [Another berserker link](../monsters/berserker.md) here.
        [Guards](../monsters/guard.md) protect.
        """

        result = extract_monster_hyperlinks(markdown_content)
        assert result == ["berserker", "guard"]

    def test_extract_monster_hyperlinks_empty_content(self):
        """Test extraction from empty or no-link content."""
        assert extract_monster_hyperlinks("") == []
        assert extract_monster_hyperlinks("No links here!") == []
        assert extract_monster_hyperlinks("[Not a monster](../other/page.md)") == []

    def test_extract_tagline_basic(self):
        """Test extraction of tagline from markdown content."""
        markdown_content = """
        # Soldiers & Fighters

        *Battle-Hardened Warriors of Duty, Honor, or Fortune*

        Some content here.
        """

        result = extract_tagline(markdown_content)
        assert result == "Battle-Hardened Warriors of Duty, Honor, or Fortune"

    def test_extract_tagline_missing(self):
        """Test tagline extraction when no tagline exists."""
        markdown_content = """
        # Title Only

        Regular content without italic tagline.
        """

        result = extract_tagline(markdown_content)
        assert result is None

    def test_extract_yaml_frontmatter(self):
        """Test extraction of YAML frontmatter."""
        content = """---
title: Test Title
short_title: Test
is_monster_family: true
---

# Content

Some markdown content.
"""

        result = extract_yaml_frontmatter(content)
        assert result["title"] == "Test Title"
        assert result["short_title"] == "Test"
        assert result["is_monster_family"] is True

    def test_strip_yaml_frontmatter(self):
        """Test stripping YAML frontmatter from content."""
        content = """---
title: Test Title
---

# Content

Some markdown content.
"""

        result = strip_yaml_frontmatter(content)
        expected = "# Content\n\nSome markdown content.\n"
        assert result == expected


class TestMonsterFamilyModel:
    """Test the MonsterFamilyInfo data structure (consolidated model)."""

    def test_monster_family_model_creation(self):
        """Test creating a MonsterFamilyInfo instance with consolidated structure."""
        from datetime import datetime
        from foe_foundry_data.base import MonsterInfoModel, MonsterFamilyInfo, MonsterTemplateInfoModel

        monsters = [
            MonsterInfoModel(key="guard", name="Guard", cr=0.125, template="guard"),
            MonsterInfoModel(key="knight", name="Knight", cr=3.0, template="knight"),
        ]

        templates = [
            MonsterTemplateInfoModel(
                key="guard",
                name="Guard",
                url="/monsters/guard/", 
                image="/img/monsters/guard.webp",
                tagline="Watchful Sentries",
                transparent_edges=False,
                grayscale=False,
                background_color="#333333",
                mask_css="",
                is_new=False,
                create_date=datetime(2024, 1, 1),
            ),
            MonsterTemplateInfoModel(
                key="knight",
                name="Knight",
                url="/monsters/knight/",
                image="/img/monsters/knight.webp", 
                tagline="Noble Warriors",
                transparent_edges=True,
                grayscale=False,
                background_color=None,
                mask_css="mask-image: url('/img/monsters/knight.webp')",
                is_new=True,
                create_date=datetime(2024, 2, 1),
            ),
        ]

        family = MonsterFamilyInfo(
            key="soldiers_and_fighters",
            name="Soldiers & Fighters",
            icon="favicon",
            tag_line="Battle-Hardened Warriors",
            monsters=monsters,
            templates=templates,
        )

        assert family.key == "soldiers_and_fighters"
        assert family.name == "Soldiers & Fighters"
        assert family.tag_line == "Battle-Hardened Warriors"
        assert len(family.monsters) == 2
        assert family.monsters[0].name == "Guard"
        assert family.monsters[1].name == "Knight"
        assert len(family.templates) == 2
        assert family.templates[0].name == "Guard"
        assert family.templates[1].name == "Knight"


class TestMonsterFamilyLoading:
    """Test the monster family loading functionality."""

    @patch("foe_foundry_data.monster_families.data.Path.cwd")
    def test_load_families_finds_family_files(self, mock_cwd, tmp_path):
        """Test that load_monster_families finds and processes family markdown files."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Create a test family file
        family_content = """---
title: Test Soldiers & Fighters | Foe Foundry
short_title: Test Soldiers & Fighters
icon: rally-the-troops
tag_line: Test Battle-Hardened Warriors
is_monster_family: true
---

# Test Soldiers & Fighters

*Test Battle-Hardened Warriors*

| [Guards](../monsters/guard.md) | *Watchful Sentries* |
| [Knights](../monsters/knight.md) | *Noble Warriors* |
"""

        family_file = families_dir / "test_soldiers.md"
        family_file.write_text(family_content)

        # Create a non-family file that should be ignored
        non_family_content = """---
title: Not a Monster Family
is_monster_family: false
---

# Regular Page
"""

        non_family_file = families_dir / "regular_page.md"
        non_family_file.write_text(non_family_content)

        # Mock Path.cwd() to return our test directory
        mock_cwd.return_value = tmp_path

        # Mock the ref_resolver to avoid dependency issues
        with patch("foe_foundry_data.monster_families.data.ref_resolver") as mock_resolver:
            # Mock the resolve_monster_ref method to return mock references
            mock_ref = type(
                "MockRef",
                (),
                {"template": type("MockTemplate", (), {
                    "key": "test_template",
                    "monsters": []
                })()},
            )()
            mock_resolver.resolve_monster_ref.return_value = mock_ref

            # Mock AllTemplates to return mock templates
            with patch(
                "foe_foundry_data.monster_families.data.AllTemplates"
            ) as mock_all_templates:
                mock_template = type(
                    "MockTemplate",
                    (),
                    {
                        "key": "test_template",
                        "name": "Test Template",
                        "tag_line": "Test Template Tagline",
                        "primary_image_url": None,
                        "create_date": datetime(2024, 1, 1),
                        "monsters": [
                            type(
                                "MockMonster",
                                (),
                                {"key": "guard", "name": "Guard", "cr": 0.125},
                            )(),
                            type(
                                "MockMonster",
                                (),
                                {"key": "knight", "name": "Knight", "cr": 3.0},
                            )(),
                        ],
                    },
                )()
                mock_all_templates.__iter__ = lambda x: iter([mock_template])

                # Load families using the new system
                families = load_monster_families()

        # Verify results
        assert len(families) == 1
        family = families[0]
        assert (
            family.key == "test-soldiers"
        )  # name_to_key converts underscores to hyphens
        assert family.name == "Test Soldiers & Fighters"
        assert family.tag_line == "Test Battle-Hardened Warriors"
        assert len(family.monsters) == 2

    def test_load_families_validates_required_fields(self, tmp_path):
        """Test that MonsterFamilies validates required fields and raises appropriate errors."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Test missing title
        no_title_content = """---
is_monster_family: true
---

# Test Family

*Test Tagline*
"""

        no_title_file = families_dir / "no_title.md"
        no_title_file.write_text(no_title_content)

        with patch("foe_foundry_data.monster_families.data.Path.cwd", return_value=tmp_path):
            with pytest.raises(ValueError, match="Invalid title"):
                load_monster_families()

    def test_load_families_validates_tagline(self, tmp_path):
        """Test that load_families validates tagline presence."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Test missing tagline
        no_tagline_content = """---
title: Test Family
family_name: Test Family
icon: test-icon
is_monster_family: true
---

# Test Family

Regular content without italic tagline.
"""

        no_tagline_file = families_dir / "no_tagline.md"
        no_tagline_file.write_text(no_tagline_content)

        with patch("foe_foundry_data.monster_families.data.Path.cwd", return_value=tmp_path):
            with pytest.raises(ValueError, match="Tag line not found"):
                load_monster_families()

    def test_load_families_validates_monster_references(self, tmp_path):
        """Test that load_families validates monster references."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Test invalid monster reference
        invalid_ref_content = """---
title: Test Family
family_name: Test Family
icon: test-icon
tag_line: Test Tagline
is_monster_family: true
---

# Test Family

*Test Tagline*

[Invalid Monster](../monsters/nonexistent.md) reference.
"""

        invalid_ref_file = families_dir / "invalid_ref.md"
        invalid_ref_file.write_text(invalid_ref_content)

        with patch("foe_foundry_data.monster_families.data.Path.cwd", return_value=tmp_path):
            with patch("foe_foundry_data.monster_families.data.ref_resolver") as mock_resolver:
                # Mock resolver to return None for invalid references
                mock_resolver.resolve_monster_ref.return_value = None

                with pytest.raises(
                    ValueError,
                    match="Monster reference 'nonexistent' .* could not be resolved",
                ):
                    load_monster_families()

    @pytest.mark.integration
    def test_load_actual_soldiers_family(self):
        """Integration test: Load the actual soldiers_and_fighters family file."""
        # This test requires the actual project structure to be in place
        project_root = Path(__file__).parent.parent.parent
        families_dir = project_root / "docs" / "families"
        soldiers_file = families_dir / "soldiers_and_fighters.md"

        if not soldiers_file.exists():
            pytest.skip("soldiers_and_fighters.md file not found")

        # Test that we can at least extract the basic information
        with soldiers_file.open() as f:
            content = f.read()

        frontmatter = extract_yaml_frontmatter(content)
        markdown_content = strip_yaml_frontmatter(content)
        tagline = extract_tagline(content)
        monster_links = extract_monster_hyperlinks(markdown_content)

        # Verify expected values for soldiers & fighters family
        assert frontmatter.get("is_monster_family") is True
        assert frontmatter.get("short_title") == "Soldiers & Fighters"
        assert tagline == "Battle-Hardened Warriors of Duty, Honor, or Fortune"

        # Should find the expected monster types
        expected_monsters = {"berserker", "guard", "knight", "warrior"}
        assert set(monster_links) == expected_monsters
