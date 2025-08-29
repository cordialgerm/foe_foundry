from typing import Any, Dict, List, Optional

from foe_foundry.ac_templates import (
    ArcaneArmor,
    BerserkersDefense,
    Breastplate,
    ChainmailArmor,
    ChainShirt,
    HideArmor,
    HolyArmor,
    LeatherArmor,
    NaturalArmor,
    NaturalPlating,
    PatchworkArmor,
    PlateArmor,
    SplintArmor,
    StuddedLeatherArmor,
    Unarmored,
    UnholyArmor,
    flat,
)
from foe_foundry.attack_template import AttackTemplate, natural, spell, weapon
from foe_foundry.creature_types import CreatureType
from foe_foundry.creatures._data import GenerationSettings
from foe_foundry.creatures.species import AllSpecies, CreatureSpecies
from foe_foundry.damage import Condition, DamageType
from foe_foundry.environs import (
    Affinity,
    Biome,
    Development,
    EnvironmentAffinity,
    ExtraplanarInfluence,
    Region,
    Terrain,
)
from foe_foundry.movement import Movement
from foe_foundry.powers import PowerSelection
from foe_foundry.role_types import MonsterRole
from foe_foundry.senses import Senses
from foe_foundry.size import Size
from foe_foundry.skills import AbilityScore, Skills, StatScaling
from foe_foundry.statblocks import BaseStatblock

from ._template import Monster, MonsterTemplate, MonsterVariant
from .base_stats import base_stats

try:
    from ..spells import CasterType
except ImportError:
    CasterType = None


class YamlMonsterTemplate(MonsterTemplate):
    def __init__(self, yaml_data: dict):
        # Store yaml_data for use in methods
        self.yaml_data = yaml_data

        template_data = yaml_data["template"]

        # Extract required fields
        name = template_data["name"]

        # Parse variants from yaml_data
        variants = parse_variants_from_template_yaml(template_data)

        # Parse species from yaml_data
        species = parse_species_from_template_yaml(template_data)

        # Parse environments from yaml_data
        environments = parse_environments_from_template_yaml(template_data)

        # Parse sentient flag
        is_sentient_species = template_data.get("is_sentient_species", False)

        # Call parent constructor with parsed data
        super().__init__(
            name=name,
            tag_line="TODO LATER",
            description="TODO LATER",
            treasure=["TODO LATER"],
            variants=variants,
            species=species,
            environments=environments,
            is_sentient_species=is_sentient_species,
        )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        stats = parse_statblock_from_yaml(self.yaml_data, settings)
        attacks = parse_attacks_from_yaml(self.yaml_data, settings)
        return stats, attacks

    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        # Import the appropriate powers based on template key
        template_key = self.yaml_data["template"]["key"]  # Use the key from YAML data instead
        monster_key = settings.monster_key

        try:
            # Import powers module for the template
            module_name = template_key.replace('-', '_')
            powers_module = __import__(f"foe_foundry.creatures.{module_name}.powers", fromlist=[''])
            
            # Map monster keys to power loadouts based on template
            if template_key == "wolf":
                if monster_key == "wolf":
                    return PowerSelection(powers_module.LoadoutWolf)
                elif monster_key == "dire-wolf":
                    return PowerSelection(powers_module.LoadoutDireWolf)
                elif monster_key == "winter-wolf":
                    return PowerSelection(powers_module.LoadoutFrostWolf)
                elif monster_key == "fellwinter-packlord":
                    return PowerSelection(powers_module.LoadoutPacklord)
                else:
                    return PowerSelection(powers_module.LoadoutWolf)
            elif template_key == "animated-armor":
                if monster_key == "animated-armor":
                    return PowerSelection(powers_module.LoadoutAnimatedArmor)
                elif monster_key == "animated-runeplate":
                    return PowerSelection(powers_module.LoadoutRunicSpellplate)
                else:
                    return PowerSelection(powers_module.LoadoutAnimatedArmor)
            else:
                # For other templates, try to find a default loadout
                # Look for common loadout names
                loadout_attrs = [attr for attr in dir(powers_module) 
                               if attr.startswith('Loadout') and not attr.endswith('__')]
                if loadout_attrs:
                    # Use the first loadout found
                    loadout = getattr(powers_module, loadout_attrs[0])
                    return PowerSelection(loadout)
                
                # If no loadout found, return empty selection
                return PowerSelection([])
                
        except (ImportError, AttributeError) as e:
            # If powers module doesn't exist or loadout not found, raise an error
            raise ValueError(f"Could not load powers for template {template_key}: {e}") from e


