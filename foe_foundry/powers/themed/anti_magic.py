from datetime import datetime
from typing import List

from ...attack_template import weapon
from ...attributes import Stats
from ...creature_types import CreatureType
from ...damage import Attack, AttackType, Condition, DamageType, conditions
from ...features import ActionType, Feature
from ...power_types import PowerType
from ...role_types import MonsterRole
from ...statblocks import BaseStatblock
from ..power import LOW_POWER, Power, PowerCategory, PowerWithStandardScoring


class _ArcaneHunt(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Aberration,
                CreatureType.Monstrosity,
                CreatureType.Fiend,
            ],
            require_attack_types=AttackType.MeleeNatural,
            bonus_roles=[
                MonsterRole.Bruiser,
                MonsterRole.Ambusher,
                MonsterRole.Soldier,
            ],
        )

        super().__init__(
            name="Arcane Hunt",
            power_category=PowerCategory.Theme,
            power_level=LOW_POWER,
            source="Foe Foundry",
            reference_statblock="Death Dog",
            icon="hunter-eyes",
            theme="Anti-Magic",
            power_types=[PowerType.Movement, PowerType.Debuff],
            score_args=score_args,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Arcane Hunt",
            action=ActionType.Reaction,
            description=f"Whenever a creature within 120 feet casts a spell, {stats.selfref} howls with hunger and moves up to its speed towards the caster. \
                It gains advantage on attacks against the caster until the end of its next turn.",
        )
        return [feature]


class _FractalForm(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Aberration,
                CreatureType.Construct,
                CreatureType.Celestial,
            ],
            bonus_attack_types=AttackType.AllMelee(),
        )
        super().__init__(
            name="Fractal Form",
            power_category=PowerCategory.Theme,
            source="Foe Foundry",
            theme="Anti-Magic",
            icon="abstract-061",
            reference_statblock="Deva",
            power_types=[PowerType.Defense],
            score_args=score_args,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Fractal Form",
            action=ActionType.Feature,
            description=f"{stats.selfref.capitalize()}'s form is an impossibly shifting visage of strange fractal shapes. It cannot be targeted by attacks or spells \
                unless the source of that attack or spell is within 10 feet of {stats.selfref}.",
        )
        return [feature]


class _Spellbreaker(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_attack_types=AttackType.MeleeWeapon,
            bonus_roles=[MonsterRole.Bruiser, MonsterRole.Soldier],
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
        super().__init__(
            name="Spellbreaker",
            power_category=PowerCategory.Theme,
            source="A5E SRD Spellbreaker",
            theme="Anti-Magic",
            icon="cancel",
            reference_statblock="Berserker",
            power_types=[PowerType.Debuff],
            score_args=score_args,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Spellbreaker",
            action=ActionType.Reaction,
            description=f"If a hostile creature begins casting a spell within reach of {stats.selfref} then it may make a melee attack against the caster. \
                If the attack hits, the caster must make a Concentration check against the damage of the attack. On a failure, the spell casting fails.",
        )
        return [feature]


class _RedirectTeleport(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Aberration,
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Celestial,
                CreatureType.Monstrosity,
            ],
            require_attack_types=AttackType.AllMelee(),
            bonus_roles=[
                MonsterRole.Controller,
                MonsterRole.Leader,
                MonsterRole.Support,
            ],
        )

        super().__init__(
            name="Redirect Teleport",
            source="Foe Foundry",
            theme="Anti-Magic",
            icon="direction-signs",
            reference_statblock="Aboleth",
            power_category=PowerCategory.Theme,
            power_types=[PowerType.Movement, PowerType.Debuff],
            score_args=score_args,
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Redirect Teleport",
            action=ActionType.Reaction,
            description=f"Whenever a creature that {stats.selfref} can see within 120 feet begins teleporting, {stats.selfref} can redirect that teleportation. \
                The original teleportation spell or effect fails, and instead the creature is transported to the nearest unoccupied space. \
                The space must be on a solid or liquid that can support the creature.",
        )
        return [feature]


