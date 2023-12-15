from ..features import ActionType
from ..skills import Stats
from .spell import Spell

BladeBarrier: Spell = Spell(
    name="Blade Barrier",
    level=6,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="""You create a vertical wall of whirling, razor-sharp blades made of magical energy. The wall appears within range and lasts for the duration. You can make a straight wall up to 100 feet long, 20 feet high, and 5 feet thick, or a ringed wall up to 60 feet in diameter, 20 feet high, and 5 feet thick. The wall provides three-quarters cover to creatures behind it, and its space is difficult terrain.
When a creature enters the wall's area for the first time on a turn or starts its turn there, the creature must make a Dexterity saving throw. On a failed save, the creature takes 6d10 slashing damage. On a successful save, the creature takes half as much damage.""",
    range="90 feet",
)


ChainLightning: Spell = Spell(
    name="Chain Lightning",
    level=6,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="""You create a bolt of lightning that arcs toward a target of your choice that you can see within range. Three bolts then leap from that target to as many as three other targets, each of which must be within 30 feet of the first target. A target can be a creature or an object and can be targeted by only one of the bolts.
A target must make a Dexterity saving throw. The target takes 10d8 lightning damage on a failed save, or half as much damage on a successful one.""",
    range="150 feet",
)

Darkness: Spell = Spell(
    name="Darkness",
    level=2,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=None,
    description="""Magical darkness spreads from a point you choose within range to fill a 15-foot-radius sphere for the duration. The darkness spreads around corners. A creature with darkvision can't see through this darkness, and nonmagical light can't illuminate it.
If the point you choose is on an object you are holding or one that isn't being worn or carried, the darkness emanates from the object and moves with it. Completely covering the source of the darkness with an opaque object, such as a bowl or a helm, blocks the darkness.
If any of this spell's area overlaps with an area of light created by a spell of 2nd level or lower, the spell that created the light is dispelled.""",
    range="60 feet",
)

FaerieFire: Spell = Spell(
    name="Faerie Fire",
    level=1,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="""Each object in a 20-foot cube within range is outlined in blue, green, or violet light (your choice). Any creature in the area when the spell is cast is also outlined in light if it fails a Dexterity saving throw. For the duration, objects and affected creatures shed dim light in a 10-foot radius.
Any attack roll against an affected creature or object has advantage if the attacker can see it, and the affected creature or object can't benefit from being invisible.""",
)

Fireball: Spell = Spell(
    name="Fireball",
    level=3,
    school="evocation",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="A bright streak flashes from your pointing finger to a point you choose within range then blossoms with a low roar into an explosion of flame. Each creature in a 20-foot-radius sphere centered on that point must make a Dexterity saving throw. A target takes 8d6 fire damage on a failed save, or half as much damage on a successful one.",
    upcast_description="When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.",
    range="150 feet",
)

FlameStrike: Spell = Spell(
    name="Flame Strike",
    level=5,
    school="evocation",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="""A vertical column of divine fire roars down from the heavens in a location you specify. Each creature in a 10-foot-radius, 40-foot-high cylinder centered on a point within range must make a Dexterity saving throw. A creature takes 4d6 fire damage and 4d6 radiant damage on a failed save, or half as much damage on a successful one.""",
    upcast_description="When you cast this spell using a spell slot of 6th level or higher, the fire damage or the radiant damage (your choice) increases by 1d6 for each slot level above 5th.",
    range="60 feet",
)

Forcecage: Spell = Spell(
    name="Forcecage",
    level=7,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""An immobile, invisible, cube-shaped prison composed of magical force springs into existence around an area you choose within range. The prison can be a cage or a solid box, as you choose.
A prison in the shape of a cage can be up to 20 feet on a side and is made from 1/2-inch diameter bars spaced 1/2 inch apart.
A prison in the shape of a box can be up to 10 feet on a side, creating a solid barrier that prevents any matter from passing through it and blocking any spells cast into or out from the area.
When you cast the spell, any creature that is completely inside the cage's area is trapped. Creatures only partially within the area, or those too large to fit inside the area, are pushed away from the center of the area until they are completely outside the area.
A creature inside the cage can't leave it by nonmagical means. If the creature tries to use teleportation or interplanar travel to leave the cage, it must first make a Charisma saving throw. On a success, the creature can use that magic to exit the cage. On a failure, the creature can't exit the cage and wastes the use of the spell or effect. The cage also extends into the Ethereal Plane, blocking ethereal travel.
This spell can't be dispelled by dispel magic.""",
    range="100 feet",
)

