from ..features import ActionType
from ..skills import AbilityScore
from .spell import Spell

Cloudkill = Spell(
    name="Cloudkill",
    level=5,
    school="conjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=True,
    action_type=ActionType.Action,
    save=AbilityScore.CON,
    description="""You create a 20-foot radius sphere of poisonous, yellow-green fog centered on a point you choose within range. The fog spreads around corners. It lasts for the duration or until strong wind disperses the fog, ending the spell. Its area is heavily obscured.\n\nWhen a creature enters the spell's area for the first time on a turn or starts its turn there, that creature must make a Constitution saving throw. The creature takes 5d8 poison damage on a failed save, or half as much damage on a successful one. Creatures are affected even if they hold their breath or don't need to breathe.\n\nThe fog moves 10 feet away from you at the start of each of your turns, rolling along the surface of the ground. The vapors, being heavier than air, sink to the lowest level of the land, even pouring down openings.""",
    upcast_description="""When you cast this spell using a spell slot of 6th level or higher, the damage increases by 1d8 for each slot level above 5th.""",
)

Wish: Spell = Spell(
    name="Wish",
    level=9,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=False,
    concentration=False,
    description="""Wish is the mightiest spell a mortal creature can cast. By simply speaking aloud, you can alter the very foundations of reality in accord with your desires.\n\nThe basic use of this spell is to duplicate any other spell of 8th level or lower. You don't need to meet any requirements in that spell, including costly components. The spell simply takes effect.\n\nAlternatively, you can create one of the following effects of your choice:\n- You create one object of up to 25,000 gp in value that isn't a magic item. The object can be no more than 300 feet in any dimension, and it appears in an unoccupied space you can see on the ground.\n- You allow up to twenty creatures that you can see to regain all hit points, and you end all effects on them described in the greater restoration spell.\n- You grant up to ten creatures that you can see resistance to a damage type you choose.\n- You grant up to ten creatures you can see immunity to a single spell or other magical effect for 8 hours. For instance, you could make yourself and all your companions immune to a lich's life drain attack.\n- You undo a single recent event by forcing a reroll of any roll made within the last round (including your last turn). Reality reshapes itself to accommodate the new result. For example, a wish spell could undo an opponent's successful save, a foe's critical hit, or a friend's failed save. You can force the reroll to be made with advantage or disadvantage, and you can choose whether to use the reroll or the original roll.\n\nYou might be able to achieve something beyond the scope of the above examples. State your wish to the GM as precisely as possible. The GM has great latitude in ruling what occurs in such an instance; the greater the wish, the greater the likelihood that something goes wrong. This spell might simply fail, the effect you desire might only be partly achieved, or you might suffer some unforeseen consequence as a result of how you worded the wish. For example, wishing that a villain were dead might propel you forward in time to a period when that villain is no longer alive, effectively removing you from the game. Similarly, wishing for a legendary magic item or artifact might instantly transport you to the presence of the item's current owner.\n\nThe stress of casting this spell to produce any effect other than duplicating another spell weakens you. After enduring that stress, each time you cast a spell until you finish a long rest, you take 1d10 necrotic damage per level of that spell. This damage can't be reduced or prevented in any way. In addition, your Strength drops to 3, if it isn't 3 or lower already, for 2d4 days. For each of those days that you spend resting and doing nothing more than light activity, your remaining recovery time decreases by 2 days. Finally, there is a 33 percent chance that you are unable to cast wish ever again if you suffer this stress.""",
)


Entangle: Spell = Spell(
    name="Entangle",
    level=1,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.STR,
    upcast=False,
    concentration=True,
    description="""Grasping weeds and vines sprout from the ground in a 20-foot square starting from a point within range. For the duration, these plants turn the ground in the area into difficult terrain.\n\nA creature in the area when you cast the spell must succeed on a Strength saving throw or be restrained by the entangling plants until the spell ends. A creature restrained by the plants can use its action to make a Strength check against your spell save DC. On a success, it frees itself.\n\nWhen the spell ends, the conjured plants wilt away.""",
    range="90 feet",
)

