from ..ac_templates import ArcaneArmor
from ..attack_template import spell
from ..creature_types import CreatureType
from ..powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.creature.mage import (
    AdeptMage,
    ApprenticeMage,
    Archmage,
    Mage,
    ProtectiveMagic,
)
from ..powers.creature_type import undead
from ..powers.roles import artillery, controller
from ..powers.spellcaster import (
    abjurer,
    conjurer,
    divination,
    elementalist,
    enchanter,
    illusionist,
    metamagic,
    necromancer,
    transmuter,
)
from ..powers.themed import (
    anti_magic,
    anti_ranged,
    chaotic,
    charm,
    deathly,
    diseased,
    domineering,
    poison,
    storm,
    teleportation,
    temporal,
    tough,
    tricky,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from ..statblocks import BaseStatblock
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

ApprenticeVariant = CreatureVariant(
    name="Apprentice",
    description="Apprentices are young mages who are still learning the ways of magic. They are eager to prove themselves and are often sent on quests or missions to gain experience and knowledge.",
    suggested_crs=[
        SuggestedCr(
            name="Mage Neophyte",
            cr=1 / 4,
            other_creatures={"Apprentice Wizard": "motm"},
        ),
        SuggestedCr(
            name="Mage Apprentice", cr=2, other_creatures={"Mage Apprentice": "mm25"}
        ),
    ],
)

AbjurerVariant = CreatureVariant(
    name="Abjurer",
    description="Abjurers are mages who specialize in protective spells. They are skilled at creating magical barriers, wards, and other defenses to protect themselves and their allies from harm.",
    suggested_crs=[
        SuggestedCr(name="Abjurer Mage Adept", cr=4),
        SuggestedCr(name="Abjurer Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Abjurer Master Mage", cr=9),
        SuggestedCr(name="Abjurer Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Abjurer Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

ConjurerVariant = CreatureVariant(
    name="Conjurer",
    description="Conjurers are mages who specialize in summoning creatures and objects from other planes of existence. They can create temporary allies to fight alongside them, or they could use their powers to create magical traps or barriers.",
    suggested_crs=[
        SuggestedCr(name="Conjurer Mage Adept", cr=4),
        SuggestedCr(name="Conjurer Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Conjurer Master Mage", cr=9),
        SuggestedCr(name="Conjurer Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Conjurer Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

DivinerVariant = CreatureVariant(
    name="Diviner",
    description="Diviners are mages who specialize in seeing the future and uncovering hidden truths. They can use their powers to predict the actions of their enemies, or they could use their insights to uncover secrets and solve mysteries.",
    suggested_crs=[
        SuggestedCr(name="Diviner Mage Adept", cr=4),
        SuggestedCr(name="Diviner Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Diviner Master Mage", cr=9),
        SuggestedCr(name="Diviner Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Diviner Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

ElementalistVariant = CreatureVariant(
    name="Elementalist",
    description="Elementalists are mages who specialize in controlling the elements. They can harness the power of earth, air, fire, and water to create powerful spells and magical effects.",
    suggested_crs=[
        SuggestedCr(name="Pyromancer", cr=6),
        SuggestedCr(name="Cryomancer", cr=6),
        SuggestedCr(name="Electromancer", cr=6),
        SuggestedCr(name="Toximancer", cr=6),
    ],
)

EnchanterVariant = CreatureVariant(
    name="Enchanter",
    description="Enchanters are mages who specialize in manipulating the minds of others. They can charm, beguile, or dominate other creatures, or they could use their powers to create magical items or artifacts.",
    suggested_crs=[
        SuggestedCr(name="Enchanter Mage Adept", cr=4),
        SuggestedCr(name="Enchanter Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Enchanter Master Mage", cr=9),
        SuggestedCr(name="Enchanter Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Enchanter Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

IllusionistVariant = CreatureVariant(
    name="Illusionist",
    description="Illusionists are mages who specialize in creating illusions and phantasms. They can create lifelike images, sounds, and other sensory effects to deceive or distract their enemies, or they could use their powers to create magical traps or barriers.",
    suggested_crs=[
        SuggestedCr(name="Illusionist Mage Adept", cr=4),
        SuggestedCr(name="Illusionist Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Illusionist Master Mage", cr=9),
        SuggestedCr(name="Illusionist Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Illusionist Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

NecromancerVariant = CreatureVariant(
    name="Necromancer",
    description="Necromancers are mages who specialize in death magic. They can raise the dead to serve as their minions, drain the life force from their enemies, or create powerful curses and hexes to bring ruin to their foes.",
    suggested_crs=[
        SuggestedCr(name="Necromancer Mage Adept", cr=4),
        SuggestedCr(name="Necromancer Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Necromancer Master Mage", cr=9),
        SuggestedCr(name="Necromancer Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Necromancer Archmagus Paramount", cr=16, is_legendary=True),
    ],
)

TransmuterVariant = CreatureVariant(
    name="Transmuter",
    description="Transmuters are mages who specialize in changing the properties of objects and creatures. They can turn lead into gold, transform their enemies into harmless creatures, or create powerful elixirs and potions to enhance their own abilities.",
    suggested_crs=[
        SuggestedCr(name="Transmuter Mage Adept", cr=4),
        SuggestedCr(name="Transmuter Mage", cr=6, srd_creatures=["Mage"]),
        SuggestedCr(name="Transmuter Master Mage", cr=9),
        SuggestedCr(name="Transmuter Archmage", cr=12, srd_creatures=["Archmage"]),
        SuggestedCr(name="Transmuter Archmagus Paramount", cr=16, is_legendary=True),
    ],
)


def power_matches_cr(p: Power, cr: float) -> bool:
    score_args: dict = p.score_args  # type: ignore
    min_cr = score_args.get("require_cr", 0)
    max_cr = score_args.get("require_max_cr", 100)
    return min_cr <= cr <= max_cr


class _MageWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, name: str, cr: float, variant: CreatureVariant
    ):
        self.stats = stats
        self.variant = variant

        force = []
        esoteric = []

        if variant is ApprenticeVariant:
            force.append(ApprenticeMage)
        elif variant is AbjurerVariant:
            force.append(
                next(p for p in abjurer.AbjurationWizards() if power_matches_cr(p, cr))
            )
            esoteric.append(anti_magic.SpellStealer)
        elif variant is ConjurerVariant:
            force.append(
                next(
                    p for p in conjurer.ConjurationWizards() if power_matches_cr(p, cr)
                )
            )
            esoteric += [
                anti_magic.RedirectTeleport,
                teleportation.Scatter,
                teleportation.BendSpace,
            ]
        elif variant is DivinerVariant:
            force.append(
                next(
                    p for p in divination.DivinationWizards() if power_matches_cr(p, cr)
                )
            )
            esoteric += temporal.TemporalPowers
        elif variant is EnchanterVariant:
            force.append(
                next(p for p in enchanter.EnchanterWizards() if power_matches_cr(p, cr))
            )
            esoteric += domineering.DomineeringPowers
            esoteric += charm.CharmPowers
            esoteric.remove(charm.WardingCharm)
        elif variant is IllusionistVariant:
            force.append(
                next(
                    p
                    for p in illusionist.IllusionistWizards()
                    if power_matches_cr(p, cr)
                )
            )
            esoteric += tricky.TrickyPowers
        elif variant is NecromancerVariant:
            force.append(
                next(
                    p
                    for p in necromancer.NecromancerWizards()
                    if power_matches_cr(p, cr)
                )
            )
            esoteric += deathly.DeathlyPowers
            esoteric += undead.UndeadPowers
            esoteric.remove(undead.UndeadFortitude)
            esoteric.remove(deathly.ShadowWalk)
        elif variant is TransmuterVariant:
            force.append(
                next(
                    p
                    for p in transmuter.TransmutationWizards()
                    if power_matches_cr(p, cr)
                )
            )
            esoteric += [
                chaotic.ChaoticSpace,
                teleportation.BendSpace,
                teleportation.Scatter,
            ]
        elif variant is ElementalistVariant:
            if name == "Pyromancer":
                force.append(elementalist.Pyromancer)
            elif name == "Cryomancer":
                force.append(elementalist.Cryomancer)
            elif name == "Electromancer":
                force.append(elementalist.Electromancer)
                esoteric += storm.StormPowers
            elif name == "Toximancer":
                force.append(elementalist.Toximancer)
                esoteric += poison.PoisonPowers
                esoteric += diseased.DiseasedPowers

        if cr >= 12:
            force += [
                tough.MagicResistance,
                teleportation.MistyStep,
                ProtectiveMagic,
                Archmage,
            ]
        elif cr >= 6:
            force += [teleportation.MistyStep, ProtectiveMagic, Mage]
        elif cr >= 4:
            force += [ProtectiveMagic, AdeptMage]
        else:
            force += [ApprenticeMage]

        # general purpose mage powers
        general = metamagic.MetamagicPowers + [
            artillery.TwinSpell,
            anti_ranged.Overchannel,
        ]

        # the Controlling spells don't really fit with the themes of the mages
        suppress = controller.ControllingSpells + [tricky.HypnoticPatern]

        self.force = force
        self.general = general
        self.esoteric = esoteric
        self.suppress = suppress

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.force or p in self.suppress:
            return CustomPowerWeight(0, ignore_usual_requirements=False)
        elif p in self.general:
            return CustomPowerWeight(2, ignore_usual_requirements=False)
        elif p in self.esoteric:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        else:
            return CustomPowerWeight(0.1, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force


def generate_mage(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    stats = base_stats(
        name=name,
        cr=cr,
        stats=[
            Stats.STR.scaler(StatScaling.Default, mod=-2),
            Stats.DEX.scaler(StatScaling.Default, mod=2),
            Stats.INT.scaler(StatScaling.Primary),
            Stats.WIS.scaler(StatScaling.Medium),
            Stats.CHA.scaler(StatScaling.Default),
        ],
        hp_multiplier=0.85 * settings.hp_multiplier,
        damage_multiplier=1.2 * settings.damage_multiplier,
    )

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    stats = stats.copy(
        creature_type=CreatureType.Humanoid,
        size=Size.Medium,
        languages=["Common"],
        creature_class="Wizard",
        caster_type=CasterType.Arcane,
        # mages have many bonus actions, reactions, and limited use abilities
        selection_target_args=dict(
            limited_uses_target=-1,
            limited_uses_max=3 if cr <= 11 else 4,
            reaction_target=-1,
            reaction_max=2 if cr <= 11 else 3,
            spellcasting_powers_target=-1,
            spellcasting_powers_max=-1,
            bonus_action_target=-1,
            bonus_action_max=2,
            recharge_target=-1,
            recharge_max=2,
        ),
    )

    # SPEED
    if cr >= 12:
        stats = stats.copy(speed=stats.speed.grant_flying())

    # ARMOR CLASS
    stats = stats.add_ac_template(ArcaneArmor)

    # ATTACKS
    if variant is ApprenticeVariant:
        attack = spell.ArcaneBurst.with_display_name("Magic Missile")
        primary_role = MonsterRole.Artillery
        additional_roles = []
    elif variant is AbjurerVariant:
        attack = spell.ArcaneBurst.with_display_name("Runic Blast")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
    elif variant is ConjurerVariant:
        attack = spell.ArcaneBurst.with_display_name("Conjured Blast")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery, MonsterRole.Support]
    elif variant is DivinerVariant:
        attack = spell.ArcaneBurst.with_display_name("Time Warp")
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
    elif variant is ElementalistVariant:
        primary_role = MonsterRole.Artillery
        additional_roles = []
        if name == "Pyromancer":
            attack = spell.Firebolt
        elif name == "Cryomancer":
            attack = spell.Frostbolt
        elif name == "Electromancer":
            attack = spell.Shock
        elif name == "Toximancer":
            attack = spell.Poisonbolt
    elif variant is EnchanterVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Gaze.with_display_name("Mind-Shattering Gaze")
    elif variant is IllusionistVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Gaze.with_display_name("Shred Reality")
    elif variant is NecromancerVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.Deathbolt.with_display_name("Necrotic Blast")
    elif variant is TransmuterVariant:
        primary_role = MonsterRole.Controller
        additional_roles = [MonsterRole.Artillery]
        attack = spell.ArcaneBurst.with_display_name("Shred Matter")
    else:
        raise ValueError(f"Unknown variant {variant}")

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)

    # ROLES
    stats = stats.with_roles(
        primary_role=primary_role, additional_roles=additional_roles
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Perception)
    if cr >= 6:
        stats = stats.grant_proficiency_or_expertise(Skills.History)
    if cr >= 12:
        stats = stats.grant_proficiency_or_expertise(Skills.Arcana, Skills.Initiative)

    # SAVES
    if cr >= 6:
        stats = stats.grant_save_proficiency(Stats.WIS, Stats.INT)

    # # POWER MODIFIER
    # # reduce number of powers generated because mages have a lot of hard-coded powers already
    # stats = stats.apply_monster_dials(
    #     MonsterDials(
    #         recommended_powers_modifier=-1 * (MEDIUM_POWER if cr >= 4 else LOW_POWER)
    #     )
    # )

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=_MageWeights(stats, name, cr, variant),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


MageTemplate: CreatureTemplate = CreatureTemplate(
    name="Mage",
    tag_line="Magical Scholars and Spellcasters",
    description="Mages are magical wonder-workers, ranging from spellcasting overlords to reclusive witches. They study mystical secrets and possess insight into monsters, legends, omens, and other lore. Mages often gather allies or hire assistants to aid them in their research or to attain magical might.",
    environments=[],
    treasure=["Arcana", "Individual"],
    variants=[
        ApprenticeVariant,
        AbjurerVariant,
        ConjurerVariant,
        DivinerVariant,
        ElementalistVariant,
        EnchanterVariant,
        IllusionistVariant,
        NecromancerVariant,
        TransmuterVariant,
    ],
    species=[],
    callback=generate_mage,
)
