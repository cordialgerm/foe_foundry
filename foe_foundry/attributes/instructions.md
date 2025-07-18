# INSTRUCTIONS:

We're going to work together to create a new utility that generalizes a lot of boilerplate code in this repository.

I will start by explainig the problem statement. As part of creating statblocks, I need to invoke


```python
        # STATS
        stats = base_stats(
            name=name,
            variant_key=settings.variant.key,
            template_key=settings.monster_template,
            monster_key=settings.monster_key,
            cr=cr,
            stats=[
                Stats.STR.scaler(StatScaling.Primary),
                Stats.DEX.scaler(StatScaling.Medium, mod=1),
                Stats.INT.scaler(StatScaling.Medium, mod=4),
                Stats.WIS.scaler(StatScaling.Medium, mod=2),
                Stats.CHA.scaler(StatScaling.Medium, mod=6),
            ],
            hp_multiplier=settings.hp_multiplier,
            damage_multiplier=settings.damage_multiplier,
        )
```
