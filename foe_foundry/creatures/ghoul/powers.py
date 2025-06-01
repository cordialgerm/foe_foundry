from ...powers import PowerLoadout
from ...powers.creature import ghoul
from ...powers.creature_type import undead
from ...powers.roles import bruiser, skirmisher
from ...powers.spellcaster import necromancer
from ...powers.themed import (
    cruel,
    cursed,
    deathly,
    diseased,
    poison,
    reckless,
    technique,
)

desired_diseases = {
    diseased.FilthFever,
    diseased.FleshRot,
    diseased.BlindingSickness,
}

PerksCannibal = [ghoul.Cannibal]

PerksDiseasedClaws = [technique.WeakeningAttack]

PerksRavenous = [
    bruiser.Rend,
    cruel.BloodiedFrenzy,
    reckless.BloodiedRage,
    reckless.Charger,
    reckless.RecklessFlurry,
    skirmisher.HarassingRetreat,
]

PerksDeathlyStench = [undead.StenchOfDeath, poison.VileVomit, poison.PoisonousBurst] + [
    p
    for p in diseased.ToxicBreathPowers
    if p.disease in desired_diseases  # type: ignore
]

PerksGravelordSpellcasting = [necromancer.NecromancerMaster]

PerksGravelord = [
    deathly.EndlessServitude,
    deathly.FleshPuppets,
    undead.StygianBurst,
    cursed.AuraOfDespair,
    cursed.BestowCurse,
    cursed.UnholyAura,
]

LoadoutBase = [
    PowerLoadout(
        name="Cannibal",
        flavor_text="Cannibalism is a way of life for ghouls",
        powers=PerksCannibal,
    ),
    PowerLoadout(
        name="Diseased Claws",
        flavor_text="Virulent infections from a single scratch",
        powers=PerksDiseasedClaws,
    ),
]

LoadoutGhoul = LoadoutBase + [
    PowerLoadout(
        name="Ravenous",
        flavor_text="Insatiable hunger and feral instincts",
        powers=PerksRavenous,
    ),
]

LoadoutGhast = LoadoutGhoul + [
    PowerLoadout(
        name="Deathly Stench",
        flavor_text="The stench can lay low even the most stalwart of heroes",
        powers=PerksDeathlyStench,
    )
]

LoadoutGhastGravelord = LoadoutBase + [
    PowerLoadout(
        name="Gravelord Spellcasting",
        flavor_text="A ghast that has mastered the dark arts of necromancy",
        powers=PerksGravelordSpellcasting,
    ),
    PowerLoadout(
        name="Gravelord",
        flavor_text="A ghast that commands legions of undead",
        powers=PerksGravelord,
    ),
]
