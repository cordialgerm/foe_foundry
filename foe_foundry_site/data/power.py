from __future__ import annotations

from dataclasses import field
from datetime import datetime
from typing import List, Set

import numpy as np
from pydantic.dataclasses import dataclass

from foe_foundry import AttackType, CreatureType, MonsterRole
from foe_foundry.creature_templates import get_creature_template
from foe_foundry.powers import Power
from foe_foundry.statblocks.common import get_common_stats


@dataclass(kw_only=True)
class FeatureModel:
    name: str
    action: str
    recharge: int | None = None
    uses: int | None = None
    replaces_multiattack: int = 0
    modifies_attack: bool = False
    description_md: str


@dataclass(kw_only=True)
class PowerModel:
    key: str
    name: str
    power_type: str
    source: str
    theme: str
    power_level: str
    create_date: datetime | None
    features: List[FeatureModel]
    creature_types: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    damage_types: List[str] = field(default_factory=list)
    attack_types: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

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

        # If the power has a suggested CR, then use that as our baseline
        # Otherwise, use the Specialist (CR 4) as our baseline for reasonable power descriptions
        stats = get_common_stats(power.suggested_cr or 4).copy()

        # if the power has a secondary damage type, apply that
        if secondary_damage_type:
            stats = stats.copy(secondary_damage_type=secondary_damage_type)

        # if the power has any preconditions, be sure to apply those
        stats = power.modify_stats(stats)

        creature_template = get_creature_template(creature_type)
        stats = creature_template.create(
            base_stats=stats, rng_factory=rng, role_template=role, skip_power_selection=True
        )

        features = power.generate_features(stats)
        feature_models = []
        for feature in features:
            # normally we would skip displaying hidden features (in the statblock itself)
            # however, if the feature modifies the attack we have no way of displaying it in the API without returning it as a feature
            # also, if the feature just produces a single hidden feature then we should display it otherwise the power would be shown as doing nothing
            skip_if_hidden = not (feature.modifies_attack or len(features) == 1)
            if feature.hidden and skip_if_hidden:
                continue
            feature_model = FeatureModel(
                name=feature.name,
                action=feature.action.name,
                recharge=feature.recharge,
                uses=feature.uses,
                replaces_multiattack=feature.replaces_multiattack,
                description_md=feature.description,
                modifies_attack=feature.modifies_attack,
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

        spellcasting_md = stats.spellcasting_md
        if spellcasting_md:
            feature_models.append(
                FeatureModel(
                    name="Spellcasting",
                    action="Action",
                    replaces_multiattack=2,
                    description_md=spellcasting_md,
                )
            )

        tags = set()
        if power.creature_types and len(power.creature_types) <= 4:
            tags.update([ct.lower() for ct in power.creature_types])
        if power.damage_types and len(power.damage_types) <= 4:
            tags.update([d.lower() for d in power.damage_types])
        if power.theme:
            tags.add(power.theme.lower())
        if power.roles and len(power.roles) <= 4:
            tags.update([r.lower() for r in power.roles])

        # spell
        # weapon
        # natural
        def check(options: Set[AttackType]) -> bool:
            if power.attack_types is None or len(power.attack_types) == 0:
                return False
            return all([a in options for a in power.attack_types])

        if check(AttackType.AllMelee()):
            tags.add("melee")
        if check(AttackType.AllRanged()):
            tags.add("ranged")
        if check(AttackType.AllSpell()):
            tags.add("spell")
        if check(AttackType.AllNatural()):
            tags.add("natural")

        def to_str(enums):
            return [str(e) for e in enums] if enums is not None else []

        return PowerModel(
            key=power.key,
            name=power.name,
            create_date=power.create_date,
            theme=power.theme or "UNKNOWN",
            power_type=power.power_type.name,
            source=power.source or "UNKNOWN",
            power_level=power.power_level_text,
            features=feature_models,
            creature_types=to_str(power.creature_types),
            damage_types=to_str(power.damage_types),
            roles=to_str(power.roles),
            tags=list(sorted(tags)),
        )
