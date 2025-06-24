from ...powers import PowerLoadout
from ...powers.creature import mage, simulacrum
from ...powers.roles import artillery
from ...powers.spellcaster import metamagic
from ...powers.themed import (
    anti_ranged,
    emanation,
    icy,
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

PerksMagicPowers = [
    technique.FreezingAttack,
    technique.SlowingAttack,
    metamagic.ArcaneMastery,
    anti_ranged.Overchannel,
    artillery.TwinSpell,
    artillery.SuppresingFire,
    emanation.IllusoryReality,
    emanation.RunicWards,
    teleportation.BendSpace,
    teleportation.Scatter,
    emanation.TimeRift,
    emanation.SummonersRift,
    emanation.HypnoticLure,
    emanation.RecombinationMatrix,
    emanation.BitingFrost,
] + icy.IcyPowers

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
        name="Magical Specialization",
        flavor_text="A mage capable of a simulacrum typically endows it with unique abilities",
        powers=PerksMagicPowers,
    ),
]
