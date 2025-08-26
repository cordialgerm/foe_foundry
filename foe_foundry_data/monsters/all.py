import json
from dataclasses import asdict
from datetime import datetime
from functools import cached_property
from pathlib import Path

from foe_foundry.creatures import AllTemplates
from foe_foundry.powers import Power
from foe_foundry.utils.env import get_base_url
from foe_foundry_data.refs import MonsterRef, MonsterRefResolver

from .data import MonsterModel


class DateTimeEncoder(json.JSONEncoder):
    """Custom JSON encoder that handles datetime objects."""

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


class _MonsterCache:
    def __init__(self):
        self.cache_dir = Path.cwd() / "cache" / "monsters"

    @cached_property
    def one_of_each_monster(self) -> list[MonsterModel]:
        # Try to load from cache first
        if self.cache_dir.exists():
            cached_monsters = self._load_from_cache()
            if cached_monsters:
                return cached_monsters

        # Fallback to runtime generation if cache is missing
        self.generate_cache()
        results = self._load_from_cache()
        if results is None:
            raise ValueError("Failed to load monster cache")
        return results

    def _load_from_cache(self) -> list[MonsterModel] | None:
        """Load monsters from cached JSON files."""
        try:
            monsters = []
            json_files = list(self.cache_dir.glob("*.json"))

            if not json_files:
                return None

            for json_file in json_files:
                with json_file.open("r", encoding="utf-8") as f:
                    data = json.load(f)

                    # Convert ISO datetime string back to datetime object
                    if "create_date" in data and isinstance(data["create_date"], str):
                        data["create_date"] = datetime.fromisoformat(
                            data["create_date"]
                        )

                    monster = MonsterModel(**data)
                    monsters.append(monster)

            # Sort monsters for consistent ordering
            monsters.sort(key=lambda m: m.key)
            return monsters

        except Exception:
            # If there's any error loading from cache, fall back to generation
            return None

    def _generate_monsters(self) -> list[MonsterModel]:
        """Generate monsters at runtime (fallback behavior)."""
        monsters = []
        for template in AllTemplates:
            for variant in template.variants:
                for monster in variant.monsters:
                    species = None
                    stats = template.generate_monster(
                        variant=variant, monster=monster, species=species
                    )
                    m = MonsterModel.from_monster(
                        stats=stats.finalize(),
                        template=template,
                        variant=variant,
                        monster=monster,
                        species=species,
                        base_url=get_base_url(),
                    )
                    monsters.append(m)
        return monsters

    def _is_cache_fresh(self) -> bool:
        """Check if the monster cache is fresh and doesn't need regeneration."""
        if not self.cache_dir.exists():
            return False
        
        json_files = list(self.cache_dir.glob("*.json"))
        if not json_files:
            return False
        
        # Check if cache files exist and are reasonably recent
        # In a real implementation, you might check against source file timestamps
        # For now, we'll assume cache is fresh if it exists and has files
        return len(json_files) > 0

    def generate_cache(self) -> None:
        """Generate and save monster cache to disk. Called during build time."""
        # Performance optimization: skip generation if cache is fresh
        if self._is_cache_fresh():
            import os
            if os.environ.get("SKIP_MONSTER_CACHE_GENERATION", "false").lower() == "true":
                print("Monster cache is fresh, skipping regeneration for performance.")
                return
        
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Clear existing cache files
        for json_file in self.cache_dir.glob("*.json"):
            json_file.unlink()

        # Generate all monsters
        monsters = self._generate_monsters()

        # Save each monster as an individual JSON file
        for monster in monsters:
            cache_file = self.cache_dir / f"{monster.key}.json"
            with cache_file.open("w", encoding="utf-8") as f:
                json.dump(
                    asdict(monster),
                    f,
                    ensure_ascii=False,
                    indent=2,
                    cls=DateTimeEncoder,
                )

    @cached_property
    def lookup(self) -> dict[str, MonsterModel]:
        return {monster.key: monster for monster in self.one_of_each_monster}


Monsters = _MonsterCache()


def monsters_for_power(power: Power) -> list[MonsterRef]:
    resolver = MonsterRefResolver()

    refs = []
    for monster in Monsters.one_of_each_monster:
        for loadout in monster.loadouts:
            for p in loadout.powers:
                if p.key == power.key:
                    ref = resolver.resolve_monster_ref(monster.name)
                    if ref is not None:
                        ref = ref.resolve()
                        refs.append(ref)

    def sort_by_name(ref: MonsterRef) -> str:
        return ref.monster.key if ref.monster is not None else ref.original_monster_name

    refs = sorted(refs, key=sort_by_name)
    return refs
