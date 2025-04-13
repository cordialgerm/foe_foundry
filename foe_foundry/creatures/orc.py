import numpy as np

from ..ac_templates import ArcaneArmor, HideArmor, PlateArmor, StuddedLeatherArmor
from ..attack_template import spell, weapon
from ..creature_types import CreatureType
from ..damage import DamageType
from ..powers import (
    LOW_POWER,
    MEDIUM_POWER,
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    select_powers,
)
from ..powers.roles import defender, leader, soldier
from ..powers.species import orc
from ..powers.spellcaster import shaman
from ..powers.themed import (
    anti_ranged,
    bestial,
    cowardly,
    cruel,
    fast,
    fearsome,
    gadget,
    honorable,
    reckless,
    shamanic,
    sneaky,
    technique,
    thuggish,
    totemic,
    tough,
)
from ..role_types import MonsterRole
from ..size import Size
from ..skills import Skills, Stats, StatScaling
from ..spells import CasterType
from .base_stats import base_stats
from .template import (
    CreatureTemplate,
    CreatureVariant,
    GenerationSettings,
    StatsBeingGenerated,
    SuggestedCr,
)

OrcSoldierVariant = CreatureVariant(
    name="Orc Soldier",
    description="Orc Soldiers are the backbone of any orc warband. They are strong and tough, and they fight with a ferocity that is unmatched.",
    suggested_crs=[SuggestedCr(name="Orc Soldier", cr=1 / 2, srd_creatures=["Orc"])],
)

OrcReaverVariant = CreatureVariant(
    name="Orc Reaver",
    description="Orc Reavers are the most aggressive and bloodthirsty warriors in the warband. They charge into battle with reckless abandon, seeking to kill and maim as many foes as possible.",
    suggested_crs=[SuggestedCr(name="Orc Reaver", cr=1)],
)

OrcHardenedOneVariant = CreatureVariant(
    name="Orc Hardened One",
    description="Orc Hardened Ones are the elite warriors of the orc warband. They are tough and resilient, and they fight with a brutal efficiency. They are often the elite bodyguard of the warchief.",
    suggested_crs=[
        SuggestedCr(name="Orc Hardened One", cr=2, other_creatures={"Orog": "mm14"}),
    ],
)

OrcBloodriteShamanVariant = CreatureVariant(
    name="Orc Bloodrite Shaman",
    description="Orc Bloodrite Shamans are the spiritual leaders of the orc warband. They are powerful spellcasters who can call upon the spirits of their ancestors to aid them in battle. They often create powerful totems to protect their allies and curse their enemies.",
    suggested_crs=[
        SuggestedCr(
            name="Orc Bloodrite Shaman",
            cr=2,
            other_creatures={
                "Orc Claw of Luthic": "vgtm",
                "Orc Hand of Yurtrus": "vgtm",
                "Orc Eye of Gruumsh": "vgtm",
            },
        ),
        SuggestedCr(name="Orc Bloodrite Elder Shaman", cr=5),
    ],
)

OrcBloodletterVariant = CreatureVariant(
    name="Orc Bloodletter",
    description="Orc Bloodletters are the most feared and deadly warriors in the orc warband. They are skilled in the art of assassination and can strike from the shadows with deadly precision.",
    suggested_crs=[
        SuggestedCr(
            name="Orc Bloodletter",
            cr=4,
            other_creatures={"Orc Blade of Ilneval": "vgtm"},
        )
    ],
)

OrcWarchiefVariant = CreatureVariant(
    name="Orc Warchief",
    description="Orc Warchiefs are the leaders of the orc warband. They are powerful warriors and skilled tacticians who can rally their allies to victory. They are often accompanied by a retinue of elite warriors. The most powerful warchiefs die their tusks red in the blood of their foes.",
    suggested_crs=[
        SuggestedCr(
            name="Orc Warchief", cr=4, other_creatures={"Orc War Chief": "mm14"}
        ),
        SuggestedCr(name="Orc Warchief of the Bloody Fang", cr=7, is_legendary=True),
    ],
)


