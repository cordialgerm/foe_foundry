from ..features import ActionType
from .spell import Spell

Commune = Spell(
    name="Commune",
    level=5,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="You contact your deity or a divine proxy and ask up to three questions that can be answered with a yes or no. You must ask your questions before the spell ends. You receive a correct answer for each question.",
)

DetectEvilAndGood = Spell(
    name="Detect Evil and Good",
    level=1,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""
For the duration, you know if there is an aberration, celestial, elemental, fey, fiend, or undead within 30 feet of you, as well as where the creature is located. Similarly, you know if there is a place or object within 30 feet of you that has been magically consecrated or desecrated.

The spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.
""",
)

DetectMagic = Spell(
    name="Detect Magic",
    level=1,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="For the duration, you sense the presence of magic within 30 feet of you. \
If you sense magic in this way, you can use your action to see a faint aura around any visible creature or object in the area that bears magic, and you learn its school of magic, if any. \
The spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.",
)

DetectThoughts = Spell(
    name="Detect Thoughts",
    level=2,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="For the duration, you can read the thoughts of certain creatures. \
        When you cast the spell and as your action on each turn until the spell ends, you can focus your mind on any one creature that you can see within 30 feet of you. \
        If the creature you choose has an Intelligence of 3 or lower or doesn't speak any language, the creature is unaffected. \
        You initially learn the surface thoughts of the creature—what is most on its mind in that moment. \
        As an action, you can either shift your attention to another creature's thoughts or attempt to probe deeper into the same creature's mind. \
        If you probe deeper, the target must make a Wisdom saving throw. \
        If it fails, you gain insight into its reasoning (if any), its emotional state, and something that looms large in its mind (such as something it worries over, loves, or hates). \
        If it succeeds, the spell ends. \
        Either way, the target knows that you are probing into its mind, and unless you shift your attention to another creature's thoughts, the creature can use its action on its turn to make an Intelligence check contested by your Intelligence check; \
        if it succeeds, the spell ends. \
        Questions verbally directed at the target creature naturally shape the course of its thoughts, so this spell is particularly effective as part of an interrogation.",
)

ArcaneEye = Spell(
    name="Arcane Eye",
    level=4,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="You create an invisible, magical eye within range that hovers in the air for the duration. \
You mentally receive visual information from the eye, which has normal vision and darkvision out to 30 feet. \
The eye can look in every direction. As an action, you can move the eye up to 30 feet in any direction. \
There is no limit to how far away from you the eye can move, but it can't enter another plane of existence. \
A solid barrier blocks the eye's movement, but the eye can pass through an opening as small as 1 inch in diameter.",
)

Scrying = Spell(
    name="Scrying",
    level=5,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="You can see and hear a particular creature you choose that is on the same plane of existence as you. \
The target must make a Wisdom saving throw, which is modified by how well you know the target and the sort of physical connection you have to it. \
If a target knows you're casting this spell, it can fail the saving throw voluntarily if it wants to be observed. \
Knowledge & Save Modifier: Secondhand (you have heard of the target) +5, Firsthand (you have met the target) +0, Familiar (you know the target well) -5, Connection & Save Modifier: Likeness or picture -2, Possession or garment -4, Body part, lock of hair, bit of nail, or the like -10, On a successful save, the target isn't affected, and you can't use this spell against it again for 24 hours. \
On a failed save, the spell creates an invisible sensor within 10 feet of the target. \
You can see and hear through the sensor as if you were there. \
The sensor moves with the target, remaining within 10 feet of it for the duration. \
A creature that can see invisible objects sees the sensor as a luminous orb about the size of your fist. \
Instead of targeting a creature, you can choose a location you have seen before as the target of this spell. \
When you do, the sensor appears at that location and doesn't move.",
)

Foresight = Spell(
    name="Foresight",
    level=9,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="You touch a willing creature and bestow a limited ability to see into the immediate future. \
For the duration, the target can't be surprised and has advantage on attack rolls, ability checks, and saving throws. \
Additionally, other creatures have disadvantage on attack rolls against the target for the duration.",
)
