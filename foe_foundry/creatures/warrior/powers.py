from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.roles import leader, soldier
from foe_foundry.powers.themed import technique

# Shock Weapons
PerksOffensiveLine = [
    technique.CleavingAttack,
    technique.OverpoweringStrike,
    technique.GrazingAttack,
    technique.ProneAttack,
    technique.PushingAttack,
]

# Defensive Weapons
PerksDefensiveLine = [
    technique.PolearmMaster,
    technique.BaitAndSwitch,
    technique.ParryAndRiposte,
    technique.ArmorMaster,
    technique.DisarmingAttack,
    technique.Dueling,
    technique.ShieldMaster,
    technique.Interception,
]

# Martial Training
PerksMartialTraining = [
    soldier.CoordinatedStrike,
    soldier.Disciplined,
    soldier.BreakMagic,
    soldier.Lunge,
    soldier.PackTactics,
    soldier.Phalanx,
    soldier.Lunge,
    soldier.MightyLeap,
]

# Commander
PerksCommander = [
    leader.CommandTheAttack,
    leader.CommandTheTroops,
    leader.InspiringCommander,
]

# Legendary
PerksLegendaryWarrior = [soldier.ActionSurge]


LoadoutShockInfantry = [
    PowerLoadout(
        name="Great Weapon Fighting",
        flavor_text="Great weapon fighters pierce through enemy lines",
        powers=PerksOffensiveLine,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Warriors are trained to fight in formation",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
]
LoadoutShockInfantryVeteran = [
    PowerLoadout(
        name="Great Weapon Fighting",
        flavor_text="Great weapon fighters pierce through enemy lines",
        powers=PerksOffensiveLine,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Warriors are trained to fight in formation",
        powers=PerksMartialTraining,
        selection_count=2,
        replace_with_species_powers=True,
    ),
]

LoadoutLineInfantry = [
    PowerLoadout(
        name="Defensive Fighting",
        flavor_text="Defensive fighters hold the line against threats",
        powers=PerksDefensiveLine,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Warriors are trained to fight in formation",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
]
LoadoutLineInfantryVeteran = [
    PowerLoadout(
        name="Defensive Fighting",
        flavor_text="Defensive fighters hold the line against threats",
        powers=PerksDefensiveLine,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Warriors are trained to fight in formation",
        powers=PerksMartialTraining,
        selection_count=2,
        replace_with_species_powers=True,
    ),
]

LoadoutCommander = [
    PowerLoadout(
        name="Great Weapon Fighting",
        flavor_text="Great weapon fighters pierce through enemy lines",
        powers=PerksOffensiveLine,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Warriors are trained to fight in formation",
        powers=PerksMartialTraining,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Commanding Presence",
        flavor_text="Commanders lead their troops with skill and authority",
        powers=PerksCommander,
    ),
]

LoadoutLegendaryWarrior = LoadoutCommander + [
    PowerLoadout(
        name="Legendary Warrior",
        flavor_text="Legendary warriors are paragons of martial skill",
        powers=PerksLegendaryWarrior,
    )
]
