from ...powers import (
    PowerLoadout,
)
from ...powers.creature import cultist
from ...powers.roles import defender, leader
from ...powers.spellcaster import cult
from ...powers.themed import (
    anti_magic,
    charm,
    cowardly,
    cursed,
    deathly,
    domineering,
    fearsome,
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
    cursed.CursedWound,
    cursed.VoidSiphon,
    cursed.UnholyAura,
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

LoadoutCultist = [
    PowerLoadout(
        name="Disposable Pawn",
        flavor_text="A lowly cultist, serving their master.",
        powers=PerksDisposableMinions,
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
