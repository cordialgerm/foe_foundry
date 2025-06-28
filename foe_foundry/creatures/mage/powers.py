from ...powers import (
    CustomPowerSelection,
    CustomPowerWeight,
    Power,
    PowerLoadout
)
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
from ...statblocks import BaseStatblock
from .._data import (
    MonsterVariant,
)

def power_matches_cr(p: Power, cr: float) -> bool:
    score_args: dict = p.score_args  # type: ignore
    min_cr = score_args.get("require_cr", 0)
    max_cr = score_args.get("require_max_cr", 100)
    return min_cr <= cr <= max_cr



Attacks =  [
    technique.SappingAttack,
    technique.PushingAttack,
    technique.ProneAttack,
    technique.SlowingAttack,
    technique.DazingAttacks,
]
AdeptSpellcasting = [mage.AdeptMage]
MageSpellcasting = [mage.Mage]
ArchmageSpellcasting = [mage.Archmage]

Mistystep = [
    teleportation.MistyStep,
]
Protective = [mage.ProtectiveMagic]
MagicResistance = [tough.MagicResistance]

Metamagic = [
    metamagic.ArcaneMastery,
    metamagic.SubtleMind,
    metamagic.SpellEcho,
    metamagic.ManaSurge,
    metamagic.Mindshackle,
    metamagic.Runeburst,
    anti_ranged.Overchannel,
    artillery.TwinSpell,
]

### Apprentice
PerksApprenticeSpellcasting = [mage.ApprenticeMage]
PerksApprenticeTechniques = [
    technique.PushingAttack,
    technique.SlowingAttack,
    technique.ProneAttack,
]
LoadoutApprentice = [
    PowerLoadout(
        name = "Apprentice Mage",
        flavor_text = "A novice spellcaster with basic magical abilities.",
        powers = PerksApprenticeSpellcasting
    ),
    PowerLoadout(
        name = "Minor Offensive Techniques",
        flavor_text = "Basic techniques to enhance physical attacks.",
        powers = PerksApprenticeTechniques
    )
]

### Abjurer
AbjurerAdept = [p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 4)]
AbjurerMage = [p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 6)]
AbjurerArchmage = [p for p in abjurer.AbjurationWizards() if power_matches_cr(p, 12)]
AbjurerAttacks = Attacks + [anti_magic.SpellStealer]
AbjurerEsotera = [emanation.RunicWards]


