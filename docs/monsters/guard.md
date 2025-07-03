
---

GuardVariant = MonsterVariant(
    name="Guard",
    description="Guards are perceptive, but most have little martial training. They might be bouncers, lookouts, members of a city watch, or other keen-eyed warriors.",
    monsters=[
        Monster(
            name="Guard",
            cr=1 / 8,
            srd_creatures=["Guard"],
            other_creatures={"Watchman": "alias"},
        ),
        Monster(name="Sergeant of the Watch", cr=1),
    ],
)
CommanderVariant = MonsterVariant(
    name="Captain of the Watch",
    description="Guard captains often have ample professional experience. They might be accomplished bodyguards, protectors of magic treasures, veteran watch members, or similar wardens.",
    monsters=[
        Monster(
            name="Guard Captain",
            cr=4,
            other_creatures={"Guard Captain": "mm25"},
        ),
        Monster(name="Lord of the Watch", cr=8, is_legendary=True),
    ],
)


---