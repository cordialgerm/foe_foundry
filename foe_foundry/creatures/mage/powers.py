from foe_foundry.utils.combine import combine_items

from ...powers import Power, PowerLoadout
from ...powers.creature import mage
from ...powers.creature_type import undead
from ...powers.roles import artillery
from ...powers.spellcaster import (
    abjurer,
    conjurer,
    divination,
    elementalist,
    enchanter,
    illusionist,
    metamagic,
    necromancer,
    transmuter,
)
from ...powers.themed import (
    anti_magic,
    anti_ranged,
    chaotic,
    charm,
    deathly,
    diseased,
    domineering,
    emanation,
    icy,
    illusory,
    poison,
    storm,
    technique,
    teleportation,
    temporal,
    tough,
)


def power_matches_cr(p: Power, cr: float) -> bool:
    score_args: dict = p.score_args  # type: ignore
    min_cr = score_args.get("require_cr", 0)
    max_cr = score_args.get("require_max_cr", 100)
    return min_cr <= cr <= max_cr


Attacks = [
    technique.SappingAttack,
    technique.PushingAttack,
    technique.ProneAttack,
    technique.SlowingAttack,
    technique.DazingAttacks,
]
AdeptSpellcasting = [mage.AdeptMage]
MageSpellcasting = [mage.Mage]
ArchmageSpellcasting = [mage.Archmage]

Mistystep = PowerLoadout(
    name="Evasive Magic",
    flavor_text="A good mage keeps their enemies at a distance",
    powers=[
        teleportation.MistyStep,
    ],
)
Protective = PowerLoadout(
    name="Defensive Magic",
    flavor_text="A simple spell, but quite effective",
    powers=[mage.ProtectiveMagic],
)
MagicResistance = PowerLoadout(
    name="Magic Resistance",
    flavor_text="Archmages have studied how to resist inimical magic",
    powers=[tough.MagicResistance],
)

# MageGeneralPurpose = [
#     anti_ranged.Overchannel,
#     artillery.TwinSpell,
#     artillery.SuppresingFire,
# ]

ArcaneStudy = PowerLoadout(
    name="Arcane Study",
    flavor_text="Advanced arcane techniques and training",
    powers=[
        metamagic.ArcaneMastery,
        metamagic.SubtleMind,
        metamagic.SpellEcho,
        metamagic.ManaSurge,
        metamagic.Mindshackle,
        metamagic.Runeburst,
        anti_ranged.Overchannel,
        artillery.TwinSpell,
    ],
)

### Apprentice
PerksApprenticeSpellcasting = [mage.ApprenticeMage]
PerksApprenticeTechniques = [
    technique.PushingAttack,
    technique.SlowingAttack,
    technique.ProneAttack,
]
LoadoutApprentice = [
    PowerLoadout(
        name="Apprentice Mage",
        flavor_text="A novice spellcaster with basic magical abilities.",
        powers=PerksApprenticeSpellcasting,
    ),
    PowerLoadout(
        name="Minor Offensive Techniques",
        flavor_text="Basic techniques to enhance physical attacks.",
        powers=PerksApprenticeTechniques,
    ),
]

### Abjurer
AbjurerAdept = PowerLoadout(
    name="Abjuration",
    flavor_text="Magic that protects and wards against threats",
    powers=[p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 4)],
    locked=True,
)
AbjurerMage = PowerLoadout(
    name="Abjuration",
    flavor_text="Magic that protects and wards against threats",
    powers=[p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 6)],
    locked=True,
)
AbjurerArchmage = PowerLoadout(
    name="Abjuration",
    flavor_text="Magic that protects and wards against threats",
    powers=[p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 12)],
    locked=True,
)
AbjurerAttacks = PowerLoadout(
    name="Runic Offense",
    flavor_text="Sometimes, a good offense is a good defense",
    powers=Attacks + [anti_magic.SpellStealer],
)
AbjurerEsotera = PowerLoadout(
    name="Abjuration Esotera",
    flavor_text="Advanced abjuration techniques and wards",
    powers=[emanation.RunicWards],
)

