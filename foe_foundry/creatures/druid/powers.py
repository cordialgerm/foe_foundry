from ...powers import PowerLoadout
from ...powers.creature import druid
from ...powers.roles import support
from ...powers.spellcaster import druidic, metamagic
from ...powers.themed import (
    icy,
    poison,
    shamanic,
    storm,
    totemic,
)

PerksBestial = [druid.BestialWrath]

PerksPrimalPowers = totemic.TotemicPowers + [
    shamanic.CommuneWithAir,
    shamanic.CommuneWithLand,
    druid.PrimalEncouragement,
    metamagic.PrimalMastery,
    support.Guidance,
]

PerksElemental = (
    icy.IcyPowers
    + storm.StormPowers
    + [poison.PoisonDart, poison.VenemousMiasma, poison.PoisonousBurst]
)

PerksDruidicAdept = [druidic.DruidicAdeptPower]
PerksDruidicMaster = [druidic.DruidicMasterPower]
PerksDruidicExpert = [druidic.DruidicExpertPower]

LoadoutBase = [
    PowerLoadout(
        name="Bestial Wrath",
        flavor_text="The wrath of nature, made manifest",
        powers=PerksBestial,
        locked=True,
    ),
    PowerLoadout(
        name="Primal Attunement",
        flavor_text="Attuned to the primal forces of nature",
        powers=PerksPrimalPowers,
        replace_with_species_powers=True,
    ),
]


LoadoutDruid = LoadoutBase + [
    PowerLoadout(
        name="Druidic Adept",
        flavor_text="Adept at harnessing the power of nature",
        powers=PerksDruidicAdept,
        locked=True,
    ),
]

LoadoutGreenwarden = LoadoutBase + [
    PowerLoadout(
        name="Druidic Master",
        flavor_text="Master of the primal forces",
        powers=PerksDruidicMaster,
        locked=True,
    ),
    PowerLoadout(
        name="Elemental Affinity",
        flavor_text="Attuned to the primal forces of nature",
        powers=PerksElemental,
    ),
]

LoadoutArchdruid = LoadoutBase + [
    PowerLoadout(
        name="Archdruid",
        flavor_text="Master of the primal forces",
        powers=PerksDruidicExpert,
    ),
    PowerLoadout(
        name="Elemental Affinity",
        flavor_text="Attuned to the primal forces of nature",
        powers=PerksElemental,
    ),
]
