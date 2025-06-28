from ...powers import PowerLoadout
from ...powers.roles import defender, leader, soldier
from ...powers.species import orc
from ...powers.spellcaster import shaman
from ...powers.themed import (
    anti_ranged,
    bestial,
    cruel,
    fearsome,
    honorable,
    reckless,
    shamanic,
    sneaky,
    technique,
    totemic,
    tough,
)

PerksBloodfury = [orc.Bloodfury]
PerksWarriorBase = [
    orc.Bloodfury,
    orc.BloodrageDash,
    orc.BloodrageBlow,
    orc.BloodrageEndurance,
    orc.SavageMomentum,
]
PerksWarriorBaseAttacks = [
    technique.BleedingAttack,
    technique.DisarmingAttack,
    technique.CleavingAttack,
]


PerksSoldier = PerksWarriorBase + [
    soldier.MightyLeap,
    soldier.PreciseStrike,
]
PerksSoldierAttack = PerksWarriorBaseAttacks.copy()
LoadoutSoldier = [
    PowerLoadout(
        name="Warrior's Training",
        flavor_text="Extensive training since childhood",
        powers=PerksSoldier,
    ),
    PowerLoadout(
        name="Offensive Training",
        flavor_text="TODO ABCDEFGHIFSDFSDFD",
        powers=PerksSoldierAttack,
    ),
]

PerksReaver = [
    reckless.RecklessFlurry,
    reckless.Overrun,
    reckless.BloodiedRage,
    reckless.RelentlessEndurance,
    reckless.Toss,
    bestial.RetributiveStrike,
    cruel.BrutalCritical,
    cruel.BloodiedFrenzy,
    fearsome.FearsomeRoar,
]
PerksReaverAttack = [
    technique.BleedingAttack,
    technique.CleavingAttack,
    technique.DisarmingAttack,
    technique.OverpoweringStrike,
    technique.PushingAttack,
    technique.ProneAttack,
    technique.WhirlwindOfSteel,
]
LoadoutReaver = [
    PowerLoadout(
        name="Reaver",
        flavor_text="A savage warrior revels in the chaos of battle",
        powers=PerksReaver,
    ),
    PowerLoadout(
        name="Savage Attacks",
        flavor_text="Savage offense for a savage warrior",
        powers=PerksReaverAttack,
    ),
]

PerksHardenedOneHonorable = honorable.HonorablePowers
PerksHardenedOneDefender = [
    defender.Protection,
    defender.Taunt,
    defender.ZoneOfControl,
]
PerksHardenedOneSoldier = [
    technique.Interception,
    tough.JustAScratch,
    soldier.CoordinatedStrike,
]
PerksHardenedOneTechniques = [
    technique.ArmorMaster,
    technique.DisarmingAttack,
    technique.Interception,
    technique.ParryAndRiposte,
]
LoadoutHardenedOne = [
    PowerLoadout(
        name="Honorable",
        flavor_text="An honorable warrior who fights with dignity",
        powers=PerksHardenedOneHonorable,
    ),
    PowerLoadout(
        name="Defender",
        flavor_text="A stalwart defender who protects their allies",
        powers=PerksHardenedOneDefender,
    ),
    PowerLoadout(
        name="Discipline",
        flavor_text="A disciplined warrior who fights with precision",
        powers=PerksHardenedOneSoldier,
    ),
    PowerLoadout(
        name="Elite Training",
        flavor_text="An elite warrior with advanced training",
        powers=PerksHardenedOneSoldier,
    ),
]