LoadoutAbjurerAdept = [AbjurerAdept, AbjurerAttacks, Mistystep]
LoadoutAbjurerMage = [AbjurerMage, AbjurerAttacks, ArcaneStudy, Mistystep, Protective]
LoadoutAbjurerArchmage = [
    AbjurerArchmage,
    AbjurerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    AbjurerEsotera,
    Protective,
]

### Conjurer
ConjurerAdept = PowerLoadout(
    name="Conjuration",
    flavor_text="Magic that summons and manipulates creatures and objects",
    powers=[p for p in conjurer.ConjurationWizards() if power_matches_cr(p, 4)],
)
ConjurerMage = PowerLoadout(
    name="Conjuration",
    flavor_text="Magic that summons and manipulates creatures and objects",
    powers=[p for p in conjurer.ConjurationWizards() if power_matches_cr(p, 6)],
)
ConjurerArchmage = PowerLoadout(
    name="Conjuration",
    flavor_text="Magic that summons and manipulates creatures and objects",
    powers=[p for p in conjurer.ConjurationWizards() if power_matches_cr(p, 12)],
)
ConjurerAttacks = PowerLoadout(
    name="Conjured Offense",
    flavor_text="Conjuration excells at offense",
    powers=Attacks.copy(),
)
ConjurerEsotera = PowerLoadout(
    name="Conjuration Esotera",
    flavor_text="Advanced conjuration techniques and spells",
    powers=[
        anti_magic.RedirectTeleport,
        teleportation.Scatter,
        teleportation.BendSpace,
        emanation.SummonersRift,
    ],
)

