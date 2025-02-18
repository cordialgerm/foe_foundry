from typing import List

import numpy as np

from ...ac_templates import HeavyArmor
from ...attack_template import natural, spell, weapon
from ...attributes import Skills, Stats
from ...creature_types import CreatureType
from ...damage import AttackType, DamageType, conditions
from ...die import Die
from ...features import ActionType, Feature
from ...role_types import MonsterRole
from ...spells import transmutation
from ...statblocks import BaseStatblock
from ...utils import easy_multiple_of_five
from ...utils.summoning import determine_summon_formula
from ..creatures import giant
from ..power import HIGH_POWER, MEDIUM_POWER, Power, PowerType, PowerWithStandardScoring
from ..roles import artillery, bruiser
from ..themed import fast, holy, organized, reckless, tough


class _DeathKnight(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Dread Knight",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=[CreatureType.Undead, CreatureType.Humanoid],
                require_roles=[
                    MonsterRole.Leader,
                    MonsterRole.Default,
                    MonsterRole.Bruiser,
                ],
                require_stats=[Stats.CHA, Stats.STR],
                bonus_damage=DamageType.Necrotic,
                attack_names=[
                    "-",  # default is NO_AFFINITY - that's what - means
                    weapon.SwordAndShield,
                    weapon.MaceAndShield,
                    weapon.Greataxe,
                    weapon.Greatsword,
                ],
                require_cr=5,
            ),
        )

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        if stats.secondary_damage_type != DamageType.Necrotic:
            stats = stats.copy(secondary_damage_type=DamageType.Necrotic)

        stats = stats.copy(creature_class="Death Knight")
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(2)})
        return stats

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        cr_target = stats.cr / 4

        feature1 = Feature(
            name="Death Knight's Curse",
            action=ActionType.Action,
            replaces_multiattack=1,
            uses=1,
            description=f"{stats.roleref.capitalize()} curses up to four targets it can see within 30 feet. \
                Each target must make a DC {dc} Charisma save or be affected as by the *Bane* spell (save ends at end of turn).",
        )

        # TODO - remove rng
        rng = np.random.default_rng(20210518)
        _, _, description = determine_summon_formula(
            summoner=CreatureType.Undead, summon_cr_target=cr_target, rng=rng
        )

        feature2 = Feature(
            name="Death Knight's Summons",
            action=ActionType.Action,
            uses=1,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} calls upon the dead to serve. {description}",
        )

        return [feature1, feature2]


def _EldritchKnights() -> List[Power]:
    class _EldritchKnight(PowerWithStandardScoring):
        def __init__(self, element: DamageType):
            self.element = element
            super().__init__(
                name=f"Eldritch Knight {element.adj.capitalize()}",
                power_type=PowerType.Theme,
                power_level=HIGH_POWER,
                source="Foe Foundry",
                theme="class",
                score_args=dict(
                    require_no_creature_class=True,
                    require_types=[CreatureType.Humanoid, CreatureType.Fey],
                    bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Bruiser],
                    require_stats=[Stats.INT, Stats.STR],
                    bonus_damage=element,
                    require_damage_exact_match=True,
                    require_cr=3,
                    attack_names=[
                        "-",
                        weapon.SwordAndShield,
                        weapon.Greataxe,
                        weapon.Greatsword,
                        weapon.MaceAndShield,
                        weapon.RapierAndShield,
                        weapon.Polearm,
                        weapon.Maul,
                        weapon.Staff,
                    ],
                    # reduce odds of each individual occurance because there are 3 eldritch knight options
                    score_multiplier=0.75,
                ),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dc = stats.difficulty_class_easy
            dmg = stats.target_value(1.5)

            feature1 = Feature(
                name="Misty Step",
                action=ActionType.BonusAction,
                uses=3,
                description=f"{stats.roleref.capitalize()} teleports up to 30 feet to an unoccupied space it can see",
            )

            feature2 = Feature(
                name="Elemental Burst",
                action=ActionType.Action,
                replaces_multiattack=2,
                recharge=5,
                description=f"{stats.roleref.capitalize()} unleashes an explosion of arcane power. \
                    Each creature in a 20-foot radius sphere centered on a point within 60 feet must make \
                    a DC {dc} Dexterity saving throw, taking {dmg.description} {self.element} damage on a failure. \
                    On a success, a creature takes half damage instead.",
            )

            return [feature1, feature2]

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            stats = stats.copy(secondary_damage_type=self.element)
            stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})
            stats = stats.copy(
                creature_class="Eldritch Knight", has_unique_movement_manipulation=True
            )
            return stats

    return [
        _EldritchKnight(element)
        for element in [DamageType.Fire, DamageType.Cold, DamageType.Lightning]
    ]


