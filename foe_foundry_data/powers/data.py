from __future__ import annotations

from dataclasses import field
from datetime import datetime
from functools import cached_property
from pathlib import Path
from typing import List, Set

import numpy as np
from pydantic.dataclasses import dataclass

from foe_foundry import AttackType
from foe_foundry.creatures import GenerationSettings
from foe_foundry.creatures.warrior import warrior
from foe_foundry.features import ActionType
from foe_foundry.powers import Power
from foe_foundry.statblocks import Statblock

from ..icons import icon_path
from ..monsters import monsters_for_power
from ..refs import MonsterRef, MonsterRefResolver

MonsterReferences = MonsterRefResolver()


def _get_best_statblock(
    requested_statblock: str,
    requested_cr: float | None,
) -> Statblock:
    monster_ref = MonsterReferences.resolve_monster_ref(requested_statblock)

    rng = np.random.default_rng(20240711)

    # it's possible that we don't yet have a statblock for the requested monster
    # in that case, just fall back to the Warrior
    update_name_to = None
    if monster_ref is None:
        monster_ref = MonsterRef(
            original_monster_name=requested_statblock,
            template=warrior.WarriorTemplate,
            variant=None,
            monster=None,
        )
        update_name_to = requested_statblock

    if monster_ref.monster is not None and monster_ref.variant is not None:
        if requested_cr is None:
            requested_cr = monster_ref.monster.cr
        else:
            requested_cr = 4.0

        setting = GenerationSettings(
            creature_name=monster_ref.monster.name
            if update_name_to is None
            else update_name_to,
            monster_template=monster_ref.template.name,
            monster_key=monster_ref.monster.key,
            cr=requested_cr,
            is_legendary=False,
            variant=monster_ref.variant,
            rng=rng,
            monster=monster_ref.monster,
            species=monster_ref.species,
        )
    else:
        # if we don't have a specific statblock to generate, find the one with the closest CR match
        crs = []
        settings = []
        for setting in monster_ref.template.generate_settings():
            settings.append(setting)
            crs.append(setting.cr)

        crs = np.array(crs)
        err = np.pow(crs - (requested_cr or 4.0), 2)
        min_index = np.argmin(err)
        setting = settings[min_index]

    stats = monster_ref.template.generate(setting).finalize()

    if update_name_to is not None:
        stats = stats.copy(name=update_name_to, creature_class=update_name_to)

    return stats


@dataclass(kw_only=True)
class FeatureModel:
    name: str
    title: str
    action: str
    recharge: int | None = None
    uses: int | None = None
    replaces_multiattack: int = 0
    modifies_attack: bool = False
    description_md: str
    is_spellcasting: bool = False
    is_attack: bool = False

    @property
    def description(self) -> str:
        return self.description_md


@dataclass(kw_only=True)
class MonsterInPower:
    name: str
    monster_template: str
    url: str | None
    template_url: str | None
    cr: float
    is_legendary: bool

    @property
    def cr_caption(self) -> str:
        if self.cr == 0.125:
            return "CR 1/8"
        elif self.cr == 0.25:
            return "CR 1/4"
        elif self.cr == 0.5:
            return "CR 1/2"
        else:
            return f"CR {self.cr:.0f}"


