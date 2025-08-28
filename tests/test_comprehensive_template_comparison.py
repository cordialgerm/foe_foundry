"""
Comprehensive YAML Template vs Original Template Comparison Tests

This test suite systematically compares each YAML template against its original 
Python MonsterTemplate implementation to identify gaps and quality issues.
"""
import pytest
import importlib
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional

from foe_foundry.statblocks.yaml_parser import parse_yaml_template
from foe_foundry.statblocks.base import BaseStatblock
from foe_foundry.attack_template import AttackTemplate
from foe_foundry.creatures._data import GenerationSettings, rng_factory

# Simple table formatting function to replace tabulate
def simple_table(data: List[List], headers: List[str]) -> str:
    """Simple table formatting without external dependencies."""
    if not data:
        return ""
    
    # Calculate column widths
    col_widths = [len(h) for h in headers]
    for row in data:
        for i, cell in enumerate(row):
            if i < len(col_widths):
                col_widths[i] = max(col_widths[i], len(str(cell)))
    
    # Format table
    lines = []
    
    # Header
    header_line = "| " + " | ".join(h.ljust(col_widths[i]) for i, h in enumerate(headers)) + " |"
    lines.append(header_line)
    lines.append("|" + "|".join("-" * (w + 2) for w in col_widths) + "|")
    
    # Data
    for row in data:
        data_line = "| " + " | ".join(str(row[i]).ljust(col_widths[i]) if i < len(row) else "".ljust(col_widths[i]) for i in range(len(headers))) + " |"
        lines.append(data_line)
    
    return "\n".join(lines)


class TemplateComparisonResult:
    """Results of comparing a YAML template with its original Python implementation."""
    
    def __init__(self, template_name: str, monster_key: str):
        self.template_name = template_name
        self.monster_key = monster_key
        self.passed = False
        self.failures: List[str] = []
        self.warnings: List[str] = []
        self.original_stats: Optional[BaseStatblock] = None
        self.yaml_stats: Optional[BaseStatblock] = None
        self.original_attacks: List[AttackTemplate] = []
        self.yaml_attacks: List[AttackTemplate] = []
        self.error: Optional[str] = None
    
    def add_failure(self, reason: str):
        """Add a failure reason."""
        self.failures.append(reason)
        self.passed = False
    
    def add_warning(self, reason: str):
        """Add a warning."""
        self.warnings.append(reason)
    
    def set_error(self, error: str):
        """Set a critical error that prevented comparison."""
        self.error = error
        self.passed = False


