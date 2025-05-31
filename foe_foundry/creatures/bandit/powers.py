from ...powers import PowerLoadout
from ...powers.creature import goblin
from ...powers.roles import artillery, leader
from ...powers.themed import cowardly, gadget, sneaky, technique, thuggish

PerksMook = [
    goblin.FlingFilth,
    cowardly.FeignDeath,
    cowardly.GrovelAndBeg,
]

PerksSneaky = [
    sneaky.CheapShot,
    gadget.SmokeBomb,
    sneaky.ExploitAdvantage,
    sneaky.Vanish,
]

PerksRanged = [
    artillery.SuppresingFire,
    technique.VexingAttack,
    technique.Sharpshooter,
    artillery.Overwatch,
    artillery.FocusShot,
]

PerksLeader = [
    thuggish.KickTheLickspittle,
    leader.CommandTheAttack,
    leader.FanaticFollowers,
    leader.StayInFormation,
    leader.Intimidate,
]

PerksTheBoss = [thuggish.MobBoss]

LoadoutBandit = [
    PowerLoadout(
        name="Mook", flavor_text="Live again to fight another day.", powers=PerksMook
    ),
    PowerLoadout(
        name="Fight Dirty", flavor_text="Hit 'em where it hurts.", powers=PerksSneaky
    ),
]

LoadoutBanditVeteran = LoadoutBandit + [
    PowerLoadout(
        name="Shoot 'Em",
        flavor_text="Keep your distance and pick 'em off.",
        powers=PerksRanged,
    )
]

LoadoutBanditCaptain = [
    PowerLoadout(
        name="Fight Dirty", flavor_text="Hit 'em where it hurts.", powers=PerksSneaky
    ),
    PowerLoadout(
        name="Shoot 'Em",
        flavor_text="Keep your distance and pick 'em off.",
        powers=PerksRanged,
    ),
    PowerLoadout(
        name="Lead from the Rear", flavor_text="You go first!", powers=PerksLeader
    ),
]

LoadoutBanditLegend = LoadoutBanditCaptain + [
    PowerLoadout(
        name="The Boss",
        flavor_text="The boss is here to make sure you do your job.",
        powers=PerksTheBoss,
        locked=True,
    )
]
