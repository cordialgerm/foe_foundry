from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.roles import bruiser, leader, soldier
from foe_foundry.powers.themed import fearsome, honorable, reckless, technique, tough

# Berserk
PerksBerserk = [reckless.Reckless]

# Unstoppable Offense
PerksUnstoppableOffense = [
    reckless.Charger,
    reckless.Overrun,
    reckless.RecklessFlurry,
    reckless.Toss,
    reckless.WildCleave,
]

# Battle Hardened
PerksBattleHardened = [
    technique.ProneAttack,
    technique.CleavingAttack,
    technique.PushingAttack,
    bruiser.CleavingBlows,
    bruiser.Rend,
    honorable.Challenge,
]

# Shrug it Off
PerksShrugItOff = [
    reckless.BloodiedRage,
    reckless.RelentlessEndurance,
    tough.JustAScratch,
]

# Lead the Charge
PerksLeadTheCharge = [
    fearsome.FearsomeRoar,
    leader.CommandTheAttack,
    honorable.MortalVow,
]

# Legendary
PerksLegendary = [soldier.ActionSurge]


LoadoutBerserker = [
    PowerLoadout(
        name="Berserk",
        flavor_text="The joy of battle calls and the berserker answers",
        powers=PerksBerserk,
        locked=True,
    ),
    PowerLoadout(
        name="Unstoppable Offense",
        flavor_text="Nothing can stop the berserker's charge",
        powers=PerksUnstoppableOffense,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Shrug it Off",
        flavor_text="Wounds are a reward for a good fight",
        powers=PerksShrugItOff,
    ),
]

LoadoutBerserkerVeteran = LoadoutBerserker + [
    PowerLoadout(
        name="Battle Hardened",
        flavor_text="The scars of battle are a badge of honor",
        powers=PerksBattleHardened,
    ),
]

LoadoutBerserkerCommander = LoadoutBerserkerVeteran + [
    PowerLoadout(
        name="Lead the Charge",
        flavor_text="A true leader is first into the fray",
        powers=PerksLeadTheCharge,
    ),
]


LoadoutBerserkerLegend = LoadoutBerserkerCommander + [
    PowerLoadout(
        name="Legendary",
        flavor_text="A legend in their own time",
        powers=PerksLegendary,
        locked=True,
    ),
]
