"""
YAML Template Parser

Parses declarative YAML statblock templates and returns BaseStatblock and AttackTemplate objects
similar to what MonsterTemplate.generate_stats() produces.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml

from ..attack_template import AttackTemplate, natural, spell, weapon
from ..creature_types import CreatureType
from ..damage import Condition, DamageType
from ..role_types import MonsterRole
from ..size import Size
from ..skills import AbilityScore, Skills, StatScaling
from ..statblocks.base import BaseStatblock


def get_ac_template_by_name(template_name: str):
    """Get AC template by name - placeholder implementation."""
    # This would need to be implemented to return the actual AC template
    # For now, return None to avoid errors
    return None


def parse_yaml_template(
    yaml_path: Path, monster_key: str, cr: float = None
) -> Tuple[BaseStatblock, List[AttackTemplate]]:
    """
    Parse a YAML template and return BaseStatblock and AttackTemplate objects.

    Args:
        yaml_path: Path to the YAML template file
        monster_key: The specific monster variant to generate (e.g., 'berserker', 'berserker-legend')
        cr: Optional CR override

    Returns:
        Tuple of (BaseStatblock, list[AttackTemplate])
    """
    parser = YAMLTemplateParser()
    return parser.parse_template(yaml_path, monster_key, cr)


class YAMLTemplateParser:
    """Parser for YAML statblock templates."""

    def __init__(self):
        self.templates = {}

    def load_template(self, yaml_path: Path) -> Dict[str, Any]:
        """Load a YAML template from file."""
        with open(yaml_path, "r", encoding="utf-8") as f:
            template_data = yaml.safe_load(f)
        return template_data

    def parse_template(
        self, yaml_path: Path, monster_key: str, cr: float = None
    ) -> Tuple[BaseStatblock, List[AttackTemplate]]:
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
        common_data = template_data.get("common", {})
        monster_data = template_data.get(monster_key, {})

        # Find monster info from template metadata
        monster_info = None
        for monster in template_data.get("template", {}).get("monsters", []):
            if monster["key"] == monster_key:
                monster_info = monster
                break

        if not monster_info:
            raise ValueError(f"Monster '{monster_key}' not found in template")

        # Use provided CR or template CR
        actual_cr = cr if cr is not None else monster_info["cr"]
        is_legendary = monster_info.get("legendary", False)

        # Merge common and monster-specific data
        merged_data = self._merge_template_data(common_data, monster_data)

        # Build the statblock
        statblock = self._build_statblock(
            merged_data, monster_info["name"], actual_cr, is_legendary
        )

        # Build attacks
        attacks = self._build_attacks(merged_data)

        return statblock, attacks

    def _merge_template_data(
        self, common_data: Dict[str, Any], monster_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Merge common template data with monster-specific overrides."""
        merged = common_data.copy()

        for key, value in monster_data.items():
            if key == "<<":
                continue  # Skip YAML anchor reference

            if (
                isinstance(value, dict)
                and key in merged
                and isinstance(merged[key], dict)
            ):
                # Deep merge for nested dictionaries
                merged[key] = {**merged[key], **value}
            elif (
                isinstance(value, list)
                and key in merged
                and isinstance(merged[key], list)
            ):
                # Replace lists entirely (no merging)
                merged[key] = value
            else:
                # Direct replacement
                merged[key] = value

        return merged

    def _build_statblock(
        self, data: Dict[str, Any], name: str, cr: float, is_legendary: bool
    ) -> BaseStatblock:
        """Build a BaseStatblock from template data using the base_stats function."""

        # Parse ability scores
        abilities_data = data.get("abilities", {})
        stats = {}
        for ability_name, scaling_info in abilities_data.items():
            ability = getattr(AbilityScore, ability_name, None)
            if ability:
                stats[ability] = self._parse_stat_scaling(scaling_info)

        # Get HP and damage multipliers
        hp_multiplier = data.get("hp_multiplier", 1.0)
        damage_multiplier = data.get("damage_multiplier", 1.0)

        # Create base statblock using base_stats function
        try:
            from ..creatures.base_stats import base_stats

            statblock = base_stats(
                name=name,
                template_key="yaml_template",
                variant_key="yaml_variant",
                monster_key=name.lower().replace(" ", "-"),
                species_key=None,
                cr=cr,
                stats=stats,
                hp_multiplier=hp_multiplier,
                damage_multiplier=damage_multiplier,
            )
        except Exception as e:
            raise RuntimeError(f"Failed to create base statblock: {e}")

        # Apply modifications using copy method
        modifications = {}

        # Basic creature information
        if "creature_type" in data:
            primary_type = getattr(CreatureType, data["creature_type"])
            additional_types = []
            if "additional_types" in data:
                additional_types = [
                    getattr(CreatureType, t) for t in data["additional_types"]
                ]

            # Use with_types if additional types exist
            if additional_types:
                statblock = statblock.with_types(
                    primary_type=primary_type, additional_types=additional_types
                )
            else:
                modifications["creature_type"] = primary_type

        if "size" in data:
            modifications["size"] = getattr(Size, data["size"])

        if "languages" in data:
            modifications["languages"] = data["languages"]

        if "creature_class" in data:
            modifications["creature_class"] = data["creature_class"]

        if "creature_subtype" in data:
            modifications["creature_subtype"] = data["creature_subtype"]

        # Apply modifications
        if modifications:
            statblock = statblock.copy(**modifications)

        # Add movement if specified
        movement_data = data.get("movement", {})
        if movement_data:
            current_movement = statblock.speed
            movement_kwargs = {}
            if "walk" in movement_data:
                movement_kwargs["walk"] = movement_data["walk"]
            if "climb" in movement_data:
                movement_kwargs["climb"] = movement_data["climb"]
            if "fly" in movement_data:
                movement_kwargs["fly"] = movement_data["fly"]
            if "swim" in movement_data:
                movement_kwargs["swim"] = movement_data["swim"]

            if movement_kwargs:
                new_movement = current_movement.copy(**movement_kwargs)
                statblock = statblock.copy(speed=new_movement)

        # Add senses if specified
        senses_data = data.get("senses", {})
        if senses_data:
            current_senses = statblock.senses
            senses_kwargs = {}
            if "darkvision" in senses_data:
                senses_kwargs["darkvision"] = senses_data["darkvision"]
            if "blindsight" in senses_data:
                senses_kwargs["blindsight"] = senses_data["blindsight"]
            if "tremorsense" in senses_data:
                senses_kwargs["tremorsense"] = senses_data["tremorsense"]
            if "truesight" in senses_data:
                senses_kwargs["truesight"] = senses_data["truesight"]

            if senses_kwargs:
                new_senses = current_senses.copy(**senses_kwargs)
                statblock = statblock.copy(senses=new_senses)

        # Add legendary status
        if is_legendary:
            # Check for legendary configuration
            legendary_data = data.get("legendary", {})
            if legendary_data:
                actions = legendary_data.get("actions", 3)
                resistances = legendary_data.get("resistances", 3)
                statblock = statblock.as_legendary(
                    actions=actions, resistances=resistances
                )
            else:
                statblock = statblock.as_legendary()

        # Add roles
        roles_data = data.get("roles", {})
        if roles_data.get("primary"):
            primary_role = getattr(MonsterRole, roles_data["primary"])
            additional_roles = [
                getattr(MonsterRole, role) for role in roles_data.get("additional", [])
            ]
            statblock = statblock.with_roles(
                primary_role=primary_role, additional_roles=additional_roles
            )

        # Add attack reduction if specified
        attack_reduction = data.get("attack_reduction")
        if attack_reduction:
            statblock = statblock.with_reduced_attacks(reduce_by=attack_reduction)

        # Add AC templates
        ac_templates = data.get("ac_templates", [])
        for ac_template_info in ac_templates:
            template_name = ac_template_info.get("template")
            modifier = ac_template_info.get("modifier", 0)
            if template_name:
                ac_template = get_ac_template_by_name(template_name)
                if ac_template:
                    statblock = statblock.add_ac_template(ac_template, modifier)

        # Add condition immunities
        condition_immunities = data.get("condition_immunities", [])
        for condition_name in condition_immunities:
            condition = getattr(Condition, condition_name, None)
            if condition:
                statblock = statblock.grant_resistance_or_immunity(
                    conditions={condition}
                )

        # Add nested immunities structure
        immunities_data = data.get("immunities", {})
        if immunities_data:
            # Damage type immunities
            damage_immunities = immunities_data.get("damage_types", [])
            damage_type_objs = set()
            for dt_name in damage_immunities:
                dt = getattr(DamageType, dt_name, None)
                if dt:
                    damage_type_objs.add(dt)

            # Condition immunities
            condition_immunities = immunities_data.get("conditions", [])
            condition_objs = set()
            for cond_name in condition_immunities:
                cond = getattr(Condition, cond_name, None)
                if cond:
                    condition_objs.add(cond)

            if damage_type_objs or condition_objs:
                statblock = statblock.grant_resistance_or_immunity(
                    immunities=damage_type_objs if damage_type_objs else None,
                    conditions=condition_objs if condition_objs else None,
                )

        # Add nested resistances structure
        resistances_data = data.get("resistances", {})
        if resistances_data:
            # Damage type resistances
            damage_resistances = resistances_data.get("damage_types", [])
            damage_type_objs = set()
            for dt_name in damage_resistances:
                dt = getattr(DamageType, dt_name, None)
                if dt:
                    damage_type_objs.add(dt)

            if damage_type_objs:
                statblock = statblock.grant_resistance_or_immunity(
                    resistances=damage_type_objs
                )

        # Add damage immunities/resistances/vulnerabilities (legacy format)
        for immunity_type in [
            "damage_immunities",
            "damage_resistances",
            "damage_vulnerabilities",
        ]:
            damage_types = data.get(immunity_type, [])
            damage_type_objs = set()
            for dt_name in damage_types:
                dt = getattr(DamageType, dt_name, None)
                if dt:
                    damage_type_objs.add(dt)

            if damage_type_objs:
                if immunity_type == "damage_immunities":
                    statblock = statblock.grant_resistance_or_immunity(
                        immunities=damage_type_objs
                    )
                elif immunity_type == "damage_resistances":
                    statblock = statblock.grant_resistance_or_immunity(
                        resistances=damage_type_objs
                    )
                # Note: damage_vulnerabilities would need separate handling if implemented

        # Add skills
        skills_data = data.get("skills", {})
        proficiency_skills = skills_data.get("proficiency", [])
        expertise_skills = skills_data.get("expertise", [])

        # Grant proficiency for all skills
        for skill_name in proficiency_skills:
            skill = getattr(Skills, skill_name, None)
            if skill:
                statblock = statblock.grant_proficiency_or_expertise(skill)

        # Grant expertise for expertise skills (this might override proficiency)
        for skill_name in expertise_skills:
            skill = getattr(Skills, skill_name, None)
            if skill:
                # Note: may need different method for expertise
                statblock = statblock.grant_proficiency_or_expertise(skill)

        # Add saving throw proficiencies
        saves = data.get("saves", [])
        for save_name in saves:
            ability = getattr(AbilityScore, save_name, None)
            if ability:
                statblock = statblock.copy(
                    attributes=statblock.attributes.grant_save_proficiency(ability)
                )

        # Add secondary damage type if specified
        secondary_damage_type = self._parse_secondary_damage_type(
            data.get("attacks", {}).get("main", {}).get("secondary_damage_type")
        )
        if secondary_damage_type:
            statblock = statblock.copy(secondary_damage_type=secondary_damage_type)

        # Add spellcasting if specified
        spellcasting_data = data.get("spellcasting", {})
        if spellcasting_data:
            caster_type_name = spellcasting_data.get("caster_type")
            if caster_type_name:
                try:
                    from ..spells import CasterType

                    caster_type = getattr(CasterType, caster_type_name, None)
                    if caster_type:
                        statblock = statblock.grant_spellcasting(
                            caster_type=caster_type
                        )
                except ImportError:
                    # Skip spellcasting if CasterType not available
                    pass

        return statblock

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

    def _build_attacks(self, data: Dict[str, Any]) -> List[AttackTemplate]:
        """Build attack templates from template data."""
        attacks = []

        attacks_data = data.get("attacks", {})

        # Main attack
        main_attack = attacks_data.get("main", {})
        if main_attack:
            attack = self._build_single_attack(main_attack)
            if attack:
                attacks.append(attack)

        # Secondary attack
        secondary_attack = attacks_data.get("secondary", {})
        if secondary_attack and secondary_attack is not None:
            attack = self._build_single_attack(secondary_attack)
            if attack:
                attacks.append(attack)

        return attacks

    def _build_single_attack(
        self, attack_data: Dict[str, Any]
    ) -> Optional[AttackTemplate]:
        """Build a single attack template."""
        base_name = attack_data.get("base")
        if not base_name:
            return None

        # Get the base attack template - check weapon, natural, and spell
        base_attack = getattr(weapon, base_name, None)
        if not base_attack:
            base_attack = getattr(natural, base_name, None)
        if not base_attack:
            base_attack = getattr(spell, base_name, None)
        if not base_attack:
            return None

        attack = base_attack

        # Apply display name if specified
        display_name = attack_data.get("display_name")
        if display_name:
            attack = attack.with_display_name(display_name)

        # Apply reach if specified
        reach = attack_data.get("reach")
        if reach:
            if hasattr(attack, "copy"):
                attack = attack.copy(reach=reach)

        # Apply damage scalar if specified
        damage_scalar = attack_data.get("damage_scalar")
        if damage_scalar:
            if hasattr(attack, "copy"):
                attack = attack.copy(damage_scalar=damage_scalar)

        # Apply damage type override if specified
        damage_type = attack_data.get("damage_type")
        if damage_type:
            damage_type_obj = getattr(DamageType, damage_type, None)
            if damage_type_obj and hasattr(attack, "copy"):
                attack = attack.copy(damage_type=damage_type_obj)

        # Apply damage multiplier if specified
        damage_multiplier = attack_data.get("damage_multiplier", 1.0)
        if damage_multiplier != 1.0:
            # Check if the method exists
            if hasattr(attack, "with_damage_multiplier"):
                attack = attack.with_damage_multiplier(damage_multiplier)
            else:
                # Skip damage multiplier if method not available
                pass

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
