from ...ac_templates import NaturalArmor
from ...attack_template import natural
from ...creature_types import CreatureType
from ...movement import Movement
from ...powers import (
    NewPowerSelection,
    flags,
    select_powers,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import Skills, Stats, StatScaling
from .._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from ..base_stats import base_stats
from . import powers

ChimeraVariant = MonsterVariant(
    name="Chimera",
    description="Legends say that chimera are heralds of imminent divine wrath or impending disaster. The greed, pride, and anger of mortal kind manifests into a monstrous three-headed beast, part lion, ram, and dragon. The lion head craves conquest, the goat hungers for spite, and the dragon seethes with wrath. Scholars debate whether chimeras are creations of wrathful gods, foul demons, or capricious fae. Regardless, the presence of a chimera is a certain sign of disaster.",
    monsters=[
        Monster(name="Chimera", cr=6, srd_creatures=["Chimera"]),
        Monster(name="Chimera Sovereign", cr=10),
    ],
)


def choose_powers(settings: GenerationSettings) -> NewPowerSelection:
    if settings.monster_key == "chimera":
        return NewPowerSelection(powers.LoadoutChimera, settings.rng)
    elif settings.monster_key == "chimera-sovereign":
        return NewPowerSelection(powers.LoadoutChimeraSovereign, settings.rng)
    else:
        raise ValueError(f"Unknown monster key: {settings.monster_key}")


def generate_chimera(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    rng = settings.rng

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Primary),
            Stats.DEX.scaler(StatScaling.Default),
            Stats.CON.scaler(StatScaling.Constitution, mod=4),
            Stats.INT.scaler(StatScaling.Default, mod=-8),
            Stats.WIS.scaler(StatScaling.Medium, mod=2),
            Stats.CHA.scaler(StatScaling.Default, mod=-1.5),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Monstrosity,
        size=Size.Large,
        creature_class="Chimera",
        languages=["Draconic"],
        senses=stats.senses.copy(darkvision=60),
    )

    # ARMOR CLASS
    stats = stats.add_ac_template(NaturalArmor, ac_modifier=-1)

    # ATTACKS
    attack = natural.Bite.with_display_name("Three-Headed Bites")
    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    stats = stats.with_set_attacks(3)  # 3 heads = 3 attacks

    # ROLES
    stats = stats.with_roles(
        primary_role=MonsterRole.Bruiser,
    )

    # MOVEMENT
    stats = stats.with_flags(flags.NO_TELEPORT).copy(speed=Movement(walk=30, fly=60))

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(
        Skills.Perception
    ).grant_proficiency_or_expertise(Skills.Perception)  # expertise

    # SAVES
    if stats.cr >= 8:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.CON)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=choose_powers(settings),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


ChimeraTemplate: MonsterTemplate = MonsterTemplate(
    name="Chimera",
    tag_line="Monstrous Messenger of Imminent Disaster",
    description="Legends say that chimera are heralds of imminent divine wrath or impending disaster. The greed, pride, and anger of mortal kind manifests into a monstrous three-headed beast, part lion, ram, and dragon. The lion head craves conquest, the goat hungers for spite, and the dragon seethes with wrath. Scholars debate whether chimeras are creations of wrathful gods, foul demons, or capricious fae. Regardless, the presence of a chimera is a certain sign of disaster.",
    environments=["Grassland", "Hill", "Mountain"],
    treasure=[],
    variants=[ChimeraVariant],
    species=[],
    callback=generate_chimera,
)
