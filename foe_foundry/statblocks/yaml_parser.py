"""
YAML Template Parser

Parses declarative YAML statblock templates and returns BaseStatblock and AttackTemplate objects
similar to what MonsterTemplate.generate_stats() produces.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

from ..statblocks.base import BaseStatblock
from ..attack_template import AttackTemplate
from ..creature_types import CreatureType
from ..size import Size
from ..role_types import MonsterRole
from ..skills import AbilityScore, StatScaling
from ..movement import Movement
from ..senses import Senses
from ..attributes import Attributes
from ..die import DieFormula, Die
from ..damage import DamageType


class YAMLTemplateParser:
    """Parser for YAML statblock templates."""
    
    def __init__(self):
        self.templates = {}
    
    def load_template(self, yaml_path: Path) -> Dict[str, Any]:
        """Load a YAML template from file."""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            template_data = yaml.safe_load(f)
        return template_data
    
    def parse_template(self, yaml_path: Path, monster_key: str, cr: float = None) -> Tuple[BaseStatblock, List[AttackTemplate]]:
        """
        Parse a YAML template and return BaseStatblock and AttackTemplate objects.
        
        Args:
            yaml_path: Path to the YAML template file
            monster_key: The specific monster variant to generate (e.g., 'assassin', 'assassin-legend')
            cr: Optional CR override
            
        Returns:
            Tuple of (BaseStatblock, list[AttackTemplate])
        """
        template_data = self.load_template(yaml_path)
        
        # Find the monster definition
        monster_info = None
        for monster in template_data['template']['monsters']:
            if monster['key'] == monster_key:
                monster_info = monster
                break
        
        if not monster_info:
            raise ValueError(f"Monster '{monster_key}' not found in template")
        
        # Use provided CR or get from monster definition
        monster_cr = cr if cr is not None else monster_info['cr']
        monster_name = monster_info['name']
        is_legendary = monster_info.get('legendary', False)
        
        # Get common stats
        common_stats = template_data['common']
        
        # Get variant-specific overrides
        variant_stats = template_data.get(monster_key, {})
        
        # Merge common and variant stats
        merged_stats = self._merge_stats(common_stats, variant_stats)
        
        # Build BaseStatblock
        base_stats = self._build_base_statblock(
            name=monster_name,
            template_key=template_data['template']['key'],
            monster_key=monster_key,
            cr=monster_cr,
            is_legendary=is_legendary,
            stats=merged_stats
        )
        
        # Build AttackTemplates
        attacks = self._build_attack_templates(merged_stats.get('attacks', {}))
        
        return base_stats, attacks
    
    def _merge_stats(self, common: Dict[str, Any], variant: Dict[str, Any]) -> Dict[str, Any]:
        """Merge common stats with variant-specific overrides."""
        # Deep copy common stats
        import copy
        merged = copy.deepcopy(common)
        
        # Apply variant overrides
        for key, value in variant.items():
            if key == '<<':
                continue  # Skip YAML anchor reference
            merged[key] = value
        
        return merged
    
    def _build_base_statblock(self, name: str, template_key: str, monster_key: str, 
                              cr: float, is_legendary: bool, stats: Dict[str, Any]) -> BaseStatblock:
        """Build a BaseStatblock from merged stats."""
        
        # Parse creature type
        creature_type_str = stats.get('creature_type', 'Humanoid')
        creature_type = getattr(CreatureType, creature_type_str, CreatureType.Humanoid)
        
        # Parse size
        size_str = stats.get('size', 'Medium')
        size = getattr(Size, size_str, Size.Medium)
        
        # Parse roles
        roles_data = stats.get('roles', {})
        primary_role = getattr(MonsterRole, roles_data.get('primary', 'Default'), MonsterRole.Default)
        additional_roles = [
            getattr(MonsterRole, role, MonsterRole.Default) 
            for role in roles_data.get('additional', [])
        ]
        
        # Parse abilities (simplified for now)
        abilities_data = stats.get('abilities', {})
        attributes = self._build_attributes(abilities_data, cr)
        
        # Build basic movement (30 ft walk speed default)
        walk_speed = stats.get('walk_speed', 30)
        fly_speed = stats.get('fly_speed')
        climb_speed = stats.get('climb_speed')
        burrow_speed = stats.get('burrow_speed')
        
        movement = Movement(
            walk=walk_speed,
            fly=fly_speed,
            climb=climb_speed,
            burrow=burrow_speed
        )
        
        # Build senses
        senses = Senses(
            darkvision=stats.get('darkvision', 0),
            blindsight=stats.get('blindsight', 0),
            truesight=stats.get('truesight', 0)
        )
        
        # Calculate HP (simplified - using a basic formula)
        hp_multiplier = stats.get('hp_multiplier', 1.0)
        hp_formula = self._calculate_hp_formula(cr, size, hp_multiplier)
        
        # Create BaseStatblock
        base_stats = BaseStatblock(
            name=name,
            template_key=template_key,
            variant_key=monster_key,  # Simplified
            monster_key=monster_key,
            species_key=None,  # Simplified
            cr=cr,
            hp=hp_formula,
            creature_type=creature_type,
            creature_class=stats.get('creature_class'),
            role=primary_role,
            additional_roles=additional_roles,
            speed=movement,
            size=size,
            senses=senses,
            attributes=attributes,
            languages=stats.get('languages', []),
            damage_multiplier=stats.get('damage_multiplier', 1.0),
            secondary_damage_type=self._parse_damage_type(stats.get('secondary_damage_type')),
            primary_damage_type=self._parse_damage_type(stats.get('primary_damage_type')),
            is_legendary=is_legendary
        )
        
        return base_stats
    
    def _build_attributes(self, abilities_data: Dict[str, Any], cr: float) -> Attributes:
        """Build Attributes from abilities data (simplified)."""
        # This is a simplified implementation
        # In reality, we'd need to implement the StatScaling logic
        base_scores = {
            'STR': 10,
            'DEX': 10, 
            'CON': 10,
            'INT': 10,
            'WIS': 10,
            'CHA': 10
        }
        
        # Apply some basic CR-based scaling
        cr_bonus = int(cr // 4)
        
        for ability, scaling in abilities_data.items():
            if scaling == 'Primary':
                base_scores[ability] = 13 + cr_bonus + 2
            elif scaling == 'Medium':
                base_scores[ability] = 12 + cr_bonus
            elif scaling == 'Constitution':
                base_scores[ability] = 12 + cr_bonus + 1
            # Default stays at 10 + small bonus
            elif scaling == 'Default':
                base_scores[ability] = 10 + cr_bonus // 2
        
        # Calculate proficiency bonus based on CR
        proficiency = 2 + int(cr // 4)
        if proficiency > 9:
            proficiency = 9  # Cap at +9
        
        return Attributes(
            proficiency=proficiency,
            STR=base_scores['STR'],
            DEX=base_scores['DEX'],
            CON=base_scores['CON'],
            INT=base_scores['INT'],
            WIS=base_scores['WIS'],
            CHA=base_scores['CHA']
        )
    
    def _calculate_hp_formula(self, cr: float, size: Size, hp_multiplier: float) -> DieFormula:
        """Calculate HP formula based on CR and size (simplified)."""
        # This is a very simplified HP calculation
        # In reality, we'd use the same logic as base_stats()
        
        # Base HP by CR (rough approximation)
        base_hp_by_cr = {
            0.125: 7, 0.25: 9, 0.5: 11, 1: 13, 2: 16, 3: 19, 4: 22,
            5: 25, 6: 28, 7: 31, 8: 34, 9: 37, 10: 40, 11: 43, 12: 46,
            13: 49, 14: 52, 15: 55, 16: 58, 17: 61, 18: 64, 19: 67, 20: 70,
            21: 73, 22: 76, 23: 79, 24: 82, 25: 85, 26: 88, 27: 91, 28: 94, 29: 97, 30: 100
        }
        
        base_hp = base_hp_by_cr.get(cr, int(cr * 3 + 10))
        final_hp = int(base_hp * hp_multiplier)
        
        # Create a simple die formula (this is very simplified)
        die_count = max(1, final_hp // 6)
        bonus = final_hp - (die_count * 4)  # Rough average for d8
        
        return DieFormula.from_dice(d8=die_count, mod=bonus)
    
    def _parse_damage_type(self, damage_type_data) -> DamageType | None:
        """Parse damage type from YAML data."""
        if not damage_type_data:
            return None
        
        if isinstance(damage_type_data, str):
            return getattr(DamageType, damage_type_data, None)
        
        # Handle list of damage types (random choice) - for now just take first
        if isinstance(damage_type_data, list) and damage_type_data:
            return getattr(DamageType, damage_type_data[0], None)
        
        return None
    
    def _build_attack_templates(self, attacks_data: Dict[str, Any]) -> List[AttackTemplate]:
        """Build AttackTemplate objects from attacks data."""
        attack_templates = []
        
        # Handle main attack
        main_attack = attacks_data.get('main')
        if main_attack:
            attack_template = self._build_single_attack(main_attack)
            if attack_template:
                attack_templates.append(attack_template)
        
        # Handle secondary attack
        secondary_attack = attacks_data.get('secondary')
        if secondary_attack:
            attack_template = self._build_single_attack(secondary_attack)
            if attack_template:
                attack_templates.append(attack_template)
        
        return attack_templates
    
    def _build_single_attack(self, attack_data: Dict[str, Any]) -> AttackTemplate | None:
        """Build a single AttackTemplate from attack data."""
        base_name = attack_data.get('base')
        if not base_name or base_name == 'TBD':
            return None
        
        # This is very simplified - in reality we'd need to import
        # and look up the actual weapon/attack templates
        display_name = attack_data.get('display_name', base_name)
        damage_multiplier = attack_data.get('damage_multiplier', 1.0)
        
        # Create a basic attack template (this is a placeholder)
        from ..attack_template.weapon import Daggers  # Example import
        
        # This is a simplified approach - in reality we'd have a registry
        # of all available attack templates to look up by name
        return AttackTemplate(
            attack_name=base_name,
            display_name=display_name,
            die=Die.d6,  # Placeholder
            damage_scalar=damage_multiplier
        )


def parse_yaml_template(yaml_path: Path, monster_key: str, cr: float = None) -> Tuple[BaseStatblock, List[AttackTemplate]]:
    """
    Convenience function to parse a YAML template.
    
    Args:
        yaml_path: Path to the YAML template file
        monster_key: The specific monster variant to generate
        cr: Optional CR override
        
    Returns:
        Tuple of (BaseStatblock, list[AttackTemplate])
    """
    parser = YAMLTemplateParser()
    return parser.parse_template(yaml_path, monster_key, cr)