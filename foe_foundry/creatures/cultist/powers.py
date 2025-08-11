from ...powers import (
    PowerLoadout,
)
from ...powers.creature import cultist
from ...powers.creature_type import aberration, demon, devil, fiend, undead
from ...powers.roles import defender, leader
from ...powers.spellcaster import cult
from ...powers.themed import (
    aberrant,
    anti_magic,
    charm,
    cowardly,
    cursed,
    deathly,
    domineering,
    emanation,
    fearsome,
    psychic,
    technique,
    tough,
)

PerksDisposableMinions = [
    defender.Protection,
    cowardly.GrovelAndBeg,
    cowardly.ScurryAndScatter,
    cultist.SacrificialPawns,
    cultist.Indoctrination,
    cultist.PyramidScheme,
]
PerksDarkBoons = [
    cultist.Indoctrination,
    cursed.RayOfEnfeeblement,
    cursed.BestowCurse,
    tough.JustAScratch,
    anti_magic.SealOfSilence,
    charm.CharmingWords,
]
PerksDarkBlessings = PerksDarkBoons + [
    cursed.UnholyAura,
    cursed.RejectDivinity,
    deathly.DrainingBlow,
    cursed.VoidSiphon,
    cursed.CurseOfVengeance,
    fearsome.NightmarishVisions,
    technique.FrighteningAttack,
]
PerksCultLeader = [leader.FanaticFollowers]
PerksCharismatic = [
    domineering.Dominate,
    domineering.CommandingPresence,
    charm.MentalSummons,
]

PerksAberrantBoons = [
    psychic.DissonantWhispers,
    psychic.MirroredPain,
    psychic.ReadThoughts,
    technique.GrapplingAttack,
    aberration.MadenningWhispers,
    aberration.TentacleGrapple,
    aberration.TentacleSlam,
]
PerksAberrantBlessings = [
    psychic.Telekinetic,
    psychic.PsionicBlast,
    aberration.GazeOfTheFarRealm,
    aberrant.WarpReality,
]

PerksFiendishBoons = [
    fiend.FiendishCackle,
    demon.BlackBlood,
    technique.BurningAttack,
    technique.GrazingAttack,
    technique.CleavingAttack,
]
PerksFiendishBlessings = PerksFiendishBoons + [
    fiend.FieryTeleportation,
    devil.WallOfFire,
    devil.DevlishMinions,
]

PerksDeathlyBoons = [
    deathly.ShadowWalk,
    deathly.DrainStrength,
    undead.SoulChill,
    undead.SoulTether,
    undead.StenchOfDeath,
    technique.NoHealingAttack,
    technique.BleedingAttack,
]
PerksDeathlyBlessings = PerksDeathlyBoons + [
    deathly.DevourSoul,
    deathly.EndlessServitude,
    deathly.FleshPuppets,
    emanation.ShadowRift,
]

# CULTISTS
LoadoutCultist = [
    PowerLoadout(
        name="Disposable Pawn",
        flavor_text="A lowly cultist, serving their master.",
        powers=PerksDisposableMinions,
        selection_count=2,
        replace_with_species_powers=True,
    )
]
LoadoutCultFanatic = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingAdpet],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBoons,
        selection_count=2,
        replace_with_species_powers=True,
    ),
]
LoadoutCultGrandMaster = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingMaster],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Blessing",
        flavor_text="A dark blessing from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Cult Leader",
        flavor_text="A leader of the cult, with many followers.",
        powers=PerksCultLeader,
    ),
]
LoadoutCultExarch = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingExpert],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Blessing",
        flavor_text="A dark blessing from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Cult Leader",
        flavor_text="A leader of the cult, with many followers.",
        powers=PerksCultLeader,
    ),
    PowerLoadout(
        name="Charismatic",
        flavor_text="Others listen and obey.",
        powers=PerksCharismatic,
    ),
]

# ABERRANT CULTISTS
LoadoutAberrantInitiate = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingAdpet],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBoons,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Aberrant Boon",
        flavor_text="A gift from beyond the stars.",
        powers=PerksAberrantBoons,
    ),
]
LoadoutAberrantCultist = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingMaster],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Aberrant Boon",
        flavor_text="A gift from beyond the stars.",
        powers=PerksAberrantBlessings,
    ),
]
LoadoutAberrantGrandMaster = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingExpert],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Aberrant Boon",
        flavor_text="A gift from beyond the stars.",
        powers=PerksAberrantBlessings,
    ),
    PowerLoadout(
        name="Cult Leader",
        flavor_text="A leader of the cult, with many followers.",
        powers=PerksCultLeader,
    ),
]

# DEATH CULTISTS
LoadoutDeathCultInitiate = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingAdpet],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBoons,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Deathly Boon",
        flavor_text="A gift from the grave.",
        powers=PerksDeathlyBoons,
    ),
]
LoadoutDeathCultist = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingMaster],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Deathly Boon",
        flavor_text="A gift from the grave.",
        powers=PerksDeathlyBlessings,
    ),
]
LoadoutDeathCultGrandMaster = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingExpert],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Deathly Boon",
        flavor_text="A gift from the grave.",
        powers=PerksDeathlyBlessings,
    ),
    PowerLoadout(
        name="Cult Leader",
        flavor_text="A leader of the cult, with many followers.",
        powers=PerksCultLeader,
    ),
]

# FIENDISH CULTISTS
LoadoutFiendishInitiate = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingAdpet],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBoons,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Fiendish Boon",
        flavor_text="A gift from the hells or abyss.",
        powers=PerksFiendishBoons,
    ),
]

LoadoutFiendishCultist = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingMaster],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Boon",
        flavor_text="A dark boon from the cult.",
        powers=PerksDarkBoons,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Fiendish Mark",
        flavor_text="A mark from the hells or abyss.",
        powers=PerksFiendishBoons,
    ),
]

LoadoutFiendishGrandMaster = [
    PowerLoadout(
        name="Fanatical Belief",
        flavor_text="Fanaticism is a powerful weapon.",
        powers=[cult.CultSpellcastingExpert],
        locked=True,
    ),
    PowerLoadout(
        name="Dark Blessing",
        flavor_text="A dark blessing from the cult.",
        powers=PerksDarkBlessings,
        selection_count=2,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Fiendish Mark",
        flavor_text="A mark from the hells or abyss.",
        powers=PerksFiendishBlessings,
    ),
    PowerLoadout(
        name="Cult Leader",
        flavor_text="A leader of the cult, with many followers.",
        powers=PerksCultLeader,
    ),
]
