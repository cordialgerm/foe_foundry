from foe_foundry_agent.research.state import parse_research_notes

EXAMPLE_1 = """
```md
---
type: relevant-monster
relevance: high
monster_key: Gelatinous Cube
research_summary: Use Engulf and transparent ambush tactics as the model for the whale’s spit-out symbiotic oozes; they restrain and dissolve prey before the whale recalls and swallows them.
source_refs: https://foefoundry.com/monsters/gelatinous-cube/#gelatinous-cube,power-engulf-in-ooze
---

Notable traits:
- Engulf: moves into a space to restrain and deal acid damage each turn
- Transparent: hard to notice until too late; slow but inexorable
- Immunities/traits typical of oozes (acid, many conditions); squeezes through tight spaces

Adaptation ideas:
- Cubelets: The whale uses an action to expel 1–3 Small “cubelets” that immediately attempt Engulf on nearby targets; HP and damage scaled as minions.
- Recall Symbiotes: Bonus action or legendary action—oozes surge back toward the whale. If a cubelet adjacent to the mouth is Engulfing a target, that target must save or become Swallowed.
- Digestive Synergy: While a cubelet Engulfs a creature, the whale’s Swallow deals extra acid at the start of the swallowed creature’s turns.
```

```md
---
type: relevant-monster
relevance: high
monster_key: Killer Whale
research_summary: Provides the aquatic chassis blindsight via echolocation, high swim speed, and “hold breath” to scale up into a Gargantuan apex that herds prey into its maw.
source_refs: monster://killer-whale
---

Notable traits:
- Aquatic hunter baseline (Huge beast): high swim speed, powerful bite
- Echolocation/blindsight; loses it if deafened
- Hold Breath; oceanic ambusher profile

Adaptation ideas:
- Scale to Gargantuan “ooze-host leviathan” with siege damage and thick hide; add acid resistance/immunity.
- Vacuum Gulp: 60‑ft cone water current that pulls creatures/oozes toward the mouth; on fail, creatures move and can be immediately Swallowed if adjacent.
- Reef-Ramming Charge: Replace typical “ram” with a turbulent body-check that creates difficult terrain and knocks prone in water, setting up the ooze Engulf + Gulp combo.
```

```md
---
type: scratchpad
relevance: high
research_summary: 'Combine a “Vile Vomit” expulsion (spawning corrosive minions), Engulf lockdown, and a Tarrasque-style Swallow that converts Engulfed targets into swallowed prey via a suction cone.'
source_refs: https://foefoundry.com/monsters/mage/#toximancer,power-vile-vomit,monster://tarrasque,power-swallow
---

- Signature loop: Expel Oozes (action) → Oozes Engulf/Restrict → Vacuum Gulp (cone pull; bonus/legendary) → Swallow converted targets.
- Vile Vomit variant: Cone/line that creates 2–3 ooze puddles (difficult terrain, acid start-of-turn). Puddles coalesce into minion oozes on initiative count 20.
- Swallow template: Use Swallow (Tarrasque/Purple Worm style) but add “Acid Bath” from symbiotes: extra acid damage; creatures have disadvantage to escape due to viscous slime.
- Symbiotic Split: When the whale takes slashing/lightning, it sheds a Tiny ooze (Black Pudding split homage) once per round.
- Recall Symbiotes: Legendary action to move each ooze up to its speed toward the whale; Engulfed victims dragged along.
- Lair/Environmental: Rip current undertow, clouded acidic slick, reef choke points to amplify the pull-and-gulp gameplay.
```
"""


def test_parse_research_notes_examples():
    notes = parse_research_notes(EXAMPLE_1)
    assert len(notes) == 3
    assert notes[0].type == "relevant-monster"
    assert notes[0].monster_key == "Gelatinous Cube"
    assert "Engulf" in notes[0].research_content
    assert notes[1].monster_key == "Killer Whale"
    assert notes[2].type == "scratchpad"
    assert "Vile Vomit" in notes[2].research_content
    assert notes[2].monster_key is None
    assert notes[2].relevance == "high"
    assert notes[2].source_refs.startswith("https://foefoundry.com/monsters/mage")
