from ..features import ActionType
from ..skills import Stats
from .spell import Spell

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
