from ..ac_templates import PlateArmor, StuddedLeatherArmor, UnholyArmor
from ..attack_template import natural, spell, weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    LOW_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature_type.aberration import AberrationPowers
from ..powers.creature_type.fiend import FiendishPowers
from ..powers.creature_type.undead import UndeadPowers
from ..powers.roles.defender import Protection
from ..powers.spellcaster.cult import CultCasters
from ..powers.spellcaster.fiendish import FiendishCasters
from ..powers.spellcaster.necromancer import NecromancerWizards
from ..powers.spellcaster.psionic import PsionicCasters
from ..powers.themed.cruel import CruelPowers
from ..powers.themed.cursed import (
    BestowCurse,
    CursedPowers,
    RayOfEnfeeblement,
    RejectDivinity,
    UnholyAura,
)
from ..powers.themed.deathly import DeathlyPowers
from ..powers.themed.domineering import DomineeringPowers
from ..powers.themed.fast import Evasion
from ..powers.themed.gadget import GadgetPowers
from ..powers.themed.psychic import PsychicPowers
from ..powers.themed.trap import TrapPowers
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import MonsterDials
from ._data import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
    StatsBeingGenerated,
)
from .base_stats import BaseStatblock, base_stats

CultistVariant = MonsterVariant(
    name="Cultist",
    description="Cultists devote themselves to their faith's leaders and otherworldly masters. While this zeal grants cultists no magical powers, it gives them remarkable resolve in the face of threats. Cultists perform much of a cult's mundane work, which might include evangelism, criminal acts, or serving as sacrifices.",
    monsters=[
        Monster(name="Cultist", cr=1 / 8, srd_creatures=["Cultist"]),
        Monster(name="Cultist Fanatic", cr=2, srd_creatures=["Cult Fanatic"]),
        Monster(
            name="Cultist Grand Master",
            cr=10,
            other_creatures={"Cultist Hierophant": "mm25"},
        ),
        Monster(name="Cultist Exarch", cr=14, is_legendary=True),
    ],
)

AberrantVariant = MonsterVariant(
    name="Aberrant Cultist",
    description="Aberrant cultists pursue mind-bending powers from alien forces.",
    monsters=[
        Monster(name="Aberrant Cultist Initiate", cr=4),
        Monster(
            name="Aberrant Cultist", cr=8, other_creatures={"Aberrant Cultist": "mm25"}
        ),
        Monster(name="Aberrant Cultist Grand Master", cr=14),
    ],
)

NecroVariant = MonsterVariant(
    name="Death Cultist",
    description="Death cultists revel in nihilistic forces, embracing them as paths to undeath, multiversal purity, or entropic inevitability. These cultists serve powerful undead beings, apocalyptic prophecies, or immortals with power over death",
    monsters=[
        Monster(name="Death Cultist Initiate", cr=4),
        Monster(name="Death Cultist", cr=8, other_creatures={"Death Cultist": "mm25"}),
        Monster(name="Death Cultist Grand Master", cr=14),
    ],
)

FiendVariant = MonsterVariant(
    name="Fiendish Cultist",
    description="Fiend cultists worship fiends or evil deities. They often work to bring ruin to innocents or to summon their sinister patron into the world. Fiend cultists might serve infamous powers such as archdevils and demon lords, or foul immortals",
    monsters=[
        Monster(name="Fiend Cultist Initiate", cr=4),
        Monster(name="Fiend Cultist", cr=8, other_creatures={"Fiend Cultist": "mm25"}),
        Monster(name="Fiend Cultist Grand Master", cr=14),
    ],
)


class _CustomWeights(CustomPowerSelection):
    def __init__(self, stats: BaseStatblock, variant: MonsterVariant):
        self.stats = stats
        self.variant = variant

    def force_powers(self) -> list[Power]:
        # Low-CR Cultists always have Protection
        if self.stats.cr <= 1:
            return [Protection]
        else:
            return []

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        powers = []
        highly_desirable_powers = []

        suppress_powers = GadgetPowers + TrapPowers + [Evasion]
        if p in suppress_powers:
            return CustomPowerWeight(0)  # Cultists shouldn't really be "high tech"

        if p is Protection:
            # Protection is always available to minion cultists
            return CustomPowerWeight(0)

        if self.stats.cr >= 2:
            powers += [RejectDivinity, RayOfEnfeeblement, UnholyAura, BestowCurse]
            powers += DomineeringPowers
            highly_desirable_powers += CultCasters()

        if self.variant is AberrantVariant:
            powers += AberrationPowers
            powers += PsychicPowers
            highly_desirable_powers += PsionicCasters()

        if self.variant is NecroVariant:
            powers += DeathlyPowers
            powers += UndeadPowers
            highly_desirable_powers += NecromancerWizards

        if self.variant is FiendVariant:
            powers += CruelPowers
            powers += CursedPowers
            powers += FiendishPowers
            highly_desirable_powers += FiendishCasters()

        if p in highly_desirable_powers:
            return CustomPowerWeight(2.0, ignore_usual_requirements=True)
        elif p in powers:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        else:
            # downvote powers not in the list because we have a lot of options above
            return CustomPowerWeight(0.5)