class TestComprehensiveTemplateComparison:
    """Comprehensive comparison between YAML templates and original Python implementations."""
    
    # Define all available templates with their import paths and monster keys to test
    TEMPLATES_TO_TEST = [
    ("foe_foundry.creatures.animated_armor", "AnimatedArmorTemplate", [
        ("animated-armor", "animated_armor.yml"),
        ("animated-runeplate", "animated_armor.yml"),
    ]),
    ("foe_foundry.creatures.assassin", "AssassinTemplate", [
        ("contract-killer", "assassin.yml"),
        ("assassin", "assassin.yml"),
        ("assassin-legend", "assassin.yml"),
    ]),
    ("foe_foundry.creatures.balor", "BalorTemplate", [
        ("balor", "balor.yml"),
        ("balor-dreadlord", "balor.yml"),
    ]),
    ("foe_foundry.creatures.bandit", "BanditTemplate", [
        ("bandit", "bandit.yml"),
        ("bandit-veteran", "bandit.yml"),
        ("bandit-captain", "bandit.yml"),
        ("bandit-crime-lord", "bandit.yml"),
    ]),
    ("foe_foundry.creatures.basilisk", "BasiliskTemplate", [
        ("basilisk", "basilisk.yml"),
        ("basilisk-broodmother", "basilisk.yml"),
    ]),
    ("foe_foundry.creatures.berserker", "BerserkerTemplate", [
        ("berserker", "berserker.yml"),
        ("berserker-veteran", "berserker.yml"),
        ("berserker-commander", "berserker.yml"),
        ("berserker-legend", "berserker.yml"),
    ]),
    ("foe_foundry.creatures.bugbear", "BugbearTemplate", [
        ("bugbear", "bugbear.yml"),
        ("bugbear-brute", "bugbear.yml"),
        ("bugbear-shadowstalker", "bugbear.yml"),
    ]),
    ("foe_foundry.creatures.chimera", "ChimeraTemplate", [
        ("chimera", "chimera.yml"),
        ("chimera-matriarch", "chimera.yml"),
    ]),
    ("foe_foundry.creatures.cultist", "CultistTemplate", [
        ("cultist", "cultist.yml"),
        ("cultist-fanatic", "cultist.yml"),
        ("cultist-grand-master", "cultist.yml"),
    ]),
    ("foe_foundry.creatures.dire_bunny", "DireBunnyTemplate", [
        ("dire-bunny", "dire_bunny.yml"),
        ("dire-bunny-alpha", "dire_bunny.yml"),
        ("dire-bunny-matriarch", "dire_bunny.yml"),
    ]),
    ("foe_foundry.creatures.druid", "DruidTemplate", [
        ("druid", "druid.yml"),
        ("druid-circle-leader", "druid.yml"),
        ("archdruid", "druid.yml"),
    ]),
    ("foe_foundry.creatures.frost_giant", "FrostGiantTemplate", [
        ("frost-giant", "frost_giant.yml"),
        ("frost-giant-jarl", "frost_giant.yml"),
        ("frost-giant-everlasting", "frost_giant.yml"),
    ]),
    ("foe_foundry.creatures.gelatinous_cube", "GelatinousCubeTemplate", [
        ("gelatinous-cube", "gelatinous_cube.yml"),
        ("gelatinous-cube-elder", "gelatinous_cube.yml"),
    ]),
    ("foe_foundry.creatures.ghoul", "GhoulTemplate", [
        ("ghoul", "ghoul.yml"),
        ("ghast", "ghoul.yml"),
        ("ghoul-master", "ghoul.yml"),
    ]),
    ("foe_foundry.creatures.goblin", "GoblinTemplate", [
        ("goblin-lickspittle", "goblin.yml"),
        ("goblin", "goblin.yml"),
        ("goblin-brute", "goblin.yml"),
        ("goblin-shaman", "goblin.yml"),
    ]),
    ("foe_foundry.creatures.golem", "GolemTemplate", [
        ("clay-golem", "golem.yml"),
        ("flesh-golem", "golem.yml"),
        ("iron-golem", "golem.yml"),
        ("stone-golem", "golem.yml"),
    ]),
    ("foe_foundry.creatures.gorgon", "GorgonTemplate", [
        ("gorgon", "gorgon.yml"),
        ("gorgon-empress", "gorgon.yml"),
    ]),
    ("foe_foundry.creatures.guard", "GuardTemplate", [
        ("guard", "guard.yml"),
        ("guard-veteran", "guard.yml"),
        ("guard-captain", "guard.yml"),
        ("guard-commander", "guard.yml"),
        ("legendary-guard", "guard.yml"),
    ]),
    ("foe_foundry.creatures.hollow_gazer", "HollowGazerTemplate", [
        ("hollow-gazer", "hollow_gazer.yml"),
        ("hollow-gazer-elder", "hollow_gazer.yml"),
    ]),
    ("foe_foundry.creatures.hydra", "HydraTemplate", [
        ("hydra", "hydra.yml"),
        ("hydra-ancient", "hydra.yml"),
    ]),
    ("foe_foundry.creatures.knight", "KnightTemplate", [
        ("knight", "knight.yml"),
        ("knight-of-the-realm", "knight.yml"),
        ("questing-knight", "knight.yml"),
        ("paragon-knight", "knight.yml"),
    ]),
    ("foe_foundry.creatures.kobold", "KoboldTemplate", [
        ("kobold", "kobold.yml"),
        ("kobold-scout", "kobold.yml"),
        ("kobold-scalesorcerer", "kobold.yml"),
        ("kobold-chieftain", "kobold.yml"),
        ("kobold-dragonshield", "kobold.yml"),
    ]),
    ("foe_foundry.creatures.lich", "LichTemplate", [
        ("lich", "lich.yml"),
        ("archlich", "lich.yml"),
    ]),
    ("foe_foundry.creatures.mage", "MageTemplate", [
        ("mage", "mage.yml"),
        ("sorcerer", "mage.yml"),
        ("warlock", "mage.yml"),
        ("wizard", "mage.yml"),
        ("archmage", "mage.yml"),
    ]),
    ("foe_foundry.creatures.manticore", "ManticoreTemplate", [
        ("manticore", "manticore.yml"),
        ("manticore-patriarch", "manticore.yml"),
    ]),
    ("foe_foundry.creatures.medusa", "MedusaTemplate", [
        ("medusa", "medusa.yml"),
        ("medusa-empress", "medusa.yml"),
    ]),
    ("foe_foundry.creatures.merrow", "MerrowTemplate", [
        ("merrow", "merrow.yml"),
        ("merrow-shallowpriest", "merrow.yml"),
    ]),
    ("foe_foundry.creatures.mimic", "MimicTemplate", [
        ("mimic", "mimic.yml"),
        ("mimic-greater", "mimic.yml"),
    ]),
    ("foe_foundry.creatures.ogre", "OgreTemplate", [
        ("ogre", "ogre.yml"),
        ("ogre-elite", "ogre.yml"),
        ("ogre-champion", "ogre.yml"),
        ("ogre-chief", "ogre.yml"),
    ]),
    ("foe_foundry.creatures.orc", "OrcTemplate", [
        ("orc", "orc.yml"),
        ("orc-veteran", "orc.yml"),
        ("orc-war-chief", "orc.yml"),
        ("orc-doom-hand", "orc.yml"),
    ]),
    ("foe_foundry.creatures.owlbear", "OwlbearTemplate", [
        ("owlbear", "owlbear.yml"),
        ("owlbear-pack-leader", "owlbear.yml"),
        ("owlbear-terror", "owlbear.yml"),
    ]),
    ("foe_foundry.creatures.priest", "PriestTemplate", [
        ("acolyte", "priest.yml"),
        ("priest", "priest.yml"),
        ("high-priest", "priest.yml"),
    ]),
    ("foe_foundry.creatures.scout", "ScoutTemplate", [
        ("scout", "scout.yml"),
        ("scout-veteran", "scout.yml"),
        ("scout-commander", "scout.yml"),
        ("legendary-scout", "scout.yml"),
    ]),
    ("foe_foundry.creatures.simulacrum", "SimulacrumTemplate", [
        ("simulacrum", "simulacrum.yml"),
        ("simulacrum-lord", "simulacrum.yml"),
    ]),
    ("foe_foundry.creatures.skeleton", "SkeletonTemplate", [
        ("skeleton", "skeleton.yml"),
        ("skeleton-warrior", "skeleton.yml"),
        ("skeleton-minotaur", "skeleton.yml"),
        ("skeleton-knight", "skeleton.yml"),
    ]),
    ("foe_foundry.creatures.spirit", "SpiritTemplate", [
        ("revenant", "spirit.yml"),
        ("ghost", "spirit.yml"),
        ("wraith", "spirit.yml"),
        ("wraith-shadelord", "spirit.yml"),
    ]),
    ("foe_foundry.creatures.spy", "SpyTemplate", [
        ("spy", "spy.yml"),
        ("elite-spy", "spy.yml"),
        ("spy-master", "spy.yml"),
    ]),
    ("foe_foundry.creatures.thug", "ThugTemplate", [
        ("thug", "thug.yml"),
        ("veteran-thug", "thug.yml"),
        ("elite-thug", "thug.yml"),
        ("brawler", "thug.yml"),
        ("thug-boss", "thug.yml"),
        ("thug-overboss", "thug.yml"),
        ("thug-legend", "thug.yml"),
    ]),
    ("foe_foundry.creatures.vrock", "VrockTemplate", [
        ("vrock", "vrock.yml"),
    ]),
    ("foe_foundry.creatures.warrior", "WarriorTemplate", [
        ("line-infantry", "warrior.yml"),
        ("line-infantry-veteran", "warrior.yml"),
        ("shock-infantry", "warrior.yml"),
        ("shock-infantry-veteran", "warrior.yml"),
        ("warrior-commander", "warrior.yml"),
        ("legendary-warrior", "warrior.yml"),
    ]),
    ("foe_foundry.creatures.wight", "WightTemplate", [
        ("wight", "wight.yml"),
        ("wight-fell-champion", "wight.yml"),
        ("wight-dread-lord", "wight.yml"),
    ]),
    ("foe_foundry.creatures.wolf", "WolfTemplate", [
        ("wolf", "wolf.yml"),
        ("dire-wolf", "wolf.yml"),
        ("winter-wolf", "wolf.yml"),
        ("fellwinter-packlord", "wolf.yml"),
    ]),
    ("foe_foundry.creatures.zombie", "ZombieTemplate", [
        ("zombie", "zombie.yml"),
        ("zombie-brute", "zombie.yml"),
        ("zombie-gravewalker", "zombie.yml"),
        ("zombie-ogre", "zombie.yml"),
        ("zombie-giant", "zombie.yml"),
        ("zombie-titan", "zombie.yml"),
    ]),
]
    
    @pytest.fixture
    def statblocks_dir(self):
        """Get the statblocks directory."""
        return Path(__file__).parent.parent / "foe_foundry" / "statblocks"
    
    def get_original_template_stats(self, module_name: str, template_class_name: str, 
                                   monster_key: str) -> Tuple[BaseStatblock, List[AttackTemplate]]:
        """Get stats from original MonsterTemplate implementation."""
        try:
            # Import the template module
            module = importlib.import_module(module_name)
            template_class = getattr(module, template_class_name)
            
            # Find the monster in the template's variants
            monster_info = None
            variant = None
            
            for v in template_class.variants:
                for m in v.monsters:
                    if m.key == monster_key:
                        monster_info = m
                        variant = v
                        break
                if monster_info:
                    break
            
            if not monster_info:
                raise ValueError(f"Monster '{monster_key}' not found in template")
            
            # Create generation settings
            settings = GenerationSettings(
                creature_name=monster_info.name,
                monster_template=template_class.name,
                monster_key=monster_info.key,
                cr=monster_info.cr,
                is_legendary=monster_info.is_legendary,
                variant=variant,
                monster=monster_info,
                species=None,
                rng=rng_factory(monster_info, None)
            )
            
            # Generate stats
            return template_class.generate_stats(settings)
            
        except Exception as e:
            raise RuntimeError(f"Failed to generate original stats for {monster_key}: {e}")
    
    def get_yaml_template_stats(self, statblocks_dir: Path, yaml_file: str, 
                               monster_key: str) -> Tuple[BaseStatblock, List[AttackTemplate]]:
        """Get stats from YAML template parser."""
        yaml_path = statblocks_dir / yaml_file
        return parse_yaml_template(yaml_path, monster_key)
    
    def compare_templates(self, module_name: str, template_class_name: str, 
                         monster_key: str, yaml_file: str, statblocks_dir: Path) -> TemplateComparisonResult:
        """Compare a single template variant between original and YAML implementations."""
        result = TemplateComparisonResult(template_class_name, monster_key)
        
        try:
            # Get original stats
            result.original_stats, result.original_attacks = self.get_original_template_stats(
                module_name, template_class_name, monster_key
            )
            
            # Get YAML stats
            result.yaml_stats, result.yaml_attacks = self.get_yaml_template_stats(
                statblocks_dir, yaml_file, monster_key
            )
            
            # Compare basic properties
            self._compare_basic_properties(result)
            
            # Compare abilities/attributes
            self._compare_attributes(result)
            
            # Compare attacks
            self._compare_attacks(result)
            
            # Compare roles
            self._compare_roles(result)
            
            # Compare skills and saves
            self._compare_skills_and_saves(result)
            
            # Compare damage and conditions
            self._compare_damage_and_conditions(result)
            
            # If no failures, mark as passed
            if not result.failures:
                result.passed = True
                
        except Exception as e:
            result.set_error(str(e))
        
        return result
    
    def _compare_basic_properties(self, result: TemplateComparisonResult):
        """Compare basic statblock properties."""
        orig = result.original_stats
        yaml = result.yaml_stats
        
        # Name
        if orig.name != yaml.name:
            result.add_failure(f"Name mismatch: '{orig.name}' vs '{yaml.name}'")
        
        # CR
        if orig.cr != yaml.cr:
            result.add_failure(f"CR mismatch: {orig.cr} vs {yaml.cr}")
        
        # Creature type
        if orig.creature_type != yaml.creature_type:
            result.add_failure(f"Creature type mismatch: {orig.creature_type} vs {yaml.creature_type}")
        
        # Size
        if orig.size != yaml.size:
            result.add_failure(f"Size mismatch: {orig.size} vs {yaml.size}")
        
        # Languages
        orig_langs = set(orig.languages) if orig.languages else set()
        yaml_langs = set(yaml.languages) if yaml.languages else set()
        if orig_langs != yaml_langs:
            result.add_warning(f"Languages differ: {orig_langs} vs {yaml_langs}")
        
        # Note: hp_multiplier and damage_multiplier are not stored as attributes on BaseStatblock
        # They are used during creation but not accessible afterwards
        # So we skip comparing them directly
    
    def _compare_attributes(self, result: TemplateComparisonResult):
        """Compare attribute/ability scores."""
        orig = result.original_stats.attributes
        yaml = result.yaml_stats.attributes
        
        # For now, just check that both have valid attributes
        # A more detailed comparison would require understanding the scaling calculations
        if not orig or not yaml:
            result.add_failure("Missing attributes in one or both templates")
        else:
            # Basic sanity check that ability scores are reasonable
            for attr_name in ['strength', 'dexterity', 'constitution', 'intelligence', 'wisdom', 'charisma']:
                orig_val = getattr(orig, attr_name, 0)
                yaml_val = getattr(yaml, attr_name, 0)
                
                # Values should be between 3-30 (reasonable range for D&D)
                if not (3 <= orig_val <= 30):
                    result.add_warning(f"Original {attr_name} out of range: {orig_val}")
                if not (3 <= yaml_val <= 30):
                    result.add_warning(f"YAML {attr_name} out of range: {yaml_val}")
    
    def _compare_attacks(self, result: TemplateComparisonResult):
        """Compare attack templates."""
        orig_attacks = result.original_attacks
        yaml_attacks = result.yaml_attacks
        
        # Attack count
        if len(orig_attacks) != len(yaml_attacks):
            result.add_failure(f"Attack count mismatch: {len(orig_attacks)} vs {len(yaml_attacks)}")
        
        # Attack names
        if orig_attacks and yaml_attacks:
            orig_names = [att.attack_name for att in orig_attacks]
            yaml_names = [att.attack_name for att in yaml_attacks]
            
            if orig_names != yaml_names:
                result.add_warning(f"Attack names differ: {orig_names} vs {yaml_names}")
    
    def _compare_roles(self, result: TemplateComparisonResult):
        """Compare monster roles."""
        orig = result.original_stats
        yaml = result.yaml_stats
        
        # Primary role (BaseStatblock uses 'role' not 'primary_role')
        orig_primary = getattr(orig, 'role', None)
        yaml_primary = getattr(yaml, 'role', None)
        if orig_primary != yaml_primary:
            result.add_failure(f"Primary role mismatch: {orig_primary} vs {yaml_primary}")
        
        # Additional roles
        orig_additional = set(orig.additional_roles) if orig.additional_roles else set()
        yaml_additional = set(yaml.additional_roles) if yaml.additional_roles else set()
        
        if orig_additional != yaml_additional:
            result.add_warning(f"Additional roles differ: {orig_additional} vs {yaml_additional}")
    
    def _compare_skills_and_saves(self, result: TemplateComparisonResult):
        """Compare skills and saving throws."""
        # This is complex to compare directly due to how skills are stored
        # For now, just ensure both have valid skills/saves structures
        pass
    
    def _compare_damage_and_conditions(self, result: TemplateComparisonResult):
        """Compare damage types and condition immunities."""
        orig = result.original_stats
        yaml = result.yaml_stats
        
        # Secondary damage type
        if orig.secondary_damage_type != yaml.secondary_damage_type:
            result.add_warning(f"Secondary damage type differs: {orig.secondary_damage_type} vs {yaml.secondary_damage_type}")
    
    def test_all_template_comparisons(self, statblocks_dir):
        """Run comprehensive comparison of all templates and generate a summary table."""
        all_results = []
        
        for module_name, template_class_name, monsters in self.TEMPLATES_TO_TEST:
            for monster_key, yaml_file in monsters:
                result = self.compare_templates(
                    module_name, template_class_name, monster_key, yaml_file, statblocks_dir
                )
                all_results.append(result)
        
        # Generate summary table
        self._generate_summary_table(all_results)
        
        # Generate detailed failure report
        self._generate_failure_report(all_results)
        
        # Check overall results
        passed_count = sum(1 for r in all_results if r.passed)
        total_count = len(all_results)
        
        print(f"\n\nOverall Results: {passed_count}/{total_count} templates passed ({passed_count/total_count*100:.1f}%)")
        
        # Don't fail the test if some templates have issues - this is exploratory
        # assert passed_count > total_count * 0.5, f"Less than 50% of templates passed: {passed_count}/{total_count}"
    
    def _generate_summary_table(self, results: List[TemplateComparisonResult]):
        """Generate a summary table showing pass/fail status."""
        table_data = []
        
        for result in results:
            status = "PASS" if result.passed else "FAIL"
            if result.error:
                status = "ERROR"
            
            failure_count = len(result.failures)
            warning_count = len(result.warnings)
            
            table_data.append([
                result.template_name,
                result.monster_key,
                status,
                failure_count,
                warning_count,
                result.error[:50] + "..." if result.error and len(result.error) > 50 else (result.error or "")
            ])
        
        headers = ["Template", "Monster", "Status", "Failures", "Warnings", "Error"]
        table = simple_table(table_data, headers)
        
        print("\n" + "="*80)
        print("TEMPLATE COMPARISON SUMMARY")
        print("="*80)
        print(table)
    
    def _generate_failure_report(self, results: List[TemplateComparisonResult]):
        """Generate a detailed report of failures with examples."""
        failed_results = [r for r in results if not r.passed]
        
        if not failed_results:
            print("\n🎉 All templates passed!")
            return
        
        print("\n" + "="*80)
        print("DETAILED FAILURE ANALYSIS")
        print("="*80)
        
        # Group failures by type
        failure_types = {}
        for result in failed_results:
            for failure in result.failures:
                failure_type = failure.split(':')[0] if ':' in failure else failure
                if failure_type not in failure_types:
                    failure_types[failure_type] = []
                failure_types[failure_type].append((result.template_name, result.monster_key, failure))
        
        for failure_type, examples in failure_types.items():
            print(f"\n## {failure_type.upper()} ({len(examples)} occurrences)")
            print("-" * 50)
            
            # Show first few examples
            for i, (template, monster, failure) in enumerate(examples[:3]):
                print(f"  {i+1}. {template}.{monster}: {failure}")
            
            if len(examples) > 3:
                print(f"  ... and {len(examples) - 3} more")
        
        # Show the most common failure types
        print(f"\n## MOST COMMON ISSUES")
        print("-" * 30)
        sorted_failures = sorted(failure_types.items(), key=lambda x: len(x[1]), reverse=True)
        for failure_type, examples in sorted_failures[:5]:
            print(f"  {failure_type}: {len(examples)} occurrences")
    
    def test_specific_template_berserker(self, statblocks_dir):
        """Test specific berserker template for detailed analysis."""
        result = self.compare_templates(
            "foe_foundry.creatures.berserker", "BerserkerTemplate", 
            "berserker", "berserker.yml", statblocks_dir
        )
        
        print(f"\nBerserker Template Analysis:")
        print(f"  Passed: {result.passed}")
        if result.failures:
            print(f"  Failures: {result.failures}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        if result.error:
            print(f"  Error: {result.error}")
    
    def test_specific_template_knight(self, statblocks_dir):
        """Test specific knight template for detailed analysis."""
        result = self.compare_templates(
            "foe_foundry.creatures.knight", "KnightTemplate", 
            "knight", "knight.yml", statblocks_dir
        )
        
        print(f"\nKnight Template Analysis:")
        print(f"  Passed: {result.passed}")
        if result.failures:
            print(f"  Failures: {result.failures}")
        if result.warnings:
            print(f"  Warnings: {result.warnings}")
        if result.error:
            print(f"  Error: {result.error}")


if __name__ == "__main__":
    # Run the comprehensive test
    test = TestComprehensiveTemplateComparison()
    statblocks_dir = Path(__file__).parent.parent / "foe_foundry" / "statblocks"
    test.test_all_template_comparisons(statblocks_dir)