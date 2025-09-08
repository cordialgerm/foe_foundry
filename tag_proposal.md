# Tag System Proposal

This document outlines the comprehensive tag system for monsters and powers in Foe Foundry. Tags are organized into categories to help users search, filter, and understand the inventory of monsters and powers.

## Tag Categories

### Creature Types
Based on D&D 5e creature types from `CreatureType` enum:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| aberration | Strange and otherworldly creatures | tentacle-strike.svg | `CreatureType.Aberration` |
| beast | Natural animals and creatures | bear-head.svg | `CreatureType.Beast` |
| celestial | Divine and heavenly creatures | angel-wings.svg | `CreatureType.Celestial` |
| construct | Artificial beings and golems | robot-golem.svg | `CreatureType.Construct` |
| dragon | Dragons and draconic creatures | dragon-head.svg | `CreatureType.Dragon` |
| elemental | Elemental beings of pure elements | atom.svg | `CreatureType.Elemental` |
| fey | Magical creatures from faerie realm | fairy.svg | `CreatureType.Fey` |
| fiend | Demonic and devilish creatures | devil-mask.svg | `CreatureType.Fiend` |
| giant | Large humanoid creatures | giant.svg | `CreatureType.Giant` |
| humanoid | Humans and humanlike creatures | person.svg | `CreatureType.Humanoid` |
| monstrosity | Unnatural but not otherworldly creatures | monster-grasp.svg | `CreatureType.Monstrosity` |
| ooze | Amorphous creatures like slimes | slime.svg | `CreatureType.Ooze` |
| plant | Vegetable creatures | carnivorous-plant.svg | `CreatureType.Plant` |
| undead | Formerly living creatures | skull-crossed-bones.svg | `CreatureType.Undead` |

### Monster Roles
Based on `MonsterRole` enum for tactical combat roles:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| ambusher | Strikes from hiding or surprise | ninja-mask.svg | `MonsterRole.Ambusher` |
| artillery | Long-range attackers | crossbow.svg | `MonsterRole.Artillery` |
| bruiser | Heavy damage dealers | muscle-up.svg | `MonsterRole.Bruiser` |
| controller | Battlefield manipulators | magic-portal.svg | `MonsterRole.Controller` |
| defender | Protective tank-like creatures | shield.svg | `MonsterRole.Defender` |
| leader | Command and support others | crown.svg | `MonsterRole.Leader` |
| skirmisher | Mobile hit-and-run fighters | running-ninja.svg | `MonsterRole.Skirmisher` |
| support | Provides assistance to allies | mailed-fist.svg | `MonsterRole.Support` |
| soldier | Standard combat troops | sword-brandish.svg | `MonsterRole.Soldier` |
| legendary | Exceptional boss-tier creatures | crown-of-thorns.svg | Special legendary status |

### Environments - Biomes
Based on `Biome` enum for natural environments:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| arctic | Cold, icy regions | snowflake-1.svg | `Biome.arctic` |
| desert | Hot, dry sandy regions | cactus.svg | `Biome.desert` |
| forest | Wooded areas with trees | tree-branch.svg | `Biome.forest` |
| jungle | Dense tropical forests | vine-leaf.svg | `Biome.jungle` |
| grassland | Open grassy plains | grass.svg | `Biome.grassland` |
| farmland | Cultivated agricultural land | wheat.svg | `Biome.farmland` |
| ocean | Vast saltwater bodies | wave-crest.svg | `Biome.ocean` |
| river | Flowing freshwater | river.svg | `Biome.river` |
| lake | Large freshwater bodies | water-drop.svg | `Biome.lake` |
| swamp | Wetland marshes | swamp.svg | `Biome.swamp` |
| underground | Subterranean environments | cave-entrance.svg | `Biome.underground` |
| extraplanar | Other-dimensional spaces | portal.svg | `Biome.extraplanar` |

### Environments - Terrain
Based on `Terrain` enum for physical features:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| mountain | High rocky peaks | mountain-cave.svg | `Terrain.mountain` |
| hill | Elevated gentle slopes | hills.svg | `Terrain.hill` |
| plain | Flat open areas | horizon-road.svg | `Terrain.plain` |
| water | Water-covered areas | water-drop.svg | `Terrain.water` |

