from ...powers import PowerLoadout
from ...powers.creature import goblin
from ...powers.roles import bruiser, leader, soldier
from ...powers.themed import cruel, reckless, sneaky, technique, thuggish, tough

PerksStreetFighting = [
    soldier.PackTactics,
    goblin.FlingFilth,
    sneaky.CheapShot,
    thuggish.ExploitTheChaos,
]
PerksRoughStrength = [
    bruiser.StunningBlow,
    reckless.Charger,
    reckless.Overrun,
    reckless.Toss,
]
PerksExtraTough = [tough.JustAScratch]
PerksAttack = [
    technique.ProneAttack,
    technique.GrazingAttack,
    technique.CleavingAttack,
    reckless.BloodiedRage,
    cruel.BloodiedFrenzy,
]

PerksBrawler = [technique.ExpertBrawler]
PerksBrawlerRoughStrength = [
    reckless.Toss,
    bruiser.StunningBlow,
    tough.JustAScratch,
]

PerksMobBoss = [
    leader.Intimidate,
    leader.CommandTheAttack,
    leader.FanaticFollowers,
    thuggish.KickTheLickspittle,
    thuggish.MobBoss,
]
PerksLegendary = [soldier.ActionSurge]

LoadoutThug = [
    PowerLoadout(
        name="Street Fighting",
        flavor_text="Dirty streets lead to dirty fighting.",
        powers=PerksStreetFighting,
    )
]
LoadoutVeteranThug = LoadoutThug + [
    PowerLoadout(
        name="Rough Strength",
        flavor_text="The strongest rule the streets",
        powers=PerksRoughStrength,
    ),
    PowerLoadout(
        name="Heavy Hitter",
        flavor_text="A big hit can turn the tide of battle.",
        powers=PerksAttack,
    ),
]
LoadoutEliteThug = LoadoutVeteranThug + [
    PowerLoadout(
        name="Extra Tough",
        flavor_text="The more scars, the tougher the fighter.",
        powers=PerksExtraTough,
    ),
]

LoadoutBrawler = LoadoutThug + [
    PowerLoadout(
        name="Rough Strength",
        flavor_text="The strongest rule the streets",
        powers=PerksBrawlerRoughStrength,
    ),
    PowerLoadout(
        name="Brawler",
        flavor_text="Big muscles, bigger punches.",
        powers=PerksBrawler,
    ),
]

LoadoutThugBoss = LoadoutVeteranThug + [
    PowerLoadout(
        name="Boss",
        flavor_text="The most vicious rise to the top",
        powers=PerksMobBoss,
    )
]
LoadoutThugOverboss = LoadoutThugBoss + [
    PowerLoadout(
        name="Extra Tough",
        flavor_text="The more scars, the tougher the fighter.",
        powers=PerksExtraTough,
    )
]
LoadoutThugLegend = LoadoutThugOverboss + [
    PowerLoadout(
        name="Legendary Fighter",
        flavor_text="Who hasn't heard their name?",
        powers=PerksLegendary,
    )
]
