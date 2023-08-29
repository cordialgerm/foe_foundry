
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
  - [ ] Giant
  - [ ] Humanoid
  - [ ] Monstrosity
  - [ ] Ooze
  - [ ] Plant
  - [ ] Undead
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
- [ ] Powers need to be able to add additional info to attack clause
- [ ] Creatures with a secondary damage type should have their attack action modified to do partial damage of that type

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



BaseStatblock

Powers (stats) -> stats, [features]

RoleTemplate (stats) -> stats, [PowerSlot]
CreatureTemplate (stats) -> stats, [PowerSlots]


Types of Powers:

Common - any monsters can have these, common powers have selection chances
Uncommon - limited slots for these. They have selection changes
Role - 1 slot for these. options Determined by RoleTemplate
Creature - 1 slot for these. options Determined by CreatureTemplate

Power Slots

CR <= 1
  1 Role or Creature
  Remainder Common/Uncommon (usually 0)

CR <= 5
  1 Role
  1 Creature
  Remainder Common/Uncommon (usually 0)

CR <= 10
  1 Role
  1 Creature
  1 Common/Uncommon (usually 1)
  Remainder Common/Uncommon (usually 0)

CR <= 15
  1 Role
  1 Creature
  1 Uncommon
  Remainder Common/Uncommon (usually 1)

CR > 15
  1 Role
  1 Creature
  1 Uncommon
  Remainder Common/Uncommon (usually 2)