### Environments - Development
Based on `Development` enum for civilization levels:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| wilderness | Natural untamed areas | tree-growth.svg | `Development.wilderness` |
| frontier | Minimal development outposts | wooden-sign.svg | `Development.frontier` |
| countryside | Rural villages and farms | village.svg | `Development.countryside` |
| settlement | Established communities | house.svg | `Development.settlement` |
| urban | Cities and advanced infrastructure | modern-city.svg | `Development.urban` |
| ruin | Abandoned destroyed areas | ancient-ruins.svg | `Development.ruin` |
| stronghold | Fortified military areas | castle.svg | `Development.stronghold` |
| dungeon | Underground hidden areas | dungeon-gate.svg | `Development.dungeon` |

### Environments - Extraplanar
Based on `ExtraplanarInfluence` enum for otherworldly influences:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| astral | Ethereal dreamlike qualities | cosmic-egg.svg | `ExtraplanarInfluence.astral` |
| elemental_plane | Strong elemental characteristics | atom.svg | `ExtraplanarInfluence.elemental` |
| faerie | Magical whimsical qualities | fairy-wings.svg | `ExtraplanarInfluence.faerie` |
| celestial_plane | Divine holy characteristics | holy-symbol.svg | `ExtraplanarInfluence.celestial` |
| hellish | Dark infernal characteristics | hell-crosses.svg | `ExtraplanarInfluence.hellish` |
| deathly | Dark eerie death qualities | skull-crossed-bones.svg | `ExtraplanarInfluence.deathly` |

### Damage Types / Elements
Based on `DamageType` enum for damage types:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| acid | Acidic corrosive damage | acid-blob.svg | `DamageType.Acid` |
| bludgeoning | Blunt physical damage | mace-head.svg | `DamageType.Bludgeoning` |
| cold | Freezing ice damage | ice-cube.svg | `DamageType.Cold` |
| fire | Burning flame damage | fire.svg | `DamageType.Fire` |
| force | Pure magical energy | magic-swirl.svg | `DamageType.Force` |
| lightning | Electrical shock damage | lightning-arc.svg | `DamageType.Lightning` |
| necrotic | Death and decay damage | death-skull.svg | `DamageType.Necrotic` |
| piercing | Sharp pointed damage | spear-feather.svg | `DamageType.Piercing` |
| poison | Toxic venomous damage | poison-bottle.svg | `DamageType.Poison` |
| psychic | Mental mind damage | brain-stem.svg | `DamageType.Psychic` |
| radiant | Divine light damage | sun-radiations.svg | `DamageType.Radiant` |
| slashing | Sharp cutting damage | sword-slice.svg | `DamageType.Slashing` |
| thunder | Sonic sound damage | sonic-boom.svg | `DamageType.Thunder` |

### Power Types
Based on `PowerType` enum for power categories:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| attack | Offensive combat powers | sword-brandish.svg | `PowerType.Attack` |
| defense | Protective defensive powers | shield.svg | `PowerType.Defense` |
| areaofeffect | Wide area affecting powers | explosion-rays.svg | `PowerType.AreaOfEffect` |
| movement | Mobility and positioning powers | sprint.svg | `PowerType.Movement` |
| debuff | Weakening enemy powers | cursed-star.svg | `PowerType.Debuff` |
| buff | Strengthening ally powers | muscle-up.svg | `PowerType.Buff` |
| summon | Creature summoning powers | magic-portal.svg | `PowerType.Summon` |
| environmental | Environment interaction powers | earth-spit.svg | `PowerType.Environmental` |
| aura | Persistent area effects | aura.svg | `PowerType.Aura` |
| healing | Health restoration powers | healing.svg | `PowerType.Healing` |
| utility | Non-combat utility powers | toolbox.svg | `PowerType.Utility` |
| magic | Magical spell-like powers | magic-hat.svg | `PowerType.Magic` |
| stealth | Concealment and hiding powers | hood.svg | `PowerType.Stealth` |

### Challenge Rating Tiers
Based on D&D level tiers from existing `from_cr` method:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| tier0 | Levels 1-2 (CR 0-1/2) | level-two.svg | `MonsterTag.from_cr` for CR < 1 |
| tier1 | Levels 2-4 (CR 1-3) | level-two-advanced.svg | `MonsterTag.from_cr` for CR 1-3 |
| tier2 | Levels 5-9 (CR 4-12) | level-three.svg | `MonsterTag.from_cr` for CR 4-12 |
| tier3 | Levels 10-14 (CR 13-19) | level-three-advanced.svg | `MonsterTag.from_cr` for CR 13-19 |
| tier4 | Levels 15-20 (CR 20+) | level-four.svg | `MonsterTag.from_cr` for CR 20+ |

