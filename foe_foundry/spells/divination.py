from ..features import ActionType
from .spell import Spell

Commune = Spell(
    name="Commune",
    level=5,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="""You contact your deity or a divine proxy and ask up to three questions that can be answered with a yes or no. You must ask your questions before the spell ends. You receive a correct answer for each question.\n\nDivine beings aren't necessarily omniscient, so you might receive \"unclear\" as an answer if a question pertains to information that lies beyond the deity's knowledge. In a case where a one-word answer could be misleading or contrary to the deity's interests, the GM might offer a short phrase as an answer instead.\n\nIf you cast the spell two or more times before finishing your next long rest, there is a cumulative 25 percent chance for each casting after the first that you get no answer. The GM makes this roll in secret.""",
)

DetectEvilAndGood = Spell(
    name="Detect Evil and Good",
    level=1,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""For the duration, you know if there is an aberration, celestial, elemental, fey, fiend, or undead within 30 feet of you, as well as where the creature is located. Similarly, you know if there is a place or object within 30 feet of you that has been magically consecrated or desecrated.\n\nThe spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.""",
)

DetectMagic = Spell(
    name="Detect Magic",
    level=1,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="""For the duration, you sense the presence of magic within 30 feet of you. If you sense magic in this way, you can use your action to see a faint aura around any visible creature or object in the area that bears magic, and you learn its school of magic, if any.\n\nThe spell can penetrate most barriers, but it is blocked by 1 foot of stone, 1 inch of common metal, a thin sheet of lead, or 3 feet of wood or dirt.""",
)

DetectThoughts = Spell(
    name="Detect Thoughts",
    level=2,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""For the duration, you can read the thoughts of certain creatures. When you cast the spell and as your action on each turn until the spell ends, you can focus your mind on any one creature that you can see within 30 feet of you. If the creature you choose has an Intelligence of 3 or lower or doesn't speak any language, the creature is unaffected.\n\nYou initially learn the surface thoughts of the creature-what is most on its mind in that moment. As an action, you can either shift your attention to another creature's thoughts or attempt to probe deeper into the same creature's mind. If you probe deeper, the target must make a Wisdom saving throw. If it fails, you gain insight into its reasoning (if any), its emotional state, and something that looms large in its mind (such as something it worries over, loves, or hates). If it succeeds, the spell ends. Either way, the target knows that you are probing into its mind, and unless you shift your attention to another creature's thoughts, the creature can use its action on its turn to make an Intelligence check contested by your Intelligence check; if it succeeds, the spell ends.\n\nQuestions verbally directed at the target creature naturally shape the course of its thoughts, so this spell is particularly effective as part of an interrogation.\n\nYou can also use this spell to detect the presence of thinking creatures you can't see. When you cast the spell or as your action during the duration, you can search for thoughts within 30 feet of you. The spell can penetrate barriers, but 2 feet of rock, 2 inches of any metal other than lead, or a thin sheet of lead blocks you. You can't detect a creature with an Intelligence of 3 or lower or one that doesn't speak any language.\n\nOnce you detect the presence of a creature in this way, you can read its thoughts for the rest of the duration as described above, even if you can't see it, but it must still be within range.""",
)

ArcaneEye = Spell(
    name="Arcane Eye",
    level=4,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""You create an invisible, magical eye within range that hovers in the air for the duration.\n\nYou mentally receive visual information from the eye, which has normal vision and darkvision out to 30 feet. The eye can look in every direction.\n\nAs an action, you can move the eye up to 30 feet in any direction. There is no limit to how far away from you the eye can move, but it can't enter another plane of existence. A solid barrier blocks the eye's movement, but the eye can pass through an opening as small as 1 inch in diameter.""",
)

Scrying = Spell(
    name="Scrying",
    level=5,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    concentration=True,
    description="""You can see and hear a particular creature you choose that is on the same plane of existence as you. The target must make a Wisdom saving throw, which is modified by how well you know the target and the sort of physical connection you have to it. If a target knows you're casting this spell, it can fail the saving throw voluntarily if it wants to be observed.\n\nTable- Scrying Save Modifier\n\n| Knowledge                                         | Save Modifier |\n|---------------------------------------------------|---------------|\n| Secondhand (you have heard of the target)         | +5            |\n| Firsthand (you have met the target)               | +0            |\n| Familiar (you know the target well)               | -5            |\n| Connection                                        | Save Modifier |\n| Likeness or picture                               | -2            |\n| Possession or garment                             | -4            |\n| Body part, lock of hair, bit of nail, or the like | -10           |\n|                                                   |               |\n\nOn a successful save, the target isn't affected, and you can't use this spell against it again for 24 hours.\n\nOn a failed save, the spell creates an invisible sensor within 10 feet of the target. You can see and hear through the sensor as if you were there. The sensor moves with the target, remaining within 10 feet of it for the duration. A creature that can see invisible objects sees the sensor as a luminous orb about the size of your fist.\n\nInstead of targeting a creature, you can choose a location you have seen before as the target of this spell. When you do, the sensor appears at that location and doesn't move.""",
)

Foresight = Spell(
    name="Foresight",
    level=9,
    school="divination",
    source="SRD 5.1",
    action_type=ActionType.Action,
    description="""You touch a willing creature and bestow a limited ability to see into the immediate future. For the duration, the target can't be surprised and has advantage on attack rolls, ability checks, and saving throws. Additionally, other creatures have disadvantage on attack rolls against the target for the duration.\n\nThis spell immediately ends if you cast it again before its duration ends.""",
)

ZoneOfTruth = Spell(
    name="Zone of Truth",
    level=2,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=None,
    description="""You create a magical zone that guards against deception in a 15-foot radius sphere centered on a point of your choice within range. Until the spell ends, a creature that enters the spell's area for the first time on a turn or starts its turn there must make a Charisma saving throw. On a failed save, a creature can't speak a deliberate lie while in the radius. You know whether each creature succeeds or fails on its saving throw.\n\nAn affected creature is aware of the spell and can thus avoid answering questions to which it would normally respond with a lie. Such a creature can be evasive in its answers as long as it remains within the boundaries of the truth.""",
)
