from datetime import datetime
from typing import Callable, List

from ...creature_types import CreatureType
from ...damage import Condition, DamageType, conditions
from ...die import Die, DieFormula
from ...features import ActionType, Feature
from ...statblocks import BaseStatblock
from ..power import HIGH_POWER, Power, PowerType, PowerWithStandardScoring


class _BreathPower(PowerWithStandardScoring):
    def __init__(
        self,
        name: str,
        breath: DamageType,
        save: str,
        on_failure: str | Callable[[BaseStatblock, DieFormula], str] | None = None,
    ):
        super().__init__(
            name=name,
            power_type=PowerType.Theme,
            source="Foe Foundry",
            power_level=HIGH_POWER,
            create_date=datetime(2025, 2, 28),
            theme="Breath",
            score_args=dict(require_damage=breath, require_types={CreatureType.Dragon}),
        )
        self.breath = breath
        self.save = save
        self.on_failure = on_failure

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stats = super().modify_stats_inner(stats)

        if stats.secondary_damage_type is None:
            return stats.copy(secondary_damage_type=self.breath)
        else:
            return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = breath(self.name, self.breath, stats, self.save, self.on_failure)
        return [feature]


# helper method to generate a breath attack in a consistent way
def breath(
    name: str,
    damage_type: DamageType,
    stats: BaseStatblock,
    save: str,
    on_failure: str | Callable[[BaseStatblock, DieFormula], str] | None = None,
    verb: str = "breathes",
    damage_multiplier=1.0,
    **args,
) -> Feature:
    if stats.cr <= 3:
        distance = 15
    elif stats.cr <= 7:
        distance = 30
    elif stats.cr <= 11:
        distance = 45
    else:
        distance = 60

    template = f"{distance} ft cone"

    dmg = stats.target_value(
        dpr_proportion=0.7 * damage_multiplier,
        suggested_die=Die.d8,
    )

    dc = stats.difficulty_class

    if isinstance(on_failure, str):
        additional_description = on_failure
    elif callable(on_failure):
        additional_description = on_failure(stats, dmg)
    else:
        additional_description = ""

    feature = Feature(
        name=name,
        action=ActionType.Action,
        recharge=5,
        description=f"{stats.selfref.capitalize()} {verb} {damage_type} in a {template}. \
            Each creature in the area must make a DC {dc} {save} save. \
            On a failure, the creature takes {dmg.description} {damage_type} damage or half as much on a success. \
            {additional_description}",
        **args,
    )
    return feature


def on_inferno_breath_failure(stats: BaseStatblock, breath_damage: DieFormula) -> str:
    burning_dmg = DieFormula.target_value(
        breath_damage.average / 2, force_die=breath_damage.primary_die_type
    )
    burning = conditions.Burning(burning_dmg, DamageType.Fire)
    return f"Additionally, creatures that fail by 5 or more are {burning.caption}. {burning.description_3rd}"


def on_flash_freeze_failure(stats: BaseStatblock, breath_damage: DieFormula) -> str:
    frozen = conditions.Frozen(dc=stats.difficulty_class)
    return f"Additionally, creatures that fail by 5 or more are {frozen.caption}. {frozen.description_3rd}"


def on_nerve_gas_failure(stats: BaseStatblock, breath_damage: DieFormula) -> str:
    weakened = conditions.Weakened(save_end_of_turn=False)
    return f"Additionally, creatures that fail by 5 or more are {weakened.caption} for 1 minute (save ends at end of turn). {weakened.description_3rd}"


def on_arc_lightning_failure(stats: BaseStatblock, breath_damage: DieFormula) -> str:
    shocked = conditions.Shocked()
    return f"Additionally, creatures that fail by 5 or more are {shocked.caption} for 1 minute (save ends at end of turn). {shocked.description_3rd}"


def on_flesh_melting_failure(stats: BaseStatblock, breath_damage: DieFormula) -> str:
    burning_dmg = DieFormula.target_value(breath_damage.average / 4, force_die=Die.d4)
    burning = conditions.Burning(burning_dmg, DamageType.Acid)
    poisoned = Condition.Poisoned
    return f"Additionally, creatures that fail by 5 or more are {burning.caption}. While burning this way, the creature is also {poisoned.caption}. \
        {burning.description_3rd}"


class _Susceptible:
    def __init__(self, damage_type: DamageType):
        self.damage_type = damage_type

    def on_susceptible_failure(
        self, stats: BaseStatblock, breath_damage: DieFormula
    ) -> str:
        susceptible = conditions.Susceptible(self.damage_type)
        on_failure = f"Additionally, creatures that fail the save by 5 or more are {susceptible.caption} to their next source of {self.damage_type} damage in the next minute. {susceptible.description_3rd}"
        return on_failure


FireBreath: Power = _BreathPower(
    name="Fire Breath",
    breath=DamageType.Fire,
    save="Dexterity",
    on_failure=_Susceptible(DamageType.Fire).on_susceptible_failure,
)

ColdBreath: Power = _BreathPower(
    name="Cold Breath",
    breath=DamageType.Cold,
    save="Constitution",
    on_failure=_Susceptible(DamageType.Cold).on_susceptible_failure,
)

PoisonBreath: Power = _BreathPower(
    name="Poison Breath",
    breath=DamageType.Poison,
    save="Constitution",
    on_failure=_Susceptible(DamageType.Poison).on_susceptible_failure,
)

LightningBreath: Power = _BreathPower(
    name="Lightning Breath",
    breath=DamageType.Lightning,
    save="Dexterity",
    on_failure=_Susceptible(DamageType.Lightning).on_susceptible_failure,
)

AcidBreath: Power = _BreathPower(
    name="Acid Breath",
    breath=DamageType.Acid,
    save="Dexterity",
    on_failure=_Susceptible(DamageType.Acid).on_susceptible_failure,
)

InfernoBreath: Power = _BreathPower(
    name="Inferno Breath",
    breath=DamageType.Fire,
    save="Dexterity",
    on_failure=on_inferno_breath_failure,
)

FlashFreezeBreath: Power = _BreathPower(
    name="Flash Freeze Breath",
    breath=DamageType.Cold,
    save="Constitution",
    on_failure=on_flash_freeze_failure,
)

NerveGasBreath: Power = _BreathPower(
    name="Nerve Gas Breath",
    breath=DamageType.Poison,
    save="Constitution",
    on_failure=on_nerve_gas_failure,
)

ArcLightningBreath: Power = _BreathPower(
    name="Arc-Lightning Breath",
    breath=DamageType.Lightning,
    save="Dexterity",
    on_failure=on_arc_lightning_failure,
)

FleshMeltingBreath: Power = _BreathPower(
    name="Flesh Melting Breath",
    breath=DamageType.Acid,
    save="Dexterity",
    on_failure=on_flesh_melting_failure,
)

BreathPowers: List[Power] = [
    FireBreath,
    ColdBreath,
    PoisonBreath,
    LightningBreath,
    AcidBreath,
    InfernoBreath,
    FlashFreezeBreath,
    NerveGasBreath,
    ArcLightningBreath,
    FleshMeltingBreath,
]