### Creature Families/Species
Based on creature-specific power directories and common D&D monsters:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| balor | Balor demons | devil-mask.svg | `foe_foundry/powers/creature/balor.py` |
| basilisk | Basilisk creatures | reptile-tail.svg | `foe_foundry/powers/creature/basilisk.py` |
| bugbear | Bugbear goblinoids | goblin-head.svg | `foe_foundry/powers/creature/bugbear.py` |
| chimera | Chimera creatures | griffin-symbol.svg | `foe_foundry/powers/creature/chimera.py` |
| cultist | Cult members | cultist.svg | `foe_foundry/powers/creature/cultist.py` |
| dire_bunny | Dire bunny creatures | rabbit-head.svg | `foe_foundry/powers/creature/dire_bunny.py` |
| druid | Druidic characters | oak-leaf.svg | `foe_foundry/powers/creature/druid.py` |
| frost_giant | Frost giants | giant.svg | `foe_foundry/powers/creature/frost_giant.py` |
| gelatinous_cube | Gelatinous cubes | cube.svg | `foe_foundry/powers/creature/gelatinous_cube.py` |
| ghoul | Ghoul undead | shambling-zombie.svg | `foe_foundry/powers/creature/ghoul.py` |
| goblin | Goblin creatures | goblin-head.svg | `foe_foundry/powers/creature/goblin.py` |
| gorgon | Gorgon creatures | medusa-head.svg | `foe_foundry/powers/creature/gorgon.py` |
| guard | Guard NPCs | guards.svg | `foe_foundry/powers/creature/guard.py` |
| hydra | Hydra creatures | hydra.svg | `foe_foundry/powers/creature/hydra.py` |
| knight | Knight characters | mounted-knight.svg | `foe_foundry/powers/creature/knight.py` |
| kobold | Kobold creatures | goblin-head.svg | `foe_foundry/powers/creature/kobold.py` |
| lich | Lich undead | evil-book.svg | `foe_foundry/powers/creature/lich.py` |
| mage | Spellcaster mages | wizard-staff.svg | `foe_foundry/powers/creature/mage.py` |
| manticore | Manticore creatures | griffin-symbol.svg | `foe_foundry/powers/creature/manticore.py` |
| merrow | Merrow creatures | triton-head.svg | `foe_foundry/powers/creature/merrow.py` |
| mimic | Mimic creatures | mimic-chest.svg | `foe_foundry/powers/creature/mimic.py` |
| nothic | Nothic creatures | one-eyed.svg | `foe_foundry/powers/creature/nothic.py` |
| ogre | Ogre creatures | ogre.svg | `foe_foundry/powers/creature/ogre.py` |
| simulacrum | Simulacrum constructs | android-mask.svg | `foe_foundry/powers/creature/simulacrum.py` |
| skeletal | Skeletal undead | skeleton.svg | `foe_foundry/powers/creature/skeletal.py` |
| spider | Spider creatures | spider-web.svg | `foe_foundry/powers/creature/spider.py` |
| spirit | Spirit creatures | ghost.svg | `foe_foundry/powers/creature/spirit.py` |
| vrock | Vrock demons | harpy.svg | `foe_foundry/powers/creature/vrock.py` |
| wight | Wight undead | ghost.svg | `foe_foundry/powers/creature/wight.py` |
| wolf | Wolf creatures | wolf-head.svg | `foe_foundry/powers/creature/wolf.py` |
| zombie | Zombie undead | shambling-zombie.svg | `foe_foundry/powers/creature/zombie.py` |

