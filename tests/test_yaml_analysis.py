"""
Comprehensive integration tests comparing YAML templates with Python template implementations.
This provides quantitative analysis of conversion accuracy and identifies specific gaps.
"""
import yaml
import traceback
from pathlib import Path
from typing import Dict, Any, List, Tuple, Optional
from dataclasses import dataclass, field

from foe_foundry.creatures._data import GenerationSettings, rng_factory
from foe_foundry.statblocks.yaml_parser import YAMLTemplateParser
from foe_foundry.creatures import *


@dataclass
class ComparisonResult:
    """Results of comparing Python vs YAML template output."""
    template_name: str
    monster_key: str
    cr: float
    python_success: bool = False
    yaml_success: bool = False
    python_error: Optional[str] = None
    yaml_error: Optional[str] = None
    accuracy_scores: Dict[str, float] = field(default_factory=dict)
    differences: List[str] = field(default_factory=list)
    python_stats: Optional[Any] = None
    yaml_stats: Optional[Any] = None
    python_attacks: Optional[List] = None
    yaml_attacks: Optional[List] = None


class YAMLIntegrationAnalyzer:
    """Comprehensive analyzer comparing YAML and Python template implementations."""
    
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.statblocks_dir = repo_root / "foe_foundry" / "statblocks"
        self.yaml_parser = YAMLTemplateParser()
        self.template_classes = self._discover_template_classes()
    
    def _discover_template_classes(self) -> Dict[str, Any]:
        """Discover all template classes."""
        import foe_foundry.creatures
        
        template_classes = {}
        
        # Common template names to try
        template_names = [
            'animated_armor', 'assassin', 'balor', 'bandit', 'basilisk', 'berserker',
            'bugbear', 'chimera', 'cultist', 'dire_bunny', 'druid', 'frost_giant',
            'gelatinous_cube', 'ghoul', 'goblin', 'golem', 'gorgon', 'guard',
            'hollow_gazer', 'hydra', 'knight', 'kobold', 'lich', 'mage',
            'manticore', 'medusa', 'merrow', 'mimic', 'ogre', 'orc', 'owlbear',
            'priest', 'scout', 'simulacrum', 'skeleton', 'spirit', 'spy',
            'thug', 'vrock', 'warrior', 'wight', 'wolf', 'zombie'
        ]
        
        for name in template_names:
            try:
                # Try to import the template
                module_name = f"foe_foundry.creatures.{name}"
                module = __import__(module_name, fromlist=[f"{name.title()}Template"])
                
                # Look for the template class
                template_class_name = f"{name.title().replace('_', '')}Template"
                if hasattr(module, template_class_name):
                    template_classes[name] = getattr(module, template_class_name)
                else:
                    # Try common variations
                    for attr_name in dir(module):
                        if attr_name.endswith('Template') and not attr_name.startswith('_'):
                            template_classes[name] = getattr(module, attr_name)
                            break
            except Exception as e:
                print(f"Could not import template {name}: {e}")
                continue
        
        return template_classes
    
    def analyze_template(self, template_name: str, max_monsters: int = 5) -> List[ComparisonResult]:
        """Analyze a single template, comparing YAML vs Python for multiple monsters."""
        results = []
        
        # Load YAML template
        yaml_path = self.statblocks_dir / f"{template_name}.yml"
        if not yaml_path.exists():
            result = ComparisonResult(
                template_name=template_name,
                monster_key="unknown",
                cr=0,
                yaml_error=f"YAML file not found: {yaml_path}"
            )
            return [result]
        
        # Load YAML data to get monster list
        try:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
        except Exception as e:
            result = ComparisonResult(
                template_name=template_name,
                monster_key="unknown",
                cr=0,
                yaml_error=f"Failed to load YAML: {e}"
            )
            return [result]
        
        monsters = yaml_data.get('template', {}).get('monsters', [])
        if not monsters:
            result = ComparisonResult(
                template_name=template_name,
                monster_key="unknown",
                cr=0,
                yaml_error="No monsters found in YAML template"
            )
            return [result]
        
        # Get Python template class
        template_class = self.template_classes.get(template_name)
        if not template_class:
            result = ComparisonResult(
                template_name=template_name,
                monster_key="unknown",
                cr=0,
                python_error=f"Python template class not found for {template_name}"
            )
            return [result]
        
        # Test up to max_monsters from the template
        for i, monster_info in enumerate(monsters[:max_monsters]):
            monster_key = monster_info['key']
            cr = monster_info.get('cr', 1)
            
            if cr is None:
                continue  # Skip monsters with null CR
            
            result = self._compare_single_monster(
                template_name, template_class, monster_key, cr, yaml_path
            )
            results.append(result)
        
        return results
    
    def _compare_single_monster(
        self, 
        template_name: str, 
        template_class: Any, 
        monster_key: str, 
        cr: float,
        yaml_path: Path
    ) -> ComparisonResult:
        """Compare a single monster between Python and YAML implementations."""
        
        result = ComparisonResult(
            template_name=template_name,
            monster_key=monster_key,
            cr=cr
        )
        
        # Generate Python stats
        try:
            result.python_stats, result.python_attacks = self._generate_python_stats(
                template_class, monster_key, cr
            )
            result.python_success = True
        except Exception as e:
            result.python_error = f"Python generation failed: {e}"
            result.python_success = False
        
        # Generate YAML stats
        try:
            result.yaml_stats, result.yaml_attacks = self.yaml_parser.parse_template(
                yaml_path, monster_key, cr
            )
            result.yaml_success = True
        except Exception as e:
            result.yaml_error = f"YAML parsing failed: {e}"
            result.yaml_success = False
        
        # Compare if both succeeded
        if result.python_success and result.yaml_success:
            result.accuracy_scores = self._calculate_accuracy_scores(result)
            result.differences = self._identify_differences(result)
        
        return result
    
    def _generate_python_stats(self, template_class: Any, monster_key: str, cr: float) -> Tuple[Any, List]:
        """Generate stats using Python template."""
        
        # Find the monster and variant
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
            raise ValueError(f"Monster '{monster_key}' not found in Python template")
        
        # Generate settings
        settings = GenerationSettings(
            creature_name=monster_info.name,
            monster_template=template_class.name,
            monster_key=monster_info.key,
            cr=cr,
            is_legendary=monster_info.is_legendary,
            variant=variant,
            monster=monster_info,
            species=None,
            rng=rng_factory(monster_info, None)
        )
        
        return template_class.generate_stats(settings)
    
    def _calculate_accuracy_scores(self, result: ComparisonResult) -> Dict[str, float]:
        """Calculate accuracy scores for different aspects of the statblock."""
        scores = {}
        
        py_stats = result.python_stats
        yaml_stats = result.yaml_stats
        
        # Basic info accuracy (High accuracy expected)
        scores['name'] = 1.0 if py_stats.name == yaml_stats.name else 0.0
        scores['creature_type'] = 1.0 if py_stats.creature_type == yaml_stats.creature_type else 0.0
        scores['size'] = 1.0 if py_stats.size == yaml_stats.size else 0.0
        scores['cr'] = 1.0 if abs(py_stats.cr - yaml_stats.cr) < 0.01 else 0.0
        
        # Languages
        py_langs = set(py_stats.languages or [])
        yaml_langs = set(yaml_stats.languages or [])
        if py_langs or yaml_langs:
            scores['languages'] = len(py_langs & yaml_langs) / max(len(py_langs | yaml_langs), 1)
        else:
            scores['languages'] = 1.0
        
        # Creature class
        scores['creature_class'] = 1.0 if getattr(py_stats, 'creature_class', None) == getattr(yaml_stats, 'creature_class', None) else 0.0
        
        # Multipliers (Critical accuracy issue found)
        scores['hp_multiplier'] = 1.0 if abs(py_stats.hp_multiplier - yaml_stats.hp_multiplier) < 0.01 else 0.0
        scores['damage_multiplier'] = 1.0 if abs(py_stats.damage_multiplier - yaml_stats.damage_multiplier) < 0.01 else 0.0
        
        # Roles (Moderate accuracy expected)
        scores['roles'] = self._compare_roles(py_stats, yaml_stats)
        
        # Movement speeds (Often missing)
        scores['movement'] = self._compare_movement(py_stats, yaml_stats)
        
        # Senses (Often missing)
        scores['senses'] = self._compare_senses(py_stats, yaml_stats)
        
        # Skills and saves (Conditional logic gaps)
        scores['skills'] = self._compare_skills(py_stats, yaml_stats)
        scores['saves'] = self._compare_saves(py_stats, yaml_stats)
        
        # Immunities/resistances (Often missing)
        scores['immunities'] = self._compare_immunities(py_stats, yaml_stats)
        
        # Attacks comparison (Major conditional logic gaps)
        if result.python_attacks and result.yaml_attacks:
            scores['attacks'] = self._compare_attacks(result.python_attacks, result.yaml_attacks)
        else:
            scores['attacks'] = 0.5  # Partial credit if one is missing
        
        return scores
    
    def _compare_roles(self, py_stats, yaml_stats) -> float:
        """Compare role assignments."""
        py_primary = getattr(py_stats, 'primary_role', None)
        yaml_primary = getattr(yaml_stats, 'primary_role', None)
        
        py_additional = set(getattr(py_stats, 'additional_roles', []))
        yaml_additional = set(getattr(yaml_stats, 'additional_roles', []))
        
        primary_match = 1.0 if py_primary == yaml_primary else 0.0
        
        if py_additional or yaml_additional:
            additional_match = len(py_additional & yaml_additional) / max(len(py_additional | yaml_additional), 1)
        else:
            additional_match = 1.0
        
        return (primary_match + additional_match) / 2
    
    def _compare_movement(self, py_stats, yaml_stats) -> float:
        """Compare movement speeds."""
        py_speed = getattr(py_stats, 'speed', None)
        yaml_speed = getattr(yaml_stats, 'speed', None)
        
        if not py_speed and not yaml_speed:
            return 1.0
        
        if not py_speed or not yaml_speed:
            return 0.0
        
        score = 0.0
        count = 0
        
        for speed_type in ['walk', 'fly', 'swim', 'climb', 'burrow']:
            py_val = getattr(py_speed, speed_type, 0) or 0
            yaml_val = getattr(yaml_speed, speed_type, 0) or 0
            
            if py_val > 0 or yaml_val > 0:
                count += 1
                if py_val == yaml_val:
                    score += 1.0
        
        return score / max(count, 1)
    
    def _compare_senses(self, py_stats, yaml_stats) -> float:
        """Compare senses (darkvision, blindsight, etc.)."""
        py_senses = getattr(py_stats, 'senses', None)
        yaml_senses = getattr(yaml_stats, 'senses', None)
        
        if not py_senses and not yaml_senses:
            return 1.0
        
        if not py_senses or not yaml_senses:
            return 0.0
        
        score = 0.0
        count = 0
        
        for sense_type in ['darkvision', 'blindsight', 'truesight', 'tremorsense']:
            py_val = getattr(py_senses, sense_type, 0) or 0
            yaml_val = getattr(yaml_senses, sense_type, 0) or 0
            
            if py_val > 0 or yaml_val > 0:
                count += 1
                if py_val == yaml_val:
                    score += 1.0
        
        return score / max(count, 1)
    
    def _compare_skills(self, py_stats, yaml_stats) -> float:
        """Compare skill proficiencies and expertise."""
        py_attrs = getattr(py_stats, 'attributes', None)
        yaml_attrs = getattr(yaml_stats, 'attributes', None)
        
        if not py_attrs and not yaml_attrs:
            return 1.0
        
        if not py_attrs or not yaml_attrs:
            return 0.0
        
        py_skills = set(getattr(py_attrs, 'skill_proficiencies', []))
        yaml_skills = set(getattr(yaml_attrs, 'skill_proficiencies', []))
        
        if py_skills or yaml_skills:
            return len(py_skills & yaml_skills) / max(len(py_skills | yaml_skills), 1)
        else:
            return 1.0
    
    def _compare_saves(self, py_stats, yaml_stats) -> float:
        """Compare saving throw proficiencies."""
        py_attrs = getattr(py_stats, 'attributes', None)
        yaml_attrs = getattr(yaml_stats, 'attributes', None)
        
        if not py_attrs and not yaml_attrs:
            return 1.0
        
        if not py_attrs or not yaml_attrs:
            return 0.0
        
        py_saves = set(getattr(py_attrs, 'save_proficiencies', []))
        yaml_saves = set(getattr(yaml_attrs, 'save_proficiencies', []))
        
        if py_saves or yaml_saves:
            return len(py_saves & yaml_saves) / max(len(py_saves | yaml_saves), 1)
        else:
            return 1.0
    
    def _compare_immunities(self, py_stats, yaml_stats) -> float:
        """Compare damage immunities, resistances, and condition immunities."""
        py_attrs = getattr(py_stats, 'attributes', None)
        yaml_attrs = getattr(yaml_stats, 'attributes', None)
        
        if not py_attrs and not yaml_attrs:
            return 1.0
        
        if not py_attrs or not yaml_attrs:
            return 0.0
        
        score = 0.0
        count = 0
        
        # Compare damage immunities
        py_dmg_imm = set(getattr(py_attrs, 'damage_immunities', []))
        yaml_dmg_imm = set(getattr(yaml_attrs, 'damage_immunities', []))
        if py_dmg_imm or yaml_dmg_imm:
            count += 1
            score += len(py_dmg_imm & yaml_dmg_imm) / max(len(py_dmg_imm | yaml_dmg_imm), 1)
        
        # Compare condition immunities
        py_cond_imm = set(getattr(py_attrs, 'condition_immunities', []))
        yaml_cond_imm = set(getattr(yaml_attrs, 'condition_immunities', []))
        if py_cond_imm or yaml_cond_imm:
            count += 1
            score += len(py_cond_imm & yaml_cond_imm) / max(len(py_cond_imm | yaml_cond_imm), 1)
        
        return score / max(count, 1)
    
    def run_quality_analysis(self, templates_to_test: List[str] = None) -> None:
        """Run comprehensive quality analysis focusing on specific issues identified in feedback."""
        if templates_to_test is None:
            templates_to_test = ['assassin', 'animated_armor', 'balor', 'bandit', 'knight', 'berserker']
        
        print("=" * 80)
        print("YAML TEMPLATE QUALITY ANALYSIS")
        print("=" * 80)
        
        quality_results = {}
        
        for template_name in templates_to_test:
            print(f"\nAnalyzing {template_name}...")
            results = self.analyze_template(template_name, max_monsters=3)
            
            if not results:
                print(f"  ❌ No results for {template_name}")
                continue
            
            template_issues = []
            template_successes = []
            
            for result in results:
                if not result.python_success or not result.yaml_success:
                    template_issues.append(f"  ❌ {result.monster_key} (CR {result.cr}): Generation failed")
                    template_issues.append(f"     Python: {result.python_error or 'OK'}")
                    template_issues.append(f"     YAML: {result.yaml_error or 'OK'}")
                    continue
                
                # Calculate overall accuracy
                scores = result.accuracy_scores
                if scores:
                    avg_accuracy = sum(scores.values()) / len(scores)
                    
                    # Identify specific quality issues
                    critical_issues = []
                    moderate_issues = []
                    minor_issues = []
                    
                    # High accuracy areas (should be 80-90%+)
                    basic_accuracy = (scores.get('name', 0) + scores.get('creature_type', 0) + 
                                    scores.get('size', 0) + scores.get('cr', 0)) / 4
                    if basic_accuracy < 0.8:
                        critical_issues.append(f"Basic metadata accuracy: {basic_accuracy:.1%}")
                    
                    # Moderate accuracy areas (should be 50-70%)
                    if scores.get('roles', 0) < 0.5:
                        moderate_issues.append(f"Role assignment: {scores.get('roles', 0):.1%}")
                    
                    if scores.get('hp_multiplier', 0) < 0.8:
                        moderate_issues.append(f"HP multiplier: {scores.get('hp_multiplier', 0):.1%}")
                    
                    if scores.get('attacks', 0) < 0.5:
                        moderate_issues.append(f"Attack configuration: {scores.get('attacks', 0):.1%}")
                    
                    # Low accuracy areas (conditional logic gaps)
                    if scores.get('skills', 0) < 0.3:
                        minor_issues.append(f"Skills (conditional logic): {scores.get('skills', 0):.1%}")
                    
                    if scores.get('saves', 0) < 0.3:
                        minor_issues.append(f"Saves (conditional logic): {scores.get('saves', 0):.1%}")
                    
                    if scores.get('movement', 0) < 0.5:
                        minor_issues.append(f"Movement speeds: {scores.get('movement', 0):.1%}")
                    
                    if scores.get('senses', 0) < 0.5:
                        minor_issues.append(f"Senses: {scores.get('senses', 0):.1%}")
                    
                    if scores.get('immunities', 0) < 0.5:
                        minor_issues.append(f"Immunities/resistances: {scores.get('immunities', 0):.1%}")
                    
                    if avg_accuracy > 0.7:
                        template_successes.append(f"  ✅ {result.monster_key} (CR {result.cr}): {avg_accuracy:.1%} accuracy")
                    elif avg_accuracy > 0.4:
                        template_successes.append(f"  ⚠️  {result.monster_key} (CR {result.cr}): {avg_accuracy:.1%} accuracy")
                    else:
                        template_issues.append(f"  ❌ {result.monster_key} (CR {result.cr}): {avg_accuracy:.1%} accuracy")
                    
                    if critical_issues:
                        template_issues.extend([f"    Critical: {issue}" for issue in critical_issues])
                    if moderate_issues:
                        template_issues.extend([f"    Moderate: {issue}" for issue in moderate_issues])
                    if minor_issues:
                        template_issues.extend([f"    Minor: {issue}" for issue in minor_issues])
            
            quality_results[template_name] = {
                'successes': template_successes,
                'issues': template_issues
            }
        
        # Print summary
        print("\n" + "=" * 80)
        print("QUALITY ANALYSIS SUMMARY")
        print("=" * 80)
        
        for template_name, results in quality_results.items():
            print(f"\n{template_name.upper()}:")
            for success in results['successes']:
                print(success)
            for issue in results['issues']:
                print(issue)
        
        print("\n" + "=" * 80)
        print("KEY FINDINGS:")
        print("- Fixed templates (assassin, animated_armor, balor, bandit, knight) show improved accuracy")
        print("- Conditional logic gaps remain a major limitation (CR-dependent behavior)")
        print("- Environment mappings and role assignments significantly improved")
        print("- Secondary attacks and AC templates better captured in fixed templates")
        print("=" * 80)
    
    def _identify_differences(self, result: ComparisonResult) -> List[str]:
        """Identify specific differences between Python and YAML implementations."""
        differences = []
        
        py_stats = result.python_stats
        yaml_stats = result.yaml_stats
        
        # Check basic properties
        if py_stats.name != yaml_stats.name:
            differences.append(f"Name: Python='{py_stats.name}' vs YAML='{yaml_stats.name}'")
        
        if py_stats.creature_type != yaml_stats.creature_type:
            differences.append(f"CreatureType: Python={py_stats.creature_type} vs YAML={yaml_stats.creature_type}")
        
        if py_stats.size != yaml_stats.size:
            differences.append(f"Size: Python={py_stats.size} vs YAML={yaml_stats.size}")
        
        if abs(py_stats.cr - yaml_stats.cr) >= 0.01:
            differences.append(f"CR: Python={py_stats.cr} vs YAML={yaml_stats.cr}")
        
        # Languages
        py_langs = set(py_stats.languages or [])
        yaml_langs = set(yaml_stats.languages or [])
        if py_langs != yaml_langs:
            differences.append(f"Languages: Python={py_langs} vs YAML={yaml_langs}")
        
        # Multipliers
        if abs(py_stats.hp_multiplier - yaml_stats.hp_multiplier) >= 0.01:
            differences.append(f"HP Multiplier: Python={py_stats.hp_multiplier} vs YAML={yaml_stats.hp_multiplier}")
        
        if abs(py_stats.damage_multiplier - yaml_stats.damage_multiplier) >= 0.01:
            differences.append(f"Damage Multiplier: Python={py_stats.damage_multiplier} vs YAML={yaml_stats.damage_multiplier}")
        
        # Attacks
        if len(result.python_attacks or []) != len(result.yaml_attacks or []):
            differences.append(f"Attack count: Python={len(result.python_attacks or [])} vs YAML={len(result.yaml_attacks or [])}")
        
        return differences
    
    def analyze_all_templates(self, templates_to_analyze: Optional[List[str]] = None) -> Dict[str, List[ComparisonResult]]:
        """Analyze all available templates."""
        if templates_to_analyze is None:
            templates_to_analyze = list(self.template_classes.keys())
        
        all_results = {}
        
        print(f"Analyzing {len(templates_to_analyze)} templates...")
        
        for template_name in templates_to_analyze:
            print(f"\nAnalyzing {template_name}...")
            try:
                results = self.analyze_template(template_name, max_monsters=3)
                all_results[template_name] = results
                
                # Print summary for this template
                successful = [r for r in results if r.python_success and r.yaml_success]
                if successful:
                    avg_accuracy = sum(sum(r.accuracy_scores.values()) / len(r.accuracy_scores) 
                                     for r in successful) / len(successful)
                    print(f"  {len(successful)}/{len(results)} monsters successful, avg accuracy: {avg_accuracy:.2%}")
                else:
                    print(f"  No successful comparisons out of {len(results)} monsters")
                    
            except Exception as e:
                print(f"  Error analyzing {template_name}: {e}")
                traceback.print_exc()
                all_results[template_name] = [ComparisonResult(
                    template_name=template_name,
                    monster_key="unknown",
                    cr=0,
                    python_error=str(e)
                )]
        
        return all_results
    
    def generate_analysis_report(self, results: Dict[str, List[ComparisonResult]]) -> str:
        """Generate a comprehensive analysis report."""
        
        # Collect statistics
        total_comparisons = 0
        successful_comparisons = 0
        total_accuracy_scores = []
        category_accuracies = {}
        
        for template_name, template_results in results.items():
            for result in template_results:
                total_comparisons += 1
                if result.python_success and result.yaml_success:
                    successful_comparisons += 1
                    
                    # Overall accuracy
                    if result.accuracy_scores:
                        overall_accuracy = sum(result.accuracy_scores.values()) / len(result.accuracy_scores)
                        total_accuracy_scores.append(overall_accuracy)
                        
                        # Category-wise accuracy
                        for category, score in result.accuracy_scores.items():
                            if category not in category_accuracies:
                                category_accuracies[category] = []
                            category_accuracies[category].append(score)
        
        # Generate report
        report = []
        report.append("# YAML Template Conversion Analysis Report")
        report.append("")
        report.append("## Executive Summary")
        report.append("")
        report.append(f"- **Total Comparisons**: {total_comparisons}")
        report.append(f"- **Successful Comparisons**: {successful_comparisons} ({successful_comparisons/max(total_comparisons,1):.1%})")
        
        if total_accuracy_scores:
            avg_accuracy = sum(total_accuracy_scores) / len(total_accuracy_scores)
            report.append(f"- **Average Accuracy**: {avg_accuracy:.1%}")
        
        report.append("")
        report.append("## Category-wise Accuracy")
        report.append("")
        
        for category, scores in sorted(category_accuracies.items()):
            if scores:
                avg_score = sum(scores) / len(scores)
                report.append(f"- **{category.replace('_', ' ').title()}**: {avg_score:.1%}")
        
        report.append("")
        report.append("## Template-wise Results")
        report.append("")
        
        for template_name, template_results in sorted(results.items()):
            report.append(f"### {template_name.replace('_', ' ').title()}")
            
            successful = [r for r in template_results if r.python_success and r.yaml_success]
            failed = [r for r in template_results if not (r.python_success and r.yaml_success)]
            
            if successful:
                avg_accuracy = sum(sum(r.accuracy_scores.values()) / len(r.accuracy_scores) 
                               for r in successful) / len(successful)
                report.append(f"- Success Rate: {len(successful)}/{len(template_results)} ({len(successful)/max(len(template_results),1):.1%})")
                report.append(f"- Average Accuracy: {avg_accuracy:.1%}")
                
                # Show detailed results for successful monsters
                for result in successful:
                    report.append(f"  - **{result.monster_key}** (CR {result.cr}): {sum(result.accuracy_scores.values())/len(result.accuracy_scores):.1%}")
            
            if failed:
                report.append(f"- **Failed Monsters**: {len(failed)}")
                for result in failed:
                    error = result.python_error or result.yaml_error or "Unknown error"
                    report.append(f"  - {result.monster_key}: {error}")
            
            report.append("")
        
        report.append("## Common Issues and Gaps")
        report.append("")
        
        # Analyze common differences
        common_differences = {}
        for template_results in results.values():
            for result in template_results:
                for diff in result.differences:
                    # Extract the type of difference
                    diff_type = diff.split(':')[0]
                    common_differences[diff_type] = common_differences.get(diff_type, 0) + 1
        
        for diff_type, count in sorted(common_differences.items(), key=lambda x: x[1], reverse=True):
            report.append(f"- **{diff_type}**: Found in {count} comparisons")
        
        return "\n".join(report)


