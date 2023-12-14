from ..features import ActionType
from ..skills import Stats
from .spell import Spell

Bane: Spell = Spell(
    name="Bane",
    level=1,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.CHA,
    upcast=True,
    description="Up to three creatures of your choice that you can see within range must make Charisma saving throws. Whenever a target that fails this saving throw makes an attack roll or a saving throw before the spell ends, the target must roll a d4 and subtract the number rolled from the attack roll or saving throw.",
    upcast_description="When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st.",
    range="30 feet",
)


CharmPerson: Spell = Spell(
    name="Charm Person",
    level=1,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=True,
    concentration=False,
    description="You attempt to charm a humanoid you can see within range. It must make a Wisdom saving throw, and does so with advantage if you or your companions are fighting it. If it fails the saving throw, it is charmed by you until the spell ends or until you or your companions do anything harmful to it. The charmed creature regards you as a friendly acquaintance. When the spell ends, the creature knows it was charmed by you.",
    upcast_description="When you cast this spell using a spell slot of 2nd level or higher, you can target one additional creature for each slot level above 1st. The creatures must be within 30 feet of each other when you target them.",
    range="30 feet",
)


Command: Spell = Spell(
    name="Command",
    level=1,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=True,
    description="You speak a one-word command to a creature you can see within range. The target must succeed on a Wisdom saving throw or follow the command on its next turn. The spell has no effect if the target is undead, if it doesn’t understand your language, or if your command is directly harmful to it.",
    upcast_description="When you cast this spell using a spell slot of 2nd level or higher, you can affect one additional creature for each slot level above 1st. The creatures must be within 30 feet of each other when you target them.",
    range="60 feet",
)

HideousLaughter: Spell = Spell(
    name="Hideous Laughter",
    level=1,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=False,
    concentration=True,
    description="A creature of your choice that you can see within range perceives everything as hilariously funny and falls into fits of laughter if this spell affects it. The target must succeed on a Wisdom saving throw or fall prone, becoming incapacitated and unable to stand up for the duration. A creature with an Intelligence score of 4 or less isn’t affected.",
    range="30 feet",
)

HoldPerson: Spell = Spell(
    name="Hold Person",
    level=2,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=True,
    description="Choose a humanoid that you can see within range. The target must succeed on a Wisdom saving throw or be paralyzed for the duration. At the end of each of its turns, the target can make another Wisdom saving throw. On a success, the spell ends on the target.",
    upcast_description="When you cast this spell using a spell slot of 3rd level or higher, you can target one additional humanoid for each slot level above 2nd. The humanoids must be within 30 feet of each other when you target them.",
    range="60 feet",
)

Suggestion: Spell = Spell(
    name="Suggestion",
    level=2,
    school="enchantment",
    source="SRD 5.1",
    action_type=ActionType.Action,
    save=Stats.WIS,
    upcast=False,
    concentration=True,
    description="You suggest a course of activity (limited to a sentence or two) and magically influence a creature you can see within range that can hear and understand you. Creatures that can’t be charmed are immune to this effect. The suggestion must be worded in such a manner as to make the course of action sound reasonable. Asking the creature to stab itself, throw itself onto a spear, immolate itself, or do some other obviously harmful act ends the spell.",
    range="30 feet",
)
