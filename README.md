
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
- [ ] Generic Creature Templates
- [ ] Statblock Renderers (HTML, Markdown, Foundry)
- [ ] Attack Templates
- [ ] Name Templates
- [ ] Additional Creature Powers
- [ ] Specific Creature Templates


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
