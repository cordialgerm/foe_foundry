"""
YAML Template Parser

Parses declarative YAML statblock templates and returns BaseStatblock and AttackTemplate objects
similar to what MonsterTemplate.generate_stats() produces.
"""
from __future__ import annotations

import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from ..statblocks.base import BaseStatblock
from ..attack_template import AttackTemplate, weapon
from ..creature_types import CreatureType
from ..size import Size
from ..role_types import MonsterRole
from ..skills import AbilityScore, StatScaling, Skills
from ..damage import DamageType, Condition
from ..attributes import Attributes
from ..movement import Movement
from ..senses import Senses
from ..die import DieFormula


def get_ac_template_by_name(template_name: str):
    """Get AC template by name - placeholder implementation."""
    # This would need to be implemented to return the actual AC template
    # For now, return None to avoid errors
    return None


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
            monster_key: The specific monster variant to generate (e.g., 'berserker', 'berserker-legend')
            cr: Optional CR override
            
        Returns:
            Tuple of (BaseStatblock, list[AttackTemplate])
        """
        template_data = self.load_template(yaml_path)
        
        # Get the common template and the specific monster variant
        common_data = template_data.get('common', {})
        monster_data = template_data.get(monster_key, {})
        
        # Find monster info from template metadata
        monster_info = None
        for monster in template_data.get('template', {}).get('monsters', []):
            if monster['key'] == monster_key:
                monster_info = monster
                break
        
        if not monster_info:
            raise ValueError(f"Monster '{monster_key}' not found in template")
        
        # Use provided CR or template CR
        actual_cr = cr if cr is not None else monster_info['cr']
        is_legendary = monster_info.get('legendary', False)
        
        # Merge common and monster-specific data
        merged_data = self._merge_template_data(common_data, monster_data)
        
        # Build the statblock
        statblock = self._build_statblock(merged_data, monster_info['name'], actual_cr, is_legendary)
        
        # Build attacks
        attacks = self._build_attacks(merged_data)
        
        return statblock, attacks
    
    def _merge_template_data(self, common_data: Dict[str, Any], monster_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge common template data with monster-specific overrides."""
        merged = common_data.copy()
        
        for key, value in monster_data.items():
            if key == '<<': 
                continue  # Skip YAML anchor reference
            
            if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
                # Deep merge for nested dictionaries
                merged[key] = {**merged[key], **value}
            elif isinstance(value, list) and key in merged and isinstance(merged[key], list):
                # Replace lists entirely (no merging)
                merged[key] = value
            else:
                # Direct replacement
                merged[key] = value
        
        return merged
    
    def _build_statblock(self, data: Dict[str, Any], name: str, cr: float, is_legendary: bool) -> BaseStatblock:
        """Build a BaseStatblock from template data."""
        
        # Basic creature information
        creature_type = getattr(CreatureType, data.get('creature_type', 'Humanoid'))
        size = getattr(Size, data.get('size', 'Medium'))
        
        # Build attributes with ability scores
        attributes = self._build_attributes(data.get('abilities', {}), cr)
        
        # Movement
        movement = Movement(
            walk=data.get('walk_speed', 30),
            fly=data.get('fly_speed'),
            burrow=data.get('burrow_speed'),
            climb=data.get('climb_speed'),
            swim=data.get('swim_speed')
        )
        
        # Senses
        senses = Senses(
            darkvision=data.get('darkvision'),
            blindsight=data.get('blindsight'),
            truesight=data.get('truesight')
        )
        
        # Roles
        roles_data = data.get('roles', {})
        primary_role = getattr(MonsterRole, roles_data.get('primary', 'Bruiser'), None) if roles_data.get('primary') else None
        additional_roles = [getattr(MonsterRole, role) for role in roles_data.get('additional', [])]
        
        # Create base statblock
        statblock = BaseStatblock(
            name=name,
            creature_type=creature_type,
            additional_creature_types=data.get('additional_creature_types', []),
            creature_subtype=data.get('creature_subtype'),
            size=size,
            cr=cr,
            attributes=attributes,
            movement=movement,
            senses=senses,
            languages=data.get('languages', []),
            creature_class=data.get('creature_class'),
            hp_multiplier=data.get('hp_multiplier', 1.0),
            damage_multiplier=data.get('damage_multiplier', 1.0)
        )
        
        # Add roles
        if primary_role:
            statblock = statblock.with_roles(primary_role=primary_role, additional_roles=additional_roles)
        
        # Add legendary status
        if is_legendary:
            statblock = statblock.as_legendary()
        
        # Add AC templates
        ac_templates = data.get('ac_templates', [])
        for ac_template_info in ac_templates:
            template_name = ac_template_info.get('template')
            modifier = ac_template_info.get('modifier', 0)
            if template_name:
                ac_template = get_ac_template_by_name(template_name)
                if ac_template:
                    statblock = statblock.add_ac_template(ac_template, modifier)
        
        # Add condition immunities
        condition_immunities = data.get('condition_immunities', [])
        for condition_name in condition_immunities:
            condition = getattr(Condition, condition_name, None)
            if condition:
                statblock = statblock.grant_resistance_or_immunity(conditions={condition})
        
        # Add damage immunities/resistances/vulnerabilities
        for immunity_type in ['damage_immunities', 'damage_resistances', 'damage_vulnerabilities']:
            damage_types = data.get(immunity_type, [])
            damage_type_objs = set()
            for dt_name in damage_types:
                dt = getattr(DamageType, dt_name, None)
                if dt:
                    damage_type_objs.add(dt)
            
            if damage_type_objs:
                if immunity_type == 'damage_immunities':
                    statblock = statblock.grant_resistance_or_immunity(damage_types=damage_type_objs)
                elif immunity_type == 'damage_resistances':
                    statblock = statblock.grant_resistance_or_immunity(damage_types=damage_type_objs, resistance=True)
                # Note: damage_vulnerabilities would need separate handling if implemented
        
        # Add skills
        skills_data = data.get('skills', {})
        proficiency_skills = skills_data.get('proficiency', [])
        expertise_skills = skills_data.get('expertise', [])
        
        all_skills = list(set(proficiency_skills + expertise_skills))
        for skill_name in all_skills:
            skill = getattr(Skills, skill_name, None)
            if skill:
                # Grant expertise if in expertise list, otherwise proficiency
                statblock = statblock.grant_proficiency_or_expertise(skill, force_expertise=skill_name in expertise_skills)
        
        # Add saving throw proficiencies
        saves = data.get('saves', [])
        for save_name in saves:
            ability = getattr(AbilityScore, save_name, None)
            if ability:
                statblock = statblock.copy(
                    attributes=statblock.attributes.grant_save_proficiency(ability)
                )
        
        # Add secondary damage type if specified
        secondary_damage_type = self._parse_secondary_damage_type(data.get('attacks', {}).get('main', {}).get('secondary_damage_type'))
        if secondary_damage_type:
            statblock = statblock.copy(secondary_damage_type=secondary_damage_type)
        
        return statblock
    
    def _build_attributes(self, abilities_data: Dict[str, Any], cr: float) -> Attributes:
        """Build Attributes object from abilities data."""
        # Map ability names to ability score enums
        ability_map = {
            'STR': AbilityScore.STR,
            'DEX': AbilityScore.DEX,
            'CON': AbilityScore.CON,
            'INT': AbilityScore.INT,
            'WIS': AbilityScore.WIS,
            'CHA': AbilityScore.CHA
        }
        
        stats = {}
        for ability_name, scaling_info in abilities_data.items():
            ability = ability_map.get(ability_name)
            if ability:
                stats[ability] = self._parse_stat_scaling(scaling_info)
        
        # Use a base stats function to generate the attributes
        # This is a simplified version - the real implementation would use the actual base_stats function
        return self._generate_base_attributes(stats, cr)
    
    def _parse_stat_scaling(self, scaling_info: Any) -> Any:
        """Parse stat scaling information."""
        if isinstance(scaling_info, str):
            # Simple scaling like "Primary"
            return getattr(StatScaling, scaling_info, StatScaling.Default)
        elif isinstance(scaling_info, list) and len(scaling_info) >= 2:
            # Tuple format like ["Medium", 2]
            scaling_type = getattr(StatScaling, scaling_info[0], StatScaling.Default)
            modifier = int(scaling_info[1])
            return (scaling_type, modifier)
        else:
            return StatScaling.Default
    
    def _generate_base_attributes(self, stats: Dict[AbilityScore, Any], cr: float) -> Attributes:
        """Generate base attributes - simplified version for parsing."""
        # This is a placeholder - in reality this would call the actual base_stats function
        # For now, return a basic Attributes object
        return Attributes(
            strength=10, dexterity=10, constitution=10, 
            intelligence=10, wisdom=10, charisma=10
        )
    
    def _build_attacks(self, data: Dict[str, Any]) -> List[AttackTemplate]:
        """Build attack templates from template data."""
        attacks = []
        
        attacks_data = data.get('attacks', {})
        
        # Main attack
        main_attack = attacks_data.get('main', {})
        if main_attack:
            attack = self._build_single_attack(main_attack)
            if attack:
                attacks.append(attack)
        
        # Secondary attack
        secondary_attack = attacks_data.get('secondary', {})
        if secondary_attack:
            attack = self._build_single_attack(secondary_attack)
            if attack:
                attacks.append(attack)
        
        return attacks
    
    def _build_single_attack(self, attack_data: Dict[str, Any]) -> Optional[AttackTemplate]:
        """Build a single attack template."""
        base_name = attack_data.get('base')
        if not base_name:
            return None
        
        # Get the base attack template
        base_attack = getattr(weapon, base_name, None)
        if not base_attack:
            return None
        
        attack = base_attack
        
        # Apply display name if specified
        display_name = attack_data.get('display_name')
        if display_name:
            attack = attack.with_display_name(display_name)
        
        # Apply damage multiplier if specified
        damage_multiplier = attack_data.get('damage_multiplier', 1.0)
        if damage_multiplier != 1.0:
            attack = attack.with_damage_multiplier(damage_multiplier)
        
        return attack
    
    def _parse_secondary_damage_type(self, secondary_damage_data: Any) -> Optional[Any]:
        """Parse secondary damage type information."""
        if not secondary_damage_data:
            return None
        
        if isinstance(secondary_damage_data, str):
            # Single damage type
            return getattr(DamageType, secondary_damage_data, None)
        elif isinstance(secondary_damage_data, list):
            # Multiple damage types (random choice)
            damage_types = []
            for dt_name in secondary_damage_data:
                dt = getattr(DamageType, dt_name, None)
                if dt:
                    damage_types.append(dt)
            return damage_types if damage_types else None
        
        return None