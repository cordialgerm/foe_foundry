from typing import List

from foe_foundry.features import Feature
from foe_foundry.statblocks import BaseStatblock

from ...attack_template import weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Damage, DamageType
from ...die import DieFormula
from ...features import ActionType, Feature
from ...powers.power_type import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerType
from ..scoring import score
from .organized import score_could_be_organized


class _ArcaneHunt(Power):
    def __init__(self):
        super().__init__(name="Arcane Hunt", power_type=PowerType.Theme, power_level=LOW_POWER)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Aberration,
                CreatureType.Monstrosity,
                CreatureType.Fiend,
            ],
            require_attack_types=AttackType.MeleeNatural,
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Ambusher],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Arcane Hunt",
            action=ActionType.Reaction,
            description=f"Whenever a creature within 120 feet casts a spell, {stats.selfref} howls with hunger and moves up to its speed towards the caster. \
                It gains advantage on attacks against the caster until the end of its next turn.",
        )
        return [feature]


class _FractalForm(Power):
    def __init__(self):
        super().__init__(name="Fractal Form", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Aberration,
                CreatureType.Construct,
                CreatureType.Celestial,
            ],
            bonus_attack_types=AttackType.AllMelee(),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Fractal Form",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s form is an impossibly shifting visage of strange fractal shapes. It cannot be targeted by attacks or spells \
                unless the source of that attack or spell is within 10 feet of {stats.selfref}.",
        )
        return [feature]


class _MageSlayer(Power):
    def __init__(self):
        super().__init__(name="Mage Slayer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        def is_organized(c: BaseStatblock) -> bool:
            return score_could_be_organized(c, requires_intelligence=True) > 0

        return score(
            candidate=candidate,
            require_attack_types=AttackType.MeleeWeapon,
            require_callback=is_organized,
            bonus_roles=MonsterRole.Bruiser,
            attack_names=[
                weapon.SwordAndShield,
                weapon.Greataxe,
                weapon.Greatsword,
                weapon.MaceAndShield,
                weapon.Polearm,
                weapon.SpearAndShield,
                weapon.Greatsword,
            ],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Mage Slayer",
            action=ActionType.Reaction,
            description=f"If a hostile creature begins casting a spell within reach of {stats.selfref} then it may make a melee attack against the caster. \
                If the attack hits, the caster must make a Concentration check against the damage of the attack. On a failure, the spell casting fails.",
        )
        return [feature]


class _RedirectTeleport(Power):
    def __init__(self):
        super().__init__(name="Redirect Teleport", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Aberration,
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Celestial,
                CreatureType.Monstrosity,
            ],
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[MonsterRole.Controller, MonsterRole.Leader],
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Redirect Teleport",
            action=ActionType.Reaction,
            description=f"Whenever a creature that {stats.selfref} can see within 120 feet begins teleporting, {stats.selfref} can redirect that teleportation. \
                The original teleportation spell or effect fails, and instead the creature is transported to the nearest unoccupied space. \
                The space must be on a solid or liquid that can support the creature.",
        )
        return [feature]


class _SpellEater(Power):
    def __init__(self):
        super().__init__(name="Spell Eater", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[CreatureType.Aberration, CreatureType.Fey, CreatureType.Monstrosity],
            require_attack_types=AttackType.AllNatural(),
            require_cr=5,
            bonus_roles=[MonsterRole.Controller, MonsterRole.Bruiser],
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        def additional_description(a: Attack) -> Attack:
            return a.split_damage(DamageType.Force, split_ratio=0.75).copy(
                custom_target="one target that can cast a spell",
                additional_description=f"On a hit, the target loses its highest level spell slot. If the target has no spell slots remaining, it is **Stunned** until the end of its next turn.",
            )

        stats = stats.add_attack(
            name="Devour Spell",
            scalar=2.2,
            damage_type=DamageType.Piercing,
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            callback=additional_description,
        )

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _SpellStealer(Power):
    def __init__(self):
        super().__init__(name="Spell Stealer", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        def humanoid_is_arcane_trickster(c: BaseStatblock) -> bool:
            if (
                c.creature_type == CreatureType.Humanoid
                and c.attack.name != weapon.Daggers.attack_name
            ):
                return False
            return True

        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Humanoid,
                CreatureType.Fey,
                CreatureType.Aberration,
                CreatureType.Monstrosity,
            ],
            require_roles=[MonsterRole.Controller, MonsterRole.Ambusher, MonsterRole.Leader],
            require_callback=humanoid_is_arcane_trickster,
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        feature = Feature(
            name="Spell Stealer",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, if the target is a spellcaster, the spellcaster must make a DC {dc} Charisma saving throw. \
                On a failure, the target is cursed and loses the ability to cast a spell of {stats.selfref}'s choice while cursed in this way. \
                The curse can be removed with a *Remove Curse* spell or similar magic.",
        )
        return [feature]


class _TwistedMind(Power):
    def __init__(self):
        super().__init__(name="Tiwsted Mind", power_type=PowerType.Theme)

    def score(self, candidate: BaseStatblock) -> float:
        return score(
            candidate=candidate,
            require_types=[
                CreatureType.Aberration,
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Celestial,
                CreatureType.Monstrosity,
            ],
            bonus_damage=DamageType.Psychic,
            bonus_roles=MonsterRole.Controller,
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        if stats.cr >= 5:
            new_attributes = stats.attributes.grant_save_proficiency(
                Stats.WIS, Stats.INT, Stats.CHA
            )
            stats = stats.copy(attributes=new_attributes)

        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Twisted Mind",
            action=ActionType.Feature,
            description=f"If {stats.selfref} succeeds on a Wisdom, Intelligence, or Charisma saving throw against a spell or effect then it may reflect the effect back at its source. \
                The original source of the spell or effect must make the save as if it were a target of the spell or effect.",
        )
        return [feature]


ArcaneHunt: Power = _ArcaneHunt()
FractalForm: Power = _FractalForm()
MageSlayer: Power = _MageSlayer()
RedirectTeleport: Power = _RedirectTeleport()
SpellEater: Power = _SpellEater()
SpellStealer: Power = _SpellStealer()
TwistedMind: Power = _TwistedMind()

AntiMagicPowers: List[Power] = [
    ArcaneHunt,
    FractalForm,
    MageSlayer,
    RedirectTeleport,
    SpellEater,
    SpellStealer,
    TwistedMind,
]