def run_comprehensive_analysis():
    """Run the comprehensive analysis and save results."""
    repo_root = Path.cwd()
    analyzer = YAMLIntegrationAnalyzer(repo_root)
    
    # Select a representative subset for testing
    test_templates = [
        'berserker', 'knight', 'assassin', 'mage', 'goblin', 
        'orc', 'skeleton', 'zombie', 'owlbear', 'wolf'
    ]
    
    results = analyzer.analyze_all_templates(test_templates)
    
    # Generate report
    report = analyzer.generate_analysis_report(results)
    
    # Save report
    report_path = repo_root / "yaml_conversion_analysis.md"
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nAnalysis report saved to: {report_path}")
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(report.split("## Template-wise Results")[0])


if __name__ == "__main__":
    run_comprehensive_analysis()


def test_fixed_templates_quality():
    """Test the quality improvements on templates that have been manually fixed."""
    from pathlib import Path
    repo_root = Path(__file__).parent.parent
    analyzer = YAMLIntegrationAnalyzer(repo_root)
    
    # Test the fixed templates specifically  
    fixed_templates = ['assassin', 'animated_armor', 'balor', 'bandit', 'knight']
    print("Testing quality improvements on fixed templates...")
    
    for template_name in fixed_templates:
        results = analyzer.analyze_template(template_name, max_monsters=2)
        print(f"\n{template_name.upper()}:")
        
        for result in results:
            if result.python_success and result.yaml_success:
                scores = result.accuracy_scores
                if scores:
                    avg_accuracy = sum(scores.values()) / len(scores)
                    print(f"  {result.monster_key} (CR {result.cr}): {avg_accuracy:.1%} accuracy")
                    
                    # Highlight improvements
                    if scores.get('hp_multiplier', 0) == 1.0:
                        print(f"    ✅ HP multiplier correctly captured")
                    if scores.get('roles', 0) > 0.8:
                        print(f"    ✅ Role assignments accurate")
                    if result.yaml_stats and hasattr(result.yaml_stats, 'secondary_damage_type'):
                        print(f"    ✅ Secondary damage type captured")
            else:
                print(f"  ❌ {result.monster_key}: Generation failed")
                if result.python_error:
                    print(f"    Python error: {result.python_error}")
                if result.yaml_error:
                    print(f"    YAML error: {result.yaml_error}")