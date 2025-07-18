from foe_foundry.environs import Affinity, Biome, Development, ExtraplanarInfluence
from foe_foundry.environs.region import HauntedLands, UnderlandRealm
from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import Unarmored, flat
from ...attack_template import AttackTemplate, natural, spell, weapon
from ...creature_types import CreatureType
from ...damage import Condition, DamageType
from ...movement import Movement
from ...powers import (
    PowerSelection,
)
from ...role_types import MonsterRole
from ...size import Size
from ...skills import AbilityScore, Skills, StatScaling
from .._template import (
    GenerationSettings,
    Monster,
    MonsterTemplate,
    MonsterVariant,
)
from ..base_stats import AbilityScaling, base_stats
from . import powers

ShadowVariant = MonsterVariant(
    name="Shadow",
    description="A Shadow is the cast-off remnant of a soul too vile to pass cleanly into death. While the rest of the spirit is swept down the Styx, the Shadow lingers behind like a stain - alive with jealousy, hunger, and spite. Shadows are drawn to extinguish warmth, light, and life, which they revile above all.",
    monsters=[
        Monster(name="Shadow", cr=1 / 2, srd_creatures=["Shadow"]),
    ],
)

SpecterVariant = MonsterVariant(
    name="Specter",
    description="A Specter is a soul fragment, splintered by violence or unendurable pain. Lacking the memory of a Ghost or the malignant will of a Wraith, it drifts through the world in spasms of confusion and malice.",
    monsters=[
        Monster(name="Specter", cr=1, srd_creatures=["Specter"]),
    ],
)

BansheeVariant = MonsterVariant(
    name="Banshee",
    description="A Banshee is a mournful spirit borne of overwhelming tragedy, sorrow, and betrayal. In life, the spirit loved too deeply and lost too dearly. Many Banshees are spirits of women who were betrayed by a loved one, though not exclusively. The mournful wail of a banshee is often enough to drag the souls of the weak-willed directly into death and chill the minds of even the strong-of-heart",
    monsters=[
        Monster(name="Banshee", cr=4, srd_creatures=["Banshee"]),
    ],
)

GhostVariant = MonsterVariant(
    name="Ghost",
    description="Ghosts are spirits that died with memories too painful to release. They are not held by hatred or vengeance, but by the sorrowful weight of what they recall. Lives cut too short, loved ones left behind, and truths unsaid. These souls haunt the world not because they won't move on, but because their memories won't let them.",
    monsters=[
        Monster(name="Ghost", cr=4, srd_creatures=["Ghost"]),
    ],
)

RevenantVariant = MonsterVariant(
    name="Revenant",
    description="A Revenant is a soul fueled not by sorrow, but by rage. It rises not to haunt the world, but to correct a single, searing injustice. It remembers how it died and who is to blame, and will not rest until vengeance is taken. Revenants are not mindless: they are deliberate, relentless, and terrifyingly lucid. If their quarry is powerful, Revenants are known to assemble a posse of lesser undead to support their relentless quest.",
    monsters=[
        Monster(name="Revenant", cr=5, srd_creatures=["Revenant"]),
    ],
)

WraithVariant = MonsterVariant(
    name="Wraith",
    description="When a soul steeped in malice dies, it may resist the pull of the Styx. Caught in the cold eddies of that underworld current, its will festers. Twisting and swelling, it draws in the remnants of other damned spirits. Layer by layer, a powerful Wraith forms: a cursed vortex of souls too vile to cross over.",
    monsters=[
        Monster(name="Wraith", cr=5, srd_creatures=["Wraith"]),
        Monster(name="Wraith Shadelord", cr=8, is_legendary=True),
    ],
)


def _banshee_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.NoScaling, -9),
        AbilityScore.DEX: StatScaling.Medium,
        AbilityScore.CON: StatScaling.Default,
        AbilityScore.INT: (StatScaling.Medium, -1),
        AbilityScore.WIS: StatScaling.Default,
        AbilityScore.CHA: StatScaling.Primary,
    }


def _wraith_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.Default, -6),
        AbilityScore.DEX: (StatScaling.Medium, 3),
        AbilityScore.CON: (StatScaling.Constitution, 2),
        AbilityScore.INT: StatScaling.Default,
        AbilityScore.WIS: (StatScaling.Medium, 1),
        AbilityScore.CHA: StatScaling.Primary,
    }


def _specter_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.NoScaling, -9),
        AbilityScore.DEX: (StatScaling.Medium, 3),
        AbilityScore.CON: StatScaling.Default,
        AbilityScore.INT: StatScaling.Default,
        AbilityScore.WIS: StatScaling.Default,
        AbilityScore.CHA: StatScaling.Primary,
    }


