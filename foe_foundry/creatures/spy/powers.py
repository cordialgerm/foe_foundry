from foe_foundry.powers import PowerLoadout
from foe_foundry.powers.roles import ambusher, artillery
from foe_foundry.powers.themed import (
    anti_ranged,
    charm,
    clever,
    fast,
    gadget,
    poison,
    sneaky,
    technique,
)

# Cunning Action
PerksCunning = [ambusher.CunningAction]

# Secretive
PerksSecretive = [
    ambusher.StealthySneak,
    ambusher.DeadlyAmbusher,
    gadget.SmokeBomb,
    sneaky.SneakyStrike,
]

# Poisons
PerksDeadlyPoisons = [
    poison.ToxicPoison,
    poison.WeakeningPoison,
    technique.PoisonedAttack,
]

# Clever
PerksClever = [
    clever.IdentifyWeaknes,
    charm.CharmingWords,
    fast.NimbleReaction,
    gadget.PotionOfHealing,
]

# Fast
PerksQuick = [
    fast.Evasion,
    anti_ranged.HardToPinDown,
    fast.NimbleReaction,
    artillery.QuickDraw,
]


PerksBasicSpy = PerksSecretive + PerksClever
PerksBasicSpy.remove(sneaky.SneakyStrike)  # this will be forced in

LoadoutSpy = [
    PowerLoadout(
        name="Cunning",
        flavor_text="Spies live and die by their wits",
        powers=PerksCunning,
    ),
    PowerLoadout(
        name="Secretive",
        flavor_text="A knife in the back is the best way to get ahead",
        powers=PerksSecretive,
    ),
    PowerLoadout(
        name="Adaptable",
        flavor_text="Spies are always prepared for any situation",
        powers=PerksBasicSpy,
    ),
]

LoadoutEliteSpy = LoadoutSpy + [
    PowerLoadout(
        name="Deadly Poisons",
        flavor_text="A drop of poison is worth a thousand swords",
        powers=PerksDeadlyPoisons,
    )
]

LoadoutSpyMaster = LoadoutEliteSpy + [
    PowerLoadout(
        name="Quick", flavor_text="Fast hands and a quick wit", powers=PerksQuick
    )
]
