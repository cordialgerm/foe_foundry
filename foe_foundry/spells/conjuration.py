from ..features import ActionType
from ..skills import Stats
from .spell import Spell

Entangle: Spell = Spell(
    name="Entangle",
    level=1,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.STR,
    upcast=False,
    concentration=True,
    description="Grasping weeds and vines sprout from the ground in a 20-foot square starting from a point within range. For the duration, these plants turn the ground in the area into difficult terrain. A creature in the area when you cast the spell must succeed on a Strength saving throw or be restrained by the entangling plants until the spell ends. A creature restrained by the plants can use its action to make a Strength check against your spell save DC. On a success, it frees itself.",
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
    description="You create a 20-foot-radius sphere of fog centered on a point within range. The sphere spreads around corners, and its area is heavily obscured. It lasts for the duration or until a wind of moderate or greater speed (at least 10 miles per hour) disperses it.",
    range="120 feet",
    upcast_description="When you cast this spell using a spell slot of 2nd level or higher, the radius of the fog increases by 20 feet for each slot level above 1st.",
)

Grease: Spell = Spell(
    name="Grease",
    level=1,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.DEX,
    upcast=False,
    concentration=False,
    description="Slick grease covers the ground in a 10-foot square centered on a point within range and turns it into difficult terrain for the duration. When the grease appears, each creature standing in its area must succeed on a Dexterity saving throw or fall prone. A creature that enters the area or ends its turn there must also succeed on a Dexterity saving throw or fall prone.",
    range="60 feet",
)

Maze: Spell = Spell(
    name="Maze",
    level=8,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.INT,
    upcast=False,
    description="You banish a creature that you can see within range into a labyrinthine demiplane. The target remains there for the duration or until it escapes the maze. The target can use its action to attempt to escape. When it does so, it makes a DC 20 Intelligence check. If it succeeds, it escapes, and the spell ends (a minotaur or goristro demon automatically succeeds). When the spell ends, the target reappears in the space it left or, if that space is occupied, in the nearest unoccupied space.",
)

SleetStorm: Spell = Spell(
    name="Sleet Storm",
    level=3,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.DEX,
    upcast=False,
    concentration=True,
    description="Until the spell ends, freezing rain and sleet fall in a 20-foot-tall cylinder with a 40-foot radius centered on a point you choose within range. The area is heavily obscured, and exposed flames in the area are doused.",
    range="150 feet",
)

Web: Spell = Spell(
    name="Web",
    level=2,
    school="conjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.DEX,
    upcast=False,
    concentration=True,
    description="You conjure a mass of thick, sticky webbing at a point of your choice within range. The webs fill a 20-foot cube from that point for the duration. The webs are difficult terrain and lightly obscure their area.",
    range="60 feet",
)
