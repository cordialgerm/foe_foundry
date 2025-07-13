from foe_foundry.statblocks import BaseStatblock

from ...ac_templates import ArcaneArmor, HideArmor, PlateArmor, StuddedLeatherArmor
from ...attack_template import AttackTemplate, spell, weapon
from ...creature_types import CreatureType
from ...damage import DamageType
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

OrcSoldierVariant = MonsterVariant(
    name="Orc Soldier",
    description="Orc Soldiers are the backbone of any orc warband. They are strong and tough, and they fight with a ferocity that is unmatched.",
    monsters=[Monster(name="Orc Soldier", cr=1 / 2, srd_creatures=["Orc"])],
)

OrcReaverVariant = MonsterVariant(
    name="Orc Reaver",
    description="Orc Reavers are the most aggressive and bloodthirsty warriors in the warband. They charge into battle with reckless abandon, seeking to kill and maim as many foes as possible.",
    monsters=[Monster(name="Orc Reaver", cr=1)],
)

OrcHardenedOneVariant = MonsterVariant(
    name="Orc Hardened One",
    description="Orc Hardened Ones are the elite warriors of the orc warband. They are tough and resilient, and they fight with a brutal efficiency. They are often the elite bodyguard of the warchief.",
    monsters=[
        Monster(name="Orc Hardened One", cr=2, other_creatures={"Orog": "mm14"}),
    ],
)

OrcBloodriteShamanVariant = MonsterVariant(
    name="Orc Bloodrite Shaman",
    description="Orc Bloodrite Shamans are the spiritual leaders of the orc warband. They are powerful spellcasters who can call upon the spirits of their ancestors to aid them in battle. They often create powerful totems to protect their allies and curse their enemies.",
    monsters=[
        Monster(
            name="Orc Bloodrite Shaman",
            cr=2,
            other_creatures={
                "Orc Claw of Luthic": "vgtm",
                "Orc Hand of Yurtrus": "vgtm",
                "Orc Eye of Gruumsh": "vgtm",
            },
        ),
        Monster(name="Orc Bloodrite Elder Shaman", cr=5),
    ],
)

OrcBloodletterVariant = MonsterVariant(
    name="Orc Bloodletter",
    description="Orc Bloodletters are the most feared and deadly warriors in the orc warband. They are skilled in the art of assassination and can strike from the shadows with deadly precision.",
    monsters=[
        Monster(
            name="Orc Bloodletter",
            cr=4,
            other_creatures={"Orc Blade of Ilneval": "vgtm"},
        )
    ],
)

OrcWarchiefVariant = MonsterVariant(
    name="Orc Warchief",
    description="Orc Warchiefs are the leaders of the orc warband. They are powerful warriors and skilled tacticians who can rally their allies to victory. They are often accompanied by a retinue of elite warriors. The most powerful warchiefs dye their tusks red in the blood of their foes.",
    monsters=[
        Monster(name="Orc Warchief", cr=4, other_creatures={"Orc War Chief": "mm14"}),
        Monster(name="Orc Warchief of the Bloody Fang", cr=7, is_legendary=True),
    ],
)


class _OrcTemplate(MonsterTemplate):
    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        if settings.monster_key == "orc-soldier":
            return PowerSelection(powers.LoadoutSoldier)
        elif settings.monster_key == "orc-reaver":
            return PowerSelection(powers.LoadoutReaver)
        elif settings.monster_key == "orc-hardened-one":
            return PowerSelection(powers.LoadoutHardenedOne)
        elif settings.monster_key == "orc-bloodrite-shaman":
            return PowerSelection(powers.LoadoutShamanAdept)
        elif settings.monster_key == "orc-bloodrite-elder-shaman":
            return PowerSelection(powers.LoadoutShaman)
        elif settings.monster_key == "orc-bloodletter":
            return PowerSelection(powers.LoadoutBloodletter)
        elif settings.monster_key == "orc-warchief":
            return PowerSelection(powers.LoadoutWarchief)
        elif settings.monster_key == "orc-warchief-of-the-bloody-fang":
            return PowerSelection(powers.LoadoutWarchiefLegendary)
        else:
            raise ValueError(f"Unknown orc monster key: {settings.monster_key}")

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
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
                    StatScaling.Default,
                    mod=1 if variant is not OrcReaverVariant else -1,
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
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
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
            secondary_attack = weapon.JavelinAndShield.with_display_name(
                "Javelin"
            ).copy(damage_scalar=0.9)
            secondary_damage_type = None

        if variant is OrcSoldierVariant:
            # CR 1/2 Orc Soldier uses a greataxe and shouldn't have 2 attacks
            stats = stats.with_set_attacks(multiattack=1)

        stats = stats.copy(secondary_damage_type=secondary_damage_type)

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

        return stats, [attack, secondary_attack] if secondary_attack else [attack]


OrcTemplate: MonsterTemplate = _OrcTemplate(
    name="Orc",
    tag_line="Bloodrage-Fueled Ancestral Warriors",
    description="Orcs are savage and aggressive humanoids known for their brute strength and ferocity in battle. They are gifted with a powerful bloodrage that enhances their physical abilities and makes them formidable foes. Orcs are often found in warbands, led by a powerful warchief, and they are known for their brutal tactics and willingness to fight to the death.",
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
    is_sentient_species=True,
)