class _Artificer(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Artificer",
            source="Foe Foundry",
            theme="class",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                bonus_roles=[MonsterRole.Defender, MonsterRole.Leader],
                require_types=CreatureType.Humanoid,
                require_stats=Stats.INT,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.MaceAndShield,
                    weapon.SwordAndShield,
                    natural.Slam,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dazed = conditions.Dazed()
        dmg = stats.target_value(1.5, force_die=Die.d10)
        feature = Feature(
            name="Artificer's Cannon",
            action=ActionType.Action,
            recharge=5,
            replaces_multiattack=2,
            description=f"{stats.roleref.capitalize()} fires an arcane cannon at a creature it can see within 60 feet. \
                The target must make a DC {dc} Dexterity saving throw, taking {dmg.description} force damage on a failure. \
                On a success, the target takes half damage instead. If the save fails by 5 or more, the target is also {dazed.caption} for 1 minute (save ends at end of turn). {dazed.description_3rd}",
        )
        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.add_ac_template(HeavyArmor)
        stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})
        stats = stats.copy(creature_class="Artificer")
        stats = stats.copy(secondary_damage_type=DamageType.Force)
        return stats


class _Barbarian(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Barbarian",
            source="Foe Foundry",
            theme="class",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                bonus_roles=MonsterRole.Bruiser,
                require_types=[CreatureType.Humanoid, CreatureType.Giant],
                require_stats=Stats.STR,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.Greataxe,
                    weapon.Greatsword,
                    weapon.Polearm,
                    weapon.Maul,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Rage",
            action=ActionType.Feature,
            modifies_attack=True,
            hidden=True,
            description=f"On a hit, {stats.roleref} gains resistance to Bludgeoning, Slashing, and Piercing damage until the end of its next turn",
        )

        feature2 = reckless.Toss.generate_features(stats)

        return [feature1] + feature2

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(creature_class="Barbarian")
        stats = stats.scale({Stats.STR: Stats.STR.Boost(2)})
        stats = reckless.Toss.modify_stats(stats)
        return stats


class _Bard(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Bardic",
            source="Foe Foundry",
            theme="class",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                require_types=[CreatureType.Humanoid, CreatureType.Fey],
                bonus_roles=[MonsterRole.Controller, MonsterRole.Leader],
                require_stats=Stats.CHA,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.RapierAndShield,
                    weapon.Shortswords,
                    weapon.Shortbow,
                    weapon.Longbow,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dc = stats.difficulty_class
        dmg = stats.target_value(0.5, force_die=Die.d4)
        dazed = conditions.Dazed()

        feature1 = Feature(
            name="Vicious Mockery",
            action=ActionType.Action,
            replaces_multiattack=1,
            description=f"{stats.roleref.capitalize()} viciously mocks a target it can see within 60 ft. If the target can hear the insult, it must make a DC {dc} Wisdom save. \
                On a failure, it takes {dmg.description} psychic damage. Also, if {stats.roleref} has hit the target with an attack this turn and the target fails the save, \
                it becomes {dazed.caption} until the end of its next turn. {dazed.description_3rd}",
        )

        feature2 = Feature(
            name="Bardic Inspiration",
            action=ActionType.Reaction,
            uses=3,
            description=f"Whenever an ally within 30 feet that can hear {stats.roleref} misses with an attack or fails a saving throw, it can roll 1d4 and add the total to its result, potentially turning a failure into a success.",
        )

        return [feature1, feature2]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(
            secondary_damage_type=DamageType.Psychic, creature_class="Bard"
        )
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(2)})
        return stats


