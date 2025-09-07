import json
from dataclasses import asdict
from functools import cached_property
from pathlib import Path

from .data import MonsterFamilyModel
from .load import load_families as load_families_core


class _FamilyCache:
    def __init__(self):
        self.cache_dir = Path.cwd() / "cache" / "families"

    @cached_property
    def all_monster_families(self) -> list[MonsterFamilyModel]:
        # Try to load from cache first
        if self.cache_dir.exists():
            cached_families = self._load_from_cache()
            if cached_families:
                return cached_families

        # Fallback to runtime generation if cache is missing
        self.generate_cache()
        results = self._load_from_cache()
        if results is None:
            raise ValueError("Failed to load family cache")
        return results

    def _load_from_cache(self) -> list[MonsterFamilyModel] | None:
        """Load families from cached JSON files."""
        try:
            families = []
            json_files = list(self.cache_dir.glob("*.json"))

            if not json_files:
                return None

            for json_file in json_files:
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                    family = MonsterFamilyModel(**data)
                    families.append(family)

            # Sort families for consistent ordering
            families.sort(key=lambda f: f.key)
            return families

        except Exception:
            # If there's any error loading from cache, fall back to generation
            return None

    def _generate_families(self) -> list[MonsterFamilyModel]:
        """Generate families at runtime (fallback behavior)."""
        return load_families_core()

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
                )

    @cached_property
    def lookup(self) -> dict[str, MonsterFamilyModel]:
        return {family.key: family for family in self.all_monster_families}


Families = _FamilyCache()


def load_families() -> list[MonsterFamilyModel]:
    """
    Loads all monster families from the data files.

    Returns:
        list[MonsterFamilyModel]: A list of all loaded monster families.
    """
    return Families.all_monster_families