def _ghost_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.Default, -5),
        AbilityScore.DEX: StatScaling.Medium,
        AbilityScore.CON: (StatScaling.Constitution, -2),
        AbilityScore.INT: StatScaling.Default,
        AbilityScore.WIS: StatScaling.Medium,
        AbilityScore.CHA: StatScaling.Primary,
    }


def _revenant_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.Medium, 5),
        AbilityScore.DEX: (StatScaling.Medium, 1),
        AbilityScore.CON: (StatScaling.Constitution, 4),
        AbilityScore.INT: (StatScaling.Default, 0.5),
        AbilityScore.WIS: (StatScaling.Medium, 3),
        AbilityScore.CHA: StatScaling.Primary,
    }


def _shadow_stats() -> dict[AbilityScore, AbilityScaling]:
    return {
        AbilityScore.STR: (StatScaling.NoScaling, -4),
        AbilityScore.DEX: (StatScaling.Medium, 4),
        AbilityScore.CON: StatScaling.Constitution,
        AbilityScore.INT: (StatScaling.Default, -4),
        AbilityScore.WIS: StatScaling.Default,
        AbilityScore.CHA: StatScaling.Primary,
    }


class _SpiritTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "shadow":
            return PowerSelection(powers.LoadoutShadow)
        elif settings.monster_key == "specter":
            return PowerSelection(powers.LoadoutSpecter)
        elif settings.monster_key == "banshee":
            return PowerSelection(powers.LoadoutBanshee)
        elif settings.monster_key == "revenant":
            return PowerSelection(powers.LoadoutRevenant)
        elif settings.monster_key == "ghost":
            return PowerSelection(powers.LoadoutGhost)
        elif settings.monster_key in {"wraith", "wraith-shadelord"}:
            return PowerSelection(powers.LoadoutWraith)
        else:
            raise ValueError(f"Unknown monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        name = settings.creature_name
        cr = settings.cr
        variant = settings.variant
        is_legendary = settings.is_legendary

        # STATS
        if variant is ShadowVariant:
            hp_multiplier = 1.25
            damage_multiplier = 1.0
            creature_class = "Shadow"
            attrs = _shadow_stats()
        elif variant is SpecterVariant:
            hp_multiplier = 0.63
            damage_multiplier = 1.0
            creature_class = "Specter"
            attrs = _specter_stats()
        elif variant is BansheeVariant:
            hp_multiplier = 1.0
            damage_multiplier = 1.0
            creature_class = "Banshee"
            attrs = _banshee_stats()
        elif variant is RevenantVariant:
            hp_multiplier = 1.25
            damage_multiplier = 1.0
            creature_class = "Revenant"
            attrs = _revenant_stats()
        elif variant is GhostVariant:
            hp_multiplier = 0.6
            damage_multiplier = 1.1
            creature_class = "Ghost"
            attrs = _ghost_stats()
        elif variant is WraithVariant:
            hp_multiplier = 0.7
            damage_multiplier = 1.0
            creature_class = "Wraith"
            attrs = _wraith_stats()
        else:
            raise ValueError(f"Unknown variant: {variant}")

        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=attrs,
            hp_multiplier=hp_multiplier * settings.hp_multiplier,
            damage_multiplier=damage_multiplier * settings.damage_multiplier,
        )

        stats = stats.copy(
            creature_type=CreatureType.Undead,
            size=Size.Medium,
            languages=["Telepathy 60 ft."],
            creature_class=creature_class,
            creature_subtype="Spirit",
            senses=stats.senses.copy(darkvision=60),
        )

        # LEGENDARY
        if is_legendary:
            stats = stats.as_legendary()

        # SPEED
        if variant is not RevenantVariant and variant is not ShadowVariant:
            if variant is SpecterVariant:
                fly = 50
            elif variant is WraithVariant:
                fly = 60
            elif variant is GhostVariant:
                fly = 40
            elif variant is BansheeVariant:
                fly = 40
            stats = stats.copy(speed=Movement(walk=5, fly=fly, hover=True))

        # ARMOR CLASS
        if variant is RevenantVariant or variant is WraithVariant:
            stats = stats.add_ac_template(flat(ac=13))
        else:
            stats = stats.add_ac_template(Unarmored)

        # ATTACKS
        if variant is ShadowVariant:
            attack = natural.Slam.with_display_name("Shadow's Touch").copy(
                damage_type=DamageType.Necrotic, secondary_damage_type=DamageType.Cold
            )
            primary_role = MonsterRole.Ambusher
            secondary_roles = set()
        elif variant is SpecterVariant:
            attack = natural.Slam.with_display_name("Spectral Touch").copy(
                damage_type=DamageType.Necrotic, secondary_damage_type=DamageType.Cold
            )
            primary_role = MonsterRole.Bruiser
            secondary_roles = set()
        elif variant is BansheeVariant:
            attack = spell.Gaze.with_display_name("Horrifying Lament").copy(
                damage_type=DamageType.Psychic,
                secondary_damage_type=DamageType.Necrotic,
            )
            primary_role = MonsterRole.Controller
            secondary_roles = {MonsterRole.Artillery}
        elif variant is RevenantVariant:
            attack = weapon.Greatsword.with_display_name("Vengeful Strike").copy(
                damage_type=DamageType.Slashing, secondary_damage_type=DamageType.Cold
            )
            primary_role = MonsterRole.Soldier
            secondary_roles = {MonsterRole.Leader}
        elif variant is GhostVariant:
            attack = natural.Slam.with_display_name("Ghostly Touch").copy(
                damage_type=DamageType.Necrotic, secondary_damage_type=DamageType.Cold
            )
            primary_role = MonsterRole.Controller
            secondary_roles = set()
        elif variant is WraithVariant:
            attack = natural.Slam.with_display_name("Splinter Soul").copy(
                damage_type=DamageType.Necrotic, secondary_damage_type=DamageType.Cold
            )
            primary_role = MonsterRole.Controller
            secondary_roles = {MonsterRole.Leader}
        else:
            raise ValueError(f"Unknown variant: {variant.name}")

        stats = stats.with_reduced_attacks(reduce_by=1)  # spirits use fewer attacks
        stats = stats.copy(
            primary_damage_type=attack.damage_type,
            secondary_damage_type=attack.secondary_damage_type,
        )

        # ROLES
        stats = stats.with_roles(
            primary_role=primary_role,
            additional_roles=secondary_roles,
        )

        # SKILLS
        if variant is ShadowVariant:
            stats = stats.grant_proficiency_or_expertise(Skills.Stealth)

        # SAVES
        if cr >= 4:
            stats = stats.grant_save_proficiency(AbilityScore.CON)

        # IMMUNITIES
        if variant is ShadowVariant:
            vulnerabilities = {DamageType.Radiant}
        else:
            vulnerabilities = set()

        if cr >= 1 and variant is not RevenantVariant:
            resistances = {
                DamageType.Bludgeoning,
                DamageType.Piercing,
                DamageType.Slashing,
            }
        else:
            resistances = set()

        stats = stats.grant_resistance_or_immunity(
            immunities={DamageType.Necrotic, DamageType.Poison, DamageType.Cold},
            resistances=resistances
            | {
                DamageType.Acid,
                DamageType.Fire,
                DamageType.Lightning,
                DamageType.Thunder,
            },
            conditions={
                Condition.Poisoned,
                Condition.Exhaustion,
                Condition.Frightened,
                Condition.Grappled,
                Condition.Paralyzed,
                Condition.Petrified,
                Condition.Prone,
                Condition.Restrained,
                Condition.Unconscious,
            },
            vulnerabilities=vulnerabilities,
        )

        return stats, [attack]


