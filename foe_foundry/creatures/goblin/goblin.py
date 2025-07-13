from foe_foundry.environs import Affinity, Biome, Development, ExtraplanarInfluence, region, Terrain
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import Breastplate, ChainShirt, StuddedLeatherArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...powers import PowerSelection
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from ...spells import CasterType
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import base_stats
from . import powers

GoblinLickspittleVariant = MonsterVariant(
    name="Goblin Lickspittle",
    description="Goblin Lickspittles are the weakest of their kind, often serving as minions to more powerful goblins or as scouts and foragers",
    monsters=[
        Monster(
            name="Goblin Lickspittle",
            cr=1 / 8,
            other_creatures={"Goblin Minion": "mm25"},
        )
    ],
)
GoblinWarriorVariant = MonsterVariant(
    name="Goblin",
    description="Goblin warriors attack with overwhelming numbers and withdraw before their enemies can retaliate. They're also fond of setting ambushes.",
    monsters=[
        Monster(
            name="Goblin",
            cr=1 / 4,
            srd_creatures=["Goblin"],
            other_creatures={"Goblin Warrior": "mm25"},
        ),
    ],
)
GoblinBruteVariant = MonsterVariant(
    name="Goblin Brute",
    description="Goblin Brutes are larger and stronger than their kin, and they wield heavy weapons to crush their foes.",
    monsters=[
        Monster(
            name="Goblin Brute",
            cr=1 / 2,
            other_creatures={"Goblin Spinecleaver": "FleeMortals"},
        )
    ],
)
GoblinBossVariant = MonsterVariant(
    name="Goblin Boss",
    description="Goblin Bosses are larger and stronger than their kin, and they have a knack for inspiring their fellows to fight harder.",
    monsters=[
        Monster(
            name="Goblin Boss",
            cr=1,
            srd_creatures=["Goblin Boss"],
            other_creatures={"Goblin Underboss": "FleeMortals"},
        ),
        Monster(name="Goblin Warchief", cr=4),
    ],
)
GoblinShamanVariant = MonsterVariant(
    name="Goblin Shaman",
    description="Goblin Shamans are spellcasters who wield the power of the mischievous gods and spirits that goblins often worship.",
    monsters=[
        Monster(
            name="Goblin Foulhex",
            cr=1,
            other_creatures={
                "Nilbog": "motm",
                "Goblin Curspitter": "FleeMortals",
                "Goblin Warlock": "MonstrousMenagerie",
            },
        ),
        Monster(name="Goblin Shaman", cr=2, other_creatures={"Goblin Hexer": "mm25"}),
    ],
)


