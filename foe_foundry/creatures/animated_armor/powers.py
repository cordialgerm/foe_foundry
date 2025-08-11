from ...powers import PowerLoadout
from ...powers.creature_type import construct
from ...powers.roles import bruiser, defender
from ...powers.themed import anti_magic, anti_ranged, reckless, technique

PerksConstructed = [construct.ImmutableForm]

PerksDefensiveEnchantment = [
    construct.ProtectivePlating,
    construct.ExplosiveCore,
    construct.Overclock,
    defender.Protection,
    defender.Taunt,
    defender.ZoneOfControl,
    anti_magic.RuneDrinker,
    anti_magic.SealOfSilence,
    anti_ranged.ArrowWard,
    anti_ranged.DeflectMissile,
]

PerksOffensiveDefault = [
    technique.ProneAttack,
    technique.PushingAttack,
    bruiser.StunningBlow,
]

PerksOffensiveSlam = PerksOffensiveDefault + [
    reckless.Toss,
    technique.GrapplingAttack,
]

PerksOffenseEnchantmentWithLongsword = PerksOffensiveDefault + [
    reckless.WildCleave,
    technique.CleavingAttack,
]

PerksMageSlayer = [defender.SpellReflection, anti_magic.ArcaneHunt]

LoadoutAnimatedArmor = [
    PowerLoadout(
        name="Constructed Nature",
        flavor_text="Unliving animated armor",
        powers=PerksConstructed,
    ),
    PowerLoadout(
        name="Defensive Enchantments",
        flavor_text="Sigils and runes of protection",
        powers=PerksDefensiveEnchantment,
    ),
    PowerLoadout(
        name="Offensive Programming",
        flavor_text="Programming for melee combat",
        powers=PerksOffensiveSlam,
    ),
]

LoadoutRunicSpellplate = [
    PowerLoadout(
        name="Constructed Nature",
        flavor_text="Unliving animated armor",
        powers=PerksConstructed,
    ),
    PowerLoadout(
        name="Defensive Enchantments",
        flavor_text="Sigils and runes of protection",
        powers=PerksDefensiveEnchantment,
    ),
    PowerLoadout(
        name="Enchanted Spellblade",
        flavor_text="Runes of power on a longsword",
        powers=PerksOffensiveSlam,
    ),
    PowerLoadout(
        name="Anti-Magic Programming",
        flavor_text="Programming to counter magic users",
        powers=PerksMageSlayer,
    ),
]
