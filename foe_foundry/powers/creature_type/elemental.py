from datetime import datetime
from math import ceil
from typing import List

from ...creature_types import CreatureType
from ...damage import AttackType, Burning, Condition, DamageType, Dazed, Frozen, Shocked
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ...utils import summoning
from ..power import (
    HIGH_POWER,
    LOW_POWER,
    MEDIUM_POWER,
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
        icon: str,
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
            reference_statblock="Fire Elemental",
            icon=icon,
            score_args=standard_score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Fire)
        return stats


class _DamagingAura(ElementalPower):
    def __init__(self, name: str, damage_type: DamageType, icon: str):
        super().__init__(
            name=name,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            require_damage=damage_type,
            icon=icon,
        )
        self.name = name
        self.damage_type = damage_type

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = DieFormula.target_value(stats.cr)

        feature = Feature(
            name=self.name,
            description=f"Any creature who starts their turn within 10 feet of {stats.selfref} takes {dmg.description} {self.damage_type} damage",
            action=ActionType.Feature,
        )

        return [feature]


class _ElementalAffinity(ElementalPower):
    """This creature is aligned to a particular element"""

    def __init__(self, damage_type: DamageType, icon: str):
        super().__init__(
            name=f"{damage_type.name.capitalize()} Affinity",
            source="Foe Foundry",
            power_level=LOW_POWER,
            require_damage=damage_type,
            icon=icon,
        )
        self.damage_type = damage_type

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.cr <= 8:
            stats = stats.grant_resistance_or_immunity(
                resistances={self.damage_type},
                upgrade_resistance_to_immunity_if_present=True,
            )
        else:
            stats = stats.grant_resistance_or_immunity(immunities={self.damage_type})

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        upgrade_to_immunity = (
            self.damage_type in stats.damage_immunities
            or self.damage_type in stats.damage_resistances
        )

        descr = "immunity" if upgrade_to_immunity else "resistance"

        feature = Feature(
            name=f"{self.damage_type.capitalize()} Affinity",
            description=f"{stats.selfref.capitalize()} gains {descr} to {self.damage_type} damage. It gains advantage on its attacks while it is in an environment where sources of {self.damage_type} damage are prevalant.",
            action=ActionType.Feature,
        )

        return [feature]


class _ElementalSmite(ElementalPower):
    def __init__(self, dmg_type: DamageType):
        name = f"{dmg_type.adj.capitalize()} Smite"

        super().__init__(
            name=name,
            source="Foe Foundry",
            require_damage=dmg_type,
            icon="saber-slash",
            require_attack_types=AttackType.AllMelee(),
        )
        self.dmg_type = dmg_type

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg_target = 0.5
        poisoned = Condition.Poisoned
        dmg_type = self.dmg_type

        if dmg_type == DamageType.Fire:
            burning = Burning(DieFormula.from_expression("1d10"))
            dmg = stats.target_value(target=dmg_target, force_die=Die.d10)
            condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
        elif dmg_type == DamageType.Acid:
            dmg = stats.target_value(target=dmg_target, force_die=Die.d4)
            burning = Burning(DieFormula.from_expression("2d4"), DamageType.Acid)
            condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {burning.caption}. {burning.description_3rd}"
        elif dmg_type == DamageType.Cold:
            dmg = stats.target_value(target=dmg_target, force_die=Die.d8)
            frozen = Frozen(dc=dc)
            condition = f"and forces the target to make a DC {dc} Constitution saving throw. On a failure, the target is {frozen.caption}. {frozen.description_3rd}"
        elif dmg_type == DamageType.Lightning:
            dmg = stats.target_value(target=dmg_target, force_die=Die.d6)
            shocked = Shocked()
            condition = f"and forces the target to make a DC {dc} Dexterity saving throw. On a failure, the target is {shocked.caption} until the end of its next turn. {shocked.description_3rd}"
        elif dmg_type == DamageType.Poison:
            dmg = stats.target_value(target=dmg_target, force_die=Die.d8)
            condition = f"and forces the target to make a DC {dc} Constitution saving throw or become {poisoned.caption} for 1 minute (save ends at end of turn)."
        elif dmg_type == DamageType.Thunder:
            dmg = stats.target_value(target=dmg_target, force_die=Die.d8)
            dazed = Dazed()
            condition = f"and force the target to make a DC {dc} Constitution saving throw. On a failure, the target is {dazed.caption} until the end of its next turn. {dazed.description_3rd}"
        else:
            raise NotImplementedError(f"{dmg_type} is not supported")

        description = f"Immediately after hitting with an attack, {stats.selfref} deals an additional {dmg.description} {dmg_type} damage to the target {condition}"

        feature = Feature(
            name=self.name,
            action=ActionType.BonusAction,
            description=description,
            recharge=5,
        )
        return [feature]