FogCloud: Spell = Spell(
    name="Fog Cloud",
    level=1,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=True,
    concentration=True,
    description="""You create a 20-foot radius sphere of fog centered on a point within range. The sphere spreads around corners, and its area is heavily obscured. It lasts for the duration or until a wind of moderate or greater speed (at least 10 miles per hour) disperses it.""",
    range="120 feet",
    upcast_description="""When you cast this spell using a spell slot of 2nd level or higher, the radius of the fog increases by 20 feet for each slot level above 1st.""",
)

Gate: Spell = Spell(
    name="Gate",
    level=9,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=False,
    concentration=True,
    description="""You conjure a portal linking an unoccupied space you can see within range to a precise location on a different plane of existence. The portal is a circular opening, which you can make 5 to 20 feet in diameter. You can orient the portal in any direction you choose. The portal lasts for the duration.\n\nThe portal has a front and a back on each plane where it appears. Travel through the portal is possible only by moving through its front. Anything that does so is instantly transported to the other plane, appearing in the unoccupied space nearest to the portal.\n\nDeities and other planar rulers can prevent portals created by this spell from opening in their presence or anywhere within their domains.\n\nWhen you cast this spell, you can speak the name of a specific creature (a pseudonym, title, or nickname doesn't work). If that creature is on a plane other than the one you are on, the portal opens in the named creature's immediate vicinity and draws the creature through it to the nearest unoccupied space on your side of the portal. You gain no special power over the creature, and it is free to act as the GM deems appropriate. It might leave, attack you, or help you.""",
)

Grease: Spell = Spell(
    name="Grease",
    level=1,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.DEX,
    upcast=False,
    concentration=False,
    description="""Slick grease covers the ground in a 10-foot square centered on a point within range and turns it into difficult terrain for the duration.\n\nWhen the grease appears, each creature standing in its area must succeed on a Dexterity saving throw or fall prone. A creature that enters the area or ends its turn there must also succeed on a Dexterity saving throw or fall prone.""",
    range="60 feet",
)
Teleport: Spell = Spell(
    name="Teleport",
    level=7,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=False,
    concentration=False,
    description="""This spell instantly transports you and up to eight willing creatures of your choice that you can see within range, or a single object that you can see within range, to a destination you select. If you target an object, it must be able to fit entirely inside a 10-foot cube, and it can't be held or carried by an unwilling creature.\n\nThe destination you choose must be known to you, and it must be on the same plane of existence as you. Your familiarity with the destination determines whether you arrive there successfully. The GM rolls d100 and consults the table.\n\nTable- Teleport Familiarity\n\n| Familiarity       | Mishap | Similar Area | Off Target | On Target |\n|-------------------|--------|--------------|------------|-----------|\n| Permanent circle  | -      | -            | -          | 01-100    |\n| Associated object | -      | -            | -          | 01-100    |\n| Very familiar     | 01-05  | 06-13        | 14-24      | 25-100    |\n| Seen casually     | 01-33  | 34-43        | 44-53      | 54-100    |\n| Viewed once       | 01-43  | 44-53        | 54-73      | 74-100    |\n| Description       | 01-43  | 44-53        | 54-73      | 74-100    |\n| False destination | 01-50  | 51-100       | -          | -         |\n|                   |        |              |            |           |\n\nFamiliarity. "Permanent circle" means a permanent teleportation circle whose sigil sequence you know. "Associated object" means that you possess an object taken from the desired destination within the last six months, such as a book from a wizard's library, bed linen from a royal suite, or a chunk of marble from a lich's secret tomb.\n\n"Very familiar" is a place you have been very often, a place you have carefully studied, or a place you can see when you cast the spell. "Seen casually" is someplace you have seen more than once but with which you aren't very familiar. "Viewed once" is a place you have seen once, possibly using magic. "Description" is a place whose location and appearance you know through someone else's description, perhaps from a map.\n\n"False destination" is a place that doesn't exist. Perhaps you tried to scry an enemy's sanctum but instead viewed an illusion, or you are attempting to teleport to a familiar location that no longer exists.\n\nOn Target. You and your group (or the target object) appear where you want to.\n\nOff Target. You and your group (or the target object) appear a random distance away from the destination in a random direction. Distance off target is 1d10 × 1d10 percent of the distance that was to be traveled. For example, if you tried to travel 120 miles, landed off target, and rolled a 5 and 3 on the two d10s, then you would be off target by 15 percent, or 18 miles. The GM determines the direction off target randomly by rolling a d8 and designating 1 as north, 2 as northeast, 3 as east, and so on around the points of the compass. If you were teleporting to a coastal city and wound up 18 miles out at sea, you could be in trouble.\n\nSimilar Area. You and your group (or the target object) wind up in a different area that's visually or thematically similar to the target area. If you are heading for your home laboratory, for example, you might wind up in another wizard's laboratory or in an alchemical supply shop that has many of the same tools and implements as your laboratory. Generally, you appear in the closest similar place, but since the spell has no range limit, you could conceivably wind up anywhere on the plane.\n\nMishap. The spell's unpredictable magic results in a difficult journey. Each teleporting creature (or the target object) takes 3d10 force damage, and the GM rerolls on the table to see where you wind up (multiple mishaps can occur, dealing damage each time).""",
    range="10 feet",
)

