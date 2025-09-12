from datetime import datetime
from pathlib import Path
from unittest.mock import patch

import pytest

from foe_foundry_data.base import (
    MonsterFamilyInfo,
    MonsterInfoModel,
    MonsterTemplateInfoModel,
)
from foe_foundry_data.monster_families import MonsterFamilies, load_monster_families


class TestMonsterFamilyInfo:
    """Test the MonsterFamilyInfo data structure."""

    def test_monster_family_info_creation(self):
        """Test creating a MonsterFamilyInfo instance."""
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

        monsters = [
            MonsterInfoModel(
                key="guard",
                name="Guard",
                cr=1.0,
                template="guard",
                creature_type="humanoid",
                tag_line="Watchful Sentries",
            ),
            MonsterInfoModel(
                key="knight",
                name="Knight",
                cr=3.0,
                template="knight",
                creature_type="humanoid",
                tag_line="Noble Warriors",
            ),
        ]

        family = MonsterFamilyInfo(
            key="soldiers_and_fighters",
            url="TEMP",
            name="Soldiers & Fighters",
            icon="rally-the-troops",
            tag_line="Battle-Hardened Warriors",
            templates=templates,
            monsters=monsters,
        )

        assert family.key == "soldiers_and_fighters"
        assert family.name == "Soldiers & Fighters"
        assert family.icon == "rally-the-troops"
        assert family.tag_line == "Battle-Hardened Warriors"
        assert len(family.templates) == 2
        assert family.templates[0].name == "Guard"
        assert family.templates[1].name == "Knight"
        assert len(family.monsters) == 2
        assert family.monsters[0].name == "Guard"
        assert family.monsters[1].name == "Knight"


class TestMonsterFamilyLoading:
    """Test the monster family loading functionality with templates."""

    @patch("foe_foundry_data.monster_families.data.Path.cwd")
    @patch("foe_foundry_data.monster_families.data.get_base_url")
    def test_load_monster_families_finds_family_files(
        self, mock_base_url, mock_cwd, tmp_path
    ):
        """Test that load_monster_families finds and processes family markdown files."""
        mock_base_url.return_value = "http://test.example.com"

        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Create a test family file with icon
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
        with patch(
            "foe_foundry_data.monster_families.data.ref_resolver"
        ) as mock_resolver:
            # Mock the resolve_monster_ref method to return mock references
            mock_ref = type(
                "MockRef",
                (),
                {
                    "template": type(
                        "MockTemplate", (), {"key": "test_template", "monsters": []}
                    )()
                },
            )()
            mock_resolver.resolve_monster_ref.return_value = mock_ref

            # Mock AllTemplates to return mock templates
            with patch(
                "foe_foundry_data.monster_families.data.AllTemplates"
            ) as mock_all_templates:
                # Create mock monster objects
                mock_monster1 = type(
                    "MockMonster",
                    (),
                    {
                        "key": "test_guard",
                        "name": "Test Guard",
                        "cr": 1.0,
                    },
                )()
                mock_monster2 = type(
                    "MockMonster",
                    (),
                    {
                        "key": "test_knight",
                        "name": "Test Knight",
                        "cr": 3.0,
                    },
                )()

                mock_template = type(
                    "MockTemplate",
                    (),
                    {
                        "key": "test_template",
                        "name": "Test Template",
                        "tag_line": "Test Template Tagline",
                        "primary_image_url": None,
                        "create_date": datetime(2024, 1, 1),
                        "monsters": [mock_monster1, mock_monster2],
                    },
                )()
                mock_all_templates.__iter__ = lambda x: iter([mock_template])

                # Load families
                families = load_monster_families()

        # Verify results
        assert len(families) == 1
        family = families[0]
        assert (
            family.key == "test-soldiers"
        )  # name_to_key converts underscores to hyphens
        assert family.name == "Test Soldiers & Fighters"
        assert family.icon == "rally-the-troops"
        assert family.tag_line == "Test Battle-Hardened Warriors"
        assert len(family.templates) == 1
        assert family.templates[0].key == "test_template"
        assert family.templates[0].name == "Test Template"
        assert len(family.monsters) == 2
        assert family.monsters[0].key == "test_guard"
        assert family.monsters[0].name == "Test Guard"
        assert family.monsters[0].template == "test_template"
        assert family.monsters[1].key == "test_knight"
        assert family.monsters[1].name == "Test Knight"
        assert family.monsters[1].template == "test_template"

    def test_load_monster_families_validates_icon_field(self, tmp_path):
        """Test that load_monster_families validates icon field presence."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Test missing icon
        no_icon_content = """---