def generate_cultist(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        variant_key=settings.variant.key,
        template_key=settings.monster_template,
        monster_key=settings.monster_key,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default, mod=1),
            Stats.DEX.scaler(StatScaling.Medium, mod=1),
            Stats.INT.scaler(StatScaling.Default),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Primary),
        ],
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Cultist",
        caster_type=CasterType.Pact,
    )

    # ARMOR CLASS
    if stats.cr <= 2:
        stats = stats.add_ac_template(StuddedLeatherArmor)
    elif variant is FiendVariant:
        stats = stats.add_ac_template(PlateArmor)
    else:
        stats = stats.add_ac_template(UnholyArmor)

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # ATTACKS
    if variant is CultistVariant:
        if cr <= 1:
            attack = weapon.Daggers.with_display_name("Ritual Dagger")
            primary_damage_type = DamageType.Piercing
            secondary_attack = None
            secondary_damage_type = DamageType.Necrotic
        else:
            attack = spell.Deathbolt
            primary_damage_type = DamageType.Necrotic
            secondary_attack = weapon.Daggers.with_display_name("Ritual Dagger")
            secondary_damage_type = DamageType.Necrotic
    elif variant is AberrantVariant:
        attack = spell.Gaze.with_display_name("Mind Rot")
        primary_damage_type = DamageType.Psychic
        secondary_attack = natural.Tentacle.with_display_name("Aberrant Tentacle")
        secondary_damage_type = DamageType.Psychic
    elif variant is NecroVariant:
        attack = spell.Deathbolt.with_display_name("Deathly Ray")
        primary_damage_type = DamageType.Necrotic
        secondary_damage_type = DamageType.Necrotic
        secondary_attack = None
    elif variant is FiendVariant:
        attack = weapon.Greataxe.with_display_name("Infernal Axe")
        primary_damage_type = DamageType.Slashing
        secondary_attack = spell.Firebolt.with_display_name("Scorching Ray")
        secondary_damage_type = DamageType.Fire

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(
        primary_damage_type=primary_damage_type,
        secondary_damage_type=secondary_damage_type,
    )

    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # ROLES
    additional_roles = []
    primary_role = MonsterRole.Controller
    if cr >= 10:
        additional_roles.append(MonsterRole.Leader)
    if variant is not FiendVariant:
        additional_roles.append(MonsterRole.Artillery)
    if variant is FiendVariant:
        primary_role = MonsterRole.Bruiser
        additional_roles.append(MonsterRole.Controller)

    stats = stats.with_roles(
        primary_role=primary_role,
        additional_roles=additional_roles,
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Deception, Skills.Religion)
    if cr >= 2:
        stats = stats.grant_proficiency_or_expertise(Skills.Persuasion)
    if cr >= 8:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if cr >= 2:
        stats = stats.grant_save_proficiency(Stats.WIS)

    # POWERS
    features = []

    # ADDITIONAL POWERS

    # Cultists can use more power at higher CRs to keep them interesting
    if variant == CultistVariant and stats.cr >= 2:
        stats = stats.apply_monster_dials(
            MonsterDials(recommended_powers_modifier=LOW_POWER)
        )

    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_CustomWeights(stats, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)
    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


CultistTemplate: MonsterTemplate = MonsterTemplate(
    name="Cultist",
    tag_line="Doomsayers and Fanatics",
    description="Cultists use magic and extreme measures to spread radical beliefs. Some privately pursue esoteric secrets, while others form shadowy cabals seeking to bring about terrifying ends. Cultists often follow obscure mystical traditions or obsess over interpretations of ancient prophecies. They might worship supernatural patrons—deities, otherworldly creatures, manipulative alien minds, or stranger forces",
    environments=["Urban"],
    treasure=["Armaments", "Individual"],
    variants=[CultistVariant, AberrantVariant, NecroVariant, FiendVariant],
    species=[],
    callback=generate_cultist,
)
