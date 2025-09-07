import json
from dataclasses import asdict
from datetime import datetime
from functools import cached_property
from pathlib import Path

from foe_foundry.utils.env import get_base_url

from ..base import MonsterFamilyInfo
from .data import load_monster_families


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class _MonsterFamilyCache:
    def __init__(self):
        self.cache_dir = Path.cwd() / "cache" / "monster_families"

    @cached_property
    def families(self) -> list[MonsterFamilyInfo]:
        # Try to load from cache first
        if self.cache_dir.exists():
            cached_families = self._load_from_cache()
            if cached_families:
                return cached_families

        # Fallback to runtime generation if cache is missing
        self.generate_cache()
        results = self._load_from_cache()
        if results is None:
            raise ValueError("Failed to load monster family cache")
        return results

    def _load_from_cache(self) -> list[MonsterFamilyInfo] | None:
        """Load families from cached JSON files."""
        try:
            families = []
            json_files = list(self.cache_dir.glob("*.json"))

            if not json_files:
                return None

            for json_file in json_files:
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Convert ISO datetime strings back to datetime objects for templates
                    for template_data in data.get("templates", []):
                        if "create_date" in template_data and isinstance(template_data["create_date"], str):
                            template_data["create_date"] = datetime.fromisoformat(
                                template_data["create_date"]
                            )

                    family = MonsterFamilyInfo(**data)
                    families.append(family)

            # Sort families for consistent ordering
            families.sort(key=lambda f: f.key)
            return families

        except Exception:
            # If there's any error loading from cache, fall back to generation
            return None

    def _generate_families(self) -> list[MonsterFamilyInfo]:
        """Generate families at runtime (fallback behavior)."""
        return load_monster_families()

    def generate_cache(self) -> None:
        """Generate and save family cache to disk. Called during build time."""
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Clear existing cache files
        for json_file in self.cache_dir.glob("*.json"):
            json_file.unlink()

        # Generate all families
        families = self._generate_families()

        # Save each family as an individual JSON file
        for family in families:
            cache_file = self.cache_dir / f"{family.key}.json"
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(
                    asdict(family),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    cls=DateTimeEncoder,
                )

    @cached_property
    def lookup(self) -> dict[str, MonsterFamilyInfo]:
        return {family.key: family for family in self.families}


MonsterFamilies = _MonsterFamilyCache()