from ...powers import PowerLoadout
from ...powers.roles import defender, leader, soldier
from ...powers.spellcaster import oath
from ...powers.themed import holy, technique

PerksMartialTraining = [
    technique.BaitAndSwitch,
    technique.CleavingAttack,
    technique.DisarmingAttack,
    technique.GrazingAttack,
    technique.OverpoweringStrike,
    technique.ParryAndRiposte,
    technique.PommelStrike,
    technique.WhirlwindOfSteel,
]

PerksDefensiveTraining = [
    defender.Taunt,
    defender.ZoneOfControl,
    technique.ArmorMaster,
    technique.Interception,
    holy.Heroism,
    soldier.Disciplined,
]

PerksLeadership = [
    leader.CommandTheAttack,
    leader.StayInFormation,
    leader.InspiringCommander,
    leader.RallyTheTroops,
]

PerksOathAdept = [holy.DivineSmite, oath.OathAdept]

PerksOathMaster = [holy.DivineSmite, oath.OathMaster]

LoadoutKnight = [
    PowerLoadout(
        name="Defensive Training",
        flavor_text="Sworn to protect",
        powers=PerksDefensiveTraining,
        replace_with_species_powers=True,
    ),
    PowerLoadout(
        name="Martial Training",
        flavor_text="Honed in combat",
        powers=PerksMartialTraining,
    ),
    PowerLoadout(
        name="Leadership",
        flavor_text="Trained to command",
        powers=PerksLeadership,
    ),
]
LoadoutKnightOfTheRealm = LoadoutKnight + [
    PowerLoadout(
        name="Oath Adept",
        flavor_text="Channeling the power of an oath",
        powers=PerksOathAdept,
        selection_count=2,
        locked=True,
    ),
]
LoadoutQuestingKnight = LoadoutKnight + [
    PowerLoadout(
        name="Oath Master",
        flavor_text="Master of the oath",
        powers=PerksOathMaster,
        selection_count=2,
        locked=True,
    ),
]
LoadoutParagonKnight = LoadoutQuestingKnight