PerksBloodletterRacial = [orc.BloodrageDash, orc.BloodrageBlow, orc.EmpoweringTatoo]
PerksBloodletterEvasion = [
    sneaky.Vanish,
    sneaky.SneakyStrike,
    sneaky.ExploitAdvantage,
    anti_ranged.HardToPinDown,
]
PerksBloodletterDeadly = [
    cruel.BrutalCritical,
    fearsome.DreadGaze,
]
PerksBloodletterAttack = [
    technique.BleedingAttack,
    technique.PoisonedAttack,
]
LoadoutBloodletter = [
    PowerLoadout(
        name="Orc Bloodletter",
        flavor_text="A deadly orc assassin who strikes from the shadows",
        powers=PerksBloodletterRacial,
    ),
    PowerLoadout(
        name="Sneaky",
        flavor_text="A stealthy orc who strikes from the shadows",
        powers=PerksBloodletterEvasion,
    ),
    PowerLoadout(
        name="Deadly Assassin",
        flavor_text="A deadly assassin who strikes with precision",
        powers=PerksBloodletterDeadly,
    ),
    PowerLoadout(
        name="Cruel Blades",
        flavor_text="Vicious blades that strike with deadly force",
        powers=PerksBloodletterAttack,
    ),
]

PerksShaman = shamanic.ShamanicPowers + [
    orc.AncestralGuidance,
    orc.EmpoweringTatoo,
    orc.SpiritSeek,
    orc.ThunderwrathTattoo,
    orc.SanguineOffering,
]
PerksShamanTotems = totemic.TotemicPowers.copy()
PerksShamanAdeptSpellcasting = [shaman.ShamanAdeptPower]
PerksShamanSpellcasting = [shaman.ShamanPower]
PerksShamanAttacks = [
    technique.ShockingAttack,
    technique.VexingAttack,
    technique.SappingAttack,
]
LoadoutShamanBase = [
    PowerLoadout(
        name="Shaman",
        flavor_text="A spiritual warrior who channels the power of the spirits",
        powers=PerksShaman,
    ),
    PowerLoadout(
        name="Totems",
        flavor_text="A shaman who uses totems to enhance their powers",
        powers=PerksShamanTotems,
    ),
    PowerLoadout(
        name="Shocking Attacks",
        flavor_text="The power of the storm flows through their attacks",
        powers=PerksShamanAttacks,
    ),
]
LoadoutShamanAdept = LoadoutShamanBase + [
    PowerLoadout(
        name="Spellcasting",
        flavor_text="The power of the spirits flows through their spells",
        powers=PerksShamanAdeptSpellcasting,
    )
]
LoadoutShaman = LoadoutShamanBase + [
    PowerLoadout(
        name="Spellcasting",
        flavor_text="The power of the spirits flows through their spells",
        powers=PerksShamanSpellcasting,
    )
]


PerksLeader = PerksWarriorBase + [
    orc.EmpoweringTatoo,
    orc.ThunderwrathTattoo,
    orc.AncestralGuidance,
]
PerksLeaderWarcry = [orc.WarCryOfTheBloodiedFang, orc.WarCryOfTheChillheart]
PerksLeaderCommands = [
    leader.CommandTheAttack,
    leader.StayInFormation,
    leader.CommandTheTroops,
    leader.FanaticFollowers,
    leader.RallyTheTroops,
    leader.Intimidate,
]
PerksLeaderTechniques = [
    technique.BleedingAttack,
    technique.CleavingAttack,
    technique.DisarmingAttack,
    technique.GrazingAttack,
    technique.OverpoweringStrike,
    technique.ParryAndRiposte,
    technique.WhirlwindOfSteel,
]
PerksChieftan = [orc.Bloodfury]

LoadoutWarchief = [
    PowerLoadout(
        name="Warchief", flavor_text="AAAAAAAAAAAAAAAAAAA", powers=PerksLeader
    ),
    PowerLoadout(
        name="Warcry",
        flavor_text="A powerful warcry that inspires allies and terrifies enemies",
        powers=PerksLeaderWarcry,
    ),
    PowerLoadout(
        name="Chieftan's Commands",
        flavor_text="Commands that rally and inspire the troops",
        powers=PerksLeaderCommands,
    ),
    PowerLoadout(
        name="Chieftan's Offense",
        flavor_text="A chieftan's offense is as brutal as it is effective",
        powers=PerksLeaderTechniques,
    ),
]
LoadoutWarchiefLegendary = LoadoutWarchief + [
    PowerLoadout(
        name="Chieftan's Fury",
        flavor_text="A chieftan's fury is unmatched on the battlefield",
        powers=PerksChieftan,
    )
]
