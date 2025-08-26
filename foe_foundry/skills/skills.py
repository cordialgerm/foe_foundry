from typing import List, cast

try:
    from enum import StrEnum  # Python 3.11+
except ImportError:
    from backports.strenum import StrEnum  # Python 3.10

from .ability_scores import AbilityScore


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
    def stat(self) -> AbilityScore:
        """
        Returns the governing ability score (from Stats) for this skill.
        For example, Stealth is governed by Dexterity, Arcana by Intelligence, etc.
        """
        map = {
            Skills.Athletics: AbilityScore.STR,  # Strength
            Skills.Acrobatics: AbilityScore.DEX,  # Dexterity
            Skills.SleightOfHand: AbilityScore.DEX,  # Dexterity
            Skills.Initiative: AbilityScore.DEX,  # Dexterity
            Skills.Stealth: AbilityScore.DEX,  # Dexterity
            Skills.Arcana: AbilityScore.INT,  # Intelligence
            Skills.History: AbilityScore.INT,  # Intelligence
            Skills.Investigation: AbilityScore.INT,  # Intelligence
            Skills.Nature: AbilityScore.INT,  # Intelligence
            Skills.Religion: AbilityScore.INT,  # Intelligence
            Skills.AnimalHandling: AbilityScore.WIS,  # Wisdom
            Skills.Insight: AbilityScore.WIS,  # Wisdom
            Skills.Medicine: AbilityScore.WIS,  # Wisdom
            Skills.Perception: AbilityScore.WIS,  # Wisdom
            Skills.Survival: AbilityScore.WIS,  # Wisdom
            Skills.Deception: AbilityScore.CHA,  # Charisma
            Skills.Intimidation: AbilityScore.CHA,  # Charisma
            Skills.Performance: AbilityScore.CHA,  # Charisma
            Skills.Persuasion: AbilityScore.CHA,  # Charisma
        }
        return map[self]

    @staticmethod
    def All() -> List["Skills"]:
        """
        Returns a list of all Skills enum members.
        Useful for iteration, validation, or UI display.
        """
        return [cast(Skills, s) for s in Skills._member_map_.values()]