Maze: Spell = Spell(
    name="Maze",
    level=8,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.INT,
    upcast=False,
    description="""You banish a creature that you can see within range into a labyrinthine demiplane. The target remains there for the duration or until it escapes the maze.\n\nThe target can use its action to attempt to escape. When it does so, it makes a DC 20 Intelligence check. If it succeeds, it escapes, and the spell ends (a minotaur or goristro demon automatically succeeds).\n\nWhen the spell ends, the target reappears in the space it left or, if that space is occupied, in the nearest unoccupied space.""",
)

SleetStorm: Spell = Spell(
    name="Sleet Storm",
    level=3,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.DEX,
    upcast=False,
    concentration=True,
    description="""Until the spell ends, freezing rain and sleet fall in a 20-foot tall cylinder with a 40-foot radius centered on a point you choose within range. The area is heavily obscured, and exposed flames in the area are doused.\n\nThe ground in the area is covered with slick ice, making it difficult terrain. When a creature enters the spell's area for the first time on a turn or starts its turn there, it must make a Dexterity saving throw. On a failed save, it falls prone.\n\nIf a creature starts its turn in the spell's area and is concentrating on a spell, the creature must make a successful Constitution saving throw against your spell save DC or lose concentration.""",
    range="150 feet",
)

Web: Spell = Spell(
    name="Web",
    level=2,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.DEX,
    upcast=False,
    concentration=True,
    description="""You conjure a mass of thick, sticky webbing at a point of your choice within range. The webs fill a 20-foot cube from that point for the duration. The webs are difficult terrain and lightly obscure their area.\n\nIf the webs aren't anchored between two solid masses (such as walls or trees) or layered across a floor, wall, or ceiling, the conjured web collapses on itself, and the spell ends at the start of your next turn. Webs layered over a flat surface have a depth of 5 feet.\n\nEach creature that starts its turn in the webs or that enters them during its turn must make a Dexterity saving throw. On a failed save, the creature is restrained as long as it remains in the webs or until it breaks free.\n\nA creature restrained by the webs can use its action to make a Strength check against your spell save DC. If it succeeds, it is no longer restrained.\n\nThe webs are flammable. Any 5-foot cube of webs exposed to fire burns away in 1 round, dealing 2d4 fire damage to any creature that starts its turn in the fire.""",
    range="60 feet",
)

CallLightning: Spell = Spell(
    name="Call Lightning",
    level=3,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=AbilityScore.DEX,
    upcast=True,
    concentration=True,
    description="""A storm cloud appears in the shape of a cylinder that is 10 feet tall with a 60-foot radius, centered on a point you can see within range directly above you. The spell fails if you can't see a point in the air where the storm cloud could appear (for example, if you are in a room that can't accommodate the cloud).\n\nWhen you cast the spell, choose a point you can see under the cloud. A bolt of lightning flashes down from the cloud to that point. Each creature within 5 feet of that point must make a Dexterity saving throw. A creature takes 3d10 lightning damage on a failed save, or half as much damage on a successful one. On each of your turns until the spell ends, you can use your action to call down lightning in this way again, targeting the same point or a different one.\n\nIf you are outdoors in stormy conditions when you cast this spell, the spell gives you control over the existing storm instead of creating a new one. Under such conditions, the spell's damage increases by 1d10.\n\nWhen you cast this spell using a spell slot of 4th or higher level, the damage increases by 1d10 for each slot level above 3rd.""",
    range="120 feet",
)
