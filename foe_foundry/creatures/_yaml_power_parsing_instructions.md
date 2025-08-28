## Translating Powers to YAML

- Create a well-defined declarative YAML schema that represents the `PowerLoadout` logic that is found in `creatures/<monster>/powers.py`. See **Translating Powers to YAML**

```python
PerksPetrifying = petrifying.PetrifyingPowers

PerksMagicalNature = [
    basilisk.StoneMolt,
    basilisk.StoneEater,
    poison.PoisonousBlood,
    tough.MagicResistance,
    tough.LimitedMagicImmunity,
    anti_ranged.AdaptiveCamouflage,
    serpentine.SerpentineHiss,
]

PerksPredator = [
    bestial.RetributiveStrike,
    beast.WildInstinct,
    beast.FeedingFrenzy,
    monstrous.Frenzy,
    reckless.Charger,
    bestial.BurrowingAmbush,
    beast.BestialRampage,
    monstrous.Rampage,
    monstrous.TearApart,
    monstrous.JawClamp,
    technique.BleedingAttack,
    technique.ProneAttack,
    technique.PoisonedAttack,
]

PerksBroodmother = [basilisk.BasiliskBrood]

LoadoutBasilisk = [
    PowerLoadout(
        name="Petrification",
        flavor_text="The basilisk's petrifying gaze is its most feared weapon",
        powers=PerksPetrifying,
    ),
    PowerLoadout(
        name="Magical Nature",
        flavor_text="The basilisk's blood is infused with arcane magic",
        powers=PerksMagicalNature,
    ),
    PowerLoadout(
        name="Predator",
        flavor_text="The basilisk's jaws are deadly to its prey",
        powers=PerksPredator,
    ),
]

LoadoutBasiliskBroodmother = LoadoutBasilisk + [
    PowerLoadout(
        name="Broodmother",
        flavor_text="The broodmother jealously guards her young",
        powers=PerksBroodmother,
    )
]
```

```yaml
petrifying: &petrifying
  - power1
  - power2
  - power3
magical_nature: &magical_nature
  - StoneMolt
  - StoneEater
  - PoisonousBlood
  - ...
predator: &predator
  - RetributiveStrike
  - WildInstinct
  - ...
broodmother: &broodmother
  - BasiliskBrood

loadouts:
  basilisk:
    <<: *petrifiying
    <<: *magical_nature
    <<: *predator

  basilisk_broodmother:
    <<: *petrifying
    <<: *magical_nature
    <<: *predator
```