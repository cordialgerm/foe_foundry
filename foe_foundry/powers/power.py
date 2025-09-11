from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, List

from ..creature_types import CreatureType
from ..damage import AttackType, DamageType
from ..features import Feature
from ..power_types import PowerType
from ..role_types import MonsterRole
from ..statblocks import BaseStatblock
from ..tags.tags import MonsterTag
from ..utils import name_to_key
from .flags import theme_flag
from .power_category import PowerCategory
from .scoring import score as standard_score

RIBBON_POWER = 0.25
LOW_POWER = 0.5
MEDIUM_POWER = 1
HIGH_POWER = 1.25
EXTRA_HIGH_POWER = 1.5


class Power(ABC):
    def __init__(
        self,
        *,
        name: str,
        power_category: PowerCategory,
        theme: str,
        reference_statblock: str,
        icon: str | None = None,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
        roles: List[MonsterRole] | None = None,
        creature_types: List[CreatureType] | None = None,
        damage_types: List[DamageType] | None = None,
        attack_types: List[AttackType] | None = None,
        suggested_cr: float | None = None,
        create_date: datetime | None = None,
        power_types: List[PowerType],
    ):
        self.name = name
        self.power_category = power_category
        self.source = source
        self.power_level = power_level
        self.roles = roles
        self.creature_types = creature_types
        self.damage_types = damage_types
        self.attack_types = attack_types
        self.suggested_cr = suggested_cr
        self.create_date = create_date

        if power_types is None or len(power_types) == 0:
            raise ValueError("power_types must be a non-empty list")

        self.power_types = power_types
        self.theme = theme
        self.reference_statblock = reference_statblock
        self.icon = icon
        if self.power_level == EXTRA_HIGH_POWER:
            self.power_level_text = "Extra High Power"
        elif self.power_level == HIGH_POWER:
            self.power_level_text = "High Power"
        elif self.power_level == MEDIUM_POWER:
            self.power_level_text = "Medium Power"
        elif self.power_level == LOW_POWER:
            self.power_level_text = "Low Power"
        elif self.power_level == RIBBON_POWER:
            self.power_level_text = "Ribbon"
        else:
            raise ValueError(f"Invalid power level {self.power_level}")

    @property
    def key(self) -> str:
        return name_to_key(self.name)

    @property
    def theme_key(self) -> str | None:
        return name_to_key(self.theme) if self.theme is not None else None

    @property
    def tags(self) -> List[MonsterTag]:
        """Generate tags automatically from power properties"""
        tags = []

        # Add power type tags
        if self.power_types:
            for power_type in self.power_types:
                tags.append(MonsterTag.from_power_type(power_type))

        # Add creature type tags
        if self.creature_types:
            for creature_type in self.creature_types:
                tags.append(MonsterTag.from_creature_type(creature_type))

        # Add damage type tags
        if self.damage_types:
            for damage_type in self.damage_types:
                tags.append(MonsterTag.from_damage_type(damage_type))

        # Add role tags
        if self.roles:
            for role in self.roles:
                tags.append(MonsterTag.from_role(role))

        # Add theme tag
        if self.theme:
            tags.append(MonsterTag.from_theme(self.theme))

            # Add additional tags based on theme patterns
            additional_tags = self._get_additional_tags_for_theme(self.theme)
            tags.extend(additional_tags)

        return tags

    def _get_additional_tags_for_theme(self, theme: str) -> List[MonsterTag]:
        """Get additional tags based on theme patterns"""
        additional_tags = []
        theme_lower = theme.lower()

        # Environment tags for environment-related themes
        environment_themes = {
            "aquatic": "ocean",
            "earthy": "underground",
            "icy": "arctic",
            "storm": "plain",  # storms often occur on plains/open areas
            "flying": "mountain",  # flying creatures often found in mountains
        }

        if theme_lower in environment_themes:
            # Create environment tag (would need to add method to MonsterTag)
            # For now, create as theme tag with environment type
            env = environment_themes[theme_lower]
            additional_tags.append(MonsterTag(tag=env, tag_type="environment"))

        # Spellcaster magic school tags - these should get spellcaster_magic type
        spellcaster_themes = {
            "celestial",
            "conjurer",
            "cult",
            "divination",
            "druidic",
            "elementalist",
            "enchanter",
            "fiendish",
            "illusionist",
            "magic",
            "metamagic",
            "necromancer",
            "oath",
            "psionic",
            "shaman",
            "transmuter",
        }

        if theme_lower in spellcaster_themes:
            # Add spellcaster magic type tag
            magic_theme = f"{theme_lower}_magic"
            additional_tags.append(
                MonsterTag(tag=magic_theme, tag_type="spellcaster_magic")
            )

        return additional_tags

    @abstractmethod
    def score(self, candidate: BaseStatblock, relaxed_mode: bool = False) -> float:
        pass

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = self.modify_stats_inner(stats)
        return stats.with_flags(theme_flag(self.theme))

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        features = self.generate_features_inner(stats)
        for feature in features:
            feature.power_key = self.key
        return features

    @abstractmethod
    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        pass

    def __repr__(self):
        return f"{self.name} ({self.power_category})"

    def __hash__(self) -> int:
        return hash(self.key)

    def __eq__(self, other: Any) -> bool:
        return isinstance(other, Power) and self.key == other.key


class PowerWithStandardScoring(Power):
    def __init__(
        self,
        *,
        name: str,
        power_category: PowerCategory,
        theme: str,
        reference_statblock: str,
        icon: str | None = None,
        source: str | None = None,
        power_level: float = MEDIUM_POWER,
        create_date: datetime | None = None,
        power_types: List[PowerType],
        score_args: Dict[str, Any] | None = None,
    ):
        def resolve_arg_list(arg: str) -> List | None:
            if not score_args:
                return None

            val = score_args.get(f"require_{arg}", score_args.get(f"bonus_{arg}"))
            if val is None:
                return None
            elif isinstance(val, list):
                return val
            elif isinstance(val, set):
                return list(val)
            else:
                return [val]

        def resolve_arg(arg: str) -> Any | None:
            if not score_args:
                return None

            return score_args.get(f"require_{arg}", score_args.get(f"bonus_{arg}"))

        creature_types = resolve_arg_list("types")
        damage_types = resolve_arg_list("damage")
        roles = resolve_arg_list("roles")
        suggested_cr = resolve_arg("cr")
        attack_types = resolve_arg_list("attack_types")

        super().__init__(
            name=name,
            power_category=power_category,
            source=source,
            power_level=power_level,
            create_date=create_date,
            theme=theme,
            reference_statblock=reference_statblock,
            icon=icon,
            roles=roles,
            creature_types=creature_types,
            damage_types=damage_types,
            attack_types=attack_types,
            suggested_cr=suggested_cr,
            power_types=power_types,
        )

        self.score_args = score_args

    def score(self, candidate: BaseStatblock, relaxed_mode: bool = False) -> float:
        return standard_score(
            candidate=candidate, relaxed_mode=relaxed_mode, **self.score_args or {}
        )