# ===== PARSING HELPER FUNCTIONS =====


def merge_template_data(
    common_data: Dict[str, Any], monster_data: Dict[str, Any]
) -> Dict[str, Any]:
    """
    Merge common template data with monster-specific overrides.

    This performs a deep merge, recursively merging nested dictionaries.
    Lists are replaced entirely (no merging).

    Args:
        common_data: The common/shared configuration
        monster_data: Monster-specific overrides (can be None for empty monster sections)

    Returns:
        Merged configuration dictionary
    """
    merged = common_data.copy()

    # Handle case where monster_data is None or empty
    if monster_data is None:
        return merged

    for key, value in monster_data.items():
        if key == "<<":
            continue  # Skip YAML anchor reference

        if isinstance(value, dict) and key in merged and isinstance(merged[key], dict):
            # Deep merge for nested dictionaries - recursively merge
            merged[key] = merge_template_data(merged[key], value)
        elif (
            isinstance(value, list) and key in merged and isinstance(merged[key], list)
        ):
            # Replace lists entirely (no merging)
            merged[key] = value
        else:
            # Direct replacement
            merged[key] = value

    return merged


def parse_stat_scaling(scaling_info: Any) -> Any:
    """
    Parse stat scaling information from YAML.

    Args:
        scaling_info: String like "Primary" or list like ["Medium", 2]

    Returns:
        StatScaling enum or tuple of (StatScaling, modifier)
    """
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


def parse_abilities_from_yaml(data: Dict[str, Any]) -> Dict[AbilityScore, Any]:
    """
    Parse ability scores from YAML data.

    Args:
        data: YAML data containing abilities section

    Returns:
        Dictionary mapping AbilityScore to scaling info
    """
    abilities_data = data.get("abilities", {})
    stats = {}

    for ability_name, scaling_info in abilities_data.items():
        ability = getattr(AbilityScore, ability_name, None)
        if ability:
            stats[ability] = parse_stat_scaling(scaling_info)

    return stats


def parse_creature_types_from_yaml(
    data: Dict[str, Any],
) -> tuple[CreatureType, List[CreatureType]]:
    """
    Parse creature types from YAML data.

    Args:
        data: YAML data containing creature_type and optional additional_creature_types

    Returns:
        Tuple of (primary_type, additional_types_list)
    """
    primary_type = getattr(CreatureType, data["creature_type"])
    additional_types = []

    if "additional_creature_types" in data:
        additional_types = [
            getattr(CreatureType, t) for t in data["additional_creature_types"]
        ]

    return primary_type, additional_types


def parse_roles_from_yaml(
    data: Dict[str, Any],
) -> tuple[Optional[MonsterRole], List[MonsterRole]]:
    """
    Parse monster roles from YAML data.

    Args:
        data: YAML data containing roles section

    Returns:
        Tuple of (primary_role, additional_roles_list)
    """
    roles_data = data.get("roles", {})
    primary_role = None
    additional_roles = []

    if roles_data.get("primary"):
        primary_role = getattr(MonsterRole, roles_data["primary"])

    if roles_data.get("additional"):
        additional_roles = [
            getattr(MonsterRole, role) for role in roles_data["additional"]
        ]

    return primary_role, additional_roles


