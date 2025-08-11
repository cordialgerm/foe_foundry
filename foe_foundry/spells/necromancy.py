from ..features import ActionType
from ..skills import AbilityScore
from .spell import Spell

BestowCurse: Spell = Spell(
    name="Bestow Curse",
    level=3,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=True,
    save=AbilityScore.WIS,
    concentration=True,
    concentration_spell_level=5,  # no concentration at 5th level or higher
    description="""You touch a creature, and that creature must succeed on a Wisdom saving throw or become cursed for the duration of the spell. When you cast this spell, choose the nature of the curse from the following options:

Choose one ability score. While cursed, the target has disadvantage on ability checks and saving throws made with that ability score.
While cursed, the target has disadvantage on attack rolls against you.
While cursed, the target must make a Wisdom saving throw at the start of each of its turns. If it fails, it wastes its action that turn doing nothing.
While the target is cursed, your attacks and spells deal an extra 1d8 necrotic damage to the target.
A remove curse spell ends this effect. At the DM's option, you may choose an alternative curse effect, but it should be no more powerful than those described above. The DM has final say on such a curse's effect.""",
    upcast_description="""If you cast this spell using a spell slot of 4th level or higher, the duration is concentration, up to 10 minutes. If you use a spell slot of 5th level or higher, the duration is 8 hours. If you use a spell slot of 7th level or higher, the duration is 24 hours. If you use a 9th level spell slot, the spell lasts until it is dispelled. Using a spell slot of 5th level or higher grants a duration that doesn't require concentration.""",
)

Blight: Spell = Spell(
    name="Blight",
    level=4,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=True,
    save=AbilityScore.CON,
    description="""Necromantic energy washes over a creature of your choice that you can see within range, draining moisture and vitality from it. The target must make a Constitution saving throw. The target takes 8d8 necrotic damage on a failed save, or half as much damage on a successful one. This spell has no effect on undead or constructs.""",
    upcast_description="""When you cast this spell using a spell slot of 5th level or higher, the damage increases by 1d8 for each slot level above 4th.""",
)


BlindnessDeafness: Spell = Spell(
    name="Blindness/Deafness",
    level=2,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.CON,
    upcast=True,
    description="You can blind or deafen a foe. Choose one creature that you can see within range to make a Constitution saving throw. If it fails, the target is either blinded or deafened (your choice) for the duration. At the end of each of its turns, the target can make a Constitution saving throw. On a success, the spell ends.",
    upcast_description="When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd.",
)

CircleOfDeath: Spell = Spell(
    name="Circle of Death",
    level=6,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=True,
    save=AbilityScore.CON,
    description="""A sphere of negative energy ripples out in a 60-foot-radius sphere from a point within range. Each creature in that area must make a Constitution saving throw. A target takes 8d6 necrotic damage on a failed save, or half as much damage on a successful one.""",
    upcast_description="""When you cast this spell using a spell slot of 7th level or higher, the damage increases by 2d6 for each slot level above 6th.""",
)

Contagion: Spell = Spell(
    name="Contagion",
    level=5,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    save=AbilityScore.CON,
    concentration=True,
    description="""
Your touch inflicts disease. Make a melee spell attack against a creature within your reach. On a hit, the target is poisoned.

At the end of each of the poisoned target’s turns, the target must make a Constitution saving throw. If the target succeeds on three of these saves, it is no longer poisoned, and the spell ends. If the target fails three of these saves, the target is no longer poisoned, but choose one of the diseases below. The target is subjected to the chosen disease for the spell’s duration.

Since this spell induces a natural disease in its target, any effect that removes a disease or otherwise ameliorates a disease’s effects apply to it.

Blinding Sickness. Pain grips the creature’s mind, and its eyes turn milky white. The creature has disadvantage on Wisdom checks and Wisdom saving throws and is blinded.

Filth Fever. A raging fever sweeps through the creature’s body. The creature has disadvantage on Strength checks, Strength saving throws, and attack rolls that use Strength.

Flesh Rot. The creature’s flesh decays. The creature has disadvantage on Charisma checks and vulnerability to all damage.

Mindfire. The creature’s mind becomes feverish. The creature has disadvantage on Intelligence checks and Intelligence saving throws, and the creature behaves as if under the effects of the confusion spell during combat.

Seizure. The creature is overcome with shaking. The creature has disadvantage on Dexterity checks, Dexterity saving throws, and attack rolls that use Dexterity.

Slimy Doom. The creature begins to bleed uncontrollably. The creature has disadvantage on Constitution checks and Constitution saving throws. In addition, whenever the creature takes damage, it is stunned until the end of its next turn.""",
)

Eyebite: Spell = Spell(
    name="Eyebite",
    level=6,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.WIS,
    upcast=False,
    concentration=True,
    description="""For the spell's duration, your eyes become an inky void imbued with dread power. One creature of your choice within 60 feet of you that you can see must succeed on a Wisdom saving throw or be affected by one of the following effects of your choice for the duration. On each of your turns until the spell ends, you can use your action to target another creature but can't target a creature again if it has succeeded on a saving throw against this casting of eyebite.

Asleep. The target falls unconscious. It wakes up if it takes any damage or if another creature uses its action to shake the sleeper awake.

Panicked. The target is frightened of you. On each of its turns, the frightened creature must take the Dash action and move away from you by the safest and shortest available route, unless there is nowhere to move. If the target moves to a place at least 60 feet away from you where it can no longer see you, this effect ends.

Sickened. The target has disadvantage on attack rolls and ability checks. At the end of each of its turns, it can make another Wisdom saving throw. If it succeeds, the effect ends.""",
)

FingerOfDeath: Spell = Spell(
    name="Finger of Death",
    level=7,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    save=AbilityScore.CON,
    description="""You send negative energy coursing through a creature that you can see within range, causing it searing pain. The target must make a Constitution saving throw. It takes 7d8 + 30 necrotic damage on a failed save, or half as much damage on a successful one.

A humanoid killed by this spell rises at the start of your next turn as a zombie that is permanently under your command, following your verbal orders to the best of its ability.""",
)

RaiseDead: Spell = Spell(
    name="Raise Dead",
    level=5,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=True,
    concentration=False,
    description="""You return a dead creature you touch to life, provided that it has been dead no longer than 10 days. If the creature's soul is both willing and at liberty to rejoin the body, the creature returns to life with 1 hit point.""",
)

Resurrection: Spell = Spell(
    name="Resurrection",
    level=7,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    concentration=False,
    description="""You touch a dead creature that has been dead for no more than a century, that didn't die of old age, and that isn't undead. If its soul is free and willing, the target returns to life with all its hit points.""",
)
