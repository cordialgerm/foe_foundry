from ...powers import PowerLoadout
from ...powers.creature import ogre
from ...powers.creature_type import giant
from ...powers.roles import bruiser
from ...powers.spellcaster import shaman
from ...powers.themed import (
    clever,
    cursed,
    fearsome,
    illusory,
    reckless,
    technique,
    totemic,
)

PerkSmash = [ogre.Wallsmash]
PerkBelch = [ogre.Burnbelch]
PerkChainCrack = [ogre.ChainCrack]
PerkOniTrickster = [shaman.OniTrickster]

PerkAttack = [
    technique.ProneAttack,
    technique.PushingAttack,
    technique.CleavingAttack,
    technique.GrazingAttack,
    technique.DazingAttacks,
    bruiser.StunningBlow,
]
PerkOgreBigBoy = [
    giant.BigWindup,
    giant.GrabAndGo,
    reckless.Toss,
    reckless.Charger,
    reckless.Overrun,
    fearsome.FearsomeRoar,
]

PerkSpellcasterAttack = [
    technique.FrighteningAttack,
    technique.SlowingAttack,
    technique.DazingAttacks,
]
PerkClever = [
    clever.IdentifyWeaknes,
    illusory.PhantomMirage,
    fearsome.FearsomeRoar,
]
PerkShamanic = [
    cursed.RayOfEnfeeblement,
    cursed.CurseOfVengeance,
    totemic.SpiritChainsTotem,
    totemic.GuardianTotem,
]


LoadoutOgreBase = [
    PowerLoadout(
        name="Big 'Un", flavor_text="Puny little things", powers=PerkOgreBigBoy
    ),
    PowerLoadout(
        name="Hit 'Em Hard",
        flavor_text="Hit 'em hard, hit 'em again",
        powers=PerkAttack,
    ),
]
LoadoutSmasha = LoadoutOgreBase + [
    PowerLoadout(
        name="Wallsmasha",
        flavor_text="Smash 'da wall. Smaaaaash!",
        powers=PerkSmash,
    )
]
LoadoutBelcha = LoadoutOgreBase + [
    PowerLoadout(
        name="Burnbelcha",
        flavor_text="Burn 'em all, burn 'em good",
        powers=PerkBelch,
    )
]
LoadoutChainCrakka = LoadoutOgreBase + [
    PowerLoadout(
        name="Chain Crakka",
        flavor_text="Crack 'em wid da chain",
        powers=PerkChainCrack,
    )
]
LoadoutTrickster = [
    PowerLoadout(
        name="Trickster Attacks",
        flavor_text="Tricksy tricksy hex ya mind",
        powers=PerkSpellcasterAttack,
    ),
    PowerLoadout(
        name="Clever Ogre", flavor_text="Clever ogre, not so dumb", powers=PerkClever
    ),
    PowerLoadout(
        name="Tribal Shaman",
        flavor_text="Shaman for the brutes",
        powers=PerkShamanic,
    ),
    PowerLoadout(
        name="Shaman Spellcasting",
        flavor_text="Shamanic spellcasting",
        powers=PerkOniTrickster,
    ),
]
