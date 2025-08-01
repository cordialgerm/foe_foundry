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

PrismaticWall = Spell(
    name="Prismatic Wall",
    level=9,
    school="abjuration",
    source="SRD 5.1",
    upcast=False,
    concentration=True,
    action_type=ActionType.Action,
    save=None,
    description="""A shimmering, multicolored plane of light forms a vertical opaque wall—up to 90 feet long, 30 feet high, and 1 inch thick—centered on a point you can see within range. Alternatively, you can shape the wall into a sphere up to 30 feet in diameter centered on a point you choose within range. The wall remains in place for the duration. If you position the wall so that it passes through a space occupied by a creature, the spell fails, and your action and the spell slot are wasted.\n\nThe wall sheds bright light out to a range of 100 feet and dim light for an additional 100 feet. You and creatures you designate at the time you cast the spell can pass through and remain near the wall without harm. If another creature that can see the wall moves to within 20 feet of it or starts its turn there, the creature must succeed on a Constitution saving throw or become blinded for 1 minute.\n\nThe wall consists of seven layers, each with a different color. When a creature attempts to reach into or pass through the wall, it does so one layer at a time through all the wall's layers. As it passes or reaches through each layer, the creature must make a Dexterity saving throw or be affected by that layer's properties as described below.\n\nThe wall can be destroyed, also one layer at a time, in order from red to violet, by means specific to each layer. Once a layer is destroyed, it remains so for the duration of the spell. An antimagic field has no effect on it.\n\n- Red. The creature takes 10d6 fire damage on a failed save, or half as much damage on a successful one. While this layer is in place, nonmagical ranged attacks can't pass through the wall. The layer can be destroyed by dealing at least 25 cold damage to it.\n- Orange. The creature takes 10d6 acid damage on a failed save, or half as much damage on a successful one. While this layer is in place, magical ranged attacks can't pass through the wall. The layer is destroyed by a strong wind.\n- Yellow. The creature takes 10d6 lightning damage on a failed save, or half as much damage on a successful one. This layer can be destroyed by dealing at least 60 force damage to it.\n- Green. The creature takes 10d6 poison damage on a failed save, or half as much damage on a successful one. A passwall spell, or another spell of equal or greater level that can open a portal on a solid surface, destroys this layer.\n- Blue. The creature takes 10d6 cold damage on a failed save, or half as much damage on a successful one. This layer can be destroyed by dealing at least 25 fire damage to it.\n- Indigo. On a failed save, the creature is restrained. It must then make a Constitution saving throw at the end of each of its turns. If it successfully saves three times, the spell ends. If it fails its save three times, it permanently turns to stone and is subjected to the petrified condition. The successes and failures don't need to be consecutive; keep track of both until the creature collects three of a kind. While this layer is in place, spells can't be cast through the wall. The layer is destroyed by bright light shed by a daylight spell or a similar spell of equal or higher level.\n- Violet. On a failed save, the creature is blinded. It must then make a Wisdom saving throw at the start of your next turn. A successful save ends the blindness. If it fails that save, the creature is transported to another plane of the GM's choosing and is no longer blinded. (Typically, a creature that is on a plane that isn't its home plane is banished home, while other creatures are usually cast into the Astral or Ethereal planes.) This layer is destroyed by a dispel magic spell or a similar spell of equal or higher level that can end spells and magical effects.""",
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
    description="""Choose one creature, object, or magical effect within range. Any spell of 3rd level or lower on the target ends. For each spell of 4th level or higher on the target, make an ability check using your spellcasting ability. The DC equals 10 + the spell's level. On a successful check, the spell ends.""",
    upcast_description="""When you cast this spell using a spell slot of 4th level or higher, you automatically end the effects of a spell on the target if the spell's level is equal to or less than the level of the spell slot you used.""",
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
    description="""An immobile, faintly shimmering barrier springs into existence in a 10-foot radius around you and remains for the duration.\n\nAny spell of 5th level or lower cast from outside the barrier can't affect creatures or objects within it, even if the spell is cast using a higher level spell slot. Such a spell can target creatures and objects within the barrier, but the spell has no effect on them. Similarly, the area within the barrier is excluded from the areas affected by such spells.""",
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
    description="""You imbue a creature you touch with positive energy to undo a debilitating effect. You can reduce the target's exhaustion level by one, or end one of the following effects on the target:\n\n- One effect that charmed or petrified the target\n- One curse, including the target's attunement to a cursed magic item\n- Any reduction to one of the target's ability scores\n- One effect reducing the target's hit point maximum""",
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

MassCureWounds: Spell = Spell(
    name="Mass Cure Wounds",
    level=5,
    school="abjuration",
    source="SRD 5.1",
    upcast=False,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""A wave of healing energy washes out from a point of your choice within range. Choose up to six creatures in a 30-foot radius sphere centered on that point. Each target regains hit points equal to 3d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.""",
    range="60 feet",
)

CureWounds: Spell = Spell(
    name="Cure Wounds",
    level=1,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""A creature you touch regains a number of hit points equal to 1d8 + your spellcasting ability modifier. This spell has no effect on undead or constructs.""",
    range="Touch",
)

HealingWord: Spell = Spell(
    name="Healing Word",
    level=1,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.BonusAction,
    save=None,
    description="""A creature of your choice that you can see within range regains hit points equal to 1d4 + your spellcasting ability modifier. This spell has no effect on undead or constructs.""",
    range="60 feet",
)

Heal: Spell = Spell(
    name="Heal",
    level=6,
    school="abjuration",
    source="SRD 5.1",
    upcast=True,
    concentration=False,
    action_type=ActionType.Action,
    save=None,
    description="""Choose a creature that you can see within range. A surge of positive energy washes through the creature, causing it to regain 70 hit points. This spell also ends blindness, deafness, and any diseases affecting the target. This spell has no effect on constructs or undead.""",
    range="60 feet",
)