class _OrcPowers(CustomPowerSelection):
    def __init__(
        self,
        force: list[Power],
        always: list[Power],
        conditional: list[Power],
        suppress: list[Power],
        delta: float = 0.0,
    ):
        self.force = force
        self.suppress = (
            gadget.GadgetPowers
            + cowardly.CowardlyPowers
            + thuggish.ThuggishPowers
            + [technique.BaitAndSwitch, technique.PommelStrike, technique.ArmorMaster]
            + suppress
        )
        self.always = always
        self.orc = orc.OrcPowers
        self.conditional = conditional
        self.delta = delta

    def custom_weight(self, power: Power) -> CustomPowerWeight:
        if power in self.suppress:
            return CustomPowerWeight(weight=-1)
        elif power in self.orc:
            return CustomPowerWeight(weight=2.0, ignore_usual_requirements=False)
        elif power in self.always:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=True)
        elif power in self.conditional:
            return CustomPowerWeight(weight=1.5, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(weight=0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force

    def power_delta(self) -> float:
        return self.delta - 0.1 * sum(p.power_level for p in self.force)


def orc_powers(
    variant: CreatureVariant, rng: np.random.Generator, cr: float
) -> CustomPowerSelection:
    if variant is OrcSoldierVariant:
        return _OrcPowers(
            force=[],
            always=[],
            conditional=technique.TechniquePowers
            + reckless.RecklessPowers
            + soldier.SoldierPowers,
            suppress=[],
            delta=LOW_POWER,
        )
    elif variant is OrcReaverVariant:
        return _OrcPowers(
            force=[orc.Bloodfury],
            always=[
                anti_ranged.DeflectMissile,
                bestial.RetributiveStrike,
                cruel.BrutalCritical,
                cruel.BloodiedFrenzy,
                fearsome.FearsomeRoar,
            ]
            + reckless.RecklessPowers,
            conditional=[
                technique.BleedingAttack,
                technique.CleavingAttack,
                technique.DisarmingAttack,
                technique.OverpoweringStrike,
                technique.PushingAttack,
                technique.ProneAttack,
                technique.WhirlwindOfSteel,
            ],
            suppress=[orc.BloodrageBarrage],
            delta=LOW_POWER,
        )
    elif variant is OrcHardenedOneVariant:
        honorable_index = rng.choice(len(honorable.HonorablePowers))
        honorable_power = honorable.HonorablePowers[honorable_index]

        return _OrcPowers(
            force=[defender.Protection, honorable_power],
            always=[
                defender.Taunt,
                defender.ZoneOfControl,
                technique.BaitAndSwitch,
                technique.ArmorMaster,
                technique.BleedingAttack,
                technique.CleavingAttack,
                technique.DazingAttacks,
                technique.DisarmingAttack,
                technique.GrazingAttack,
                technique.OverpoweringStrike,
                technique.Interception,
                technique.ParryAndRiposte,
                technique.WhirlwindOfSteel,
                tough.JustAScratch,
            ],
            conditional=honorable.HonorablePowers + soldier.SoldierPowers,
            suppress=[],
        )
    elif variant is OrcBloodletterVariant:
        return _OrcPowers(
            force=[sneaky.Vanish],
            always=[
                cruel.BrutalCritical,
                anti_ranged.HardToPinDown,
                fast.Evasion,
                fast.NimbleReaction,
                fearsome.DreadGaze,
                technique.PoisonedAttack,
            ],
            conditional=sneaky.SneakyPowers,
            suppress=[sneaky.FalseAppearance],
        )
    elif variant is OrcBloodriteShamanVariant:
        totemic_power_index = rng.choice(len(totemic.TotemicPowers))
        totemic_power = totemic.TotemicPowers[totemic_power_index]
        force = [
            shaman.ShamanAdeptPower if cr <= 2 else shaman.ShamanPower,
            totemic_power,
        ]

        return _OrcPowers(
            force=force,
            always=shamanic.ShamanicPowers,
            conditional=[],
            suppress=[orc.BloodrageEndurance],
            delta=LOW_POWER if cr <= 2 else MEDIUM_POWER,
        )
    elif variant is OrcWarchiefVariant:
        warcries = [orc.WarCryOfTheBloodiedFang, orc.WarCryOfTheChillheart]
        orders = [leader.CommandTheAttack, leader.StayInFormation]
        warcry_index = rng.choice(len(warcries))
        order_index = rng.choice(len(orders))
        force = [warcries[warcry_index], orders[order_index]]

        if cr >= 7:
            force.append(orc.Bloodfury)

        return _OrcPowers(
            force=force,
            always=[
                leader.CommandTheAttack,
                leader.CommandTheTroops,
                leader.StayInFormation,
                leader.FanaticFollowers,
                leader.RallyTheTroops,
                leader.Intimidate,
                defender.Taunt,
                technique.BaitAndSwitch,
                technique.ArmorMaster,
                technique.BleedingAttack,
                technique.CleavingAttack,
                technique.DazingAttacks,
                technique.DisarmingAttack,
                technique.GrazingAttack,
                technique.OverpoweringStrike,
                technique.ParryAndRiposte,
                technique.WhirlwindOfSteel,
            ],
            conditional=[],
            suppress=[technique.Interception] + warcries + orders,
        )

    else:
        raise ValueError(f"Unknown orc variant: {variant}")


def generate_orc(settings: GenerationSettings) -> StatsBeingGenerated:
    name = settings.creature_name
    cr = settings.cr
    variant = settings.variant
    rng = settings.rng
    is_legendary = settings.is_legendary

    # STATS
    if (
        variant is OrcSoldierVariant
        or variant is OrcReaverVariant
        or variant is OrcHardenedOneVariant
    ):
        attrs = [
            Stats.STR.scaler(StatScaling.Primary, mod=2),
            Stats.DEX.scaler(StatScaling.Medium, mod=2),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(
                StatScaling.Default,
                mod=-3 if variant is not OrcHardenedOneVariant else 2,
            ),
            Stats.WIS.scaler(
                StatScaling.Default, mod=1 if variant is not OrcReaverVariant else -1
            ),
            Stats.CHA.scaler(
                StatScaling.Default,
                mod=0 if variant is not OrcHardenedOneVariant else 2,
            ),
        ]
    elif variant is OrcBloodletterVariant:
        attrs = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Primary),
            Stats.INT.scaler(StatScaling.Medium, mod=0.5),
            Stats.WIS.scaler(StatScaling.Medium, mod=1),
            Stats.CHA.scaler(StatScaling.Medium, mod=1),
        ]
    elif variant is OrcBloodriteShamanVariant:
        attrs = [
            Stats.STR.scaler(StatScaling.Default),
            Stats.DEX.scaler(StatScaling.Medium, mod=1),
            Stats.INT.scaler(StatScaling.Medium, mod=2),
            Stats.WIS.scaler(StatScaling.Primary),
            Stats.CHA.scaler(StatScaling.Default),
        ]
    elif variant is OrcWarchiefVariant:
        attrs = [
            Stats.STR.scaler(
                StatScaling.Primary,
            ),
            Stats.DEX.scaler(StatScaling.Medium),
            Stats.CON.scaler(StatScaling.Constitution, mod=2),
            Stats.INT.scaler(StatScaling.Default, mod=1),
            Stats.WIS.scaler(StatScaling.Default, mod=2),
            Stats.CHA.scaler(StatScaling.Medium, mod=1),
        ]
    else:
        raise ValueError(f"Unknown orc variant: {variant}")

    stats = base_stats(
        name=variant.name,
        cr=cr,
        stats=attrs,
        hp_multiplier=settings.hp_multiplier,
        damage_multiplier=settings.damage_multiplier,
    )

    stats = stats.copy(
        name=name,
        size=Size.Small,
        languages=["Common", "Orc"],
        creature_class="Orc",
        creature_subtype="Orc",
    ).with_types(primary_type=CreatureType.Humanoid)

    # LEGENDARY
    if is_legendary:
        stats = stats.as_legendary()

    # SENSES
    stats = stats.copy(senses=stats.senses.copy(darkvision=60))

    # ARMOR CLASS
    if variant is OrcSoldierVariant or variant is OrcReaverVariant:
        stats = stats.add_ac_template(HideArmor)
    elif variant is OrcHardenedOneVariant or variant is OrcWarchiefVariant:
        stats = stats.add_ac_template(PlateArmor)
    elif variant is OrcBloodletterVariant:
        stats = stats.add_ac_template(StuddedLeatherArmor)
    elif variant is OrcBloodriteShamanVariant:
        stats = stats.add_ac_template(ArcaneArmor)

    # ATTACKS
    if variant is OrcBloodletterVariant:
        attack = weapon.Daggers.with_display_name("Black Blades").copy(die_count=1)
        secondary_attack = weapon.Shortbow.with_display_name("Black Bow").copy(
            damage_scalar=0.9
        )
        secondary_damage_type = DamageType.Poison
    elif variant is OrcBloodriteShamanVariant:
        attack = spell.Shock.with_display_name("Thunder Shock")
        secondary_attack = None
        secondary_damage_type = None
    else:
        attack = weapon.Greataxe.with_display_name("Wicked Greataxe")
        secondary_attack = weapon.JavelinAndShield.with_display_name("Javelin").copy(
            damage_scalar=0.9
        )
        secondary_damage_type = None

    if variant is OrcSoldierVariant:
        # CR 1/2 Orc Soldier uses a greataxe and shouldn't have 2 attacks
        stats = stats.with_set_attacks(multiattack=1)

    stats = attack.alter_base_stats(stats)
    stats = attack.initialize_attack(stats)
    stats = stats.copy(secondary_damage_type=secondary_damage_type)
    if secondary_attack is not None:
        stats = secondary_attack.add_as_secondary_attack(stats)

    # SPELLS
    if variant is OrcBloodriteShamanVariant:
        stats = stats.grant_spellcasting(
            caster_type=CasterType.Primal, spellcasting_stat=Stats.WIS
        )

    # ROLES
    if variant is OrcSoldierVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles: set[MonsterRole] = set()
    elif variant is OrcHardenedOneVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles = {MonsterRole.Defender}
    elif variant is OrcReaverVariant:
        primary_role = MonsterRole.Bruiser
        secondary_roles = {MonsterRole.Soldier}
    elif variant is OrcBloodletterVariant:
        primary_role = MonsterRole.Ambusher
        secondary_roles = {MonsterRole.Skirmisher}
    elif variant is OrcBloodriteShamanVariant:
        primary_role = MonsterRole.Support
        secondary_roles = {MonsterRole.Artillery}
    elif variant is OrcWarchiefVariant:
        primary_role = MonsterRole.Soldier
        secondary_roles = {MonsterRole.Leader, MonsterRole.Bruiser}
    else:
        raise ValueError(f"Unknown orc variant: {variant}")

    stats = stats.with_roles(
        primary_role=primary_role, additional_roles=secondary_roles
    )

    # SKILLS
    stats = stats.grant_proficiency_or_expertise(Skills.Intimidation)

    if variant is OrcWarchiefVariant:
        stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

    # SAVES
    if variant is OrcBloodriteShamanVariant:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS)

    if variant is OrcWarchiefVariant:
        stats = stats.grant_save_proficiency(Stats.CON, Stats.WIS, Stats.STR)

    # POWERS
    features = []

    # ADDITIONAL POWERS
    stats, power_features, power_selection = select_powers(
        stats=stats,
        rng=rng,
        settings=settings.selection_settings,
        custom=orc_powers(variant, rng, cr),
    )
    features += power_features

    # FINALIZE
    stats = attack.finalize_attacks(stats, rng, repair_all=False)

    if secondary_attack is not None:
        stats = secondary_attack.finalize_attacks(stats, rng, repair_all=False)

    return StatsBeingGenerated(stats=stats, features=features, powers=power_selection)


OrcTemplate: CreatureTemplate = CreatureTemplate(
    name="Orc",
    tag_line="Bloodrage-Fueled Ancestral Warriors",
    description="Orcs are savage and aggressive humanoids known for their brute strength and ferocity in battle. They are gifted with a powerful bloodrage that enhances their physical abilities and makes them formidable foes. Orcs are often found in warbands, led by a powerful warchief, and they are known for their brutal tactics and willingness to fight to the death.",
    environments=["Forest", "Grassland", "Hill", "Feywild", "Underdark"],
    treasure=["Any"],
    variants=[
        OrcSoldierVariant,
        OrcReaverVariant,
        OrcHardenedOneVariant,
        OrcBloodriteShamanVariant,
        OrcBloodletterVariant,
        OrcWarchiefVariant,
    ],
    species=[],
    callback=generate_orc,
    is_sentient_species=True,
)
