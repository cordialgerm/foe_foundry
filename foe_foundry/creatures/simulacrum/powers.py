from ...powers import PowerLoadout
from ...powers.creature import mage, simulacrum
from ...powers.roles import artillery, skirmisher
from ...powers.spellcaster import metamagic
from ...powers.themed import (
    anti_ranged,
    emanation,
    fast,
    illusory,
    sneaky,
    technique,
    teleportation,
    tough,
)

PerksMage = [
    teleportation.MistyStep,
    tough.MagicResistance,
    mage.ProtectiveMagic,
]
PerksSimulacrum = [simulacrum.SimulacrumSpellcasting]

PerksBendReality = [
    emanation.TimeRift,
    emanation.SummonersRift,
    emanation.HypnoticLure,
    emanation.RecombinationMatrix,
    emanation.BitingFrost,
    emanation.IllusoryReality,
    emanation.RunicWards,
    teleportation.BendSpace,
    teleportation.Scatter,
]

PerksAttacks = [
    metamagic.ArcaneMastery,
    anti_ranged.Overchannel,
    artillery.TwinSpell,
    artillery.SuppresingFire,
    technique.FreezingAttack,
    technique.SlowingAttack,
]


PerksMirrorblade = [simulacrum.SimulacrumMirrorblade]
PerksMirrorbladeAttacks = [
    technique.BlindingAttack,
    technique.SappingAttack,
    technique.VexingAttack,
]
PerksUnrealSpeed = [
    fast.Evasion,
    skirmisher.HarassingRetreat,
    sneaky.Vanish,
]
PerksMirrorbladeIllusions = [
    illusory.MirrorImage,
    illusory.PhantomMirage,
    illusory.Projection,
]


LoadoutSimulacrum = [
    PowerLoadout(
        name="Mage's Shadow",
        flavor_text="A shadowy duplicate of the mage, capable of casting spells and using magical abilities.",
        powers=PerksMage,
        selection_count=3,
    ),
    PowerLoadout(
        name="Simulacrum Spellcasting",
        flavor_text="A simulacrum inherits the magical prowess of its creator",
        powers=PerksSimulacrum,
    ),
    PowerLoadout(
        name="Bend Reality",
        flavor_text="A simulacrum is illusion manifest and can bend reality to its will",
        powers=PerksBendReality,
    ),
]

LoadoutMasterworkSimulacrum = LoadoutSimulacrum + [
    PowerLoadout(
        name="Masterwork Simulacrum",
        flavor_text="A simulacrum that has been enhanced with powerful abilities.",
        powers=PerksAttacks,
        selection_count=1,
    ),
]

LoadoutMirrorbladeSimulacrum = [
    PowerLoadout(
        name="Mirrorblade",
        flavor_text="A frozen copy of a warrior, but just as deadly as the original.",
        powers=PerksMirrorblade,
    ),
    PowerLoadout(
        name="Vexing Attacks",
        flavor_text="Facing an illusory copy is distracting to all but the most trained opponents",
        powers=PerksMirrorbladeAttacks,
    ),
    PowerLoadout(
        name="Flicker",
        flavor_text="A simulacrum mirrorblade can flicker in and out of existence",
        powers=PerksMirrorbladeIllusions,
    ),
    PowerLoadout(
        name="Unreal Speed",
        flavor_text="As fast and elusive as a paradox",
        powers=PerksUnrealSpeed,
    ),
]
