from ..attributes import Skills, Stats
from ..damage import DamageType
from ..powers import LOW_POWER, MEDIUM_POWER, RIBBON_POWER
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock, MonsterDials
from .template import CreatureSpecies

ElfSpecies = CreatureSpecies(name="Elf", description="")


class _DwarfSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Dwarf",
            description="Dwarves were raised from the earth in the elder days by a deity of the forge. They are known for their hardiness, craftsmanship, their love of stone and metal, and their fierce loyalty to their clans.",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.grant_resistance_or_immunity(resistances={DamageType.Poison})
        stats = stats.apply_monster_dials(
            MonsterDials(hp_multiplier=1.1, recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.with_roles(additional_roles=[MonsterRole.Soldier])
        stats = stats.copy(name=f"Dwarf {stats.name}", creature_subtype="Dwarf")
        return stats


class _OrcSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Orc",
            description="Orcs are a powerful and aggressive species that are known for their endurance and strength",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.apply_monster_dials(
            MonsterDials(
                ac_modifier=-1,
                recommended_powers_modifier=-RIBBON_POWER,
                attack_damage_multiplier=1.1,
            )
        )
        stats = stats.copy(name=f"Orc {stats.name}", creature_subtype="Orc")
        stats = stats.scale({Stats.STR: Stats.STR.Boost(2)})
        stats = stats.with_roles(additional_roles=[MonsterRole.Bruiser])
        return stats


class _HumanSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Human",
            description="Humans are a diverse species known for their adaptability and ambition",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.cr <= 1:
            modifier = LOW_POWER
        else:
            modifier = MEDIUM_POWER

        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=modifier)
        )
        stats = stats.copy(creature_subtype="Human")
        return stats


class _HalflingSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Halfling",
            description="Halflings are a small, nimble species known for their luck and stealth",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.copy(name=f"Halfling {stats.name}", creature_subtype="Halfling")
        stats = stats.grant_proficiency_or_expertise(Skills.Stealth)
        stats = stats.scale(
            {Stats.DEX: Stats.DEX.Boost(2), Stats.WIS: Stats.WIS.Boost(2)}
        )
        stats = stats.with_roles(additional_roles=[MonsterRole.Skirmisher])
        return stats


class _GnomeSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="Gnome",
            description="Gnomes are a small, clever species known for their intelligence and curiosity",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.copy(name=f"Gnome {stats.name}", creature_subtype="Gnome")
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana)
        stats = stats.scale(
            {Stats.INT: Stats.INT.Boost(2), Stats.WIS: Stats.WIS.Boost(2)}
        )
        stats = stats.with_roles(additional_roles=[MonsterRole.Controller])
        return stats


DwarfSpecies: CreatureSpecies = _DwarfSpecies()
OrcSpecies: CreatureSpecies = _OrcSpecies()
HumanSpecies: CreatureSpecies = _HumanSpecies()
HalflingSpecies: CreatureSpecies = _HalflingSpecies()
GnomeSpecies: CreatureSpecies = _GnomeSpecies()

AllSpecies = [DwarfSpecies, HumanSpecies, OrcSpecies, GnomeSpecies, HalflingSpecies]
