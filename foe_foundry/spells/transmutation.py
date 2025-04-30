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

PlantGrowth = Spell(
    name="Plant Growth",
    level=3,
    school="transmutation",
    source="SRD 5.1",
    upcast=False,
    action_type=ActionType.Action,
    concentration=False,
    description="""You enrich the land around you with abundant plant life. Choose a point within range. All normal plants in a 100-foot radius centered on that point become thick and overgrown. The area becomes difficult terrain for the duration.
If you cast this spell using 8 hours of casting time, you enrich the land. The plants in a half-mile radius centered on that point become enriched for 1 year. The enriched area is difficult terrain for creatures other than you. If the area is used to grow food, it produces twice the normal amount of food when harvested.

If you cast this spell using 1 minute of casting time, you can choose to have the spell affect only one of the following areas:
- 20-foot radius centered on a point within range
- 40-foot radius centered on a point within range
- 100-foot radius centered on a point within range
- 1 mile radius centered on a point within range
The area becomes difficult terrain for the duration. If the area is used to grow food, it produces twice the normal amount of food when harvested.""",
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

EnlargeReduce = Spell(
    name="Enlarge/Reduce",
    level=2,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    upcast=False,
    save=Stats.CON,
    description="""You cause a creature or an object you can see within range to grow larger or smaller for the duration. Choose either a creature or an object that is neither worn nor carried. If the target is unwilling, it can make a Constitution saving throw. On a success, the spell has no effect.

If the target is a creature, everything it is wearing and carrying changes size with it. Any item dropped by an affected creature returns to normal size at once.

Enlarge. The target's size doubles in all dimensions, and its weight is multiplied by eight. This growth increases its size by one category-- from Medium to Large, for example. If there isn't enough room for the target to double its size, the creature or object attains the maximum possible size in the space available. Until the spell ends, the target also has advantage on Strength checks and Strength saving throws. The target's weapons also grow to match its new size. While these weapons are enlarged, the target's attacks with them deal 1d4 extra damage.

Reduce. The target's size is halved in all dimensions, and its weight is reduced to one-eighth of normal. This reduction decreases its size by one category--from Medium to Small, for example. Until the spell ends, the target also has disadvantage on Strength checks and Strength saving throws. The target's weapons also shrink to match its new size. While these weapons are reduced, the target's attacks with them deal 1d4 less damage (this can't reduce the damage below 1).""",
)

FleshToStone = Spell(
    name="Flesh to Stone",
    level=6,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    save=Stats.CON,
    concentration=True,
    description="""
    You attempt to turn one creature that you can see within range into stone. If the target's body is made of flesh, the creature must make a Constitution saving throw. On a failed save, it is restrained as its flesh begins to harden. On a successful save, the creature isn't affected.

A creature restrained by this spell must make another Constitution saving throw at the end of each of its turns. If it successfully saves against this spell three times, the spell ends. If it fails its saves three times, it is turned to stone and subjected to the petrified condition for the duration. The successes and failures don't need to be consecutive; keep track of both until the target collects three of a kind.

If the creature is physically broken while petrified, it suffers from similar deformities if it reverts to its original state.

If you maintain your concentration on this spell for the entire possible duration, the creature is turned to stone until the effect is removed.""",
)


Fly = Spell(
    name="Fly",
    level=3,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
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

ReverseGravity: Spell = Spell(
    name="Reverse Gravity",
    level=7,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    concentration=True,
    description="""This spell reverses gravity in a 50-foot-radius, 100- foot high cylinder centered on a point within range. All creatures and objects that aren't somehow anchored to the ground in the area fall upward and reach the top of the area when you cast this spell. A creature can make a Dexterity saving throw to grab onto a fixed object it can reach, thus avoiding the fall.

If some solid object (such as a ceiling) is encountered in this fall, falling objects and creatures strike it just as they would during a normal downward fall. If an object or creature reaches the top of the area without striking anything, it remains there, oscillating slightly, for the duration.

At the end of the duration, affected objects and creatures fall back down.""",
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

TimeStop: Spell = Spell(
    name="Time Stop",
    level=9,
    school="transmutation",
    source="SRD 5.1",
    action_type=ActionType.Action,
    upcast=False,
    concentration=False,
    description="""You briefly stop the flow of time for everyone but yourself. No time passes for other creatures, while you take 1d4 + 1 turns in a row, during which you can use actions and move as normal.

This spell ends if one of the actions you use during this period, or any effects that you create during this period, affects a creature other than you or an object being worn or carried by someone other than you. In addition, the spell ends if you move to a place more than 1,000 feet from the location where you cast it.
    """,
)
