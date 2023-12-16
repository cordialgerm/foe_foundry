from ..features import ActionType
from .spell import Spell

Banishment: Spell = Spell(
    name="Banishment",
    level=4,
    school="abjuration",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    upcast=True,
    concentration=True,
    description="""You attempt to send one creature that you can see within range to another plane of existence. The target must succeed on a Charisma saving throw or be banished.""",
    upcast_description="""When you cast this spell using a spell slot of 5th level or higher, you can target one additional creature for each slot level above 4th.""",
)

DispelEvilAndGood = Spell(
    name="Dispel Evil and Good",
    level=5,
    school="abjuration",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=None,
    description="""
Shimmering energy surrounds and protects you from fey, undead, and creatures originating from beyond the Material Plane. For the duration, celestials, elementals, fey, fiends, and undead have disadvantage on attack rolls against you.

You can end the spell early by using either of the following special functions.

Break Enchantment. As your action, you touch a creature you can reach that is charmed, frightened, or possessed by a celestial, an elemental, a fey, a fiend, or an undead. The creature you touch is no longer charmed, frightened, or possessed by such creatures.

Dismissal. As your action, make a melee spell attack against a celestial, an elemental, a fey, a fiend, or an undead you can reach. On a hit, you attempt to drive the creature back to its home plane. The creature must succeed on a Charisma saving throw or be sent back to its home plane (if it isn't there already). If they aren't on their home plane, undead are sent to the Shadowfell, and fey are sent to the Feywild.""",
)

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

GlobeOfInvulnerability = Spell(
    name="Globe of Invulnerability",
    level=6,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=True,
    action_type=ActionType.Action,
    save=None,
    description="""An immobile, faintly shimmering barrier springs into existence in a 10-foot radius around you and remains for the duration.

Any spell of 5th level or lower cast from outside the barrier can't affect creatures or objects within it, even if the spell is cast using a higher level spell slot. Such a spell can target creatures and objects within the barrier, but the spell has no effect on them. Similarly, the area within the barrier is excluded from the areas affected by such spells.""
""",
    upcast_description="""When you cast this spell using a spell slot of 7th level or higher, the barrier blocks spells of one level higher for each slot level above 6th.""",
)

GreaterRestoration = Spell(
    name="Greater Restoration",
    level=5,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""
    You imbue a creature you touch with positive energy to undo a debilitating effect. You can reduce the target's exhaustion level by one, or end one of the following effects on the target:

One effect that charmed or petrified the target
One curse, including the target's attunement to a cursed magic item
Any reduction to one of the target's ability scores
One effect reducing the target's hit point maximum
""",
)

LesserRestoration = Spell(
    name="Lesser Restoration",
    level=2,
    school="abjuration",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="You touch a creature and can end either one disease or one condition afflicting it. The condition can be blinded, deafened, paralyzed, or poisoned.",
)