def parse_movement_from_yaml(data: Dict[str, Any]) -> Optional[Movement]:
    """
    Parse movement data from YAML.

    Args:
        data: YAML data containing speed section

    Returns:
        Movement object, or None if no movement data
    """
    speed_data = data.get("speed", {})
    if not speed_data:
        return None

    # Handle both integer speed modifiers and structured speed objects
    if isinstance(speed_data, (int, float)):
        # If speed is a number, it's a speed modifier, not structured movement
        # Return None so the base template speed calculation is used
        return None
    
    if not isinstance(speed_data, dict):
        # If it's not a dict or number, we can't parse it
        return None

    movement_kwargs = {}
    for movement_type in ["walk", "climb", "fly", "swim", "burrow"]:
        if movement_type in speed_data:
            movement_kwargs[movement_type] = speed_data[movement_type]

    if "hover" in speed_data:
        movement_kwargs["hover"] = speed_data["hover"]

    return Movement(**movement_kwargs) if movement_kwargs else None


def parse_senses_from_yaml(data: Dict[str, Any]) -> Optional[Senses]:
    """
    Parse senses data from YAML.

    Args:
        data: YAML data containing senses section

    Returns:
        Senses object, or None if no senses data
    """
    senses_data = data.get("senses", {})
    if not senses_data:
        return None

    senses_kwargs = {}
    for sense_type in ["darkvision", "blindsight", "tremorsense", "truesight"]:
        if sense_type in senses_data:
            senses_kwargs[sense_type] = senses_data[sense_type]

    return Senses(**senses_kwargs) if senses_kwargs else None


def parse_damage_immunities_from_yaml(data: Dict[str, Any]) -> tuple[set, set]:
    """
    Parse damage immunities and condition immunities from YAML.

    Args:
        data: YAML data containing immunities and condition_immunities

    Returns:
        Tuple of (damage_type_immunities_set, condition_immunities_set)
    """
    damage_immunities = set()
    condition_immunities = set()

    # Handle nested immunities structure
    immunities_data = data.get("immunities", {})
    if immunities_data:
        damage_immunity_names = immunities_data.get("damage_types", [])
        for dt_name in damage_immunity_names:
            dt = getattr(DamageType, dt_name, None)
            if dt:
                damage_immunities.add(dt)

        condition_immunity_names = immunities_data.get("conditions", [])
        for cond_name in condition_immunity_names:
            cond = getattr(Condition, cond_name, None)
            if cond:
                condition_immunities.add(cond)

    # Handle legacy direct formats: damage_immunities: [...], condition_immunities: [...]
    legacy_damage_immunities = data.get("damage_immunities", [])
    if legacy_damage_immunities:
        for dt_name in legacy_damage_immunities:
            dt = getattr(DamageType, dt_name, None)
            if dt:
                damage_immunities.add(dt)

    legacy_condition_immunities = data.get("condition_immunities", [])
    for condition_name in legacy_condition_immunities:
        condition = getattr(Condition, condition_name, None)
        if condition:
            condition_immunities.add(condition)

    return damage_immunities, condition_immunities


def parse_damage_resistances_from_yaml(data: Dict[str, Any]) -> set:
    """
    Parse damage resistances from YAML.

    Args:
        data: YAML data containing resistances section

    Returns:
        Set of DamageType objects for resistances
    """
    resistances = set()

    # Try new structured format first: resistances: damage_types: [...]
    resistances_data = data.get("resistances", {})
    if resistances_data:
        damage_resistance_names = resistances_data.get("damage_types", [])
        for dt_name in damage_resistance_names:
            dt = getattr(DamageType, dt_name, None)
            if dt:
                resistances.add(dt)

    # Try legacy direct format: damage_resistances: [...]
    legacy_resistances = data.get("damage_resistances", [])
    if legacy_resistances:
        for dt_name in legacy_resistances:
            dt = getattr(DamageType, dt_name, None)
            if dt:
                resistances.add(dt)

    return resistances


