from ..features import ActionType
from ..skills import Stats
from .spell import Spell

BlindnessDeafness: Spell = Spell(
    name="Blindness/Deafness",
    level=2,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.CON,
    upcast=True,
    description="You can blind or deafen a foe. Choose one creature that you can see within range to make a Constitution saving throw. If it fails, the target is either blinded or deafened (your choice) for the duration. At the end of each of its turns, the target can make a Constitution saving throw. On a success, the spell ends.",
    upcast_description="When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd.",
)

Eyebite: Spell = Spell(
    name="Eyebite",
    level=6,
    school="necromancy",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
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
    save=Stats.CON,
    description="""You send negative energy coursing through a creature that you can see within range, causing it searing pain. The target must make a Constitution saving throw. It takes 7d8 + 30 necrotic damage on a failed save, or half as much damage on a successful one.

A humanoid killed by this spell rises at the start of your next turn as a zombie that is permanently under your command, following your verbal orders to the best of its ability.""",
)
