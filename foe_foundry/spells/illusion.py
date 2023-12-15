from ..features import ActionType
from ..skills import Stats
from .spell import Spell

Fear: Spell = Spell(
    name="Fear",
    level=3,
    school="illusion",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=False,
    description="""You project a phantasmal image of a creature's worst fears. Each creature in a 30-foot cone must succeed on a Wisdom saving throw or drop whatever it is holding and become frightened for the duration.
While frightened by this spell, a creature must take the Dash action and move away from you by the safest available route on each of its turns, unless there is nowhere to move. If the creature ends its turn in a location where it doesn't have line of sight to you, the creature can make a Wisdom saving throw. On a successful save, the spell ends for that creature.""",
)


GreaterInvisibility: Spell = Spell(
    name="Greater Invisibility",
    level=4,
    school="illusion",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    description="You or a creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is invisible as long as it is on the target's person.",
    range="Touch",
)

HypnoticPattern: Spell = Spell(
    name="Hypnotic Pattern",
    level=3,
    school="illusion",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=False,
    concentration=True,
    description="""You create a twisting pattern of colors that weaves through the air inside a 30-foot cube within range. The pattern appears for a moment and vanishes. Each creature in the area who sees the pattern must make a Wisdom saving throw. On a failed save, the creature becomes charmed for the duration. While charmed by this spell, the creature is incapacitated and has a speed of 0.
The spell ends for an affected creature if it takes any damage or if someone else uses an action to shake the creature out of its stupor.""",
)

Invisibility: Spell = Spell(
    name="Invisibility",
    level=2,
    school="illusion",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=True,
    description="A creature you touch becomes invisible until the spell ends. Anything the target is wearing or carrying is invisible as long as it is on the target's person. The spell ends for a target that attacks or casts a spell.",
    upcast_description="When you cast this spell using a spell slot of 3rd level or higher, you can target one additional creature for each slot level above 2nd.",
    range="Touch",
)

Silence: Spell = Spell(
    name="Silence",
    level=2,
    school="illusion",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=False,
    concentration=True,
    description="For the duration, no sound can be created within or pass through a 20-foot-radius sphere centered on a point you choose within range. Any creature or object entirely inside the sphere is immune to thunder damage, and creatures are deafened while entirely inside it. Casting a spell that includes a verbal component is impossible there.",
    range="120 feet",
)
