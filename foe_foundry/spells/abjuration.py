from ..features import ActionType
from .spell import Spell

DispelMagic = Spell(
    name="Dispel Magic",
    level=3,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="Choose one creature, object, or magical effect within range. Any spell of 3rd level or lower on the target ends. For each spell of 4th level or higher on the target, make an ability check using your spellcasting ability. The DC equals 10 + the spell's level. On a successful check, the spell ends.",
    upcast_description="When you cast this spell using a spell slot of 4th level or higher, you automatically end the effects of a spell on the target if the spell's level is equal to or less than the level of the spell slot you used.",
    range="120 feet",
)

Banishment: Spell = Spell(
    name="Banishment",
    level=4,
    school="abjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=True,
    concentration=False,
    description="""You attempt to send one creature that you can see within range to another plane of existence. The target must succeed on a Charisma saving throw or be banished.""",
    upcast_description="""When you cast this spell using a spell slot of 5th level or higher, you can target one additional creature for each slot level above 4th.""",
)
