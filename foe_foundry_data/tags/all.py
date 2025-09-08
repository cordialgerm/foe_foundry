"""Tag lookup cache with example monsters for each tag."""

from functools import cached_property
from typing import Dict, List
import random

from foe_foundry.tags.definitions import ALL_TAG_DEFINITIONS
from foe_foundry_data.monsters import Monsters
from foe_foundry_data.base import MonsterInfoModel

from .data import TagInfoModel


class TagLookupCache:
    """Caches tag lookups with example monsters for faster access"""

    @cached_property
    def TagLookup(self) -> Dict[str, TagInfoModel]:
        """Get all tags with their example monsters"""
        tag_models = {}
        
        # Get all monsters for finding examples
        all_monsters = Monsters.one_of_each_monster
        
        for tag_def in ALL_TAG_DEFINITIONS:
            # Find monsters that have this tag
            monsters_with_tag = [
                monster for monster in all_monsters
                if monster.tags and any(tag.tag.lower() == tag_def.name.lower() for tag in monster.tags)
            ]
            
            # Select diverse examples (up to 4)
            diverse_monsters = self._select_diverse_examples(monsters_with_tag, max_examples=4)
            
            # Convert MonsterModel to MonsterInfoModel
            example_monsters = [
                MonsterInfoModel(
                    key=monster.key,
                    name=monster.name,
                    cr=monster.cr,
                    template=monster.template_key,
                    background_image=monster.background_image,
                    creature_type=monster.creature_type,
                    tag_line=monster.tag_line,
                    tags=monster.tags
                )
                for monster in diverse_monsters
            ]
            
            # Create TagInfoModel
            tag_models[tag_def.key] = TagInfoModel.from_tag_definition(tag_def, example_monsters)
        
        return tag_models

    def _select_diverse_examples(self, monsters, max_examples: int = 4):
        """Select diverse monster examples prioritizing different families, creature types, and CRs"""
        if not monsters:
            return []
        
        if len(monsters) <= max_examples:
            return monsters
        
        # Group monsters by different attributes for diversity
        by_cr = {}
        by_creature_type = {}
        by_family = {}
        
        for monster in monsters:
            # Group by CR tier
            cr_tier = int(monster.cr // 5)  # 0-4, 5-9, 10-14, 15-19, 20+
            by_cr.setdefault(cr_tier, []).append(monster)
            
            # Group by creature type
            if monster.creature_type:
                by_creature_type.setdefault(monster.creature_type, []).append(monster)
            
            # Group by family (extract from template name)
            family = self._extract_family(monster.template_key)
            if family:
                by_family.setdefault(family, []).append(monster)
        
        selected = []
        used_monsters = set()
        
        # Strategy 1: Try to get one from each CR tier
        for cr_tier in sorted(by_cr.keys()):
            if len(selected) >= max_examples:
                break
            candidates = [m for m in by_cr[cr_tier] if m.key not in used_monsters]
            if candidates:
                chosen = random.choice(candidates)
                selected.append(chosen)
                used_monsters.add(chosen.key)
        
        # Strategy 2: Fill remaining slots with different creature types
        for creature_type in by_creature_type:
            if len(selected) >= max_examples:
                break
            candidates = [m for m in by_creature_type[creature_type] if m.key not in used_monsters]
            if candidates:
                chosen = random.choice(candidates)
                selected.append(chosen)
                used_monsters.add(chosen.key)
        
        # Strategy 3: Fill remaining slots with different families
        for family in by_family:
            if len(selected) >= max_examples:
                break
            candidates = [m for m in by_family[family] if m.key not in used_monsters]
            if candidates:
                chosen = random.choice(candidates)
                selected.append(chosen)
                used_monsters.add(chosen.key)
        
        # Strategy 4: Fill any remaining slots randomly
        while len(selected) < max_examples:
            candidates = [m for m in monsters if m.key not in used_monsters]
            if not candidates:
                break
            chosen = random.choice(candidates)
            selected.append(chosen)
            used_monsters.add(chosen.key)
        
        return selected[:max_examples]
    
    def _extract_family(self, template_key: str) -> str:
        """Extract family name from template key"""
        # Simple extraction - template keys like "goblin_warrior" -> "goblin"
        if not template_key:
            return ""
        
        parts = template_key.lower().split('_')
        if len(parts) > 1:
            return parts[0]
        
        return template_key.lower()

    @cached_property
    def AllTags(self) -> List[TagInfoModel]:
        """Get all tags as a list"""
        return list(self.TagLookup.values())


Tags = TagLookupCache()