SpiritTemplate: MonsterTemplate = _SpiritTemplate(
    name="Spirit",
    tag_line="Echoes of Rage and Regret",
    description="Spirits are the echoes and imprints of the deceased that refuse to pass due to unbearable grief, unfinished purpose, or wrathful vengeance. A Spirit forms when a soul is anchored to the Mortal Realm by dreadful purpose, rather than being carried peacefully upon the Styx to the Great Beyond. Existing neither truly in death nor in life, the spirit is a hollow echo of its former self",
    treasure=[],
    variants=[
        ShadowVariant,
        SpecterVariant,
        BansheeVariant,
        RevenantVariant,
        GhostVariant,
        WraithVariant,
    ],
    species=[],
    environments=[
        # Spirits are most commonly found in places touched by death and haunting
        (HauntedLands, Affinity.native),  # Cursed lands with undead presence
        (UnderlandRealm, Affinity.native),  # Ancient underground tombs and crypts
        # Extraplanar influences where death and negative energy seep through
        (ExtraplanarInfluence.deathly, Affinity.native),  # Places touched by death
        (ExtraplanarInfluence.astral, Affinity.common),  # Ethereal and spirit realms
        # Development types - ruins and abandoned places where spirits linger
        (Development.ruin, Affinity.native),  # Ancient ruins and abandoned structures
        (
            Development.settlement,
            Affinity.common,
        ),  # Villages and towns with tragic histories
        (Development.countryside, Affinity.common),  # Rural areas with old graveyards
        (
            Development.wilderness,
            Affinity.uncommon,
        ),  # Remote areas with ancient battlefields
        # Underground environments where spirits may be bound to crypts
        (Biome.underground, Affinity.common),  # Dungeons, crypts, and catacombs
    ],
)
