from ..features import ActionType
from ..skills import Stats
from .spell import Spell

ControlWeather = Spell(
    name="Control Weather",
    level=8,
    school="transmutation",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=None,
    description="""
    You take control of the weather within 5 miles of you for the duration. You must be outdoors to cast this spell. Moving to a place where you don’t have a clear path to the sky ends the spell early.

When you cast the spell, you change the current weather conditions, which are determined by the DM based on the climate and season. You can change precipitation, temperature, and wind. It takes 1d4 × 10 minutes for the new conditions to take effect. Once they do so, you can change the conditions again. When the spell ends, the weather gradually returns to normal.""",
)


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

SpikeGrowth: Spell = Spell(
    name="Spike Growth",
    level=2,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.DEX,
    upcast=False,
    concentration=True,
    description="""The ground in a 20-foot radius centered on a point within range twists and sprouts hard spikes and thorns. The area becomes difficult terrain for the duration. When a creature moves into or within the area, it takes 2d4 piercing damage for every 5 feet it travels.

The transformation of the ground is camouflaged to look natural. Any creature that can't see the area at the time the spell is cast must make a Wisdom (Perception) check against your spell save DC to recognize the terrain as hazardous before entering it.""",
)

Telekinesis: Spell = Spell(
    name="Telekinesis",
    level=5,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.STR,
    upcast=False,
    concentration=True,
    description="""
You gain the ability to move or manipulate creatures or objects by thought. When you cast the spell, and as your action each round for the duration, you can exert your will on one creature or object that you can see within range, causing the appropriate effect below. You can affect the same target round after round, or choose a new one at any time. If you switch targets, the prior target is no longer affected by the spell.

Creature. You can try to move a Huge or smaller creature. Make an ability check with your spellcasting ability contested by the creature's Strength check. If you win the contest, you move the creature up to 30 feet in any direction, including upward but not beyond the range of this spell. Until the end of your next turn, the creature is restrained in your telekinetic grip. A creature lifted upward is suspended in mid-air.

On subsequent rounds, you can use your action to attempt to maintain your telekinetic grip on the creature by repeating the contest.

Object. You can try to move an object that weighs up to 1,000 pounds. If the object isn't being worn or carried, you automatically move it up to 30 feet in any direction, but not beyond the range of this spell.

If the object is worn or carried by a creature, you must make an ability check with your spellcasting ability contested by that creature's Strength check. If you succeed, you pull the object away from that creature and can move it up to 30 feet in any direction but not beyond the range of this spell.

You can exert fine control on objects with your telekinetic grip, such as manipulating a simple tool, opening a door or a container, stowing or retrieving an item from an open container, or pouring the contents from a vial.""",
)