class _SpellEater(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Aberration,
                CreatureType.Fey,
                CreatureType.Monstrosity,
            ],
            require_attack_types=AttackType.AllNatural(),
            require_cr=5,
            bonus_roles=[
                MonsterRole.Controller,
                MonsterRole.Bruiser,
                MonsterRole.Soldier,
                MonsterRole.Support,
            ],
        )
        super().__init__(
            name="Spell Eater",
            source="Foe Foundry",
            theme="Anti-Magic",
            icon="swallow",
            reference_statblock="Chuul",
            power_category=PowerCategory.Theme,
            power_types=[PowerType.Attack, PowerType.Debuff],
            score_args=score_args,
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        stunned = Condition.Stunned

        def additional_description(a: Attack) -> Attack:
            return a.split_damage(DamageType.Force, split_ratio=0.75).copy(
                custom_target="one target that can cast a spell",
                additional_description=f"On a hit, the target loses its highest level spell slot. If the target has no spell slots remaining, it is {stunned.caption} until the end of its next turn.",
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

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        return []


class _SpellStealer(PowerWithStandardScoring):
    def __init__(self):
        def humanoid_is_arcane_trickster(c: BaseStatblock) -> bool:
            if (
                c.creature_type == CreatureType.Humanoid
                and c.attack.name != weapon.Daggers.attack_name
            ):
                return False
            return True

        score_args = dict(
            require_types=[
                CreatureType.Humanoid,
                CreatureType.Fey,
                CreatureType.Aberration,
                CreatureType.Monstrosity,
            ],
            require_roles=[
                MonsterRole.Controller,
                MonsterRole.Ambusher,
                MonsterRole.Leader,
                MonsterRole.Support,
            ],
            require_callback=humanoid_is_arcane_trickster,
        )

        super().__init__(
            name="Spell Stealer",
            source="Foe Foundry",
            theme="Anti-Magic",
            icon="robber",
            reference_statblock="Spy",
            power_category=PowerCategory.Theme,
            score_args=score_args,
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class_easy
        cursed = conditions.Cursed().caption
        feature = Feature(
            name="Spell Stealer",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"On a hit, if the target is a spellcaster, the spellcaster must make a DC {dc} Charisma saving throw. \
                On a failure, the target is {cursed} and loses the ability to cast a spell of {stats.selfref}'s choice while cursed in this way. \
                The curse can be removed with a *Remove Curse* spell or similar magic.",
        )
        return [feature]


class _TwistedMind(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
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
        super().__init__(
            name="Tiwsted Mind",
            source="Foe Foundry",
            theme="Anti-Magic",
            icon="brain-tentacle",
            reference_statblock="Aboleth",
            power_category=PowerCategory.Theme,
            score_args=score_args,
            power_types=[PowerType.Defense],
        )

    def modify_stats_inner(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Psychic)

        if stats.cr >= 5:
            new_attributes = stats.attributes.grant_save_proficiency(
                Stats.WIS, Stats.INT, Stats.CHA
            )
            stats = stats.copy(attributes=new_attributes)

        return stats

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Twisted Mind",
            action=ActionType.Feature,
            description=f"If {stats.selfref} succeeds on a Wisdom, Intelligence, or Charisma saving throw against a spell or effect then it may reflect the effect back at its source. \
                The original source of the spell or effect must make the save as if it were a target of the spell or effect.",
        )
        return [feature]


class _SealOfSilence(PowerWithStandardScoring):
    def __init__(self):
        score_args = dict(
            require_types=[
                CreatureType.Humanoid,
                CreatureType.Fey,
                CreatureType.Fiend,
                CreatureType.Celestial,
            ],
            require_roles=[
                MonsterRole.Defender,
                MonsterRole.Leader,
                MonsterRole.Controller,
                MonsterRole.Support,
            ],
            require_cr=7,
        )
        super().__init__(
            name="Seal of Silence",
            source="A5E SRD Dread Knight Champion",
            theme="Anti-Magic",
            reference_statblock="Wight",
            icon="silenced",
            create_date=datetime(2023, 11, 22),
            power_category=PowerCategory.Theme,
            score_args=score_args,
            power_types=[PowerType.Debuff],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Seal of Silence",
            action=ActionType.Feature,
            description=f"When {stats.selfref} succeeeds on a saving throw against a spell cast by a creature it can see, the caster of the spell makes a DC {stats.difficulty_class} \
                Constitution saving throw. On a failure, the caster is magically unable to speak or cast spells with a vocal component until the end of the caster's next turn.",
        )
        return [feature]


class _RuneDrinker(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Rune Drinker",
            source="A5E SRD Chuul",
            theme="Anti-Magic",
            icon="rune-stone",
            reference_statblock="Chuul",
            create_date=datetime(2023, 11, 28),
            power_category=PowerCategory.Theme,
            score_args=dict(
                require_types=[CreatureType.Monstrosity, CreatureType.Aberration],
                bonus_roles=[MonsterRole.Defender],
                require_cr=1,
            ),
            power_types=[PowerType.Defense],
        )

    def generate_features_inner(self, stats: BaseStatblock) -> List[Feature]:
        feature = Feature(
            name="Rune Drinker",
            action=ActionType.Feature,
            description=f"Whenever {stats.selfref} takes damage from a magic weapon, until the start of {stats.selfref}'s next turn, \
                attacks made with that weapon have disadvantage, and {stats.selfref} gains a +4 bonus to its AC.",
        )
        return [feature]


ArcaneHunt: Power = _ArcaneHunt()
FractalForm: Power = _FractalForm()
RedirectTeleport: Power = _RedirectTeleport()
RuneDrinker: Power = _RuneDrinker()
SealOfSilence: Power = _SealOfSilence()
Spellbreaker: Power = _Spellbreaker()
SpellEater: Power = _SpellEater()
SpellStealer: Power = _SpellStealer()
TwistedMind: Power = _TwistedMind()

AntiMagicPowers: List[Power] = [
    ArcaneHunt,
    FractalForm,
    RedirectTeleport,
    RuneDrinker,
    SealOfSilence,
    Spellbreaker,
    SpellEater,
    SpellStealer,
    TwistedMind,
]
