from ..features import ActionType
from ..skills import Stats
from .spell import Spell

Disintegrate = Spell(
    name="Disintegrate",
    level=6,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=True,
    save=Stats.DEX,
    description="""A thin green ray springs from your pointing finger to a target that you can see within range. The target can be a creature, an object, or a creation of magical force, such as the wall created by wall of force.

A creature targeted by this spell must make a Dexterity saving throw. On a failed save, the target takes 10d6 + 40 force damage. The target is disintegrated if this damage leaves it with 0 hit points.

A disintegrated creature and everything it is wearing and carrying, except magic items, are reduced to a pile of fine gray dust. The creature can be restored to life only by means of a true resurrection or a wish spell.

This spell automatically disintegrates a Large or smaller nonmagical object or a creation of magical force. If the target is a Huge or larger object or creation of force, this spell disintegrates a 10-foot- cube portion of it. A magic item is unaffected by this spell.""",
    upcast_description="""When you cast this spell using a spell slot of 7th level or higher, the damage increases by 3d6 for each slot level above 6th.""",
)


Fly = Spell(
    name="Fly",
    level=3,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="You touch a willing creature. \
        The target gains a flying speed of 60 feet for the duration. \
        When the spell ends, the target falls if it is still aloft, unless it can stop the fall.",
)

Levitate = Spell(
    name="Levitate",
    level=2,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""One creature or loose object of your choice that you can see within range rises vertically, up to 20 feet, and remains suspended there for the duration. The spell can levitate a target that weighs up to 500 pounds. An unwilling creature that succeeds on a Constitution saving throw is unaffected.

The target can move only by pushing or pulling against a fixed object or surface within reach (such as a wall or a ceiling), which allows it to move as if it were climbing. You can change the target's altitude by up to 20 feet in either direction on your turn. If you are the target, you can move up or down as part of your move. Otherwise, you can use your action to move the target, which must remain within the spell's range.

When the spell ends, the target floats gently to the ground if it is still aloft.""",
)

Slow: Spell = Spell(
    name="Slow",
    level=3,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=False,
    concentration=True,
    description="""You alter time around up to six creatures of your choice in a 40-foot cube within range. Each target must succeed on a Wisdom saving throw or be affected by this spell for the duration.

An affected target's speed is halved, it takes a −2 penalty to AC and Dexterity saving throws, and it can't use reactions. On its turn, it can use either an action or a bonus action, not both. Regardless of the creature's abilities or magic items, it can't make more than one melee or ranged attack during its turn.

If the creature attempts to cast a spell with a casting time of 1 action, roll a d20. On an 11 or higher, the spell doesn't take effect until the creature's next turn, and the creature must use its action on that turn to complete the spell. If it can't, the spell is wasted.

A creature affected by this spell makes another Wisdom saving throw at the end of each of its turns. On a successful save, the effect ends for it.""",
)
