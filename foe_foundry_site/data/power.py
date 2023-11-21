from __future__ import annotations

from dataclasses import field
from typing import List

from pydantic.dataclasses import dataclass

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
        stats = Specialist.copy()

        # TODO - if the power has a creature type, damage type, or role associated with it then apply that here
        # TODO - call those preconditions out in the power definition
        stats = power.modify_stats(stats)

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

        return PowerModel(
            key=power.key,
            name=power.name,
            power_type=power.power_type.name,
            source=power.source or "UNKNOWN",
            power_level=power.power_level_text,
            features=feature_models,
        )
