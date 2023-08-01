
## Ideas

- [ ] Creature Powers and Templates
  - [x] Aberration
  - [x] Beast
  - [x] Celestial
  - [x] Construct
  - [ ] Dragon
  - [ ] Elemental
  - [ ] Fey
  - [ ] Fiend
  - [ ] Giant
  - [ ] Humanoid
  - [ ] Monstrosity
  - [ ] Ooze
  - [ ] Plant
  - [ ] Undead
- [ ] Role Powers
- [ ] Create a visualization that shows likelyhood of creature + role going for a giving power
- [ ] Tag Powers
- [ ] Creature Templates
- [ ] Statblock Renderers
  - [x] HTML
  - [ ] Markdown
  - [ ] Foundry
- [ ] Attack Templates
- [ ] Name Templates
- [ ] Additional Creature Powers
- [ ] Specific Creature Templates


## Structural Enhancements

- [ ] Redesign how attribute scaling works. Right now it's mixed in between monster dials and base stats and min/max/bonuses. Instead, attributes should be generated directly by the creature type based on CR


- [x] Powers need to be able to modify attack damage
- [ ] Powers need to be able to add additional info to attack clause
- [x] action that replaces a multiattack instance needs to be implemented

## Bug List

- [ ] negative stat modifiers render with a ?
- [ ] feature blocks sometimes have duplicate . at the end
- [x] role modifiers don't appear to modify HP
- [x] attack action range should be based on creature's attack type



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
