---
title: Foe Foundry Design Philosophy | Create Better 5E Monsters
description: Learn the core monster design philosophy behind Foe Foundry - a GM toolset for creating flavorful, powerful, and easy-to-run D&D 5E monsters using 200+ unique powers and procedurally generated abilities.
image: img/foe_foundry_icon.png
json_ld: true
---

# Foe Foundry Design Philosophy


<a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> is a toolkit for Game Masters to create powerful, flavorful, and easy-to-run monsters for 5th Edition and fantasy TTRPGs.

<a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> gives GMs the tools to create exciting, unique monsters without the grind. Summon foes packed with flavorful abilities, scale them instantly to your party’s level, and get back to what matters — having fun and thrilling your players. With a growing library of handcrafted powers and templates, Foe Foundry makes monster creation fast, fun, and unforgettable.  
Built by a GM for GMs, because your monsters (and even your peaky players) deserve better.

---

## Why Foe Foundry?

Too many monster statblocks are forgettable. They're either bloated with fiddly mechanics or stripped down to the point of boredom. Foe Foundry monsters aim to hit the sweet spot: **easy to run**, **mechanically exciting**, and **thematically unforgettable**.

We reimagined custom TTRPG monster design to be more dynamic, memorable, and intuitive to use at the table, taking inspiration from excellent monster innovations in books like [Forge of Foes](https://slyflourish.com/build_a_quick_monster_with_forge_of_foes.html) and systems like Level Up: Advanced 5E.  

Foe Foundry is a 5E monster builder that expands on these innovations by making it really easy to create unique CR-scaled monsters while also following design philosophies that lead to more engagement and interesting monsters. You can use these encounter design tools to scale monsters and encounters to any situation!

---

## Monster Design Principles

- **Monsters should be powerful, flavorful, and easy to run**. No more boring french-vanilla "Bite Claw Claw" monsters.
- **The primary threat of a monster should come from its damage.** If you just multiattack with the monster, it should present a challenge in its raw damage output. Abilities should then add interesting flavor, unique mechanics, and other tactical effects to make combat exciting
- **Monsters shouldn't have to sacrifice damage output to do something interesting**. Foe Foundry monsters often have bonus actions or powerful actions that can replace attacks in the multiattack. This way, your monster will always do something interesting on its turn and still be able to threaten players with damage output
- **Monsters should have a clearly identified role**. Foe Foundry monsters have explicit roles that dictate their behavior and combat style. For example, monsters may be brutes, ambushers, leaders, etc. This leads to interesting encounters but also makes the monster easier to run.
- **Monsters are procedurally generated using 200+ Unique Powers**. These unique powers are assigned to monsters based on their creature type, role, CR, size, attributes, skill proficiencies, etc. The powers automatically scale damage, range, DCs, etc. based on the creature they're being applied to!
- **Monsters should use interactive debuffs** - instead of paralyzing a character, Foe Foundry monsters use new conditions like **Dazed**, **Shocked**, **Frozen**, etc. These conditions take away less player agency and are more interactive than their harsher cousins like Paralyzed and Stunned.

---

## How Does Monster Generation Work?

1. You choose a hand-crafted [**Monster Template**](../monsters/index.md) like [[Spirits]] or [[Manticores]]
1. Each template has multiple **Variants** that represent different roles and/or CRs related to the monster. For example, a [[Ghost]] vs [[Specter]] for [[Spirits]] or a [[Manticore]] vs [[Manticore Ravager]]
1. Some humanoid templates also let you choose a **Species** to further customize the creature!
1. <a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> then selects powers for the creature based on a menu of 400+ powers using a series of sophisticated algorithms and random weightings

Each monster template and power was meticulously designed, implemented, and balanced by me. Foe Foundry doesn't produce AI slop!

---

## Foe Foundry vs the Monster Manual

Wondering how <a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> compares to the official *Monster Manual*?  

Here’s a side-by-side look at how our monster design toolkit improves the GM experience for your 5E TTRPGs:

| Feature | **Monster Manual** | **Foe Foundry** |
|--------|---------------------|------------------|
| **Monster Variety** | Many iconic creatures like **Orcs** and **Drow** rely on generic humanoid statblocks with light reflavoring. | Every monster has a **bespoke statblock**, plus optional **species templates** to customize NPCs in seconds. |
| **Lore and Encounters** | Lore is minimal and rarely connects to specific mechanics. No adventures or encounter suggestions included. | Every monster includes rich **lore**, **tactics**, and **encounter hooks** to spark ideas and make running them effortless. |
| **Customization** | Offers little guidance on how to tweak monsters for flavor or mechanics. | Designed for customization. Swap out powers, adjust species, or tweak CR easily with built-in scaling and templates. |
| **CR Scaling** | No official guidance on how to increase or decrease a monster’s CR. | Monsters **automatically scale** — powers adjust damage, DCs, and effects based on the monster’s level and stats. |
| **Design Philosophy** | Many monsters sacrifice threat level to do something “interesting” or waste actions on subpar abilities. | Monsters are **lethal and flavorful**, with mechanics that **never waste a turn** and always feel dynamic in combat. |

---

## Monster Statistic Baselines

Foe Foundry uses monster baselines that are then increased or decreased by each template. The baselines are based on work in the [Lazy 5E Monser Building Resource Document](https://slyflourish.com/lazy_5e_monster_building_resource_document.html). See [Credits](credits.md) for more information on this work.


<table>
    <tbody><tr>
      <th>CR</th>
      <th>Eqv Char Lvl</th>
      <th>AC/DC</th>
      <th>HP</th>
      <th>Prof Bonus</th>
      <th>Damage per Round</th>
      <th># Attacks</th>
      <th>Damage</th>
      <th>Example Monster</th>
    </tr>
    <tr>
      <td>0</td>
      <td>&lt; 1</td>
      <td>10</td>
      <td>3 (2-4)</td>
      <td>+2</td>
      <td>2</td>
      <td>1</td>
      <td>2 (1d4)</td>
      <td>Commoner, rat, spider</td>
    </tr>
    <tr>
      <td>1/8</td>
      <td>&lt; 1</td>
      <td>11</td>
      <td>9 (7-11)</td>
      <td>+3</td>
      <td>3</td>
      <td>1</td>
      <td>4 (1d6 + 1)</td>
      <td>Bandit, cultist, giant rat</td>
    </tr>
    <tr>
      <td>1/4</td>
      <td>1</td>
      <td>11</td>
      <td>13 (10-16)</td>
      <td>+3</td>
      <td>5</td>
      <td>1</td>
      <td class="nowrap">5 (1d6 + 2)</td>
      <td>Acolyte, skeleton, wolf</td>
    </tr>
    <tr>
      <td>1/2</td>
      <td>2</td>
      <td>12</td>
      <td class="nowrap">22 (17-28)</td>
      <td>+4</td>
      <td>8</td>
      <td>2</td>
      <td class="nowrap">4 (1d4 + 2)</td>
      <td>Black bear, scout, shadow</td>
    </tr>
    <tr>
      <td>1</td>
      <td>3</td>
      <td>12</td>
      <td>33 (25-41)</td>
      <td>+5</td>
      <td>12</td>
      <td>2</td>
      <td>6 (1d8 + 2)</td>
      <td>Dire wolf, specter, spy</td>
    </tr>
    <tr>
      <td>2</td>
      <td>5</td>
      <td>13</td>
      <td>45 (34-56)</td>
      <td>+5</td>
      <td>17</td>
      <td>2</td>
      <td>9 (2d6 + 2)</td>
      <td>Ghast, ogre, priest</td>
    </tr>
    <tr>
      <td>3</td>
      <td>7</td>
      <td>13</td>
      <td>65 (49-81)</td>
      <td>+5</td>
      <td>23</td>
      <td>2</td>
      <td>12 (2d8 + 3)</td>
      <td>Knight, mummy, werewolf</td>
    </tr>
    <tr>
      <td>4</td>
      <td>9</td>
      <td>14</td>
      <td>84 (64-106)</td>
      <td>+6</td>
      <td>28</td>
      <td>2</td>
      <td>14 (3d8 + 1)</td>
      <td>Ettin, ghost</td>
    </tr>
    <tr>
      <td>5</td>
      <td>10</td>
      <td>15</td>
      <td>95 (71-119)</td>
      <td>+7</td>
      <td>35</td>
      <td>3</td>
      <td>12 (3d6 + 2)</td>
      <td>Elemental, gladiator, vampire spawn</td>
    </tr>
    <tr>
      <td>6</td>
      <td>11</td>
      <td>15</td>
      <td>112 (84-140)</td>
      <td>+7</td>
      <td>41</td>
      <td>3</td>
      <td>14 (3d6 + 4)</td>
      <td>Mage, medusa, wyvern</td>
    </tr>
    <tr>
      <td>7</td>
      <td>12</td>
      <td>15</td>
      <td>130 (98-162)</td>
      <td>+7</td>
      <td>47</td>
      <td>3</td>
      <td>16 (3d8 + 3)</td>
      <td>Stone giant, young black dragon</td>
    </tr>
    <tr>
      <td>8</td>
      <td>13</td>
      <td>15</td>
      <td>136 (102-170)</td>
      <td>+7</td>
      <td>53</td>
      <td>3</td>
      <td>18 (3d10 + 2)</td>
      <td>Assassin, frost giant</td>
    </tr>
    <tr>
      <td>9</td>
      <td>15</td>
      <td>16</td>
      <td>145 (109-181)</td>
      <td>+8</td>
      <td>59</td>
      <td>3</td>
      <td>19 (3d10 + 3)</td>
      <td>Bone devil, fire giant, young blue dragon</td>
    </tr>
    <tr>
      <td>10</td>
      <td>16</td>
      <td>17</td>
      <td>155 (116-194)</td>
      <td>+9</td>
      <td>65</td>
      <td>4</td>
      <td>16 (3d8 + 3)</td>
      <td>Stone golem, young red dragon</td>
    </tr>
    <tr>
      <td>11</td>
      <td>17</td>
      <td>17</td>
      <td>165 (124-206)</td>
      <td>+9</td>
      <td>71</td>
      <td>4</td>
      <td>18 (3d10 + 2)</td>
      <td>Djinni, efreeti, horned devil</td>
    </tr>
    <tr>
      <td>12</td>
      <td>18</td>
      <td>17</td>
      <td>175 (131-219)</td>
      <td>+9</td>
      <td>77</td>
      <td>4</td>
      <td>19 (3d10 + 3)</td>
      <td>Archmage, erinyes</td>
    </tr>
    <tr>
      <td>13</td>
      <td>19</td>
      <td>18</td>
      <td>184 (138-230)</td>
      <td>+10</td>
      <td>83</td>
      <td>4</td>
      <td>21 (4d8 + 3)</td>
      <td>Adult white dragon, storm giant, vampire</td>
    </tr>
    <tr>
      <td>14</td>
      <td>20</td>
      <td>19</td>
      <td>196 (147-245)</td>
      <td>+11</td>
      <td>89</td>
      <td>4</td>
      <td>22 (4d10)</td>
      <td>Adult black dragon, ice devil</td>
    </tr>
    <tr>
      <td>15</td>
      <td>&gt; 20</td>
      <td>19</td>
      <td>210 (158-263)</td>
      <td>+11</td>
      <td>95</td>
      <td>5</td>
      <td>19 (3d10 + 3)</td>
      <td>Adult green dragon, mummy lord, purple worm</td>
    </tr>
    <tr>
      <td>16</td>
      <td>&gt; 20</td>
      <td>19</td>
      <td>229 (172-286)</td>
      <td>+11</td>
      <td>101</td>
      <td>5</td>
      <td>21 (4d8 + 3)</td>
      <td>Adult blue dragon, iron golem, marilith</td>
    </tr>
    <tr>
      <td>17</td>
      <td>&gt; 20</td>
      <td>20</td>
      <td>246 (185-308)</td>
      <td>+12</td>
      <td>107</td>
      <td>5</td>
      <td>22 (3d12 + 3)</td>
      <td>Adult red dragon</td>
    </tr>
    <tr>
      <td>18</td>
      <td>&gt; 20</td>
      <td>21</td>
      <td>266 (200-333)</td>
      <td>+13</td>
      <td>113</td>
      <td>5</td>
      <td>23 (4d10 + 1)</td>
      <td>Demilich</td>
    </tr>
    <tr>
      <td>19</td>
      <td>&gt; 20</td>
      <td>21</td>
      <td>285 (214-356)</td>
      <td>+13</td>
      <td>119</td>
      <td>5</td>
      <td>24 (4d10 + 2)</td>
      <td>Balor</td>
    </tr>
    <tr>
      <td>20</td>
      <td>&gt; 20</td>
      <td>21</td>
      <td>300 (225-375)</td>
      <td>+13</td>
      <td>132</td>
      <td>5</td>
      <td>26 (4d12)</td>
      <td>Ancient white dragon, pit fiend</td>
    </tr>
    <tr>
      <td>21</td>
      <td>&gt; 20</td>
      <td>22</td>
      <td>325 (244-406)</td>
      <td>+14</td>
      <td>150</td>
      <td>5</td>
      <td>30 (4d12 + 4)</td>
      <td>Ancient black dragon, lich, solar</td>
    </tr>
    <tr>
      <td>22</td>
      <td>&gt; 20</td>
      <td>23</td>
      <td>350 (263-438)</td>
      <td>+15</td>
      <td>168</td>
      <td>5</td>
      <td>34 (4d12 + 8)</td>
      <td>Ancient green dragon</td>
    </tr>
    <tr>
      <td>23</td>
      <td>&gt; 20</td>
      <td>23</td>
      <td>375 (281-469)</td>
      <td>+15</td>
      <td>186</td>
      <td>5</td>
      <td>37 (6d10 + 4)</td>
      <td>Ancient blue dragon, kraken</td>
    </tr>
    <tr>
      <td>24</td>
      <td>&gt; 20</td>
      <td>23</td>
      <td>400 (300-500)</td>
      <td>+15</td>
      <td>204</td>
      <td>5</td>
      <td>41 (6d10 + 8)</td>
      <td>Ancient red dragon</td>
    </tr>
    <tr>
      <td>25</td>
      <td>&gt; 20</td>
      <td>24</td>
      <td>430 (323-538)</td>
      <td>+16</td>
      <td>222</td>
      <td>5</td>
      <td>44 (6d10 + 11)</td>
      <td></td>
    </tr>
    <tr>
      <td>26</td>
      <td>&gt; 20</td>
      <td>25</td>
      <td>460 (345-575)</td>
      <td>+17</td>
      <td>240</td>
      <td>5</td>
      <td>48 (6d10 + 15)</td>
      <td></td>
    </tr>
    <tr>
      <td>27</td>
      <td>&gt; 20</td>
      <td>25</td>
      <td>490 (368-613)</td>
      <td>+17</td>
      <td>258</td>
      <td>5</td>
      <td>52 (6d10 + 19)</td>
      <td></td>
    </tr>
    <tr>
      <td>28</td>
      <td>&gt; 20</td>
      <td>25</td>
      <td>540 (405-675)</td>
      <td>+17</td>
      <td>276</td>
      <td>5</td>
      <td>55 (6d10 + 22)</td>
      <td></td>
    </tr>
    <tr>
      <td>29</td>
      <td>&gt; 20</td>
      <td>26</td>
      <td>600 (450-750)</td>
      <td>+18</td>
      <td>294</td>
      <td>5</td>
      <td>59 (6d10 + 26)</td>
      <td></td>
    </tr>
    <tr>
      <td>30</td>
      <td>&gt; 20</td>
      <td>27</td>
      <td class="nowrap">666 (500-833)</td>
      <td>+19</td>
      <td>312</td>
      <td>5</td>
      <td class="nowrap">62 (6d10 + 29)</td>
      <td>Tarrasque</td>
    </tr>
  </tbody></table>