def parse_skills_from_yaml(data: Dict[str, Any]) -> tuple[List[Skills], List[Skills]]:
    """
    Parse skill proficiencies and expertises from YAML.

    Args:
        data: YAML data containing skills section

    Returns:
        Tuple of (proficiency_skills_list, expertise_skills_list)
    """
    skills_data = data.get("skills", {})
    proficiency_skills = []
    expertise_skills = []

    for skill_name in skills_data.get("proficiency", []):
        skill = getattr(Skills, skill_name, None)
        if skill:
            proficiency_skills.append(skill)

    for skill_name in skills_data.get("expertise", []):
        skill = getattr(Skills, skill_name, None)
        if skill:
            expertise_skills.append(skill)

    return proficiency_skills, expertise_skills


def parse_ac_templates_from_yaml(data: Dict[str, Any]) -> List[Any]:
    """
    Parse AC templates from YAML data.

    Args:
        data: YAML data containing ac_templates section

    Returns:
        List of ArmorClassTemplate objects

    Raises:
        ValueError: If no ac_templates are specified
    """
    if "ac_templates" not in data:
        raise ValueError("ac_templates section is required but not found in YAML data")
    
    ac_templates_data = data["ac_templates"]
    if not ac_templates_data:
        raise ValueError("ac_templates cannot be empty - at least one AC template must be specified")
    
    templates = []

    # Map template names to actual template objects
    template_map = {
        "ArcaneArmor": ArcaneArmor,
        "BerserkersDefense": BerserkersDefense,
        "Breastplate": Breastplate,
        "ChainShirt": ChainShirt,
        "ChainmailArmor": ChainmailArmor,
        "flat": flat,
        "HideArmor": HideArmor,
        "HolyArmor": HolyArmor,
        "LeatherArmor": LeatherArmor,
        "NaturalArmor": NaturalArmor,
        "NaturalPlating": NaturalPlating,
        "PatchworkArmor": PatchworkArmor,
        "PlateArmor": PlateArmor,
        "SplintArmor": SplintArmor,
        "StuddedLeatherArmor": StuddedLeatherArmor,
        "Unarmored": Unarmored,
        "UnholyArmor": UnholyArmor,
    }

    for template_data in ac_templates_data:
        if isinstance(template_data, dict):
            template_name = template_data.get("template")
            if template_name and template_name in template_map:
                templates.append(template_map[template_name])
        elif isinstance(template_data, str):
            # Handle simple string format
            if template_data in template_map:
                templates.append(template_map[template_data])

    return templates


def parse_saving_throws_from_yaml(data: Dict[str, Any]) -> List[AbilityScore]:
    """
    Parse saving throw proficiencies from YAML.

    Args:
        data: YAML data containing saves section

    Returns:
        List of AbilityScore objects for save proficiencies
    """
    saves = []
    save_names = data.get("saves", [])

    for save_name in save_names:
        ability = getattr(AbilityScore, save_name, None)
        if ability:
            saves.append(ability)

    return saves


def parse_secondary_damage_type_from_yaml(secondary_damage_data: Any) -> Optional[Any]:
    """
    Parse secondary damage type information from YAML.

    Args:
        secondary_damage_data: String, list of strings, or None

    Returns:
        DamageType, list of DamageTypes, or None
    """
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


