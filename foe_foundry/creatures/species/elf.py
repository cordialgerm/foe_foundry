from ...attack_template import spell
from ...attributes import Skills, Stats
from ...damage import AttackType
from ...powers import RIBBON_POWER
from ...role_types import MonsterRole
from ...spells import CasterType
from ...statblocks import BaseStatblock, MonsterDials
from .species import CreatureSpecies


class _HighElfSpecies(CreatureSpecies):
    def __init__(self):
        super().__init__(
            name="High Elf",
            description="High Elves are a tall, slender species known for their grace and intelligence",
        )

    def alter_base_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=-RIBBON_POWER)
        )
        stats = stats.copy(name=f"High Elf {stats.name}", creature_subtype="Elf")
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana)
        stats = stats.grant_spellcasting(CasterType.Arcane, Stats.INT)
        stats = stats.with_roles(additional_roles=[MonsterRole.Artillery])

        if not stats.attack_types.intersection(AttackType.AllSpell()):
            attack = spell.ArcaneBurst
            stats = attack.add_as_secondary_attack(stats)

        return stats


# High Elf Power Brainstorm

# Arcane Mastery - add extra damage to a spell or spell attack
# Fey Step - like Misty Step

# Wood Elf Power Brainstorm

# Stealth and Perception proficiency
# Vanish into the Woods - become invisible when in natural terrain
# Fleet of Foot - faster movement

# Dark Elf Power Brainstorm

# Faerie Fire
# Darkness

HighElfSpecies: CreatureSpecies = _HighElfSpecies()
