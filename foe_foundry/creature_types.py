from enum import StrEnum, auto


class CreatureType(StrEnum):
    Aberration = auto()
    Beast = auto()
    Celestial = auto()
    Construct = auto()
    Dragon = auto()
    Elemental = auto()
    Fey = auto()
    Fiend = auto()
    Giant = auto()
    Humanoid = auto()
    Monstrosity = auto()
    Ooze = auto()
    Plant = auto()
    Undead = auto()

    @property
    def is_living(self) -> bool:
        return self in {
            CreatureType.Aberration,
            CreatureType.Beast,
            CreatureType.Dragon,
            CreatureType.Fey,
            CreatureType.Giant,
            CreatureType.Humanoid,
            CreatureType.Monstrosity,
            CreatureType.Ooze,
            CreatureType.Plant,
        }

    @property
    def could_use_weapon(self) -> bool:
        return self in {
            CreatureType.Celestial,
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
        }

    @property
    def could_wear_armor(self) -> bool:
        return self in {
            CreatureType.Celestial,
            CreatureType.Fiend,
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
            CreatureType.Undead,
            CreatureType.Elemental,
        }

    @property
    def could_use_equipment(self) -> bool:
        return self in {
            CreatureType.Fey,
            CreatureType.Humanoid,
            CreatureType.Construct,
            CreatureType.Giant,
        }
