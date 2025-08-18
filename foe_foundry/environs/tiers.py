from enum import StrEnum, auto


class Tiers(StrEnum):
    """Tiers of the environment, used to define the level of challenge and complexity in the environment."""

    # At Tier 0 (levels 1st–2nd) your characters are novices. They are taking their very first steps towards destiny, perhaps traveling further from their homes than ever before. The obstacles and foes they face are only slightly more perilous than what commoners contend with, albeit more frequent.
    tier_0 = auto()

    # At Tier 1 (levels 3rd–4th) your characters are local heroes. They are coming into their own as adventurers and learning the basic elements of their classes. Threats are small in scale and scope.
    tier_1 = auto()  # low-level environments, suitable for starting characters.

    # At Tier 2 (levels 5th–10th) your characters are regional heroes. They are accessing new levels of martial or magical power and can use skills, features, and magic that attract attention and acclaim.
    tier_2 = auto()

    # At Tier 3 (levels 11th–16th) your characters are masters of their craft, well beyond the abilities of other people and even other adventurers. Spells can bend the definition of what’s possible while martial characters taking to the battlefield can and have turned the tides of massive battles.
    tier_3 = auto()  # high-level environments, suitable for experienced characters.

    # At Tier 4 (levels 17th–20th) your characters have reached a point where the challenges they face are of world-changing size and proportion. At this tier, your character’s actions have the potential to fundamentally alter the lives and wellbeing of those that rely on (or fear) them.
    tier_4 = auto()  # very high-level environments, suitable for powerful characters.