class _GoblinTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        """Selects the powers for the goblin based on its variant."""
        variant = settings.variant

        if variant is GoblinLickspittleVariant:
            return PowerSelection(
                loadouts=powers.LoadoutLickspittle,
            )
        elif variant is GoblinWarriorVariant:
            return PowerSelection(
                loadouts=powers.LoadoutWarrior,
            )
        elif variant is GoblinBruteVariant:
            return PowerSelection(
                loadouts=powers.LoadoutBrute,
            )
        elif variant is GoblinShamanVariant:
            if settings.monster_key == "goblin-foulhex":
                return PowerSelection(
                    loadouts=powers.LoadoutShaman,
                )
            elif settings.monster_key == "goblin-shaman":
                return PowerSelection(
                    loadouts=powers.LoadoutShamanAdept,
                )
            else:
                raise ValueError(f"Unknown goblin shaman key: {settings.monster_key}")
        elif variant is GoblinBossVariant:
            if settings.monster_key == "goblin-boss":
                return PowerSelection(loadouts=powers.LoadoutBoss)
            elif settings.monster_key == "goblin-warchief":
                return PowerSelection(loadouts=powers.LoadoutWarchief)
            else:
                raise ValueError(f"Unknown goblin boss key: {settings.monster_key}")
        else:
            raise ValueError(f"Unknown goblin variant: {variant}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        rng = settings.rng

        # STATS
        if variant is GoblinLickspittleVariant or variant is GoblinWarriorVariant:
            hp_multiplier = 0.7 if cr < 0.5 else 0.8
            damage_multiplier = 1.0 if cr < 0.5 else 1.1
            attrs = [
                Stats.STR.scaler(StatScaling.Default, mod=-3),
                Stats.DEX.scaler(StatScaling.Primary, mod=2 if cr <= 1 else 0),
                Stats.INT.scaler(StatScaling.Default, mod=-1),
                Stats.WIS.scaler(StatScaling.Default, mod=-2),
                Stats.CHA.scaler(StatScaling.Default, mod=-2),
            ]
        elif variant is GoblinBruteVariant:
            hp_multiplier = 1.0
            damage_multiplier = 1.0
            attrs = [
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.INT.scaler(StatScaling.Default, mod=-1),
                Stats.WIS.scaler(StatScaling.Default, mod=-2),
                Stats.CHA.scaler(StatScaling.Default, mod=-2),
            ]
        elif variant is GoblinShamanVariant:
            hp_multiplier = 0.8
            damage_multiplier = 1.1
            attrs = [
                Stats.STR.scaler(StatScaling.Default),
                Stats.DEX.scaler(StatScaling.Medium, mod=2),
                Stats.INT.scaler(StatScaling.Primary),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Default),
            ]
        elif variant is GoblinBossVariant:
            hp_multiplier = 1.0
            damage_multiplier = 1.0
            attrs = [
                Stats.STR.scaler(StatScaling.Default),
                Stats.DEX.scaler(StatScaling.Primary),
                Stats.INT.scaler(StatScaling.Default),
                Stats.WIS.scaler(StatScaling.Default),
                Stats.CHA.scaler(StatScaling.Default),
            ]
        else:
            raise ValueError(f"Unknown goblin variant: {variant}")

        stats = base_stats(
            name=variant.name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=damage_multiplier * settings.damage_multiplier,
        )

        stats = stats.copy(
            name=name,
            size=Size.Small,
            languages=["Common", "Goblin"],
            creature_class="Goblin",
            creature_subtype="Goblinoid",
        ).with_types(
            primary_type=CreatureType.Humanoid, additional_types=CreatureType.Fey
        )

        # SENSES
        stats = stats.copy(senses=stats.senses.copy(darkvision=60))

        # ARMOR CLASS
        if variant is GoblinBossVariant or variant is GoblinBruteVariant:
            if stats.cr >= 3:
                stats = stats.add_ac_template(Breastplate)
            else:
                stats = stats.add_ac_template(ChainShirt)
        elif variant is GoblinWarriorVariant or variant is GoblinLickspittleVariant:
            stats = stats.add_ac_template(StuddedLeatherArmor)

        # ATTACKS
        if variant is GoblinWarriorVariant or variant is GoblinLickspittleVariant:
            attack = weapon.Daggers.with_display_name("Stick'Em").copy(die_count=1)
            secondary_attack = weapon.Shortbow.with_display_name("Shoot'Em")
        elif variant is GoblinBruteVariant:
            attack = weapon.Maul.with_display_name("Smash'Em")
            secondary_attack = None
        elif variant is GoblinBossVariant:
            attack = weapon.Maul.with_display_name("Smash'Em")
            secondary_attack = weapon.Shortbow.with_display_name("Shoot'Em")
        elif variant is GoblinShamanVariant:
            attack = spell.Gaze.with_display_name("Hex'Em")
            secondary_attack = None
        else:
            raise ValueError(f"Unknown goblin variant: {variant}")

        if secondary_attack is not None:
            secondary_attack = secondary_attack.copy(damage_scalar=0.9)

        # SPELLS
        if variant is GoblinShamanVariant:
            stats = stats.grant_spellcasting(
                caster_type=CasterType.Primal, spellcasting_stat=Stats.INT
            )

        # ROLES
        if variant is GoblinLickspittleVariant or variant is GoblinWarriorVariant:
            primary_role = MonsterRole.Skirmisher
            secondary_roles = {MonsterRole.Artillery, MonsterRole.Ambusher}
        elif variant is GoblinBruteVariant:
            primary_role = MonsterRole.Soldier
            secondary_roles = {MonsterRole.Skirmisher, MonsterRole.Bruiser}
        elif variant is GoblinBossVariant:
            primary_role = MonsterRole.Leader
            secondary_roles = {MonsterRole.Soldier}
        elif variant is GoblinShamanVariant:
            primary_role = MonsterRole.Controller
            secondary_roles = MonsterRole.Artillery

        stats = stats.with_roles(
            primary_role=primary_role, additional_roles=secondary_roles
        )

        # SKILLS
        stats = stats.grant_proficiency_or_expertise(Skills.Stealth)

        # SAVES
        if cr >= 3:
            stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


GoblinTemplate: MonsterTemplate = _GoblinTemplate(
    name="Goblin",
    tag_line="Wild tricksters and troublemakers",
    description="Goblins are small, black-hearted humanoids that lair in despoiled dungeons and other dismal settings. Individually weak, they gather in large numbers to torment other creatures.",
    treasure=["Any"],
    environments=[
        (Development.ruin, Affinity.native),  # native to forgotten ruins and despoiled dungeons
        (Biome.underground, Affinity.native),  # live in winding cave complexes and warrens
        (Terrain.hill, Affinity.common), # often found in hilly or rocky areas
        (region.Feywood, Affinity.common),  # ancestral connection to faerie realms
        (Development.wilderness, Affinity.common),  # common in wild areas away from civilization
        (ExtraplanarInfluence.faerie, Affinity.common),  # fey origins give them affinity for fey-touched areas
        (Development.frontier, Affinity.common),  # often raid frontier settlements
        (region.CountryShire, Affinity.uncommon),  # occasionally threaten rural areas
        (Development.settlement, Affinity.rare),  # rarely venture into established settlements
    ],
    variants=[
        GoblinLickspittleVariant,
        GoblinWarriorVariant,
        GoblinBruteVariant,
        GoblinShamanVariant,
        GoblinBossVariant,
    ],
    species=[],
    is_sentient_species=True,
)