class _ElementalBurst(ElementalPower):
    def __init__(self, damage_type: DamageType, icon: str = "bright-explosion"):
        name = damage_type.adj.capitalize() + " Burst"
        super().__init__(
            name=name,
            source="Foe Foundry",
            icon=icon,
            require_damage=damage_type,
        )
        self.damage_type = damage_type

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        uses = int(ceil(stats.cr / 5))
        dmg = stats.target_value(target=0.75)
        damage_type = self.damage_type
        distance = 5 if stats.cr <= 7 else 10
        dc = stats.difficulty_class
        feature = Feature(
            name=self.name,
            action=ActionType.Reaction,
            uses=uses,
            description=f"When {stats.selfref} is hit by a melee attack, their form explodes with {damage_type.adj} energy. \
                    Each other creature within {distance} ft must make a DC {dc} Dexterity saving throw, \
                    taking {dmg.description} {damage_type} damage on a failure and half as much damage on a success.",
        )
        return [feature]


class _ElementalFireball(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Elemental Fireball",
            source="Foe Foundry",
            icon="fireball",
            require_damage=DamageType.Fire,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Fireball"
        dc = stats.difficulty_class
        dmg_type = DamageType.Fire
        dmg = stats.target_value(dpr_proportion=0.7, force_die=Die.d6)
        description = f"{stats.selfref.capitalize()} targets a 20 ft sphere at a point it can see within 150 feet. A fiery explosion fills the space. \
            All creatures within the space must make a DC {dc} Dexterity saving throw, taking {dmg.description} {dmg_type} damage on a failure and half as much on a success."

        feature = Feature(
            name=name, action=ActionType.Action, description=description, recharge=5
        )
        return [feature]


class _AcidicBlast(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Acidic Blast",
            source="Foe Foundry",
            icon="acid",
            require_damage=DamageType.Acid,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Acidic Blast"
        dc = stats.difficulty_class
        dmg_type = DamageType.Acid
        dmg = stats.target_value(dpr_proportion=0.6, force_die=Die.d4)

        # acid damage is always done in d4s and should be an even number
        # this is because the ongoing damage should be half that amount
        dmg = stats.target_value(target=1.0, force_die=Die.d4, force_even=True)
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
            icon="icicles-fence",
            require_damage=DamageType.Cold,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Cone of Cold"
        dc = stats.difficulty_class
        dmg_type = DamageType.Cold
        dmg = stats.target_value(dpr_proportion=0.8, force_die=Die.d8)
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
            icon="lightning-branches",
            require_damage=DamageType.Lightning,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Lightning Bolt"
        dc = stats.difficulty_class
        dmg_type = DamageType.Lightning
        dmg = stats.target_value(dpr_proportion=0.8, force_die=Die.d6)
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
            icon="poison-gas",
            require_damage=DamageType.Poison,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Poison Cloud"
        dc = stats.difficulty_class
        dmg_type = DamageType.Poison
        duration = DieFormula.from_expression("1d4 + 2")
        poisoned = Condition.Poisoned
        dmg = stats.target_value(dpr_proportion=0.6, force_die=Die.d6)
        description = f"{stats.selfref.capitalize()} creates a 20-ft radius cloud of toxic gas centered at a point it can see within 60 feet. Each creature that starts its turn in the cloud \
            must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg.description} {dmg_type} damage and is {poisoned.caption} until the end of its next turn. On a success, a creature takes half as much damage and is not poisoned. \
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
            icon="rolling-energy",
            require_damage=DamageType.Thunder,
            power_level=HIGH_POWER,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        name = "Thunderwave"
        dc = stats.difficulty_class
        dmg_type = DamageType.Thunder
        dmg = stats.target_value(dpr_proportion=0.65, force_die=Die.d10)
        prone = Condition.Prone
        description = f"{stats.selfref.capitalize()} releases a burst of thundrous energy in a 15 ft. cube originating from {stats.selfref}. \
            Each creature in the area must make a DC {dc} Constitution saving throw. On a failure, a creature takes {dmg.description} {dmg_type} thunder damage and is knocked up to 10 feet away and lands {prone.caption}. \
            On a success, a creature takes half as much damage and is not knocked prone."

        feature = Feature(
            name=name,
            action=ActionType.Action,
            description=description,
            recharge=5,
            replaces_multiattack=2,
        )
        return [feature]


class _ElementalReplication(ElementalPower):
    def __init__(self):
        super().__init__(
            name="Elemental Replication",
            source="Foe Foundry",
            icon="backup",
            power_level=HIGH_POWER,
            require_secondary_damage_type=True,
            require_cr=4.0,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        rng = stats.create_rng("elemental replication")
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


FireElementalAffinity = _ElementalAffinity(DamageType.Fire, icon="wildfires")
IceElementalAffinity = _ElementalAffinity(DamageType.Cold, icon="snowing")
AcidElementalAffinity = _ElementalAffinity(DamageType.Acid, icon="acid-blob")
LightningElementalAffinity = _ElementalAffinity(
    DamageType.Lightning, icon="lightning-storm"
)
PoisonElementalAffinity = _ElementalAffinity(DamageType.Poison, icon="mushrooms")

FireBurst = _ElementalBurst(DamageType.Fire, icon="fire-ray")
IceBurst = _ElementalBurst(DamageType.Cold, icon="ice-spear")
AcidBurst = _ElementalBurst(DamageType.Acid, icon="chemical-bolt")
LightningBurst = _ElementalBurst(DamageType.Lightning)
PoisonBurst = _ElementalBurst(DamageType.Poison)


FireSmite = _ElementalSmite(DamageType.Fire)
IceSmite = _ElementalSmite(DamageType.Cold)
AcidSmite = _ElementalSmite(DamageType.Acid)
LightningSmite = _ElementalSmite(DamageType.Lightning)
PoisonSmite = _ElementalSmite(DamageType.Poison)


CorrosiveFumesAura = _DamagingAura(
    name="Corrosive Fumes", damage_type=DamageType.Acid, icon="bottle-vapors"
)
ArcticChillAura = _DamagingAura(
    name="Arctic Chill", damage_type=DamageType.Cold, icon="thermometer-cold"
)
SuperheatedAura = _DamagingAura(
    name="Superheated", damage_type=DamageType.Fire, icon="thermometer-hot"
)
DisintegratingAura = _DamagingAura(
    name="Disintegrating Presence", damage_type=DamageType.Force, icon="disintegrate"
)
ArcingElectricityAura = _DamagingAura(
    name="Arcing Electricity", damage_type=DamageType.Lightning, icon="electric-whip"
)
DeathlyPresenceAura = _DamagingAura(
    name="Deathly Presence", damage_type=DamageType.Necrotic, icon="death-zone"
)
ToxicPresenceAura = _DamagingAura(
    name="Toxic Presence", damage_type=DamageType.Poison, icon="poison-gas"
)
ElementalFireball = _ElementalFireball()
AcidicBlast = _AcidicBlast()
ConeOfCold = _ConeOfCold()
LightningBolt = _LightningBolt()
PoisonCloud = _PoisonCloud()
Thunderwave = _Thunderwave()
ElementalReplication = _ElementalReplication()

ElementalPowers = [
    FireElementalAffinity,
    IceElementalAffinity,
    AcidElementalAffinity,
    LightningElementalAffinity,
    PoisonElementalAffinity,
    FireBurst,
    IceBurst,
    AcidBurst,
    LightningBurst,
    PoisonBurst,
    FireSmite,
    IceSmite,
    AcidSmite,
    LightningSmite,
    PoisonSmite,
    CorrosiveFumesAura,
    ArcticChillAura,
    SuperheatedAura,
    DisintegratingAura,
    ArcingElectricityAura,
    DeathlyPresenceAura,
    ToxicPresenceAura,
    AcidicBlast,
    ConeOfCold,
    ElementalFireball,
    ElementalReplication,
    LightningBolt,
    PoisonCloud,
    Thunderwave,
]