class _WarPriest(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="War Priest",
            source="Foe Foundry",
            theme="class",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                require_types=CreatureType.Humanoid,
                require_stats=Stats.WIS,
                bonus_roles=[MonsterRole.Leader, MonsterRole.Defender],
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.MaceAndShield,
                    weapon.SwordAndShield,
                    weapon.Greatsword,
                    weapon.Maul,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        dmg = stats.target_value(0.75, force_die=Die.d6)

        feature1 = holy.MassCureWounds.generate_features(stats)

        feature2 = Feature(
            name="War God's Blessing",
            action=ActionType.Reaction,
            recharge=6,
            description=f"Whenever another ally within 30 feet of {stats.roleref} makes an attack, {stats.roleref} \
                can add +10 to the attack roll. If the attack hits, it deals an additional {dmg.description} radiant damage",
        )

        return feature1 + [feature2]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(
            secondary_damage_type=DamageType.Radiant, creature_class="Cleric"
        )
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        stats = holy.MassCureWounds.modify_stats(stats)
        return stats


class _Ranger(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Ranger",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=[CreatureType.Humanoid, CreatureType.Fey],
                require_stats=Stats.DEX,
                bonus_roles=[
                    MonsterRole.Ambusher,
                    MonsterRole.Skirmisher,
                    MonsterRole.Artillery,
                ],
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.Longbow,
                    weapon.Shortbow,
                    weapon.Shortswords,
                    weapon.Daggers,
                    weapon.JavelinAndShield,
                    weapon.Crossbow,
                    weapon.HandCrossbow,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        return artillery.FocusShot.generate_features(stats)

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        new_attrs = stats.attributes.grant_proficiency_or_expertise(Skills.Perception)
        stats = stats.copy(creature_class="Ranger", attributes=new_attrs)
        stats = stats.scale({Stats.DEX: Stats.DEX.Boost(2)})
        stats = artillery.FocusShot.modify_stats(stats)
        stats = stats.add_spell(transmutation.SpikeGrowth.for_statblock())
        return stats


def _ArcaneArchers() -> List[Power]:
    class _ArcaneArcher(PowerWithStandardScoring):
        def __init__(self, option_index: int):
            self.option_index = option_index
            super().__init__(
                name="Arcane Archer",
                power_type=PowerType.Theme,
                power_level=HIGH_POWER,
                source="Foe Foundry",
                theme="class",
                score_args=dict(
                    require_no_creature_class=True,
                    require_types=[CreatureType.Humanoid, CreatureType.Fey],
                    require_stats=Stats.DEX,
                    bonus_roles=[
                        MonsterRole.Artillery,
                        MonsterRole.Ambusher,
                        MonsterRole.Skirmisher,
                    ],
                    require_cr=3,
                    attack_names=[
                        "-",
                        weapon.Longbow,
                        weapon.Shortbow,
                        weapon.Crossbow,
                        weapon.HandCrossbow,
                    ],
                    # reduce odds of each individual occurance because there are 3 arcane archer options
                    score_multiplier=0.75,
                ),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            dazed = conditions.Dazed()
            weakened = conditions.Weakened()
            dc = stats.difficulty_class
            dmg = stats.target_value(0.6, force_die=Die.d10)

            feature1 = Feature(
                name="Dazing Arrow",
                action=ActionType.BonusAction,
                recharge=5,
                description=f"Immediately after hitting a target with an attack, {stats.roleref} attempts to addle the target's mind with fey magics. \
                    The target must make a DC {dc} Charisma saving throw or be {dazed.caption} for 1 minute (save ends at end of turn). {dazed.description_3rd}",
            )

            feature2 = Feature(
                name="Exploding Arrow",
                action=ActionType.BonusAction,
                recharge=5,
                description=f"Immediately after hitting a target with attack, {stats.roleref} causes the arrow to explode. \
                    Each creature within 10 feet of the target (including the target) must make a DC {dc} Dexterity saving throw \
                    or take an additional {dmg.description} fire damage.",
            )

            feature3 = Feature(
                name="Enfeebling Arrow",
                action=ActionType.BonusAction,
                recharge=5,
                description=f"Immediately after hitting a target with an attack, {stats.roleref} forces the target to make a DC {dc} Constitution save. \
                    On a failure, the target is {weakened.caption} for 1 minute (save ends at end of turn). {weakened.description}",
            )

            options = [feature1, feature2, feature3]
            feature = options[self.option_index]

            return [feature]

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            stats = stats.copy(creature_class="Arcane Archer")
            return stats

    return [_ArcaneArcher(i) for i in range(3)]


class _PsiWarrior(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Psi Warrior",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=[CreatureType.Humanoid],
                bonus_roles=[MonsterRole.Skirmisher, MonsterRole.Leader],
                require_stats=Stats.INT,
                bonus_stats=Stats.WIS,
                bonus_damage=DamageType.Psychic,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.RapierAndShield,
                    weapon.SwordAndShield,
                    weapon.Shortswords,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        protection = easy_multiple_of_five(stats.cr * 1.5, min_val=5, max_val=60)

        feature1 = Feature(
            name="Psionic Jump",
            action=ActionType.BonusAction,
            uses=3,
            description=f"{stats.roleref.capitalize()} performes a psionically boosted jump of up to 30 feet.",
        )

        feature2 = Feature(
            name="Protective Field",
            action=ActionType.Reaction,
            uses=1,
            description=f"When an ally within 30 feet of {stats.roleref} takes damage, {stats.roleref} creates a protective barrier around that ally, \
                preventing up to {protection} of the triggering damage",
        )

        return [feature1, feature2]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(
            secondary_damage_type=DamageType.Psychic,
            creature_class="Psi Warrior",
        )
        stats = stats.scale({Stats.INT: Stats.INT.Boost(2)})

        stats = stats.add_spell(transmutation.Telekinesis.for_statblock())

        return stats


class _Cavalier(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Cavalier",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=CreatureType.Humanoid,
                bonus_roles=MonsterRole.Leader,
                require_cr=3,
                attack_names=["-", weapon.Greatsword, weapon.Greataxe],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Summon Mount",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.roleref.capitalize()} summons a *Warhorse* mount to an unoccupied location within 30 feet which acts as a controlled mount. \
                {stats.roleref.capitalize()} may mount the warhorse without expending any movement",
        )

        feature2 = Feature(
            name="Expert Rider",
            action=ActionType.Feature,
            description=f"{stats.roleref.capitalize()} may force any attack targeting its mount to target {stats.roleref} instead",
        )

        feature3 = Feature(
            name="Mounted Advantage",
            action=ActionType.Feature,
            hidden=True,
            modifies_attack=True,
            description=f"The attack is made at advantage if {stats.roleref} is mounted",
        )

        return [feature1, feature2, feature3]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(creature_class="Cavalier")
        return stats


def _RuneKnights() -> List[Power]:
    class _RuneKnight(PowerWithStandardScoring):
        def __init__(self, rune: Power):
            self.rune = rune
            super().__init__(
                name=f"Rune Knight {rune.name}",
                power_type=PowerType.Theme,
                theme="class",
                power_level=HIGH_POWER,
                source="Foe Foundry",
                score_args=dict(
                    require_no_creature_class=True,
                    require_types=[CreatureType.Humanoid, CreatureType.Giant],
                    bonus_roles=[MonsterRole.Bruiser, MonsterRole.Leader],
                    bonus_damage=rune.damage_types,
                    require_stats=Stats.STR,
                    require_cr=3,
                    attack_names=[
                        "-",
                        weapon.Greataxe,
                        weapon.Greatsword,
                        weapon.Maul,
                        weapon.SwordAndShield,
                        weapon.MaceAndShield,
                    ],
                    # reduce odds of each individual occurance because there are 3 rune knight options
                    score_multiplier=0.75,
                ),
            )

        def generate_features(self, stats: BaseStatblock) -> List[Feature]:
            feature1 = Feature(
                name="Runic Armor",
                action=ActionType.Reaction,
                uses=1,
                description=f"The first time {stats.roleref} takes damage from an attack, the runes on its armor flare up and grant {stats.roleref} \
                    resistance to that attack's damage",
            )

            feature2 = self.rune.generate_features(stats)

            return [feature1] + feature2

        def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
            stats = stats.copy(creature_class="Rune Knight")
            stats = stats.add_ac_template(HeavyArmor, ac_modifier=1)
            stats = self.rune.modify_stats(stats)
            return stats

    return [
        _RuneKnight(rune) for rune in [giant.FireRune, giant.FrostRune, giant.StormRune]
    ]


class _Samurai(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Samurai",
            power_type=PowerType.Theme,
            theme="class",
            source="Foe Foundry",
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                require_types=CreatureType.Humanoid,
                bonus_roles=[MonsterRole.Leader, MonsterRole.Defender],
                require_stats=Stats.STR,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.Shortswords,
                    weapon.SwordAndShield,
                    weapon.Greatsword,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        temp_hp = easy_multiple_of_five(3.5 * stats.cr, min_val=5, max_val=50)
        feature1 = Feature(
            name="Fighting Spirit",
            action=ActionType.BonusAction,
            uses=1,
            description=f"{stats.roleref.capitalize()} channels its inner fighting spirit. It gains {temp_hp} temporary hp. While those temporary hp are active, \
                {stats.roleref} has advantage on attack rolls and saving throws",
        )

        feature2 = tough.JustAScratch.generate_features(stats)

        return [feature1] + feature2

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(creature_class="Samurai")
        stats = stats.scale({Stats.STR: Stats.STR.Boost(2)})
        stats = tough.JustAScratch.modify_stats(stats)
        return stats


class _Monk(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Monk",
            power_type=PowerType.Theme,
            source="Foe Foundry",
            theme="class",
            power_level=HIGH_POWER,
            score_args=dict(
                require_roles=[
                    MonsterRole.Skirmisher,
                    MonsterRole.Leader,
                    MonsterRole.Bruiser,
                ],
                require_stats=Stats.DEX,
                require_types=CreatureType.Humanoid,
                require_no_creature_class=True,
                require_cr=3,
                attack_names=["-", natural.Slam],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = bruiser.StunningBlow.generate_features(stats)
        feature2 = fast.Evasion.generate_features(stats)
        return feature1 + feature2

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(creature_class="Monk")
        stats = stats.scale({Stats.DEX: Stats.DEX.Boost(2)})
        stats = bruiser.StunningBlow.modify_stats(stats)
        stats = fast.Evasion.modify_stats(stats)
        return stats


class _Paladin(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Paladin",
            power_type=PowerType.Theme,
            source="Foe Foundry",
            theme="class",
            power_level=HIGH_POWER,
            score_args=dict(
                require_no_creature_class=True,
                require_types=CreatureType.Humanoid,
                bonus_damage=DamageType.Radiant,
                require_stats=Stats.STR,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.SwordAndShield,
                    weapon.MaceAndShield,
                    weapon.Maul,
                    weapon.Greatsword,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = organized.InspiringCommander.generate_features(stats)
        feature2 = holy.DivineSmite.generate_features(stats)
        return feature1 + feature2

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(
            secondary_damage_type=DamageType.Radiant, creature_class="Paladin"
        )
        stats = stats.scale({Stats.CHA: Stats.CHA.Boost(2)})
        stats = organized.InspiringCommander.modify_stats(stats)
        stats = holy.DivineSmite.modify_stats(stats)
        return stats


class _Cleric(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Cleric",
            power_type=PowerType.Theme,
            power_level=HIGH_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=CreatureType.Humanoid,
                bonus_damage=DamageType.Radiant,
                require_stats=Stats.WIS,
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.SwordAndShield,
                    weapon.MaceAndShield,
                    weapon.Maul,
                    weapon.Greatsword,
                    spell.HolyBolt,
                ],
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        feature1 = Feature(
            name="Favored by the Gods",
            action=ActionType.Reaction,
            uses=1,
            description=f"When {stats.roleref} fails a saving throw or misses an attack it may add 2d4 to that result",
        )

        feature2 = holy.WordOfRadiance.generate_features(stats)
        return [feature1] + feature2

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.copy(
            secondary_damage_type=DamageType.Radiant, creature_class="Cleric"
        )
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        stats = holy.WordOfRadiance.modify_stats(stats)
        return stats


class _Druid(PowerWithStandardScoring):
    def __init__(self):
        super().__init__(
            name="Druid",
            power_type=PowerType.Theme,
            power_level=MEDIUM_POWER,
            source="Foe Foundry",
            theme="class",
            score_args=dict(
                require_no_creature_class=True,
                require_types=[
                    CreatureType.Humanoid,
                    CreatureType.Fey,
                    CreatureType.Giant,
                ],
                bonus_roles=[
                    MonsterRole.Leader,
                    MonsterRole.Controller,
                    MonsterRole.Skirmisher,
                ],
                require_cr=3,
                attack_names=[
                    "-",
                    weapon.Staff,
                    weapon.Longbow,
                    weapon.Shortbow,
                    spell.Poisonbolt,
                    spell.Frostbolt,
                    spell.Firebolt,
                ],
                require_stats=Stats.WIS,
            ),
        )

    def generate_features(self, stats: BaseStatblock) -> List[Feature]:
        healing = stats.target_value(
            0.5, force_die=Die.d4, flat_mod=stats.attributes.WIS
        )
        uses = stats.attributes.stat_mod(Stats.WIS)

        feature = Feature(
            name="Druidic Healing",
            action=ActionType.BonusAction,
            uses=uses,
            description=f"{stats.roleref.capitalize()} utters a word of primal encouragement to a friendly ally it can see within 60 feet. \
                The ally regains {healing.description} hitpoints.",
        )

        return [feature]

    def modify_stats(self, stats: BaseStatblock) -> BaseStatblock:
        stats = stats.scale({Stats.WIS: Stats.WIS.Boost(2)})
        if stats.secondary_damage_type is None:
            stats = stats.copy(secondary_damage_type=DamageType.Poison)

        stats = stats.copy(creature_class="Druid")

        temp_hp = easy_multiple_of_five(stats.cr, min_val=5, max_val=20)
        stats = stats.add_attack(
            scalar=2.0,
            damage_type=DamageType.Piercing,
            die=Die.d6,
            name="Bestial Fury",
            attack_type=AttackType.MeleeNatural,
            replaces_multiattack=2,
            additional_description=f"On a hit, {stats.roleref} gains {temp_hp} temporary hp and the target is \
                pushed back 10 feet if it is Large or smaller",
        )

        return stats


ArcaneArchers: List[Power] = _ArcaneArchers()
Artificer: Power = _Artificer()
Barbarian: Power = _Barbarian()
Bard: Power = _Bard()
BlessedWarrior: Power = _Cleric()
Cavalier: Power = _Cavalier()
DeathKnight: Power = _DeathKnight()
Druid: Power = _Druid()
EldritchKnights: List[Power] = _EldritchKnights()
Monk: Power = _Monk()
Paladin: Power = _Paladin()
PsiWarrior: Power = _PsiWarrior()
Ranger: Power = _Ranger()
RuneKnights: List[Power] = _RuneKnights()
Samurai: Power = _Samurai()
WarPriest: Power = _WarPriest()


ClassPowers: List[Power] = (
    [
        Artificer,
        Barbarian,
        Bard,
        BlessedWarrior,
        Cavalier,
        DeathKnight,
        Druid,
        Monk,
        Paladin,
        PsiWarrior,
        Samurai,
        Ranger,
        WarPriest,
    ]
    + ArcaneArchers
    + EldritchKnights
    + RuneKnights
)