class _MageWeights(CustomPowerSelection):
    def __init__(
        self, stats: BaseStatblock, name: str, cr: float, variant: MonsterVariant
    ):
        self.stats = stats
        self.variant = variant

        force = []
        esoteric = []
        techniques = [
            technique.SappingAttack,
            technique.PushingAttack,
            technique.ProneAttack,
            technique.SlowingAttack,
            technique.DazingAttacks,
        ]


        elif variant is AbjurerVariant:

        elif variant is ConjurerVariant:
            force.append(
                next(
                    p for p in conjurer.ConjurationWizards() if power_matches_cr(p, cr)
                )
            )
            esoteric += [
                anti_magic.RedirectTeleport,
                teleportation.Scatter,
                teleportation.BendSpace,
                emanation.SummonersRift,
            ]
        elif variant is DivinerVariant:
            force.append(
                next(
                    p for p in divination.DivinationWizards() if power_matches_cr(p, cr)
                )
            )
            esoteric += temporal.TemporalPowers
            esoteric += [emanation.TimeRift]
        elif variant is EnchanterVariant:
            force.append(
                next(p for p in enchanter.EnchanterWizards() if power_matches_cr(p, cr))
            )
            esoteric += domineering.DomineeringPowers
            esoteric += charm.CharmPowers
            esoteric.remove(charm.WardingCharm)
            esoteric += [emanation.HypnoticLure]
            techniques = [
                technique.CharmingAttack,
                technique.VexingAttack,
                technique.SappingAttack,
            ]
        elif variant is IllusionistVariant:
            force.append(
                next(
                    p
                    for p in illusionist.IllusionistWizards()
                    if power_matches_cr(p, cr)
                )
            )
            esoteric += illusory.IllusoryPowers
            esoteric += [emanation.IllusoryReality]
            techniques = [
                technique.VexingAttack,
                technique.SappingAttack,
                technique.FrighteningAttack,
            ]
        elif variant is NecromancerVariant:
            force.append(
                next(
                    p for p in necromancer.NecromancerWizards if power_matches_cr(p, cr)
                )
            )
            esoteric += deathly.DeathlyPowers
            esoteric += undead.UndeadPowers
            esoteric.remove(undead.UndeadFortitude)
            esoteric.remove(deathly.ShadowWalk)
            esoteric += [emanation.ShadowRift]
            techniques = [technique.FrighteningAttack, technique.NoHealingAttack]
        elif variant is TransmuterVariant:
            force.append(
                next(
                    p
                    for p in transmuter.TransmutationWizards()
                    if power_matches_cr(p, cr)
                )
            )
            esoteric += [
                chaotic.ChaoticSpace,
                teleportation.BendSpace,
                teleportation.Scatter,
                emanation.RecombinationMatrix,
            ]
        elif variant is PyromancerVariant:
            force.append(elementalist.Pyromancer)
            techniques = [technique.BlindingAttack]
            esoteric += [emanation.RagingFlame]
        elif variant is CryomancerVariant:
            force.append(elementalist.Cryomancer)
            techniques = [
                technique.SlowingAttack
            ]  # don't include freezing attack because Cryomancer already has Flash Freeze ability
            esoteric += [emanation.BitingFrost] + icy.IcyPowers
        elif variant is ElectromancerVariant:
            force.append(elementalist.Electromancer)
            esoteric += storm.StormPowers
            esoteric += [emanation.LashingWinds]
            techniques = [
                technique.SappingAttack,
                technique.VexingAttack,
                technique.ShockingAttack,
            ]
        elif variant is ToximancerVariant:
            force.append(elementalist.Toximancer)
            esoteric += poison.PoisonPowers
            esoteric += diseased.DiseasedPowers
            esoteric += [emanation.FetidMiasma]
            techniques = [technique.PoisonedAttack]

        # Hard-Coded Powers
        if cr >= 16:
            force += [
                tough.MagicResistance,
                # don't include MistyStep because mage has a legendary teleport action
                ProtectiveMagic,
                Archmage,
            ]
        elif cr >= 12:
            force += [
                tough.MagicResistance,
                teleportation.MistyStep,
                ProtectiveMagic,
                Archmage,
            ]
        elif cr >= 6:
            force += [teleportation.MistyStep, ProtectiveMagic, Mage]
        elif cr >= 4:
            force += [ProtectiveMagic, AdeptMage]
        else:
            force += [ApprenticeMage]

        # general purpose mage powers
        general = [
            metamagic.ArcaneMastery,
            anti_ranged.Overchannel,
            artillery.TwinSpell,
            artillery.SuppresingFire,
        ]

        self.force = force
        self.general = general
        self.techniques = techniques
        self.esoteric = esoteric
        self.ignore = ignore

    def custom_weight(self, p: Power) -> CustomPowerWeight:
        if p in self.force or p in self.ignore:
            return CustomPowerWeight(0, ignore_usual_requirements=False)
        elif p in self.general:
            return CustomPowerWeight(1.5, ignore_usual_requirements=True)
        elif p in self.techniques:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        elif p in self.esoteric:
            return CustomPowerWeight(2, ignore_usual_requirements=True)
        elif p in metamagic.MetamagicPowers:
            return CustomPowerWeight(1, ignore_usual_requirements=False)
        else:
            return CustomPowerWeight(0.5, ignore_usual_requirements=False)

    def force_powers(self) -> list[Power]:
        return self.force
