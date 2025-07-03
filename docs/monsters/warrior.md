


---


ShockInfantryVariant = MonsterVariant(
    name="Shock Infantry",
    description="Shock infantry are trainees or rank-and-file troops. They are skilled at contending with commonplace, nonmagical threats head on.",
    monsters=[
        Monster(
            name="Shock Infantry",
            cr=1 / 8,
            other_creatures={"Warrior Infantry": "mm25"},
        ),
        Monster(name="Shock Infantry Veteran", cr=3, srd_creatures=["Veteran"]),
    ],
)
LineInfantryVariant = MonsterVariant(
    name="Line Infantry",
    description="Line infantry are rank-and-file troops that hold the line against commonplace, nonmagical threats.",
    monsters=[
        Monster(
            name="Line Infantry",
            cr=1 / 8,
            other_creatures={"Warrior Infantry": "mm25"},
        ),
        Monster(name="Line Infantry Veteran", cr=3, srd_creatures=["Veteran"]),
    ],
)
CommanderVariant = MonsterVariant(
    name="Warrior Commander",
    description="Skilled in both combat and leadership, warrior commanders overcome challenges through a combination of martial skill and clever tactics.",
    monsters=[
        Monster(
            name="Warrior Commander",
            cr=10,
            other_creatures={"Warrior Commander": "mm25"},
        ),
        Monster(name="Legendary Warrior", cr=14, is_legendary=True),
    ],
)

---