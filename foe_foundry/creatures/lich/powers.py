from ...powers import PowerLoadout
from ...powers.creature import lich, mage
from ...powers.creature_type import undead
from ...powers.roles import artillery
from ...powers.spellcaster import (
    metamagic,
)
from ...powers.themed import (
    anti_ranged,
    cursed,
    deathly,
    emanation,
    icy,
    technique,
)

PerksProtectiveMagic = [mage.ProtectiveMagic]
PerksSpellcasting = [lich.LichSpellcasting]

PerksAttackModifiers = [
    technique.SappingAttack,
    technique.PushingAttack,
    technique.ProneAttack,
    technique.SlowingAttack,
    technique.DazingAttacks,
    technique.FrighteningAttack,
    technique.NoHealingAttack,
]

PerksEmanations = [
    emanation.TimeRift,
    emanation.RunicWards,
    emanation.RagingFlame,
    emanation.BitingFrost,
    emanation.FetidMiasma,
    emanation.IllusoryReality,
    emanation.LashingWinds,
    icy.Blizzard,
]
PerksEmanationsArchlich = PerksEmanations.copy() + [lich.EverlastingImmortality]
PerksEmanationsArchlich.remove(emanation.RunicWards)

PerksMasterOfUndeath = [lich.SoulHarvest, lich.UndyingServants]

PerksArcaneMastery = [
    metamagic.ArcaneMastery,
    anti_ranged.Overchannel,
    artillery.TwinSpell,
    artillery.SuppresingFire,
    cursed.DisfiguringCurse,
    cursed.RejectDivinity,
    cursed.VoidSiphon,
    deathly.EndlessServitude,
    deathly.FleshPuppets,
    deathly.DrainingBlow,
    undead.SoulTether,
    undead.SoulChill,
    undead.StygianBurst,
    undead.AntithesisOfLife,
    icy.Hoarfrost,
    icy.IcyTomb,
    icy.Frostbite,
    icy.FrostNova,
]

LoadoutBase = [
    PowerLoadout(
        name="Protective Magic",
        flavor_text="The lich is protected by powerful arcane wards",
        powers=PerksProtectiveMagic,
        locked=True,
    ),
    PowerLoadout(
        name="Lich Spellcasting",
        flavor_text="The lich wields magic of the highest order",
        powers=PerksSpellcasting,
        locked=True,
    ),
    PowerLoadout(
        name="Offensive Magic",
        flavor_text="The lich uses powerful offensive magic to dominate the battlefield",
        powers=PerksAttackModifiers,
    ),
    PowerLoadout(
        name="Arcane Mastery",
        flavor_text="The lich has mastered the arcane arts, enhancing its spells and abilities",
        powers=PerksArcaneMastery,
    ),
    PowerLoadout(
        name="Master of Undeath",
        flavor_text="The lich commands the forces of undeath",
        powers=PerksMasterOfUndeath,
    ),
]


LoadoutLich = LoadoutBase + [
    PowerLoadout(
        name="Alter Reality",
        flavor_text="The lich can manipulate reality itself, bending the natural world to its will",
        powers=PerksEmanations,
    ),
]

LoadoutArchlich = LoadoutBase + [
    PowerLoadout(
        name="Alter Reality",
        flavor_text="The archlich can manipulate reality itself, bending the natural world to its will",
        powers=PerksEmanationsArchlich,
    ),
]