def parse_statblock_from_yaml(
    yaml_data: dict, settings: GenerationSettings
) -> BaseStatblock:
    """
    Parse a BaseStatblock from YAML template data.

    Args:
        yaml_data: Full YAML template data
        settings: Generation settings containing monster key and variant info

    Returns:
        Configured BaseStatblock
    """
    # Get the monster-specific data
    template_data = yaml_data["template"]

    # Find the monster info from template metadata
    monster_info = None
    for monster in template_data.get("monsters", []):
        if monster["key"] == settings.monster_key:
            monster_info = monster
            break

    if not monster_info:
        raise ValueError(f"Monster '{settings.monster_key}' not found in template")

    # Get common data - only support single "common" section
    if "common" not in yaml_data:
        raise ValueError("No 'common' section found in template")

    common_data = yaml_data["common"]

    # Get monster-specific data
    monster_data = yaml_data.get(settings.monster_key, {})

    # Merge the data
    merged_data = merge_template_data(common_data, monster_data)

    # Extract basic info
    name = monster_info["name"]
    cr = monster_info["cr"]
    is_legendary = monster_info.get("legendary", False)

    # Parse ability scores
    stats = parse_abilities_from_yaml(merged_data)

    # Get HP and damage multipliers
    hp_multiplier = merged_data.get("hp_multiplier", 1.0)
    damage_multiplier = merged_data.get("damage_multiplier", 1.0)

    # Create base statblock using base_stats function
    try:
        statblock = base_stats(
            name=name,
            template_key=template_data["key"],
            variant_key=settings.variant.key,
            monster_key=settings.monster_key,
            species_key=None,
            cr=cr,
            stats=stats,
            hp_multiplier=hp_multiplier,
            damage_multiplier=damage_multiplier,
        )
    except Exception as e:
        raise RuntimeError(f"Failed to create base statblock: {e}")

    # Apply creature types
    if "creature_type" in merged_data:
        primary_type, additional_types = parse_creature_types_from_yaml(merged_data)
        if additional_types:
            statblock = statblock.with_types(
                primary_type=primary_type, additional_types=additional_types
            )
        else:
            statblock = statblock.copy(creature_type=primary_type)

    # Apply basic properties
    modifications = {}

    if "size" in merged_data:
        modifications["size"] = getattr(Size, merged_data["size"])

    if "languages" in merged_data:
        modifications["languages"] = merged_data["languages"]

    if "creature_class" in merged_data:
        modifications["creature_class"] = merged_data["creature_class"]

    if "creature_subtype" in merged_data:
        modifications["creature_subtype"] = merged_data["creature_subtype"]

    # Apply modifications
    if modifications:
        statblock = statblock.copy(**modifications)

    # Apply AC templates
    ac_templates = parse_ac_templates_from_yaml(merged_data)
    if ac_templates:
        statblock = statblock.copy(ac_templates=ac_templates)

    # Apply movement
    movement = parse_movement_from_yaml(merged_data)
    if movement:
        statblock = statblock.copy(speed=movement)

    # Apply senses
    senses = parse_senses_from_yaml(merged_data)
    if senses:
        statblock = statblock.copy(senses=senses)

    # Apply legendary status
    if is_legendary:
        legendary_data = merged_data.get("legendary", {})
        if legendary_data:
            actions = legendary_data.get("actions", 3)
            resistances = legendary_data.get("resistances", 3)
            statblock = statblock.as_legendary(actions=actions, resistances=resistances)
        else:
            statblock = statblock.as_legendary()

    # Apply roles
    primary_role, additional_roles = parse_roles_from_yaml(merged_data)
    if primary_role:
        statblock = statblock.with_roles(
            primary_role=primary_role, additional_roles=additional_roles
        )

    # Apply immunities and resistances
    damage_immunities, condition_immunities = parse_damage_immunities_from_yaml(
        merged_data
    )
    if damage_immunities or condition_immunities:
        statblock = statblock.grant_resistance_or_immunity(
            immunities=damage_immunities if damage_immunities else None,
            conditions=condition_immunities if condition_immunities else None,
        )

    damage_resistances = parse_damage_resistances_from_yaml(merged_data)
    if damage_resistances:
        statblock = statblock.grant_resistance_or_immunity(
            resistances=damage_resistances
        )

    # Apply skills
    proficiency_skills, expertise_skills = parse_skills_from_yaml(merged_data)
    for skill in proficiency_skills:
        statblock = statblock.grant_proficiency_or_expertise(skill)

    for skill in expertise_skills:
        # Note: may need different method for expertise vs proficiency
        statblock = statblock.grant_proficiency_or_expertise(skill)

    # Apply saving throws
    saves = parse_saving_throws_from_yaml(merged_data)
    for ability in saves:
        statblock = statblock.copy(
            attributes=statblock.attributes.grant_save_proficiency(ability)
        )

    # Apply secondary damage type
    secondary_damage_type = parse_secondary_damage_type_from_yaml(
        merged_data.get("attacks", {}).get("main", {}).get("secondary_damage_type")
    )
    if secondary_damage_type:
        statblock = statblock.copy(secondary_damage_type=secondary_damage_type)

    # Apply spellcasting
    spellcasting_data = merged_data.get("spellcasting", {})
    if spellcasting_data:
        caster_type_name = spellcasting_data.get("caster_type")
        if caster_type_name and CasterType:
            caster_type = getattr(CasterType, caster_type_name, None)
            if caster_type:
                statblock = statblock.grant_spellcasting(caster_type=caster_type)

    # Apply attack reduction
    attack_reduction = merged_data.get("attack_reduction")
    if attack_reduction:
        statblock = statblock.with_reduced_attacks(reduce_by=attack_reduction)

    return statblock


