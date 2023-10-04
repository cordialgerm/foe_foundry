
## Ideas

- [x] FoF Creature Powers and Templates
- [x] Role Powers
- [x] FoF Theme Powers
- [x] Allow creature templates to customize the creature after a role has been applied
- [x] Redesign AC with AC Templates
- [ ] Weapon Powers / Fighting Styles (similar to weapon masteries)
- [ ] Utility to convert static damage #s to dice formula
- [ ] Create a Role scoring system (minimum attributes, creature types, etc.)
- [ ] Specific Creature Templates
- [ ] Biome System
- [ ] Encounter Generator
- [ ] Name Templates
- [ ] License
- [ ] Boss Nicknames - https://slyflourish.com/monstrous_descriptors.html?rss=1
- [ ] Legendary Creatures (powers, role)
- [ ] Create a visualization that shows likelyhood of creature + role going for a giving power
- [ ] Statblock Renderers
  - [x] HTML
  - [ ] Markdown
  - [ ] Foundry

## Bug List

- [ ] negative stat modifiers render with a ?
- [ ] Stick With Me! and Challenge Foe are redundant
- [ ] Controllers keep getting Pinning Shot. Why?
- [ ] Many abilities around leadership and challenging shoudl require intelligence and verbal speaking abilities

## More Sophisticated Selection System

Selection engine should take parameters like:

- max # of bonus actions
- max # of reactions
- max # of powers
- should prefer to have 1 bonus action and 1 reaction before having both
- should prefer having 1 additional action before having too many
- should there be a power budget? different powers have a point score allocated to them?
- Should try to balance feature, action, reaction, bonus action before having multiple reactions or bonus actions
- There should be some sort of "unique key" or tagging system based on the kind of ability. Try not to select duplicates. For example, right now you can get multiple death triggers

Selection system by "category"
Feature
Special Attack (max 1)
Attack Modifier (max 1)
Non-Attack Action
Reaction (prefer 0-1)
Bonus Action (prefer 0-1)
Recharge (max 1)

Features should be sorted (in a random order? or based on some sort of sort key) and applied one at a time. This way the features can build off each other

Should features be re-scored as they're built up? This would make the features build off each other more

## Powers

- Perceptive
  - Scouting
  - Keen Senses
- Deathly
  - Chain Agony (increases as it spreads)
- Magic:
  - Energy Blast
  - Energy Wall
  - Energy Beam
  - Chain Spell
  - Disintigration Beam
- Eye Beams: anti magic eye, anti healing eye, vulnerability eye, random eye beams
- Weapon Powers

### Fighting Styles / Weapon Powers

- Harpoon & Reel
- Spear
- Polearm
- Longbow
- Crossbow
- Longsword / Shield
- Greatsword / Greataxe

### Psionic

- **Devour Intellect** & **Body Thief** - https://www.dndbeyond.com/monsters/17163-intellect-devourer
- **Extract Brain** & **Tentacles** - https://www.dndbeyond.com/monsters/17104-mind-flayer

### Eye Powers

- Antimagic Cone
- See Volos' - bunch of ideas for beholders in there
- Antimagic Breath - https://www.dndbeyond.com/monsters/2059739-eyedrake
- Stunning Gaze - https://www.dndbeyond.com/monsters/2560819-gauth
- Aversion Ray
- Psychic Ray
- Slowing Ray
- Stunning Ray
- Dazing Ray
- Fear Ray
- Frost Ray
- Devour Magic Ray
- Enervation Ray
- Sleep Ray
- Freezing Ray
- Debilitating Ray
- Repulsion Ray
- Fire Ray
- Paralyzing Ray
- Death Ray
- Telekinetic Ray
- Petrification Ray
- Disintigration Ray
- Death Ray

## Spellcasting

- Spell Lists
- each monster needs a spellcasting stat
- reconcile spell save DCs with spellcasting stat
- Slaad Spells - https://www.dndbeyond.com/monsters/17113-death-slaad
- Mindflayer Spells - levitate, detect thoughts, modify memory, dominate person / monster, plane shift, feeblemind
- Angelic
- Domineering (see Amnizu)
- Innate Demonic magic (see Babau, Barlgura, Glabrezu, Mezzoloth, etc.)
- Hellfire Magic (see Pit Fiend)
