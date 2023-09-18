
## Ideas

- [ ] FoF Creature Powers and Templates
  - [x] Aberration
  - [x] Beast
  - [x] Celestial
  - [x] Construct
  - [x] Dragon
  - [x] Elemental
  - [x] Fey
  - [x] Fiend
  - [x] Giant
  - [x] Humanoid
  - [x] Monstrosity
  - [x] Ooze
  - [x] Plant
  - [x] Undead
- [x] Role Powers - all but LEADER
- [ ] FoF Theme Powers
  - [x] aberrant
  - [x] bestial
  - [x] charm
  - [x] deathly (renamed from Necromantic)
  - [ ] draconic - MOVE TO DRAGON ABOVE? or have a BREATH tag?
  - [x] elemental - TBD? merged with elemental above?
  - [x] fearsome
  - [ ] magic
  - [x] organized (rename from Leader)
  - [x] poison
  - [x] tricky (renamed from Rogue)
  - [ ] solo - MOVE TO SPECIAL SECTION BELOW
  - [x] warrior
- [ ] Additional Theme Powers
  - Flyer: Swoop
  - Monstrous: Deadly Poison, Superheated Blood
  - Deathly: Chain Agony (increases as it spreads)
  - Breath: Fire breath
  - Brutish: Throw Boulder, Toss, etc.
  - Magic: Magic Protection, Energy Blast, Energy Wall, Chain Spell
  - Runic: Tricky illusion cloud rune, Fire rune restrain
  - Gadget: Explosive Grenades, traps
  - Eye Beams: anti magic eye, anti healing eye, vulnerability eye, random eye beams
  - Holy/Unholy: healing, divine favor
  - Weapon Powers
- [ ] Create a Role scoring system (minimum attributes, creature types, etc.)
- [x] Allow creature templates to customize the creature after a role has been applied
- [ ] Legendary Creatures (powers, role)
- [ ] Create a visualization that shows likelyhood of creature + role going for a giving power
- [ ] Creature Templates
- [ ] Statblock Renderers
  - [x] HTML
  - [ ] Markdown
  - [ ] Foundry
- [ ] Attack Templates
- [ ] Name Templates
- [ ] Boss Nicknames - https://slyflourish.com/monstrous_descriptors.html?rss=1
- [ ] Additional Creature Powers
- [ ] Specific Creature Templates

## Attack Enhancements

- [x] Creatures with a secondary damage type should have their attack action modified to do partial damage of that type
- [x] Powers need to be able to add additional info to attack clause
- [ ] Weapon Powers (similar to weapon masteries)
  - good for NPCs
  - good for some monster types

## Structural Enhancements

- [x] Redesign how attribute scaling works. Right now it's mixed in between monster dials and base stats and min/max/bonuses. Instead, attributes should be generated directly by the creature type based on CR
- [x] redesign skill and save proficiencies
- [x] Powers need to be able to modify attack damage
- [x] action that replaces a multiattack instance needs to be implemented
- [x] Armor Templates - ArmorType (None, Light, Medium, Heavy, Natural, Arcane, Divine), HasShield, target AC, DEX
- [x] Add benchmarking compared to L5E
- [x] There should be a cleanup phase where HP is normalized to match CON
- [x] There should be a cleanup phase where damage is normalized to match primary stat
- [x] There should be a cleanup phase where attack to hit is normalized with primary stat

## Notes

- Stick With Me! and Challenge Foe are redundant
- Should damage types in base statblocks be empty and be populated by role templates if not specified?
- Why is parry and riposte showing up for skirmishers?

## More Sophisticated Selection System

- Selection engine should take parameters like:
  - max # of bonus actions
  - max # of reactions
  - max # of powers
  - should prefer to have 1 bonus action and 1 reaction before having both
  - should prefer having 1 additional action before having too many

## Redesign Armor Class
  - There should be templates for different types of armor class
  - should be applied by creature type & role
  - base statblock has a suggested AC which can influence the template


## Bug List

- [ ] multiattack with just a single attack shouldn't render
- [ ] negative stat modifiers render with a ?
- [ ] feature blocks sometimes have duplicate . at the end
- [x] role modifiers don't appear to modify HP
- [x] attack action range should be based on creature's attack type
- [x] Cold Damage power doesn't appear to add its damage to the attack




## misc ideas

- shoud there be some sort of tags / prerequisite system?
- what about a power budget


# TODO - additional ideas

# Perceptive (perception proficiency / expertise)
# Hunter (survival proficiency / expertise)
# Beasts often  have the ability to climb, swim, or fly, and they might be



## More Powers

### Abberrant

- **Antimagic Gullet** - https://www.dndbeyond.com/monsters/2821163-eye-monger - also grants a Swallow

### Tentacle Powers

- **Tentacle Slam** - https://www.dndbeyond.com/monsters/16973-otyugh


### Psionic

- **Psychic Whispers** (Recharge) - level-scaled dissonant whispers
- **Mind Blast** (Recharge)
- **Devour Intellect** & **Body Thief** - https://www.dndbeyond.com/monsters/17163-intellect-devourer
- **Extract Brain** & **Tentacles** - https://www.dndbeyond.com/monsters/17104-mind-flayer
- **Psychic Mirror** - reflect psychic damage

### Bestial

Gore - https://www.dndbeyond.com/monsters/2560728-aurochs - Recharge 5 - move up movement speed - on a hit, deals additional damage and inflicts bleeding damage

### Reckless

- Wild Cleave (Recharge 5) - attack every creature being surrounded, on a hit the target must make a strength save or fall prone
- Flurry of Blows (Recharge 5) - make max(3, 2x) number of attacks

### Common

- Regeneration


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

### Poison

Paralyzing Poison


## Bugs

- Controllers keep getting Pinning Shot. Why?
- Many abilities around leadership and challenging shoudl require intelligence

## Power Selection

- Should try to balance feature, action, reaction, bonus action before having multiple reactions or bonus actions
- There should be some sort of "unique key" or tagging system based on the kind of ability. Try not to select duplicates. For example, right now you can get multiple death triggers


------------


## Spellcasting

- Spell Lists
- each monster needs a spellcasting stat
- reconcile spell save DCs with spellcasting stat


Slaad Spells - https://www.dndbeyond.com/monsters/17113-death-slaad
Mindflayer Spells - levitate, detect thoughts, modify memory, dominate person / monster, plane shift, feeblemind