### Thematic Power Categories
Based on themed power directories:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| aberrant | Strange otherworldly powers | tentacle-strike.svg | `foe_foundry/powers/themed/aberrant.py` |
| anti_magic | Magic-negating powers | magic-shield.svg | `foe_foundry/powers/themed/anti_magic.py` |
| anti_ranged | Ranged-attack negating powers | shield-bounces.svg | `foe_foundry/powers/themed/anti_ranged.py` |
| aquatic | Water-based powers | wave-crest.svg | `foe_foundry/powers/themed/aquatic.py` |
| bestial | Animal-like powers | claw-slashes.svg | `foe_foundry/powers/themed/bestial.py` |
| breath | Breath weapon powers | dragon-breath.svg | `foe_foundry/powers/themed/breath.py` |
| chaotic | Unpredictable random powers | abstract-050.svg | `foe_foundry/powers/themed/chaotic.py` |
| charm | Mind-influencing powers | charm.svg | `foe_foundry/powers/themed/charm.py` |
| clever | Intelligence-based powers | brain-stem.svg | `foe_foundry/powers/themed/clever.py` |
| cowardly | Fear and retreat powers | backstab.svg | `foe_foundry/powers/themed/cowardly.py` |
| cruel | Sadistic harmful powers | serrated-slash.svg | `foe_foundry/powers/themed/cruel.py` |
| cursed | Curse-based powers | cursed-star.svg | `foe_foundry/powers/themed/cursed.py` |
| deathly | Death-themed powers | death-skull.svg | `foe_foundry/powers/themed/deathly.py` |
| diseased | Disease and plague powers | virus.svg | `foe_foundry/powers/themed/diseased.py` |
| domineering | Control and command powers | crown.svg | `foe_foundry/powers/themed/domineering.py` |
| earthy | Earth and stone powers | stone-pile.svg | `foe_foundry/powers/themed/earthy.py` |
| emanation | Radiating effect powers | aura.svg | `foe_foundry/powers/themed/emanation.py` |
| fast | Speed and haste powers | fast-arrow.svg | `foe_foundry/powers/themed/fast.py` |
| fearsome | Fear-inspiring powers | screaming.svg | `foe_foundry/powers/themed/fearsome.py` |
| flying | Flight and aerial powers | wing-cloak.svg | `foe_foundry/powers/themed/flying.py` |
| gadget | Tool and device powers | gear-hammer.svg | `foe_foundry/powers/themed/gadget.py` |
| holy | Divine blessed powers | holy-symbol.svg | `foe_foundry/powers/themed/holy.py` |
| honorable | Honor-based powers | mounted-knight.svg | `foe_foundry/powers/themed/honorable.py` |
| hunter | Tracking and hunting powers | bow-arrow.svg | `foe_foundry/powers/themed/hunter.py` |
| icy | Cold and ice powers | ice-cube.svg | `foe_foundry/powers/themed/icy.py` |
| illusory | Illusion and deception powers | invisible.svg | `foe_foundry/powers/themed/illusory.py` |
| monstrous | Monstrous creature powers | monster-grasp.svg | `foe_foundry/powers/themed/monstrous.py` |
| petrifying | Stone transformation powers | stone-block.svg | `foe_foundry/powers/themed/petrifying.py` |
| poisonous | Toxic and venomous powers | poison-cloud.svg | `foe_foundry/powers/themed/poison.py` |
| psionic | Mental and psionic powers | psychic-waves.svg | `foe_foundry/powers/themed/psychic.py` |
| reckless | Wild dangerous powers | bolt-bomb.svg | `foe_foundry/powers/themed/reckless.py` |
| serpentine | Snake-like powers | snake-tongue.svg | `foe_foundry/powers/themed/serpentine.py` |
| shamanic | Shamanic spiritual powers | totem.svg | `foe_foundry/powers/themed/shamanic.py` |
| sneaky | Stealth and subterfuge powers | ninja-mask.svg | `foe_foundry/powers/themed/sneaky.py` |
| storm | Weather and storm powers | lightning-storm.svg | `foe_foundry/powers/themed/storm.py` |
| technique | Skill-based martial powers | sword-smithing.svg | `foe_foundry/powers/themed/technique.py` |
| teleportation | Teleportation powers | teleport.svg | `foe_foundry/powers/themed/teleportation.py` |
| temporal | Time manipulation powers | time-bomb.svg | `foe_foundry/powers/themed/temporal.py` |
| thuggish | Brutish criminal powers | brass-knuckles.svg | `foe_foundry/powers/themed/thuggish.py` |
| totemic | Totemic spiritual powers | totem-head.svg | `foe_foundry/powers/themed/totemic.py` |
| tough | Resilience and durability powers | armor-vest.svg | `foe_foundry/powers/themed/tough.py` |
| trap | Trap and snare powers | box-trap.svg | `foe_foundry/powers/themed/trap.py` |

### Spellcaster Themes
Based on spellcaster power directories:

