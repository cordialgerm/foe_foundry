from datetime import datetime
from math import ceil
from typing import List

import numpy as np

from ...creature_types import CreatureType
from ...damage import AttackType, Burning, DamageType, Dazed, Frozen, Shocked
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...powers import PowerType
from ...statblocks import BaseStatblock
from ...utils import summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
    Power,
    PowerType,
    PowerWithStandardScoring,
)


class ElementalPower(PowerWithStandardScoring):
    def has_elemental_damage(self, b: BaseStatblock):
        return (
            b.secondary_damage_type is not None and b.secondary_damage_type.is_elemental
        )

    def __init__(
        self,
        name: str,
        source: str,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        **score_args,
    ):
        standard_score_args = dict(
            require_types=CreatureType.Elemental,
            require_callback=self.has_elemental_damage,
            **score_args,
        )
        super().__init__(
            name=name,
            power_type=PowerType.CreatureType,
            power_level=power_level,
            source=source,
            create_date=create_date,
            theme="Elemental",
            score_args=standard_score_args,
        )


def damaging_aura_power(name: str, damage_type: DamageType) -> Power:
    class _DamagingAura(ElementalPower):
        def __init__(self):
            super().__init__(
                name=name,
                power_level=HIGH_POWER,
                source="Foe Foundry",
                require_damage=damage_type,
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dmg = DieFormula.target_value(stats.cr)

            feature = Feature(
                name=name,
                description=f"Any creature who starts their turn within 10 feet of {stats.selfref} takes {dmg.description} {damage_type} damage",
                action=ActionType.Feature,
            )

            return [feature]

    return _DamagingAura()


def elemental_affinity_power(damage_type: DamageType) -> Power:
    name = f"{damage_type.name.capitalize()} Affinity"

    class _ElementalAffinity(ElementalPower):
        """This creature is aligned to a particular element"""

        def __init__(self):
            super().__init__(
                name=name,
                source="Foe Foundry",
                power_level=LOW_POWER,
                require_damage=damage_type,
            )

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            if stats.cr <= 8:
                stats = stats.grant_resistance_or_immunity(
                    resistances={damage_type},
                    upgrade_resistance_to_immunity_if_present=True,
                )
            else:
                stats = stats.grant_resistance_or_immunity(immunities={damage_type})

            return stats

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            upgrade_to_immunity = (
                damage_type in stats.damage_immunities
                or damage_type in stats.damage_resistances
            )

            descr = "immunity" if upgrade_to_immunity else "resistance"

            feature = Feature(
                name=f"{damage_type.capitalize()} Affinity",
                description=f"{stats.selfref.capitalize()} gains {descr} to {damage_type} damage. It gains advantage on its attacks while it is in an environment where sources of {damage_type} damage are prevalant.",
                action=ActionType.Feature,
            )

            return [feature]

    return _ElementalAffinity()


def elemental_burst_power(damage_type: DamageType) -> Power:
    name = damage_type.adj.capitalize() + " Burst"

    class _ElementalBurst(ElementalPower):
        def __init__(self):
            super().__init__(
                name=name,
                source="Foe Foundry",
                require_damage=damage_type,
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            uses = int(ceil(stats.cr / 5))
            dmg = stats.target_value(0.75)
            distance = 5 if stats.cr <= 7 else 10
            dc = stats.difficulty_class
            feature = Feature(
                name=name,
                action=ActionType.Reaction,
                uses=uses,
                description=f"When {stats.selfref} is hit by a melee attack, their form explodes with {damage_type.adj} energy. \
                    Each other creature within {distance} ft must make a DC {dc} Dexterity saving throw, \
                    taking {dmg.description} {damage_type} damage on a failure and half as much damage on a success.",
            )
            return [feature]

    return _ElementalBurst()


class _ElementalFireball(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Elemental Fireball",
            source="Foe Foundry",
            require_damage=DamageType.Fire,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Fireball"
        dc = stats.difficulty_class
        dmg_type = DamageType.Fire
        dmg = stats.target_value(1.6, force_die=Die.d6)
        description = f"{stats.selfref.capitalize()} targets a 20 ft sphere at a point it can see within 150 feet. A fiery explosion fills the space. \
            All creatures within the space must make a DC {dc} Dexterity saving throw, taking {dmg.description} {dmg_type} damage on a failure and half as much on a success."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _AcidicBlast(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Acidic Blast",
            source="Foe Foundry",
            require_damage=DamageType.Acid,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Acidic Blast"
        dc = stats.difficulty_class
        dmg_type = DamageType.Acid
        dmg = stats.target_value(1.6, force_die=Die.d4)

        # acid damage is always done in d4s and should be an even number
        # this is because the ongoing damage should be half that amount
        dmg = stats.target_value(1.0, force_die=Die.d4, force_even=True)
        ongoing = DieFormula.from_dice(**{Die.d4: dmg.n_die // 2})
        burning = Burning(damage=ongoing, damage_type=DamageType.Acid)

        description = f"{stats.selfref.capitalize()} targets a 20 ft sphere at a point it can see within 150 feet. A volatile sphere of acid explodes, inundating the space. \
            All creatures within the space must make a DC {dc} Dexterity saving throw. On a failed save, a creature takes {dmg.description} {dmg_type} damage and gains {burning} on a failed save. On a success, a creature takes half as much damage and is not burning."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _ConeOfCold(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Cone of Cold",
            source="Foe Foundry",
            require_damage=DamageType.Cold,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Cone of Cold"
        dc = stats.difficulty_class
        dmg_type = DamageType.Cold
        dmg = stats.target_value(1.6, force_die=Die.d8)
        description = f"{stats.selfref.capitalize()} releases a blast of cold air in a 60 foot cone. Each creature in the area must make a DC {dc} Constitution save, \
            taking {dmg.description} {dmg_type} damage on a failure and half as much on a success."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _LightningBolt(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Lightning Bolt",
            source="Foe Foundry",
            require_damage=DamageType.Lightning,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Lightning Bolt"
        dc = stats.difficulty_class
        dmg_type = DamageType.Lightning
        dmg = stats.target_value(1.6, force_die=Die.d6)
        description = f"{stats.selfref.capitalize()} releases a crackling bolt of lightning in a 100 ft line that is 5 ft wide. Each creature in the line must make a DC {dc} Dexterity save, \
            taking {dmg.description} {dmg_type} on a failure and half as much on a success."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _PoisonCloud(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Poison Cloud",
            source="Foe Foundry",
            require_damage=DamageType.Poison,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Poison Cloud"
        dc = stats.difficulty_class
        dmg_type = DamageType.Poison
        duration = DieFormula.from_expression("1d4 + 2")
        dmg = stats.target_value(1.6, force_die=Die.d6)
        description = f"{stats.selfref.capitalize()} creates a 20-ft radius cloud of toxic gas centered at a point it can see within 60 feet. Each creature that starts its turn in the cloud \
            must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg.description} {dmg_type} damage and is **Poisoned** until the end of its next turn. On a success, a creature takes half as much damage and is not poisoned. \
            The cloud lasts for {duration.description} and can be dispersed by a light breeze."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _Thunderwave(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Thunderwave",
            source="Foe Foundry",
            require_damage=DamageType.Thunder,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Thunderwave"
        dc = stats.difficulty_class
        dmg_type = DamageType.Thunder
        dmg = stats.target_value(1.6, force_die=Die.d10)
        description = f"{stats.selfref.capitalize()} releases a burst of thundrous energy in a 15 ft. cube originating from {stats.selfref}. \
            Each creature in the area must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg.description} {dmg_type} thunder damage and is knocked up to 10 feet away and lands **Prone**. \
            On a success, a creature takes half as much damage and is not knocked prone."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


def elemental_smite_power(dmg_type: DamageType) -> Power:
    name = f"{dmg_type.adj.capitalize()} Smite"

    class _ElementalSmite(ElementalPower):
        def __init__(self):
            super().__init__(
                name=name,
                source="Foe Foundry",
                require_damage=dmg_type,
                require_attack_types=AttackType.AllMelee(),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class
            dmg_target = 0.5

            if dmg_type == DamageType.Fire:
                burning = Burning(DieFormula.from_expression("1d10"))
                dmg = stats.target_value(dmg_target, force_die=Die.d10)
                condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
            elif dmg_type == DamageType.Acid:
                dmg = stats.target_value(dmg_target, force_die=Die.d4)
                burning = Burning(DieFormula.from_expression("2d4"), DamageType.Acid)
                condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
            elif dmg_type == DamageType.Cold:
                dmg = stats.target_value(dmg_target, force_die=Die.d8)
                frozen = Frozen(dc=dc)
                condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {frozen.caption}. {frozen.description_3rd}"
            elif dmg_type == DamageType.Lightning:
                dmg = stats.target_value(dmg_target, force_die=Die.d6)
                shocked = Shocked()
                condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {shocked.caption} until the end of its next turn. {shocked.description_3rd}"
            elif dmg_type == DamageType.Poison:
                dmg = stats.target_value(dmg_target, force_die=Die.d8)
                condition = f"and forces the target to make a DC {dc} Constitution saving throw or become **Poisoned** for 1 minute (save ends at end of turn)."
            elif dmg_type == DamageType.Thunder:
                dmg = stats.target_value(dmg_target, force_die=Die.d8)
                dazed = Dazed()
                condition = f"and force the target to make a DC {dc} Constitution saving throw. On a failure, the target is {dazed.caption} until the end of its next turn. {dazed.description_3rd}"
            else:
                raise NotImplementedError(f"{dmg_type} is not supported")

            description = f"Immediately after hitting with an attack, {stats.selfref} deals an additional {dmg.description} {dmg_type} damage to the target {condition}"

            feature = Feature(
                name=name,
                action=ActionType.BonusAction,
                description=description,
                recharge=5,
            )
            return [feature]

    return _ElementalSmite()


class _ElementalReplication(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Elemental Replication",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            require_secondary_damage_type=True,
            require_cr=4.0,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        # TODO - remove randomness
        rng = np.random.default_rng(20210518)
        _, _, description = summoning.determine_summon_formula(
            summoner=stats.secondary_damage_type,
            summon_cr_target=stats.cr / 4.0,
            rng=rng,
        )

        feature = Feature(
            name="Elemental Replication",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.selfref.capitalize()} overflows with elemental energy and replicates. {description}",
        )

        return [feature]


damage_aura_data = {
    DamageType.Acid: "Corrosive Fumes",
    DamageType.Bludgeoning: "Flurry of Blows",
    DamageType.Cold: "Arctic Chill",
    DamageType.Fire: "Superheated",
    DamageType.Force: "Disintegrating Presence",
    DamageType.Lightning: "Arcing Electricity",
    DamageType.Necrotic: "Deathly Presence",
    DamageType.Piercing: "Bristling",
    DamageType.Poison: "Toxic Presence",
    DamageType.Psychic: "Unsettling Presence",
    DamageType.Radiant: "Holy Presence",
    DamageType.Slashing: "Constant Slashing",
}

DamagingAuraPowers = [
    damaging_aura_power(name, damage_type)
    for damage_type, name in damage_aura_data.items()
]
ElementalAffinityPowers = [
    elemental_affinity_power(dt) for dt in DamageType.Elemental()
]
ElementalSmitePowers = [elemental_smite_power(dt) for dt in DamageType.Elemental()]
ElementalBurstPowers = [elemental_burst_power(dt) for dt in DamageType.Elemental()]

ElementalFireball = _ElementalFireball()
AcidicBlast = _AcidicBlast()
ConeOfCold = _ConeOfCold()
LightningBolt = _LightningBolt()
PoisonCloud = _PoisonCloud()
Thunderwave = _Thunderwave()
ElementalReplication = _ElementalReplication()

ElementalPowers = (
    DamagingAuraPowers
    + ElementalAffinityPowers
    + ElementalBurstPowers
    + ElementalSmitePowers
    + [
        AcidicBlast,
        ConeOfCold,
        ElementalFireball,
        ElementalReplication,
        LightningBolt,
        PoisonCloud,
        Thunderwave,
    ]
)
