from ...powers import (
    PowerLoadout,
)
from ...powers.creature_type import celestial
from ...powers.roles import support
from ...powers.spellcaster import celestial as celestial_spellcasting
from ...powers.themed import holy, technique

PerksMartialTraining = [
    technique.BlindingAttack,
    technique.ShieldMaster,
    technique.ArmorMaster,
]

PerksSupport = [
    support.Encouragement,
    support.Guidance,
    support.WardingBond,
    holy.Heroism,
]

PerksDivineManifestation = [
    celestial.DivineLaw,
    celestial.WordsOfRighteousness,
    celestial.RighteousJudgement,
    celestial.AbsoluteConviction,
    holy.DeathWard,
    support.Sanctuary,
]

PerksSpellcasting = [
    celestial_spellcasting.CelestialAdept,
    celestial_spellcasting.CelestialMaster,
    celestial_spellcasting.CelestialExpert,
]


LoadoutAcolyte = [
    PowerLoadout(
        name="Martial Training",
        flavor_text="Acolytes are trained in combat, soldiers of the faith",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Assistance",
        flavor_text="Acolytes assist their allies with divine powers",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Spark",
        flavor_text="Acolytes channel mere sparks of the Divine",
        powers=[celestial_spellcasting.CelestialInitiate],
        locked=True,
    ),
]

LoadoutPriest = [
    PowerLoadout(
        name="Martial Training",
        flavor_text="Priests are trained in combat, soldiers of the faith",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Assistance",
        flavor_text="Priests assist their allies with divine powers",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Adept",
        flavor_text="Priests channel embers of the Divine",
        powers=[celestial_spellcasting.CelestialAdept],
        locked=True,
    ),
]

LoadoutAnointedOne = [
    PowerLoadout(
        name="Martial Training",
        flavor_text="Priests are trained in combat, soldiers of the faith",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Assistance",
        flavor_text="Priests assist their allies with divine powers",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Manifestation",
        flavor_text="A spark of the Divine made manifest in the Mortal Realm",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Conduit",
        flavor_text="Anointed Ones glow brightly with the Divine",
        powers=[celestial_spellcasting.CelestialMaster],
        locked=True,
    ),
]

LoadoutArchpriest = [
    PowerLoadout(
        name="Martial Training",
        flavor_text="Priests are trained in combat, soldiers of the faith",
        powers=PerksMartialTraining,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Assistance",
        flavor_text="Priests assist their allies with divine powers",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Manifestation",
        flavor_text="A spark of the Divine made manifest in the Mortal Realm",
        powers=PerksSupport,
    ),
    PowerLoadout(
        name="Divine Prophet",
        flavor_text="Archpriests are infused with the Divine",
        powers=[celestial_spellcasting.CelestialExpert],
        locked=True,
    ),
]
