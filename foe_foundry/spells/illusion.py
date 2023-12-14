from ..features import ActionType
from ..skills import Stats
from .spell import Spell

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