@dataclass(kw_only=True)
class PowerModel:
    key: str
    name: str
    power_category: str
    source: str
    theme: str
    power_level: str
    icon: str | None
    create_date: datetime | None
    features: List[FeatureModel]
    monsters: List[MonsterInPower]
    reaction_count: int | str = 1
    creature_types: List[str] = field(default_factory=list)
    roles: List[str] = field(default_factory=list)
    damage_types: List[str] = field(default_factory=list)
    attack_types: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)

    @cached_property
    def feature_descriptions(self) -> str:
        features = []
        for feature in self.features:
            if feature.action == "Attack":
                action_desc = ""  # attacks are obvious
            else:
                action = ActionType(feature.action.lower())
                if action == ActionType.Feature:
                    action_desc = ""  # traits are obvious
                else:
                    action_desc = f" ({action.caption})"

            features.append(
                f"***{feature.name}***{action_desc}: {feature.description_md}  "
            )

        return "\n\n".join(features)

    @property
    def columns_suggested(self) -> bool:
        return len(self.feature_descriptions) > 300 and all(
            not f.is_attack and not f.is_spellcasting for f in self.features
        )

    @property
    def icon_path(self) -> str | None:
        if self.icon is None:
            return None

        docs_dir = Path(__file__).parent.parent.parent / "docs"
        path = icon_path(self.icon)
        return str(path.relative_to(docs_dir)) if path else None

    @property
    def reaction_header(self) -> str:
        if isinstance(self.reaction_count, int):
            if self.reaction_count > 1:
                reaction_header = f"Reactions ({self.reaction_count}/turn)"
            else:
                reaction_header = "Reactions"
        else:
            reaction_header = f"Reactions ({self.reaction_count})"

        return reaction_header

    @cached_property
    def used_by_monsters_html(self) -> str:
        if len(self.monsters) == 0:
            return ""
        elif len(self.monsters) < 5:
            return "Used by " + ", ".join(
                f"<a href='{m.url}'>{m.name} ({m.cr_caption})</a>"
                for m in self.monsters
            )

        # if there are more than 5, then only pick 1 monster per template
        seen_templates = set()
        anchors = []
        for m in self.monsters:
            if m.monster_template in seen_templates:
                continue

            seen_templates.add(m.monster_template)
            anchors.append(f"<a href='{m.template_url}'>{m.monster_template}</a>")

        return "Used by " + ", ".join(anchors)

    @staticmethod
    def from_power(power: Power) -> PowerModel:
        # If the power has a suggested CR, then use that as our baseline
        # Otherwise, use the Specialist (CR 4) as our baseline for reasonable power descriptions
        stats = _get_best_statblock(
            requested_statblock=power.reference_statblock,
            requested_cr=power.suggested_cr,
        )

        existing_attacks = {a.display_name for a in stats.additional_attacks}

        # remove existing spells from the statblock so it doesn't seem like the power added previously existing spells
        stats = stats.copy(spells=[])

        # if the power has a secondary damage type, apply that
        if power.damage_types:
            secondary_damage_type = power.damage_types[0]
            stats = stats.copy(secondary_damage_type=secondary_damage_type)

        # if the power has any preconditions, be sure to apply those
        stats = power.modify_stats(stats)

        # generate the features of the power
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
                title=feature.title,
                action=feature.action.name,
                recharge=feature.recharge,
                uses=feature.uses,
                replaces_multiattack=feature.replaces_multiattack,
                description_md=feature.description,
                modifies_attack=feature.modifies_attack,
            )
            feature_models.append(feature_model)

        for attack in stats.additional_attacks:
            if attack.display_name in existing_attacks:
                # this attack was already in the statblock before the power, so we don't need to add it again
                continue

            feature_models.append(
                FeatureModel(
                    name=attack.name,
                    title=attack.name,
                    action="Attack",
                    replaces_multiattack=attack.replaces_multiattack,
                    description_md=attack.description,
                    is_attack=True,
                )
            )

        spellcasting_md = stats.spellcasting_md
        if spellcasting_md:
            feature_models.append(
                FeatureModel(
                    name="Spellcasting",
                    title="Spellcasting",
                    action="Action",
                    replaces_multiattack=2,
                    description_md=spellcasting_md,
                    is_spellcasting=True,
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

        monsters = [
            MonsterInPower(
                name=m.monster.name,  # type: ignore
                monster_template=m.template.name,
                url=m.url,
                cr=m.monster.cr,  # type: ignore
                template_url=m.template_url,
                is_legendary=m.monster.is_legendary,  # type: ignore
            )
            for m in monsters_for_power(power)
        ]

        return PowerModel(
            key=power.key,
            name=power.name,
            create_date=power.create_date,
            theme=power.theme or "UNKNOWN",
            power_category=power.power_category.name,
            icon=power.icon,
            source=power.source or "UNKNOWN",
            power_level=power.power_level_text,
            features=feature_models,
            monsters=monsters,
            reaction_count=stats.reaction_count,
            creature_types=to_str(power.creature_types),
            damage_types=to_str(power.damage_types),
            roles=to_str(power.roles),
            tags=list(sorted(tags)),
        )
