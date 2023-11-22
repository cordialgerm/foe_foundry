from __future__ import annotations

from dataclasses import field
from typing import List

import numpy as np
from pydantic.dataclasses import dataclass

from foe_foundry import CreatureType, DamageType, MonsterRole
from foe_foundry.creature_templates import get_creature_template
from foe_foundry.powers import Power
from foe_foundry.statblocks.common import Specialist


@dataclass(kw_only=True)
class FeatureModel:
    name: str
    action: str
    recharge: int | None = None
    uses: int | None = None
    replaces_multiattack: int = 0
    description_md: str


@dataclass(kw_only=True)
class PowerModel:
    key: str
    name: str
    power_type: str
    source: str
    power_level: str
    features: List[FeatureModel]
    creature_types: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    damage_types: List[str] = field(default_factory=list)

    @property
    def feature_descriptions(self) -> str:
        return "\n\n".join(
            feature.name + ": " + feature.description_md for feature in self.features
        )

    @staticmethod
    def from_power(power: Power) -> PowerModel:
        # To give a user-friendly description of the power, we need a stablock as a base reference
        # this code will create a reasonable base creature using some metadata about the power
        # that way, the descriptive text will be reasonable instead of generic
        if power.creature_types:
            creature_type = power.creature_types[0]
        else:
            creature_type = CreatureType.Humanoid

        if power.damage_types:
            secondary_damage_type = power.damage_types[0]
        else:
            secondary_damage_type = None

        if power.roles:
            role = power.roles[0]
        else:
            role = MonsterRole.Bruiser

        def rng() -> np.random.Generator:
            return np.random.default_rng(seed=20210518)

        # Use the Specialist (CR 4) as our baseline for reasonable power descriptions
        stats = Specialist.copy()

        # if the power has a secondary damage type, apply that
        if secondary_damage_type:
            stats = stats.copy(secondary_damage_type=secondary_damage_type)

        # if the power has any preconditions, be sure to apply those
        stats = power.modify_stats(stats)

        creature_template = get_creature_template(creature_type)
        stats = creature_template.create(base_stats=stats, rng_factory=rng, role_template=role)

        features = power.generate_features(stats)
        feature_models = []
        for feature in features:
            if feature.hidden:
                continue
            feature_model = FeatureModel(
                name=feature.name,
                action=feature.action.name,
                recharge=feature.recharge,
                uses=feature.uses,
                replaces_multiattack=feature.replaces_multiattack,
                description_md=feature.description,
            )
            feature_models.append(feature_model)

        for attack in stats.additional_attacks:
            feature_models.append(
                FeatureModel(
                    name=attack.name,
                    action="Attack",
                    replaces_multiattack=attack.replaces_multiattack,
                    description_md=attack.description,
                )
            )
            attack.description

        def to_str(enums):
            return [str(e) for e in enums] if enums is not None else []

        return PowerModel(
            key=power.key,
            name=power.name,
            power_type=power.power_type.name,
            source=power.source or "UNKNOWN",
            power_level=power.power_level_text,
            features=feature_models,
            creature_types=to_str(power.creature_types),
            damage_types=to_str(power.damage_types),
            roles=to_str(power.roles),
        )
