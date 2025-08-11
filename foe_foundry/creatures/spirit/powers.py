from ...powers import PowerLoadout
from ...powers.creature import spirit
from ...powers.creature_type import undead
from ...powers.roles import leader
from ...powers.themed import (
    aberrant,
    anti_magic,
    cursed,
    deathly,
    emanation,
    fearsome,
    technique,
)

PerksSpecterFlitting = [
    spirit.SpiritStep,
    spirit.SpiritFlicker,
]
PerksSpecterSpirit = [
    spirit.Haunt,
    anti_magic.ArcaneHunt,
    anti_magic.TwistedMind,
    cursed.AuraOfDespair,
    cursed.CursedWound,
    cursed.BestowCurse,
    cursed.RayOfEnfeeblement,
]
LoadoutSpecter = [
    PowerLoadout(
        name="Flitting",
        flavor_text="Eerily flitting in and out of existence",
        powers=PerksSpecterFlitting,
    ),
    PowerLoadout(
        name="Haunting",
        flavor_text="Haunting the living with a malevolent presence",
        powers=PerksSpecterSpirit,
    ),
]


PerksShadowRequired = [deathly.DrainStrength]
PerksShadowOptions = [
    spirit.ShadowInvisibility,
    spirit.FeedOnLight,
    deathly.ShadowWalk,
    cursed.ReplaceShadow,
]
LoadoutShadow = [
    PowerLoadout(
        name="Strength Drain",
        flavor_text="Draining the strength from the living",
        powers=PerksShadowRequired,
    ),
    PowerLoadout(
        name="Shadows Manifest",
        flavor_text="Darkness incarnate",
        powers=PerksShadowOptions,
    ),
]


PerksRevenantCurse = [
    cursed.CurseOfVengeance,
    cursed.RejectDivinity,
    cursed.CursedWound,
]
PerksRevenantLeadership = [
    deathly.EndlessServitude,
    deathly.FleshPuppets,
    emanation.ShadowRift,
    leader.CommandTheAttack,
]
PerksRevenantFear = [
    undead.SoulChill,
    fearsome.DreadGaze,
    fearsome.NightmarishVisions,
]
LoadoutRevenant = [
    PowerLoadout(
        name="Vengeful",
        flavor_text="A vengeful spirit, cursed to haunt the living",
        powers=PerksRevenantCurse,
    ),
    PowerLoadout(
        name="Posse",
        flavor_text="Leading a spectral posse",
        powers=PerksRevenantLeadership,
    ),
    PowerLoadout(
        name="Terrify the Guilty",
        flavor_text="Instilling fear in the guilty",
        powers=PerksRevenantFear,
    ),
]


PerksBansheeScream = [fearsome.MindShatteringScream]
PerksBansheeAttack = [technique.FrighteningAttack]
PerksBansheeSpirit = [
    spirit.Haunt,
    spirit.SpiritStep,
    spirit.SpiritFlicker,
    spirit.GraspOfTheDead,
    fearsome.HorrifyingPresence,
    fearsome.HorrifyingVisage,
    fearsome.DreadGaze,
    fearsome.NightmarishVisions,
]
LoadoutBanshee = [
    PowerLoadout(
        name="Banshee's Scream",
        flavor_text="A piercing scream that shatters the mind",
        powers=PerksBansheeScream,
    ),
    PowerLoadout(
        name="Frightening Attack",
        flavor_text="An attack that instills fear",
        powers=PerksBansheeAttack,
    ),
    PowerLoadout(
        name="Haunt",
        flavor_text="A haunting presence that terrifies the living",
        powers=PerksBansheeSpirit,
    ),
]


PerksGhostPosession = [
    spirit.Possession,
]
PerksGhostTimeless = [
    aberrant.ModifyMemory,
    spirit.NameTheForgotten,
    emanation.TimeRift,
    emanation.IllusoryReality,
]
PerksGhostlyOffense = [
    spirit.GraspOfTheDead,
    cursed.UnholyAura,
    spirit.Haunt,
    spirit.SpiritStep,
    spirit.SpiritFlicker,
    undead.StygianBurst,
    undead.SoulChill,
    undead.AntithesisOfLife,
    fearsome.DreadGaze,
]
LoadoutGhost = [
    PowerLoadout(
        name="Possession",
        flavor_text="Possessing the living to achieve its goals",
        powers=PerksGhostPosession,
    ),
    PowerLoadout(
        name="Forgotten by Time",
        flavor_text="A timeless entity, existing beyond the constraints of time",
        powers=PerksGhostTimeless,
    ),
    PowerLoadout(
        name="Haunt",
        flavor_text="A ghostly presence that attacks with spectral might",
        powers=PerksGhostlyOffense,
    ),
]


PerksWraithDarkness = [
    spirit.FeedOnLight,
    emanation.ShadowRift,
    deathly.ShadowWalk,
]
PerksWraithLeadership = [
    cursed.UnholyAura,
    deathly.EndlessServitude,
    deathly.FleshPuppets,
]
PerksWraithDeathly = [
    deathly.DevourSoul,
    spirit.GraspOfTheDead,
    cursed.CursedWound,
    cursed.RejectDivinity,
    cursed.BestowCurse,
]
LoadoutWraith = [
    PowerLoadout(
        name="Darkness and Death",
        flavor_text="Embracing the shadows to strike fear",
        powers=PerksWraithDarkness,
    ),
    PowerLoadout(
        name="Greater Undead",
        flavor_text="Leading the undead with a commanding presence",
        powers=PerksWraithLeadership,
    ),
    PowerLoadout(
        name="Deathly Presence",
        flavor_text="Devouring the souls of the living",
        powers=PerksWraithDeathly,
    ),
]
