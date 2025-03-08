from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from typing import Callable, Dict, List, Set

from ..ac import ArmorClassTemplate
from ..attributes import Attributes, Skills
from ..creature_types import CreatureType
from ..damage import Attack, AttackType, Condition, Damage, DamageType
from ..die import Die, DieFormula
from ..hp import scale_hp_formula
from ..movement import Movement
from ..role_types import MonsterRole
from ..senses import Senses
from ..size import Size
from ..skills import Stats
from ..spells import CasterType, StatblockSpell
from ..utils import easy_multiple_of_five
from ..xp import xp_by_cr
from .dials import MonsterDials
from .suggested_powers import recommended_powers_for_cr


@dataclass(kw_only=True)
class BaseStatblock:
    name: str
    cr: float
    hp: DieFormula
    speed: Movement
    primary_attribute_score: int
    attributes: Attributes
    attack: Attack
    multiattack: int = 1
    multiattack_benchmark: int = 1
    primary_damage_type: DamageType = DamageType.Bludgeoning
    secondary_damage_type: DamageType | None = None
    difficulty_class_modifier: int = 0
    recommended_powers_modifier: float = 0
    size: Size = Size.Medium
    creature_type: CreatureType = CreatureType.Humanoid
    languages: List[str] = field(default_factory=list)
    senses: Senses = field(default_factory=Senses)
    role: MonsterRole = MonsterRole.Default
    damage_vulnerabilities: Set[DamageType] = field(default_factory=set)
    damage_resistances: Set[DamageType] = field(default_factory=set)
    damage_immunities: Set[DamageType] = field(default_factory=set)
    condition_immunities: Set[Condition] = field(default_factory=set)
    nonmagical_resistance: bool = False
    nonmagical_immunity: bool = False
    difficulty_class_easy: int = field(init=False)
    additional_attacks: List[Attack] = field(default_factory=list)
    ac_boost: int = 0
    uses_shield: bool = False
    ac_templates: List[ArmorClassTemplate] = field(default_factory=list)
    spells: List[StatblockSpell] = field(default_factory=list)
    creature_subtype: str | None = None
    creature_class: str | None = None
    damage_modifier: float = 1.0
    base_attack_damage: float
    additional_roles: list[MonsterRole] = field(default_factory=list)
    has_unique_movement_manipulation: bool = False
    is_legendary: bool = False
    has_lair: bool = False
    legendary_actions: int = 0
    legendary_resistances: int = 0
    legendary_resistance_damage_taken: int = 0
    flags: set[str] = field(default_factory=set)
    caster_type: CasterType | None = None

    def __post_init__(self):
        mod = (
            self.attributes.stat_mod(self.attributes.primary_attribute)
            + self.difficulty_class_modifier
        )
        prof = self.attributes.proficiency
        self.difficulty_class = 8 + mod + prof
        self.difficulty_class_easy = self.difficulty_class - 2

        self.recommended_powers = (
            recommended_powers_for_cr(self.cr) + self.recommended_powers_modifier
        )

        self.xp = xp_by_cr(self.cr)

    @property
    def key(self) -> str:
        return self.name.lower().replace(" ", "_")

    @property
    def primary_attribute(self) -> Stats:
        return self.attributes.primary_attribute

    @property
    def attack_types(self) -> Set[AttackType]:
        return {
            self.attack.attack_type,
            *(a.attack_type for a in self.additional_attacks),
        }

    @property
    def selfref(self) -> str:
        if self.creature_class is not None:
            return f"the {self.creature_class.lower()}"
        elif self.creature_subtype is not None:
            return f"the {self.creature_subtype.lower()}"
        else:
            return f"the {self.creature_type.value.lower()}"

    @property
    def roleref(self) -> str:
        if self.creature_class is not None:
            return f"the {self.creature_class.lower()}"
        else:
            return f"the {self.role.value.lower()}"

    @property
    def spellcasting_md(self) -> str:
        if len(self.spells) == 0:
            spellcasting = ""
        else:
            spellcasting = f"{self.selfref.capitalize()} casts one of the following spells, using {self.attributes.spellcasting_stat.description} as the spellcasting ability (spell save DC {self.attributes.spellcasting_dc}):"
            uses = [None, 5, 4, 3, 2, 1]
            for use in uses:
                line = _spell_list(self.spells, use)
                if line is None:
                    continue
                spellcasting += "<p>" + line + "</p>"

        return spellcasting

    @property
    def dpr(self) -> float:
        return (
            self.damage_modifier
            * self.base_attack_damage
            * (self.multiattack + 0.66 * self.legendary_actions)
        )

    def __copy_args__(self) -> dict:
        args: dict = dict(
            name=self.name,
            cr=self.cr,
            ac_boost=self.ac_boost,
            ac_templates=self.ac_templates.copy(),
            uses_shield=self.uses_shield,
            hp=deepcopy(self.hp),
            speed=deepcopy(self.speed),
            primary_attribute_score=self.primary_attribute_score,
            attributes=deepcopy(self.attributes),
            attack=deepcopy(self.attack),
            multiattack=self.multiattack,
            multiattack_benchmark=self.multiattack_benchmark,
            primary_damage_type=self.primary_damage_type,
            secondary_damage_type=self.secondary_damage_type,
            difficulty_class_modifier=self.difficulty_class_modifier,
            recommended_powers_modifier=self.recommended_powers_modifier,
            size=self.size,
            creature_type=self.creature_type,
            languages=deepcopy(self.languages),
            senses=deepcopy(self.senses),
            role=self.role,
            damage_vulnerabilities=deepcopy(self.damage_vulnerabilities),
            damage_resistances=deepcopy(self.damage_resistances),
            damage_immunities=deepcopy(self.damage_immunities),
            condition_immunities=deepcopy(self.condition_immunities),
            nonmagical_resistance=self.nonmagical_resistance,
            nonmagical_immunity=self.nonmagical_immunity,
            additional_attacks=[a.copy() for a in self.additional_attacks],
            spells=[s.copy() for s in self.spells],
            creature_class=self.creature_class,
            creature_subtype=self.creature_subtype,
            damage_modifier=self.damage_modifier,
            base_attack_damage=self.base_attack_damage,
            additional_roles=self.additional_roles.copy(),
            has_unique_movement_manipulation=self.has_unique_movement_manipulation,
            legendary_actions=self.legendary_actions,
            legendary_resistances=self.legendary_resistances,
            has_lair=self.has_lair,
            is_legendary=self.is_legendary,
            legendary_resistance_damage_taken=self.legendary_resistance_damage_taken,
            caster_type=self.caster_type,
        )
        return args

    def copy(self, **kwargs) -> BaseStatblock:
        args = self.__copy_args__()
        args.update(kwargs)
        return BaseStatblock(**args)

    def apply_monster_dials(self, dials: MonsterDials) -> BaseStatblock:
        args = self.__copy_args__()

        # resolve hp
        if dials.hp_multiplier != 1:
            args.update(
                hp=scale_hp_formula(
                    self.hp, target=self.hp.average * dials.hp_multiplier
                )
            )

        # resolve ac
        if dials.ac_modifier:
            new_ac_boost = self.ac_boost + dials.ac_modifier
            args.update(ac_boost=new_ac_boost)

        # resolve attack
        if dials.multiattack_modifier:
            args.update(multiattack=self.multiattack + dials.multiattack_modifier)

        if dials.attack_hit_modifier:
            args.update(
                attack=self.attack.delta(
                    hit_delta=dials.attack_hit_modifier,
                )
            )

        if dials.attack_hit_modifier:
            new_attributes = self.attributes.boost(
                stat=self.attributes.primary_attribute,
                value=2 * dials.attack_hit_modifier,
                limit=False,
            )
            args.update(attributes=new_attributes)

        if dials.attack_damage_multiplier != 1.0:
            existing = self.damage_modifier
            args.update(damage_modifier=existing * dials.attack_damage_multiplier)

        # resolve difficulty class
        if dials.difficulty_class_modifier:
            args.update(
                difficulty_class_modifier=self.difficulty_class_modifier
                + dials.difficulty_class_modifier
            )

        # resolve speed
        if dials.speed_modifier:
            args.update(speed=self.speed.delta(dials.speed_modifier))

        # resolve recommended powers
        if dials.recommended_powers_modifier:
            args.update(
                recommended_powers_modifier=self.recommended_powers_modifier
                + dials.recommended_powers_modifier
            )

        return BaseStatblock(**args)

    def scale(self, stats: Dict[Stats, int | Callable]) -> BaseStatblock:
        new_vals = {}

        primary_stat: Stats | None = None

        for stat, val in stats.items():
            if isinstance(val, int):
                new_vals[stat] = self.attributes.stat(stat) + val
            elif callable(val):
                is_primary = getattr(val, "is_primary", False)
                if is_primary:
                    primary_stat = stat
                new_vals[stat] = val(self)

        if primary_stat is not None:
            new_vals.update(primary_attribute=primary_stat)

        new_attributes = self.attributes.copy(**new_vals)
        return self.copy(attributes=new_attributes)

    def grant_spellcasting(
        self, caster_type: CasterType, spellcasting_stat: Stats | None = None
    ) -> BaseStatblock:
        if self.caster_type is not None:
            return self.copy()

        if spellcasting_stat is None:
            if caster_type == CasterType.Divine:
                spellcasting_stat = Stats.WIS
            elif caster_type == CasterType.Arcane:
                spellcasting_stat = Stats.INT
            elif caster_type == CasterType.Primal:
                spellcasting_stat = Stats.WIS
            elif caster_type == CasterType.Psionic:
                spellcasting_stat = Stats.INT
            elif caster_type == CasterType.Technomagic:
                spellcasting_stat = Stats.INT
            elif caster_type == CasterType.Innate:
                spellcasting_stat = Stats.CHA
            elif caster_type == CasterType.Pact:
                spellcasting_stat = Stats.CHA
            else:
                raise ValueError(f"Unknown caster type: {caster_type}")

        gap = self.attributes.primary_mod - self.attributes.stat_mod(spellcasting_stat)
        if gap > 1:
            boost = 2 * (gap - 1)  # don't boost spellcasting stat beyond primary stat
            new_attributes = self.attributes.boost(spellcasting_stat, boost)
            return self.copy(caster_type=caster_type, attributes=new_attributes)
        else:
            # already a spellcaster
            return self.copy(caster_type=caster_type)

    def add_ac_template(
        self,
        ac_template: ArmorClassTemplate,
        ac_modifier: int = 0,
    ) -> BaseStatblock:
        return self.add_ac_templates([ac_template], ac_modifier)

    def add_ac_templates(
        self,
        ac_templates: List[ArmorClassTemplate],
        ac_modifier: int = 0,
    ) -> BaseStatblock:
        new_templates = self.ac_templates.copy()
        for ac in ac_templates:
            if ac not in new_templates:
                new_templates.append(ac)

        new_ac_boost = self.ac_boost + ac_modifier
        return self.copy(ac_templates=new_templates, ac_boost=new_ac_boost)

    def remove_ac_templates(
        self, ac_templates: List[ArmorClassTemplate]
    ) -> BaseStatblock:
        new_templates = [ac for ac in self.ac_templates if ac not in ac_templates]
        return self.copy(ac_templates=new_templates)

    def grant_resistance_or_immunity(
        self,
        resistances: Set[DamageType] | None = None,
        immunities: Set[DamageType] | None = None,
        vulnerabilities: Set[DamageType] | None = None,
        conditions: Set[Condition] | None = None,
        nonmagical_resistance: bool | None = None,
        nonmagical_immunity: bool | None = None,
        upgrade_resistance_to_immunity_if_present: bool = False,
    ) -> BaseStatblock:
        new_resistances = self.damage_resistances.copy()
        new_immunities = self.damage_immunities.copy()
        new_vulnerabilities = self.damage_vulnerabilities.copy()

        if resistances is not None:
            for damage in resistances:
                if (
                    damage in new_resistances
                    and upgrade_resistance_to_immunity_if_present
                ):
                    new_resistances.remove(damage)
                    new_immunities.add(damage)
                else:
                    new_resistances.add(damage)

        if immunities is not None:
            for damage in immunities:
                new_immunities.add(damage)
                if damage in new_resistances:
                    new_resistances.remove(damage)

        if vulnerabilities is not None:
            for damage in vulnerabilities:
                new_vulnerabilities.add(damage)

        new_nonmagical_immunity = nonmagical_immunity or self.nonmagical_immunity
        new_nonmagical_resistance = nonmagical_resistance or self.nonmagical_resistance

        if (
            self.nonmagical_resistance
            and new_nonmagical_immunity
            and upgrade_resistance_to_immunity_if_present
        ):
            new_nonmagical_immunity = True

        if new_nonmagical_immunity:
            new_nonmagical_resistance = False

        new_conditions = self.condition_immunities.copy() | (conditions or set())

        return self.copy(
            damage_resistances=new_resistances,
            damage_immunities=new_immunities,
            damage_vulnerabilities=new_vulnerabilities,
            condition_immunities=new_conditions,
            nonmagical_immunity=new_nonmagical_immunity,
            nonmagical_resistance=new_nonmagical_resistance,
        )

    def grant_proficiency_or_expertise(self, *skills: Skills) -> BaseStatblock:
        attributes = self.attributes.grant_proficiency_or_expertise(*skills)
        return self.copy(attributes=attributes)

    def grant_save_proficiency(self, *saves: Stats) -> BaseStatblock:
        attributes = self.attributes.grant_save_proficiency(*saves)
        return self.copy(attributes=attributes)

    def add_attack(
        self,
        *,
        name: str,
        display_name: str | None = None,
        scalar: float,
        attack_type: AttackType | None = None,
        damage_type: DamageType | None = None,
        die: Die | None = None,
        callback: Callable[[Attack], Attack] | None = None,
        **attack_args,
    ) -> BaseStatblock:
        """create a new attack whose average damage is scaled"""

        target_damage = scalar * self.damage_modifier * self.base_attack_damage
        dmg_formula = DieFormula.target_value(
            target=target_damage, force_die=die, flat_mod=self.attributes.primary_mod
        )
        damage = Damage(dmg_formula, damage_type or self.primary_damage_type)

        copy_args: dict = dict(name=name, damage=damage, display_name=display_name)
        if attack_type:
            copy_args.update(attack_type=attack_type)
        copy_args.update(attack_args)

        new_attack = self.attack.copy(**copy_args)
        if callback is not None:
            new_attack = callback(new_attack)

        additional_attacks = [a for a in self.additional_attacks.copy()]
        additional_attacks.append(new_attack)

        return self.copy(additional_attacks=additional_attacks)

    def add_spells(self, spells: List[StatblockSpell]) -> BaseStatblock:
        new_spells = [s.copy() for s in self.spells]
        new_spells.extend([s.scale_for_cr(self.cr) for s in spells])
        return self.copy(spells=new_spells)

    def add_spell(self, spell: StatblockSpell) -> BaseStatblock:
        return self.add_spells([spell])

    def target_value(self, target: float = 1.0, **args) -> DieFormula:
        adjustment = 1.0

        # none of the monsters have 5 attacks, so raise an error if we try to scale more than 5 attacks
        if target >= 5:
            raise ValueError(f"Unexpected value for target: {target}")

        # low-CR monsters need to be careful with how much damage they pump out from non-attack abilities
        if self.cr <= 2:
            adjustment *= 0.8

        # if the multiplier is greater than the # of multiattacks then we also need to be careful
        if target > self.multiattack:
            adjustment *= 0.8

        scaled_target = (
            self.base_attack_damage * self.damage_modifier * target * adjustment
        )
        return DieFormula.target_value(target=scaled_target, **args)

    def with_roles(
        self,
        primary_role: MonsterRole | None = None,
        additional_roles: MonsterRole
        | set[MonsterRole]
        | list[MonsterRole]
        | None = None,
    ) -> BaseStatblock:
        if additional_roles is None:
            additional_roles = []

        if primary_role is None:
            primary_role = self.role

        if isinstance(additional_roles, MonsterRole):
            additional_roles = [additional_roles]
        elif isinstance(additional_roles, set):
            additional_roles = list(additional_roles)

        new_additional_roles = set(
            self.additional_roles.copy() + additional_roles + [self.role]
        )
        new_additional_roles.discard(MonsterRole.Default)

        return self.copy(role=primary_role, additional_roles=list(new_additional_roles))

    def as_legendary(
        self, *, actions: int = 3, resistances: int = 3, has_lair: bool = False
    ) -> BaseStatblock:
        stats = self.copy()
        if stats.is_legendary:
            return stats

        original_dpr = stats.dpr

        # HP and LR Adjustments

        # each legendary resistance will cost the monster some HP
        # so we'll want to increase the creature's HP to accomodate
        # we want bosses to die in about 4 turns so with a 4 person party that's 16 hits
        # the legendary action shouldn't feel like a waste, so it needs to do something on the order of 1/16th of the creature's HP
        # so we'll increase the creature's HP by half the amount of damage that each legendary resistance inflicts to help compensate

        turns_to_die = 3
        assumed_pcs = 4
        hits_to_die = turns_to_die * assumed_pcs
        average_damage_per_hit = stats.hp.average / hits_to_die
        lr_damage_effectiveness = (
            0.75  # it can't be 1.0 because then draining the LR would be too good
        )

        legendary_resistance_damage_taken = easy_multiple_of_five(
            lr_damage_effectiveness * average_damage_per_hit, min_val=5
        )
        new_hp_multiplier = 1.15 * (
            1.0
            + (
                0.75
                * legendary_resistance_damage_taken
                * resistances
                / stats.hp.average
            )
        )

        stats = stats.copy(
            is_legendary=True,
            legendary_actions=actions,
            legendary_resistances=resistances,
            legendary_resistance_damage_taken=legendary_resistance_damage_taken,
            has_lair=has_lair,
        )

        # AC Adjustments
        if stats.cr >= 22:
            ac_increase = 3
        elif stats.cr >= 16:
            ac_increase = 2
        else:
            ac_increase = 1

        # Damage Adjustments

        # The legendary creature will have an Attack legendary action, so its total damage output will go up dramatically
        # we need to adjust the creature's total damage output to account for this
        # we also want to reduce the total number of attacks the creature can make in a turn to not make it take too long
        if stats.multiattack >= 4:
            stats = stats.with_set_attacks(3)
        elif stats.multiattack >= 3:
            stats = stats.with_set_attacks(2)

        # Power Adjustments
        # legendary creature will have some more powers
        recommended_powers_modifier = 0.25

        # Apply HP, AC, and power adjustments
        stats = stats.apply_monster_dials(
            MonsterDials(
                hp_multiplier=new_hp_multiplier,
                ac_modifier=ac_increase,
                recommended_powers_modifier=recommended_powers_modifier,
            )
        )

        # Stat Adjustments
        stats = stats.scale({Stats.CON: 2})

        # Skill Adjustments
        # Initiative

        if stats.cr >= 8 and not stats.attributes.has_proficiency_or_expertise(
            Skills.Initiative
        ):
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        if (
            stats.cr >= 16
            and Skills.Initiative not in stats.attributes.expertise_skills
        ):
            stats = stats.grant_proficiency_or_expertise(Skills.Initiative)

        # Save Adjustments
        stats = stats.grant_save_proficiency(stats.primary_attribute, Stats.CON)

        if stats.cr >= 8:
            stats = stats.grant_save_proficiency(Stats.WIS)

        # Rescale Attack Damage
        target_dpr = 1.15 * original_dpr
        new_dpr = stats.dpr
        new_multiplier = target_dpr / new_dpr
        stats = stats.apply_monster_dials(
            MonsterDials(attack_damage_multiplier=new_multiplier)
        )

        return stats

    def with_set_attacks(self, multiattack: int) -> BaseStatblock:
        reduce_by = self.multiattack - multiattack
        if reduce_by < 0:
            raise ValueError(
                "multiattack must be less than or equal to the current value"
            )
        elif reduce_by == 0:
            return self.copy()
        else:
            return self.with_reduced_attacks(reduce_by=reduce_by)

    def with_reduced_attacks(
        self, reduce_by: int, min_attacks: int = 1
    ) -> BaseStatblock:
        if reduce_by <= 0:
            raise ValueError("reduce_by must be greater than 0")
        if reduce_by >= 4:
            raise ValueError("reduce_by must be less than 4")

        if self.multiattack <= min_attacks:
            return self.copy()
        elif self.multiattack - reduce_by < min_attacks:
            return self.with_reduced_attacks(
                reduce_by=reduce_by - 1, min_attacks=min_attacks
            )

        target_dpr = self.dpr
        stats = self.apply_monster_dials(MonsterDials(multiattack_modifier=-reduce_by))
        new_dpr = stats.dpr
        new_multiplier = target_dpr / new_dpr

        stats = stats.apply_monster_dials(
            MonsterDials(attack_damage_multiplier=new_multiplier)
        )
        return stats

    def with_flags(self, *flags: str) -> BaseStatblock:
        new_flags = self.flags.copy()
        new_flags.update(flags)
        return self.copy(flags=new_flags)


def _spell_list(all_spells: List[StatblockSpell], uses: int | None) -> str | None:
    spells = [s.caption_md for s in all_spells if s.uses == uses]
    if len(spells) == 0:
        return None

    if uses is None:
        line_prefix = "At will: "
    else:
        line_prefix = f"{uses}/day each: "

    return line_prefix + ", ".join(spells)
