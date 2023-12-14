from ..features import ActionType
from ..skills import Stats
from .spell import Spell

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