def parse_single_attack_from_yaml(
    attack_data: Dict[str, Any],
) -> Optional[AttackTemplate]:
    """
    Parse a single attack template from YAML data.

    Args:
        attack_data: YAML data for a single attack

    Returns:
        AttackTemplate or None if attack cannot be created
    """
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
    if reach and hasattr(attack, "copy"):
        attack = attack.copy(reach=reach)

    # Apply damage scalar if specified
    damage_scalar = attack_data.get("damage_scalar")
    if damage_scalar and hasattr(attack, "copy"):
        attack = attack.copy(damage_scalar=damage_scalar)

    # Apply damage type override if specified
    damage_type = attack_data.get("damage_type")
    if damage_type:
        damage_type_obj = getattr(DamageType, damage_type, None)
        if damage_type_obj and hasattr(attack, "copy"):
            attack = attack.copy(damage_type=damage_type_obj)

    # Apply damage multiplier if specified
    damage_multiplier = attack_data.get("damage_multiplier", 1.0)
    if damage_multiplier != 1.0 and hasattr(attack, "with_damage_multiplier"):
        attack = attack.with_damage_multiplier(damage_multiplier)

    return attack


def parse_attacks_from_yaml(
    yaml_data: dict, settings: GenerationSettings
) -> list[AttackTemplate]:
    """
    Parse attack templates from YAML template data.

    Args:
        yaml_data: Full YAML template data
        settings: Generation settings containing monster key

    Returns:
        List of AttackTemplate objects
    """
    # Get the merged data for this monster
    template_data = yaml_data["template"]

    # Get common data - only support single "common" section
    if "common" not in yaml_data:
        raise ValueError("No 'common' section found in template")

    common_data = yaml_data["common"]

    # Get monster-specific data
    monster_data = yaml_data.get(settings.monster_key, {})

    # Merge the data
    merged_data = merge_template_data(common_data, monster_data)

    attacks = []
    attacks_data = merged_data.get("attacks", {})

    # Main attack
    main_attack = attacks_data.get("main", {})
    if main_attack:
        attack = parse_single_attack_from_yaml(main_attack)
        if attack:
            attacks.append(attack)

    # Secondary attack
    secondary_attack = attacks_data.get("secondary", {})
    if secondary_attack and secondary_attack is not None:
        attack = parse_single_attack_from_yaml(secondary_attack)
        if attack:
            attacks.append(attack)

    return attacks


def parse_species_from_template_yaml(template_data: dict) -> list[CreatureSpecies]:
    species_option = template_data.get("species", None)
    if species_option == "all":
        return AllSpecies
    else:
        return []