GustOfWind: Spell = Spell(
    name="Gust of Wind",
    level=2,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=Stats.STR,
    description="""
    A line of strong wind 60 feet long and 10 feet wide blasts from you in a direction you choose for the spell's duration. Each creature that starts its turn in the line must succeed on a Strength saving throw or be pushed 15 feet away from you in a direction following the line.
    Any creature in the line must spend 2 feet of movement for every 1 foot it moves when moving closer to you.
    The gust disperses gas or vapor, and it extinguishes candles, torches, and similar unprotected flames in the area. It causes protected flames, such as those of lanterns, to dance wildly and has a 50 percent chance to extinguish them.
    As a bonus action on each of your turns before the spell ends, you can change the direction in which the line blasts from you.
    """,
    range="Self (60-foot line)",
)

LightningBolt: Spell = Spell(
    name="Lightning Bolt",
    level=3,
    school="evocation",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="A stroke of lightning forming a line 100 feet long and 5 feet wide blasts out from you in a direction you choose. Each creature in the line must make a Dexterity saving throw. A creature takes 8d6 lightning damage on a failed save, or half as much damage on a successful one.",
    upcast_description="When you cast this spell using a spell slot of 4th level or higher, the damage increases by 1d6 for each slot level above 3rd.",
    range="Self (100-foot line)",
)

MassCureWounds: Spell = Spell(
    name="Mass Cure Wounds",
    level=5,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""A wave of healing energy washes out from a point of your choice within range. Choose up to six creatures in a 30-foot-radius sphere centered on that point. Each target regains hit points equal to 3d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.""",
    range="60 feet",
)

WallOfFire: Spell = Spell(
    name="Wall of Fire",
    level=4,
    school="evocation",
    source="SRD 5.1",
    upcast=True,
    concentration=True,
    action_type=ActionType.Action,
    save=Stats.DEX,
    description="""
    You create a wall of fire on a solid surface within range. You can make the wall up to 60 feet long, 20 feet high, and 1 foot thick, or a ringed wall up to 20 feet in diameter, 20 feet high, and 1 foot thick. The wall is opaque and lasts for the duration.

When the wall appears, each creature within its area must make a Dexterity saving throw. On a failed save, a creature takes 5d8 fire damage, or half as much damage on a successful save.

One side of the wall, selected by you when you cast this spell, deals 5d8 fire damage to each creature that ends its turn within 10 feet of that side or inside the wall. A creature takes the same damage when it enters the wall for the first time on a turn or ends its turn there. The other side of the wall deals no damage.""",
    upcast_description="When you cast this spell using a spell slot of 5th level or higher, the damage increases by 1d6 for each slot level above 4th.",
    range="120 feet",
)

WallOfForce: Spell = Spell(
    name="Wall of Force",
    level=5,
    school="evocation",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""An invisible wall of force springs into existence at a point you choose within range. The wall appears in any orientation you choose, as a horizontal or vertical barrier or at an angle. It can be free floating or resting on a solid surface. You can form it into a hemispherical dome or a sphere with a radius of up to 10 feet, or you can shape a flat surface made up of ten 10-foot-by-10-foot panels. Each panel must be contiguous with another panel. In any form, the wall is 1/4 inch thick. It lasts for the duration. If the wall cuts through a creature's space when it appears, the creature is pushed to one side of the wall (your choice which side).
Nothing can physically pass through the wall. It is immune to all damage and can't be dispelled by dispel magic. A disintegrate spell destroys the wall instantly, however. The wall also extends into the Ethereal Plane, blocking ethereal travel through the wall.""",
)