LoadoutConjurerAdept = [ConjurerAdept, ConjurerAttacks, Mistystep]
LoadoutConjurerMage = [
    ConjurerMage,
    ConjurerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutConjurerArchmage = [
    ConjurerArchmage,
    ConjurerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    ConjurerEsotera,
]

### Diviner
DivinerAdept = PowerLoadout(
    name="Divination",
    flavor_text="Magic that foretells the future",
    powers=[p for p in divination.DivinationWizards() if power_matches_cr(p, 4)],
)
DivinerMage = PowerLoadout(
    name="Divination",
    flavor_text="Magic that foretells the future",
    powers=[p for p in divination.DivinationWizards() if power_matches_cr(p, 6)],
)
DivinerArchmage = PowerLoadout(
    name="Divination",
    flavor_text="Magic that foretells the future",
    powers=[p for p in divination.DivinationWizards() if power_matches_cr(p, 12)],
)
DivinerAttacks = PowerLoadout(
    name="Divination",
    flavor_text="Knowing your enemy's next move is half the battle",
    powers=Attacks.copy(),
)
DivinerEsotera = PowerLoadout(
    name="Divination Esotera",
    flavor_text="Advanced divination techniques and spells",
    powers=temporal.TemporalPowers + [emanation.TimeRift],
)
LoadoutDivinerAdept = [DivinerAdept, DivinerAttacks, Mistystep]
LoadoutDivinerMage = [
    DivinerMage,
    DivinerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutDivinerArchmage = [
    DivinerArchmage,
    DivinerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    DivinerEsotera,
]

### Enchanter
EnchanterAdept = PowerLoadout(
    name="Enchantment",
    flavor_text="Magic that charms and manipulates the mind",
    powers=[p for p in enchanter.EnchanterWizards() if power_matches_cr(p, 4)],
)
EnchanterMage = PowerLoadout(
    name="Enchantment",
    flavor_text="Magic that charms and manipulates the mind",
    powers=[p for p in enchanter.EnchanterWizards() if power_matches_cr(p, 6)],
)
EnchanterArchmage = PowerLoadout(
    name="Enchantment",
    flavor_text="Magic that charms and manipulates the mind",
    powers=[p for p in enchanter.EnchanterWizards() if power_matches_cr(p, 12)],
)
EnchanterAttacks = PowerLoadout(
    name="Charm Offensive",
    flavor_text="Keep your enemies off balance with mind-affecting attacks",
    powers=[
        technique.CharmingAttack,
        technique.VexingAttack,
        technique.SappingAttack,
    ],
)
EnchanterEsotera = PowerLoadout(
    name="Enchantment Esotera",
    flavor_text="Advanced enchantment techniques and spells",
    powers=combine_items(
        domineering.DomineeringPowers,
        charm.CharmPowers,
        emanation.HypnoticLure,
        exclude=charm.WardingCharm,
    ),
)

LoadoutEnchanterAdept = [EnchanterAdept, EnchanterAttacks, Mistystep]
LoadoutEnchanterMage = [
    EnchanterMage,
    EnchanterAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutEnchanterArchmage = [
    EnchanterArchmage,
    EnchanterAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    EnchanterEsotera,
]

### Illusionist
IllusionistAdept = PowerLoadout(
    name="Illusionist",
    flavor_text="Magic that deceives the mind",
    powers=[p for p in illusionist.IllusionistWizards() if power_matches_cr(p, 4)],
)
IllusionistMage = PowerLoadout(
    name="Illusionist",
    flavor_text="Magic that deceives the mind",
    powers=[p for p in illusionist.IllusionistWizards() if power_matches_cr(p, 6)],
)
IllusionistArchmage = PowerLoadout(
    name="Illusionist",
    flavor_text="Magic that deceives the mind",
    powers=[p for p in illusionist.IllusionistWizards() if power_matches_cr(p, 12)],
)
IllusionistAttacks = PowerLoadout(
    name="Illusionist Attacks",
    flavor_text="Attacks that deceive the mind",
    powers=[
        technique.VexingAttack,
        technique.SappingAttack,
        technique.FrighteningAttack,
    ],
)
IllusionistEsotera = PowerLoadout(
    name="Illusionist Esotera",
    flavor_text="Advanced illusionist techniques and spells",
    powers=illusory.IllusoryPowers + [emanation.IllusoryReality],
)

LoadoutIllusionistAdept = [IllusionistAdept, IllusionistAttacks, Mistystep]
LoadoutIllusionistMage = [
    IllusionistMage,
    IllusionistAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutIllusionistArchmage = [
    IllusionistArchmage,
    IllusionistAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    IllusionistEsotera,
]

### Necromancer
NecromancerAdept = PowerLoadout(
    name="Necromancy",
    flavor_text="Magic that manipulates life and death",
    powers=[p for p in necromancer.NecromancerWizards if power_matches_cr(p, 4)],
)
NecromancerMage = PowerLoadout(
    name="Necromancy",
    flavor_text="Magic that manipulates life and death",
    powers=[p for p in necromancer.NecromancerWizards if power_matches_cr(p, 6)],
)
NecromancerArchmage = PowerLoadout(
    name="Necromancy",
    flavor_text="Magic that manipulates life and death",
    powers=[p for p in necromancer.NecromancerWizards if power_matches_cr(p, 12)],
)
NecromancerAttacks = PowerLoadout(
    name="Necromancy Attacks",
    flavor_text="Attacks that manipulate life and death",
    powers=[technique.FrighteningAttack, technique.NoHealingAttack],
)
NecromancerEsotera = PowerLoadout(
    name="Necromancy Esotera",
    flavor_text="Advanced necromancy techniques and spells",
    powers=combine_items(
        deathly.DeathlyPowers,
        undead.UndeadPowers,
        emanation.ShadowRift,
        exclude={undead.UndeadFortitude, deathly.ShadowWalk},
    ),
)

LoadoutNecromancerAdept = [NecromancerAdept, NecromancerAttacks, Mistystep]
LoadoutNecromancerMage = [
    NecromancerMage,
    NecromancerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutNecromancerArchmage = [
    NecromancerArchmage,
    NecromancerAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    NecromancerEsotera,
]

### Transmuter
TransmuterAdept = PowerLoadout(
    name="Transmuter",
    flavor_text="Magic that transforms matter",
    powers=[p for p in transmuter.TransmutationWizards() if power_matches_cr(p, 4)],
)
TransmuterMage = PowerLoadout(
    name="Transmuter",
    flavor_text="Magic that transforms matter",
    powers=[p for p in transmuter.TransmutationWizards() if power_matches_cr(p, 6)],
)
TransmuterArchmage = PowerLoadout(
    name="Transmuter",
    flavor_text="Magic that transforms matter",
    powers=[p for p in transmuter.TransmutationWizards() if power_matches_cr(p, 12)],
)
TransmuterAttacks = PowerLoadout(
    name="Transmuter Attacks",
    flavor_text="Attacks that transform matter",
    powers=Attacks.copy(),
)
TransmuterEsotera = PowerLoadout(
    name="Transmuter Esotera",
    flavor_text="Advanced transmutation techniques and spells",
    powers=[
        chaotic.ChaoticSpace,
        teleportation.BendSpace,
        teleportation.Scatter,
        emanation.RecombinationMatrix,
    ],
)

LoadoutTransmuterAdept   = [TransmuterAdept, TransmuterAttacks, Mistystep]
LoadoutTransmuterMage = [
    TransmuterMage,
    TransmuterAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
]
LoadoutTransmuterArchmage = [
    TransmuterArchmage,
    TransmuterAttacks,
    ArcaneStudy,
    Mistystep,
    Protective,
    TransmuterEsotera,
]

### Pyromancer
Pyromancer = [elementalist.Pyromancer]
PyromancerAttacks = [technique.BlindingAttack]
PyromancerEsotera = [emanation.RagingFlame]

PyromancerLoadout = [
    PowerLoadout(
        name="Pyromancer",
        flavor_text="A master of fire magic, capable of unleashing devastating flames.",
        powers=Pyromancer,
    ),
    PowerLoadout(
        name="Fire Attacks",
        flavor_text="Attacks that burn and blind enemies with fire.",
        powers=PyromancerAttacks,
    ),
    PowerLoadout(
        name="Fire Esotera",
        flavor_text="Advanced fire techniques and spells.",
        powers=PyromancerEsotera,
    ),
]

### Cryomancer
Cryomancer = [elementalist.Cryomancer]
CryomancerAttacks = [
    technique.SlowingAttack
]  # don't include freezing attack because Cryomancer already has Flash Freeze ability
CryomancerEsotera = [emanation.BitingFrost] + icy.IcyPowers
CryomancerEsotera.remove(icy.IcyShield)

CryomancerLoadout = [
    PowerLoadout(
        name="Cryomancer",
        flavor_text="A master of ice magic, capable of freezing enemies in their tracks.",
        powers=Cryomancer,
    ),
    PowerLoadout(
        name="Ice Attacks",
        flavor_text="Attacks that slow and freeze enemies with ice.",
        powers=CryomancerAttacks,
    ),
    PowerLoadout(
        name="Ice Esotera",
        flavor_text="Advanced ice techniques and spells.",
        powers=CryomancerEsotera,
    ),
]

### Electromancer
Electromancer = [elementalist.Electromancer]
ElectromancerAttacks = [
    technique.SappingAttack,
    technique.VexingAttack,
    technique.ShockingAttack,
]
ElectromancerEsotera = storm.StormPowers + [emanation.LashingWinds]

ElectromancerLoadout = [
    PowerLoadout(
        name="Electromancer",
        flavor_text="A master of lightning magic, capable of unleashing devastating electrical storms.",
        powers=Electromancer,
    ),
    PowerLoadout(
        name="Lightning Attacks",
        flavor_text="Attacks that shock and disrupt enemies with lightning.",
        powers=ElectromancerAttacks,
    ),
    PowerLoadout(
        name="Lightning Esotera",
        flavor_text="Advanced lightning techniques and spells.",
        powers=ElectromancerEsotera,
    ),
]

### Toximancer
Toximancer = [elementalist.Toximancer]
ToximancerAttacks = [technique.PoisonedAttack]
ToximancerEsotera = combine_items(
    poison.PoisonPowers,
    diseased.DiseasedPowers,
    emanation.FetidMiasma,
    exclude={poison.PoisonDart},
)

ToximancerLoadout = [
    PowerLoadout(
        name="Toximancer",
        flavor_text="A master of poison magic, capable of debilitating enemies with toxic effects.",
        powers=Toximancer,
    ),
    PowerLoadout(
        name="Poison Attacks",
        flavor_text="Attacks that poison and weaken enemies with toxins.",
        powers=ToximancerAttacks,
    ),
    PowerLoadout(
        name="Poison Esotera",
        flavor_text="Advanced poison techniques and spells.",
        powers=ToximancerEsotera,
    ),
]
