---
title: Dynamic TTRPG Encounters with Tokens | Foe Foundry
description: Dynamic battlefield Tokens make your TTRPG combat unforgettable. Learn how to use traps, spells, and magical hazards with Foe Foundry to shape the flow of battle.
image: img/blog/trap.webp
footer:
  - Art by Carlos Castilho. Used with permission.
json_ld: true
---

# Dynamic TTRPG Encounters with Tokens

## What is a Token?

TTRPG combat can get stale if each combat follows a predictable pattern of choosing a particular target to focus fire and hitting it until it's dead, then repeating the process on the next enemy until the encounter is done. This sort of combat is *static* as opposed to *dynamic*. To keep combats fun, interactive, and tactically interesting, it's important that we introduce dynamic and interactive effects.

A **Token** is a great way to achieve this effect and can represent things as diverse as:

- an **Object** on the battlefield. Ex: a **Net token** or **Spike Trap token** trapping 
- an **Environmental Effect** (like a **Howling Winds token** battering the party in a narrow corridor unless they can close the door where the wind originates)
- a **Magical Effect** (like a **Runic Wards token** that protects an [[Abjurer Mage]]).
- a [Monument of Power](https://slyflourish.com/ancient_monuments.html) (a concept coined by Mike Shea of SlyFlourish) like an **Altar of Skulls token** that empowers nearby undead with additional necrotic damage

Tokens are created by [Foe Foundry Monster Powers](../powers/emanation.md), but you can also use these mechanics to handle situations where players want to set up their own objects or interact with other objects or effects in your encounter.

![Tokens are a great way to add interactive combat elements like traps!](../img/blog/trap.webp){.masked .blog-image-large}

## Defining a Token

A **Token** is a battlefield object created by spells, abilities, or environmental effects. Tokens persist until they are destroyed or their effect ends naturally.

Each Token has:

- **Effect**: an ongoing or triggered effect caused by the Token, such as dealing damage or summoning additional creatures
- **Charges**: when all charges are depleted, the Token is destroyed. Players can attack or interact with a **Token** to deplete its charges
- **AC/DC Threshold**: attacks must hit the AC to remove a charge. Spells, abilities, or skill checks must succeed against the DC to affect it. If the token imposes an effect or condition that requires a save, this is the DC of the save as well

## How Players Interact with Tokens

Players can interact with a Token either by attacking it directly, or by utilizing skills, spells, abilities, or items to attempt to damage, disable, or modify it in some way.

### Attacking a Token

- A Token can be attacked. If the attack hits the AC/DC, the Token loses 1 charge
- The GM may impose advantage or disadvantage depending on the type of attack and token
	- Ex: attacking a **Net token** with a bludgeoning weapon may be at disadvantage
	- Ex: dousing a **Flame Rune token** with a *Ray of Frost* spell may be at advantage 

### Using Spells, Abilities, or Items to Interact with a Token

- Players may interact with a Token using skills, spells, abilities, or items
- The GM will ask the player to make an appropriate ability check against the Token's AC/DC
- On a success, the token loses 1 charge
- The GM may consider automatically granting a success if the player used a limited resource, such a spell slot, item charge, or class feature

If the player uses a spell or ability that would normally require the token to make a save, you can instead call for the PC to make an appropriate ability check against the token's AC/DC, or you may instead simply rule it as a success given that the player utilized a limited resource.  

As an example, if a player chooses to use *Blindness/Deafness* to blind a **Floating Occular Laser token** with an AC/DC 12 you could simply rule this as a success and remove one of the tokens charges, or you could call for the player to make a DC 12 spellcasting ability check.

## Example Combat: Using a **Runic Wards token**

Let's walk through an example combat with an [[Abjurer Archmage]] who will be using the **Runic Wards** token power.

[[!Runic Wards]]

[[!Abjurer Archmage]]

The vibe we want for this combat is that the abjurer is either creating powerful wards to protect themselves or has already prepared the environment with these powerful defensive wards.  

> DM: As Boldrak rages and charges towards the Archmage she lets out a chuckle - "Your headlong charge is as foolish as it is impotent" - and with a wave of her hand three glowing Runic Wards appear above her head and form a complex series of interlocking patterns. You can tell this is powerful protective magic  
>  
> Merla: I fire my longbow at the mage to wipe that smug grin off her face. I get a 28 to hit.  
>  
> DM: You can tell your aim is true, but the arrow vaporizes when it hits the runic shield. You can tell that these Runic Wards are giving the archmage immunity to damage until they're dealt with  
>  
> Merla: Damn... well OK let me see if I can destroy one of the runes. Can I try to shoot one of the runes out of the sky?  
>  
> DM: Of course! Go ahead and make an attack.  
>  
> Merla: I got a 19 to hit.  
>  
> DM: (Checking the AC/DC of the rune, which is 18...) Perfect. Your second shot strikes true and destroys one of the runes. Now there are only two left (one of the token's charges is now depleted)  
>  
> Belmund: I want to use my mage hand and try to disable one of the runes  
>  
> DM: OK, give me a sleight of hand check, but at disadvantage because it'll be hard to get the timing right considering the spinning interlocking shields  
>  
> Belmund: I got a 15, is that enough?  
>  
> DM: Sorry, the Archmage turns and gives you a haughty laugh as your mage hand incinerates upon contact with the spinning shields  

In this example above, we can see how the token served two purposes:

- It created a unique and unexpected situation. Players aren't used to a monster getting complete damage immunity! But it did this in a balanced way where there is still a clear mechanism for the PCs to remove the effect
- It took some heat off the boss, allowing the Archmage to have some breathing room instead of being tag-teamed by 4 PC's attacks

## How to Use Tokens as a GM (Best Practices)

- Let players be creative! There's a whole world of opportunity for how the players might want to interact with a token. Lean in to whatever ideas the players propose and fall back to the rules described above to adjudicate if there's a chance of failure. You can always impose disadvantage if the idea is completely insane.
- Tokens should have a noticeable and immediate impact, otherwise there is no motivation for the players to interact with the token
- If a token imposes an effect, it's usually simpler to have that effect happen at the start or end of the turn of any character within the effect range of the token
- However, if the token needs to take its own turn, simply have the token join initiative count 0
- You can use Tokens to telegraph powerful abilities. For example, a powerful [[Conjurer Primagus]] could place a **Meteor Swarm Beckoning token** on the map that calls down a *Meteor Swarm* at the end of its second turn
- If a monster creates a Token, be sure this is either as a bonus action or a replacement effect of one of its multiattacks so that the monster's action economy isn't harmed too much by creating the token

## Why Don't Tokens have HP?

Some rules text will create named objects, like a Net, that have dedicated HP and AC and sometimes even damage vulnerabilities or immunities. The Token system is much more succinct and generalizes better. You don't have to spell out that a net has fire vulnerability and bludgeoning resistance and track specific HP of the net. Instead, if the player uses a fire ability against the net just automatically remove a charge or give the check advantage, and if the player uses a bludgeoning attack to try and smash the net, give the attack disadvantage.  

Tokens don't have HP because it's a lot easier to count charges instead of hitpoints. You can also visually describe the charges as glowing runes, whirring components of the trap, etc, so you can give players clear feedback on how much more work they need to do to disable it.

## Get Started with Foe Foundry

You can use Foe Foundry's monster builder to summon monsters using these exciting Token abilities!  

<a href="https://foefoundry.com/generate" class="burnt-parchment burnt-parchment-button branding">Summon your own monsters with Foe Foundry</a>