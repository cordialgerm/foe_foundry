---
title: Custom Conditions for 5E Monsters | FoeFoundry
short_title: Conditions
description: Explore Foe Foundry's unique custom conditions for 5E monsters. Interactive status effects like Frozen, Bleeding, and Swallowed that add tactical depth without removing player agency.
image: img/icons/favicon.webp
json_ld: true
---

# Conditions

<a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> introduces several custom conditions that monsters can inflict on player characters in your 5E TTRPG game.

These conditions are designed to be more interactive than standard 5E conditions such as **Stunned** and **Paralyzed**. These custom conditions don't take away an entire player's turn, but usually offer that player a choice if they want to use their action defensively to remove the debuff or if they want to keep using their action offensively and accept the risk or downside that the condition imposes.  

Don't worry, <a alt="Foe Foundry Skull" href="https://foefoundry.com" class="branding">Foe Foundry</a> monsters can afford to be more "lenient" in the conditions that they apply because their action economy is designed such that applying these conditions is a side effect of doing damage to PCs. In other words, Foe Foundry monsters don't rely on paralyzing a PC to be threatening.  


## Dazed

!!! info
    The Dazed condition is like a light version of incapacitated that doesn't take away the player's entire turn.

A <span class='condition condition-dazed'>Dazed</span> creature can move or take an action on its turn, but not both. It cannot take bonus actions or free object interactions.

## Frozen

!!! info
    The Frozen condition is a nice interactive condition because it imposes a debuff that presents the player with interesting choices and options for creative mechanisms to escape the debuff. It also sets up interesting combinations between monsters if another monster in the encounter deals bludgeoning damage.

A <span class='condition condition-frozen'>Frozen</span> creature is partially encased in ice. It has a movement speed of zero, attacks made against it are at advantage, and it is vulnerable to bludgeoning and thunder damage. A creature may use an action to perform a DC {dc} Strength (Athletics) check to break the ice and end the condition. The condition also ends whenever the creature takes any bludgeoning, thunder, or fire damage.

## Shocked

!!! info
    The Shocked condition can create interesting situations where players are forced to drop important weapons or quest items. Consider creating scenarios where enemies are trying to steal a particular weapon or item from the PCs and utilize shocking to try to force the PCs to drop the item.

A <span class='condition condition-shocked'>Shocked</span> creature is <span class='condition condition-dazed'>Dazed</span> and drops whatever it is carrying.

## Enraged

!!! info
    This ability is usually applied by the monster to itself as a buff.

An <span class='condition condition-enraged'>Enraged</span> creature has resistance to bludgeoning, piercing, and slashing damage. Attacks against it have advantage and its attacks have advantage.

## Swallowed

!!! info
    The Swallowed condition just codifies some abilities and behavior that various SRD monsters have had, such as the **Purple Worm**

A swallowed creature is <span class='condition condition-blinded'>Blinded</span>, <span class='condition condition-restrained'>Restrained</span>, and has total cover against attacks and effects from the outside. It takes `damage` ongoing Acid damage at the start of each of its turns. If the swallowing creature takes`regurgitate_damage_threshold` damage or more on a single turn from a creature inside it, it must make a DC `regurgitate_dc` Constitution saving throw at the end of that turn or regurgitate all swallowed creatures which fall <span class='condition condition-prone'>Prone</span> in a space within 10 feet of it. If the swallowing creature dies, the swallowed creature is no longer restrained by it and can escape by using 15 feet of movement, exiting prone.

## Engulfed

!!! info
    The Engulfed condition is designed to standardize certain interactions like what the [[Gelatinous Cube]] can do to players

A creature that is <span class='condition condition-engulfed'>Engulfed</span> is <span class='condition condition-restrained'>Restrained</span>, <span class='condition condition-suffocating'>Suffocating</span>, and cannot cast spells with Verbal components. It takes `damage` ongoing Acid damage at the end of each of its turns. It can spend an Action to make a DC `escape_dc` Athletics check to escape the engulfing creature.

## Weakened

!!! info
    The Weakened condition is another way to apply debuffs to players without taking away the entire player's turn.

A weakened creature deals half damage with its spells and attacks and has disadvantage on Strength ability checks and saving throws.

## Susceptible

!!! info
    Susceptibility is best used as a "wind up" ability, where the monster applies susceptibility to PCs and then prepares a big telegraphed ability. Then the PCs have a turn to decide how they want to address the situation.

A creature susceptible to `damage_type` ignores any immunity or resistance to `damage_type` that it may have. If it had no such immunity, it is instead vulnerable to `damage_type`.