from foe_foundry.markdown import markdown


def test_markdown():
    text = "This is a **Wight** and these are [[Zombies]] and this is a button $[[Lich]] and this is **NOTHING IMPORTANT** and this is a statblock ![[Bandit]]"

    result = markdown(text)
    assert len(result.references) == 4
