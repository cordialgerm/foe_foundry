from typing import List, cast

from backports.strenum import StrEnum

from .stats import Stats


class Skills(StrEnum):
    """
    Enum representing all 5E skills, including Initiative.
    Each skill is mapped to its governing ability score via the 'stat' property.
    Comments provide context for each skill's use in gameplay.
    """

    Athletics = "Athletics"  # STR: Climbing, jumping, swimming, grappling, shoving
    Acrobatics = (
        "Acrobatics"  # DEX: Balancing, tumbling, escaping bonds, avoiding grapples
    )
    SleightOfHand = (
        "SleightOfHand"  # DEX: Picking pockets, palming objects, performing tricks
    )
    Stealth = "Stealth"  # DEX: Hiding, moving silently, avoiding detection
    Arcana = "Arcana"  # INT: Knowledge of magic, spells, magical traditions
    History = "History"  # INT: Knowledge of historical events, legends, past cultures
    Investigation = "Investigation"  # INT: Finding clues, deducing facts, searching for hidden things
    Nature = (
        "Nature"  # INT: Knowledge of terrain, plants, animals, weather, survival lore
    )
    Religion = "Religion"  # INT: Knowledge of deities, rites, religious lore, symbols
    AnimalHandling = (
        "AnimalHandling"  # WIS: Calming, training, or intuiting animal behavior
    )
    Insight = "Insight"  # WIS: Reading body language, motives, detecting lies
    Medicine = (
        "Medicine"  # WIS: Stabilizing wounds, diagnosing illness, treating disease
    )
    Perception = "Perception"  # WIS: Spotting, hearing, or otherwise detecting things
    Survival = "Survival"  # WIS: Tracking, foraging, navigating, predicting weather
    Deception = "Deception"  # CHA: Lying, bluffing, disguising motives or intent
    Intimidation = "Intimidation"  # CHA: Threatening, coercing, frightening others
    Performance = (
        "Performance"  # CHA: Entertaining, acting, singing, playing instruments
    )
    Persuasion = "Persuasion"  # CHA: Negotiating, convincing, diplomacy, winning favor
    Initiative = "Initiative"  # DEX: Determines combat order; not a standard skill but often treated as one

    @property
    def stat(self) -> Stats:
        """
        Returns the governing ability score (from Stats) for this skill.
        For example, Stealth is governed by Dexterity, Arcana by Intelligence, etc.
        """
        map = {
            Skills.Athletics: Stats.STR,  # Strength
            Skills.Acrobatics: Stats.DEX,  # Dexterity
            Skills.SleightOfHand: Stats.DEX,  # Dexterity
            Skills.Initiative: Stats.DEX,  # Dexterity
            Skills.Stealth: Stats.DEX,  # Dexterity
            Skills.Arcana: Stats.INT,  # Intelligence
            Skills.History: Stats.INT,  # Intelligence
            Skills.Investigation: Stats.INT,  # Intelligence
            Skills.Nature: Stats.INT,  # Intelligence
            Skills.Religion: Stats.INT,  # Intelligence
            Skills.AnimalHandling: Stats.WIS,  # Wisdom
            Skills.Insight: Stats.WIS,  # Wisdom
            Skills.Medicine: Stats.WIS,  # Wisdom
            Skills.Perception: Stats.WIS,  # Wisdom
            Skills.Survival: Stats.WIS,  # Wisdom
            Skills.Deception: Stats.CHA,  # Charisma
            Skills.Intimidation: Stats.CHA,  # Charisma
            Skills.Performance: Stats.CHA,  # Charisma
            Skills.Persuasion: Stats.CHA,  # Charisma
        }
        return map[self]

    @staticmethod
    def All() -> List["Skills"]:
        """
        Returns a list of all Skills enum members.
        Useful for iteration, validation, or UI display.
        """
        return [cast(Skills, s) for s in Skills._member_map_.values()]