title: Test Family
short_title: Test Family
tag_line: Test Tagline
is_monster_family: true
---

# Test Family

*Test Tagline*
"""

        no_icon_file = families_dir / "no_icon.md"
        no_icon_file.write_text(no_icon_content)

        with patch(
            "foe_foundry_data.monster_families.data.Path.cwd", return_value=tmp_path
        ):
            with patch(
                "foe_foundry_data.monster_families.data.get_base_url",
                return_value="http://test.example.com",
            ):
                with pytest.raises(ValueError, match="Icon not found"):
                    load_monster_families()

    def test_load_monster_families_validates_tag_line_field(self, tmp_path):
        """Test that load_monster_families validates tag_line field presence."""
        # Set up test directory structure
        docs_dir = tmp_path / "docs"
        families_dir = docs_dir / "families"
        families_dir.mkdir(parents=True)

        # Test missing tag_line
        no_tag_line_content = """---
title: Test Family
short_title: Test Family
icon: test-icon
is_monster_family: true
---

# Test Family

*Test Tagline*
"""

        no_tag_line_file = families_dir / "no_tag_line.md"
        no_tag_line_file.write_text(no_tag_line_content)

        with patch(
            "foe_foundry_data.monster_families.data.Path.cwd", return_value=tmp_path
        ):
            with patch(
                "foe_foundry_data.monster_families.data.get_base_url",
                return_value="http://test.example.com",
            ):
                with pytest.raises(ValueError, match="Tag line not found"):
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

        # Load the families and find the soldiers family
        families = load_monster_families()
        soldiers_family = None
        for family in families:
            if family.key == "soldiers-and-fighters":
                soldiers_family = family
                break

        assert soldiers_family is not None
        assert soldiers_family.name == "Soldiers and Fighters"
        assert soldiers_family.icon == "rally-the-troops"
        assert (
            soldiers_family.tag_line
            == "Battle-Hardened Warriors of Duty, Honor, or Fortune"
        )
        # Should have templates for the expected monster types
        assert len(soldiers_family.templates) > 0

        # Check that we have the expected templates
        template_keys = {template.key for template in soldiers_family.templates}
        expected_templates = {"berserker", "guard", "knight", "warrior"}
        assert template_keys == expected_templates

    @pytest.mark.integration
    def test_load_actual_fanatics_family(self):
        """Integration test: Load the actual fanatics_and_faithful family file."""
        project_root = Path(__file__).parent.parent.parent
        families_dir = project_root / "docs" / "families"
        fanatics_file = families_dir / "fanatics_and_faithful.md"

        if not fanatics_file.exists():
            pytest.skip("fanatics_and_faithful.md file not found")

        # Load the families and find the fanatics family
        families = load_monster_families()
        fanatics_family = None
        for family in families:
            if family.key == "fanatics-and-faithful":
                fanatics_family = family
                break

        assert fanatics_family is not None
        assert fanatics_family.name == "Fanatics and Faithful"
        assert fanatics_family.icon == "chalice-drops"
        assert fanatics_family.tag_line == "Faithful Followers of the Occult or Divine"
        # Should have templates for the expected monster types
        assert len(fanatics_family.templates) > 0
        # Check that we have the expected templates
        template_keys = {template.key for template in fanatics_family.templates}
        expected_templates = {"priest", "cultist", "knight"}
        assert template_keys == expected_templates


class TestMonsterFamilyCache:
    """Test the monster family caching functionality."""

    def test_monster_families_cache_access(self):
        """Test accessing families through the MonsterFamilies cache."""
        # This is an integration test that verifies the cache structure works
        families = MonsterFamilies.families
        assert isinstance(families, list)
        assert len(families) > 0

        # Verify all families have the required fields
        for family in families:
            assert hasattr(family, "key")
            assert hasattr(family, "name")
            assert hasattr(family, "icon")
            assert hasattr(family, "tag_line")
            assert hasattr(family, "templates")
            assert isinstance(family.templates, list)

    def test_monster_families_lookup(self):
        """Test the lookup functionality of MonsterFamilies."""
        lookup = MonsterFamilies.lookup
        assert isinstance(lookup, dict)
        assert len(lookup) > 0

        # Test that we can find a specific family
        soldiers_family = lookup.get("soldiers-and-fighters")
        if soldiers_family is not None:
            assert soldiers_family.name == "Soldiers and Fighters"
            assert soldiers_family.icon == "rally-the-troops"
            assert (
                soldiers_family.tag_line
                == "Battle-Hardened Warriors of Duty, Honor, or Fortune"
            )