def parse_variants_from_template_yaml(template_data: dict) -> list[MonsterVariant]:
    """Parse variants from template YAML data, grouping monsters appropriately."""
    monsters: list[dict] = template_data["monsters"]

    # For the wolf template, group monsters into two variants
    # This logic should be generalized in the future for other templates
    template_key = template_data["key"]

    if template_key == "wolf":
        # Create Wolf variant (for wolf and dire-wolf)
        wolf_monsters = []
        winter_wolf_monsters = []

        for monster_data in monsters:
            name = monster_data["name"]
            cr = monster_data["cr"]
            is_legendary = monster_data.get("legendary", False)

            monster = Monster(
                name=name,
                cr=cr,
                is_legendary=is_legendary,
                srd_creatures=None,  # TODO LATER
                other_creatures=None,  # TODO LATER
            )

            # Group monsters by variant
            if monster.key in ["wolf", "dire-wolf"]:
                wolf_monsters.append(monster)
            elif monster.key in ["winter-wolf", "fellwinter-packlord"]:
                winter_wolf_monsters.append(monster)

        variants = []
        if wolf_monsters:
            variants.append(
                MonsterVariant(
                    name="Wolf",
                    description="Wolves are pack hunters that stalk their prey with cunning and ferocity.",
                    monsters=wolf_monsters,
                )
            )

        if winter_wolf_monsters:
            variants.append(
                MonsterVariant(
                    name="Winter Wolf",
                    description="Winter wolves are large, intelligent wolves with white fur and a breath weapon that can freeze their foes.",
                    monsters=winter_wolf_monsters,
                )
            )

        return variants

    else:
        # Default behavior: one variant per monster (for other templates)
        variants = []
        for monster_data in monsters:
            name = monster_data["name"]
            cr = monster_data["cr"]
            is_legendary = monster_data.get("legendary", False)

            monster = Monster(
                name=name,
                cr=cr,
                is_legendary=is_legendary,
                srd_creatures=None,  # TODO LATER
                other_creatures=None,  # TODO LATER
            )

            variant = MonsterVariant(name=name, description=name, monsters=[monster])
            variants.append(variant)

        return variants


def parse_environments_from_template_yaml(
    template_data: dict,
) -> list[EnvironmentAffinity]:
    """
    Parse environment affinities from template YAML data.

    Args:
        template_data: The template section of the YAML data

    Returns:
        List of EnvironmentAffinity objects
    """
    environments_data = template_data.get("environments", None)
    if not environments_data:
        return []

    affinities = []

    # Handle both list format and dict format
    if isinstance(environments_data, list):
        # List format: [{"development": "urban", "affinity": "common"}, ...]
        for env_data in environments_data:
            if not isinstance(env_data, dict):
                continue

            affinity_name = env_data.get("affinity", "common")
            affinity = getattr(Affinity, affinity_name, Affinity.common)

            # Create environment affinities based on the environment type
            for env_type, env_value in env_data.items():
                if env_type == "affinity":
                    continue

                try:
                    if env_type == "development":
                        env_obj = getattr(Development, env_value, None)
                    elif env_type == "biome":
                        env_obj = getattr(Biome, env_value, None)
                    elif env_type == "terrain":
                        env_obj = getattr(Terrain, env_value, None)
                    elif env_type == "region":
                        env_obj = getattr(Region, env_value, None)
                    elif env_type == "extraplanar":
                        env_obj = getattr(ExtraplanarInfluence, env_value, None)
                    else:
                        continue

                    if env_obj:
                        affinities.append((env_obj, affinity))

                except AttributeError:
                    # Skip unknown environment values
                    continue

    elif isinstance(environments_data, dict):
        # Dict format: {"urban": "common", "wilderness": "native", ...}
        for env_name, affinity_name in environments_data.items():
            try:
                affinity = getattr(Affinity, affinity_name, Affinity.common)

                # Try to find the environment in different categories
                env_obj = None
                for env_class in [
                    Development,
                    Biome,
                    Terrain,
                    Region,
                    ExtraplanarInfluence,
                ]:
                    try:
                        env_obj = getattr(env_class, env_name, None)
                        if env_obj:
                            break
                    except AttributeError:
                        continue

                if env_obj:
                    affinities.append((env_obj, affinity))

            except AttributeError:
                # Skip unknown environment or affinity values
                continue

    return affinities