| Tag | Description | Icon | Source |
|-----|-------------|------|--------|
| celestial_magic | Celestial divine magic | angel-wings.svg | `foe_foundry/powers/spellcaster/celestial.py` |
| conjurer | Summoning magic | magic-portal.svg | `foe_foundry/powers/spellcaster/conjurer.py` |
| cult_magic | Cult magic | cultist.svg | `foe_foundry/powers/spellcaster/cult.py` |
| divination | Prophetic magic | crystal-ball.svg | `foe_foundry/powers/spellcaster/divination.py` |
| druidic_magic | Nature magic | oak-leaf.svg | `foe_foundry/powers/spellcaster/druidic.py` |
| elementalist | Elemental magic | atom.svg | `foe_foundry/powers/spellcaster/elementalist.py` |
| enchanter | Mind magic | charm.svg | `foe_foundry/powers/spellcaster/enchanter.py` |
| fiendish_magic | Demonic magic | devil-mask.svg | `foe_foundry/powers/spellcaster/fiendish.py` |
| illusionist | Illusion magic | invisible.svg | `foe_foundry/powers/spellcaster/illusionist.py` |
| arcane_magic | General arcane magic | magic-hat.svg | `foe_foundry/powers/spellcaster/magic.py` |
| metamagic | Magic-altering magic | magic-swirl.svg | `foe_foundry/powers/spellcaster/metamagic.py` |
| necromancer | Death magic | skull-staff.svg | `foe_foundry/powers/spellcaster/necromancer.py` |
| oath_magic | Oath-bound magic | holy-grail.svg | `foe_foundry/powers/spellcaster/oath.py` |
| psionic_magic | Mental psychic magic | brain-tentacle.svg | `foe_foundry/powers/spellcaster/psionic.py` |
| shaman | Shamanic spirit magic | totem.svg | `foe_foundry/powers/spellcaster/shaman.py` |
| transmuter | Transformation magic | magic-trick.svg | `foe_foundry/powers/spellcaster/transmuter.py` |

## Issues

### Potential Duplicates
- `holy` theme appears in both themed powers and could overlap with `celestial`
- `shaman`/`shamanic` appears in both themed and spellcaster categories
- `magic` is very broad and might overlap with specific magical themes
- `psychic` and `psionic` are very similar concepts

### Icon Selection Notes
- Many icons are placeholders and may need refinement
- Some categories may need different icons for better distinction
- Icons should be tested for visibility and clarity at small sizes

### Missing Categories
- Attack types (melee, ranged, spell, natural) - could be derived from existing AttackType enum
- Size categories (tiny, small, medium, large, huge, gargantuan)
- Languages (if relevant for search)

## Implementation Progress

### Phase 1: Central Tag Definition System ✅ COMPLETE
- [x] Created comprehensive tag proposal document
- [x] Fixed import issues in existing `foe_foundry/tags/tags.py`
- [x] Created `foe_foundry/tags/definitions.py` with 174 tag definitions
- [x] Enhanced MonsterTag class with description and icon properties
- [x] All tag icons verified to exist in docs/img/icons/ directory
- [x] System tested and working correctly

### Phase 2: Power Tag Assignment 🔄 IN PROGRESS

The power system contains approximately 136+ power files with hundreds of individual power classes. Analysis shows:

**Power File Categories:**
- **Themed Powers**: 42 files (aberrant, anti_magic, aquatic, bestial, etc.)
- **Creature-Specific Powers**: 32 files (balor, basilisk, goblin, etc.) 
- **Spellcaster Powers**: 17 files (celestial, conjurer, necromancer, etc.)
- **Creature Type Powers**: 14 files (aberration, beast, dragon, undead, etc.)
- **Role-Based Powers**: 9 files (ambusher, artillery, controller, etc.)
- **Species-Specific Powers**: 4 files (dwarf, gnome, halfling, orc)
- **Legendary Powers**: 5 files (attack, features, move, score, special)
- **General Powers**: 3+ files (spell, attack, all)

This is a long-running task requiring systematic review of each power file and assignment of appropriate tags from our 174-tag system. Each power class needs individual consideration for proper tag combinations.

### Phase 3: Monster Tag Assignment ⏳ PENDING
- [ ] Generate comprehensive list of all monsters/creatures
- [ ] Systematically assign tags to each creature

This phase will begin after substantial completion of Phase 2.