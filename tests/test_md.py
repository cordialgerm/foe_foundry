import dotenv

from foe_foundry.markdown import markdown


def test_markdown():
    dotenv.load_dotenv()
    text = "This is a **Wight** and these are [[Zombies]] and this is a button [[$Lich]] and this is **NOTHING IMPORTANT** and this is a statblock [[!Bandit]]"
    result = markdown(text)
    assert len(result.references) == 4


def test_necromancer_primagus():
    dotenv.load_dotenv()
    text = "This is a **Necromancer Primagus** and this is [[$Necromancer Primagus]] and [[!Necromancer Primagus]]"
    result = markdown(text)
    assert len(result.references) == 3


def test_cultist_fanatic():
    dotenv.load_dotenv()
    text = "This is a **Cultist Fanatic** and this is [[$Cultist-Fanatic]] and [[!Cultist_Fanatic]]"
    result = markdown(text)
    assert len(result.references) == 3
