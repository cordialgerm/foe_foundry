import pytest

from foe_foundry.utils.key import name_to_key


@pytest.mark.parametrize(
    "input_name,expected",
    [
        ("Werewolf (Lycanthrope)", "werewolf"),
        ("Dragon (Chromatic)", "dragon"),
        ("Goblin", "goblin"),
        ("Vampire (Undead)", "vampire"),
        ("Ogre (Giant)", "ogre"),
        ("Zombie (Horde)", "zombie"),
        ("Elemental (Fire)", "elemental"),
        ("Werewolf (Lycanthrope) (Alpha)", "werewolf-lycanthrope"),
        ("Werewolf (Lycanthrope) Extra", "werewolf-lycanthrope-extra"),
        ("Dire Wolf", "dire-wolf"),
    ],
)
def test_name_to_key(input_name, expected):
    assert name_to_key(input_name) == expected
