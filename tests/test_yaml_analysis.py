"""
Simplified integration tests to compare YAML templates with Python templates.
"""
import yaml
from pathlib import Path
from typing import Dict, Any, List, Tuple

from foe_foundry.creatures._data import GenerationSettings, rng_factory


class YAMLPythonComparison:
    """Compare YAML templates with Python template behavior."""
    
    def analyze_template_gaps(self, template_class, yaml_path: Path, monster_key: str) -> Dict[str, Any]:
        """Analyze gaps between Python template and YAML template."""
        
        # Load YAML template
        with open(yaml_path, 'r', encoding='utf-8') as f:
            yaml_data = yaml.safe_load(f)
        
        # Find monster in Python template
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
            return {"error": f"Monster '{monster_key}' not found in Python template"}
        
        # Generate Python stats
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
        
        try:
            python_stats, python_attacks = template_class.generate_stats(settings)
        except Exception as e:
            return {"error": f"Failed to generate Python stats: {e}"}
        
        # Get YAML data for this monster
        yaml_common = yaml_data.get('common', {})
        yaml_variant = yaml_data.get(monster_key, {})
        
        # Analyze differences
        gaps = {}
        
        # Basic properties
        gaps['basic'] = self._compare_basic_properties(python_stats, yaml_common, yaml_variant)
        
        # Attacks
        gaps['attacks'] = self._compare_attacks(python_attacks, yaml_common.get('attacks', {}), yaml_variant.get('attacks', {}))
        
        # Abilities  
        gaps['abilities'] = self._compare_abilities(python_stats, yaml_common, yaml_variant)
        
        # Other complex features
        gaps['complex'] = self._analyze_complex_features(template_class, settings)
        
        return gaps
    
    def _compare_basic_properties(self, python_stats, yaml_common: Dict, yaml_variant: Dict) -> Dict[str, Any]:
        """Compare basic properties like name, CR, type, size."""
        gaps = {}
        
        # Check creature type
        python_type = str(python_stats.creature_type)
        yaml_type = yaml_variant.get('creature_type') or yaml_common.get('creature_type')
        if python_type.lower() != str(yaml_type).lower():
            gaps['creature_type'] = {'python': python_type, 'yaml': yaml_type}
        
        # Check size
        python_size = str(python_stats.size)
        yaml_size = yaml_variant.get('size') or yaml_common.get('size')
        if python_size.lower() != str(yaml_size).lower():
            gaps['size'] = {'python': python_size, 'yaml': yaml_size}
        
        # Check languages
        python_langs = set(python_stats.languages) if python_stats.languages else set()
        yaml_langs = set(yaml_variant.get('languages') or yaml_common.get('languages', []))
        if python_langs != yaml_langs:
            gaps['languages'] = {'python': list(python_langs), 'yaml': list(yaml_langs)}
        
        # Check creature class
        python_class = python_stats.creature_class
        yaml_class = yaml_variant.get('creature_class') or yaml_common.get('creature_class')
        if python_class != yaml_class:
            gaps['creature_class'] = {'python': python_class, 'yaml': yaml_class}
        
        return gaps
    
    def _compare_attacks(self, python_attacks: List, yaml_common_attacks: Dict, yaml_variant_attacks: Dict) -> Dict[str, Any]:
        """Compare attack configurations."""
        gaps = {}
        
        # Attack count
        python_count = len(python_attacks)
        yaml_attacks = yaml_variant_attacks or yaml_common_attacks
        
        # Estimate YAML attack count
        yaml_count = 0
        if yaml_attacks.get('main'):
            yaml_count += 1
        if yaml_attacks.get('secondary'):
            yaml_count += 1
        
        if python_count != yaml_count:
            gaps['attack_count'] = {'python': python_count, 'yaml': yaml_count}
        
        # Attack names
        python_names = [att.attack_name for att in python_attacks]
        yaml_main = yaml_attacks.get('main', {}).get('base', 'TBD')
        yaml_secondary = yaml_attacks.get('secondary', {}).get('base')
        yaml_names = [name for name in [yaml_main, yaml_secondary] if name and name != 'TBD']
        
        if python_names != yaml_names:
            gaps['attack_names'] = {'python': python_names, 'yaml': yaml_names}
        
        return gaps
    
    def _compare_abilities(self, python_stats, yaml_common: Dict, yaml_variant: Dict) -> Dict[str, Any]:
        """Compare ability scores and scaling."""
        gaps = {}
        
        # Get YAML abilities
        yaml_abilities = yaml_variant.get('abilities') or yaml_common.get('abilities', {})
        
        if not yaml_abilities:
            gaps['missing_abilities'] = "No abilities defined in YAML"
            return gaps
        
        # Compare ability score values (roughly)
        python_attrs = python_stats.attributes
        ability_diffs = {}
        
        for ability in ['STR', 'DEX', 'CON', 'INT', 'WIS', 'CHA']:
            python_score = getattr(python_attrs, ability, 10)
            yaml_scaling = yaml_abilities.get(ability, 'Default')
            
            # Rough expected scores based on scaling type
            cr = python_stats.cr
            expected_ranges = {
                'Primary': (15 + cr//2, 20 + cr//2),
                'Medium': (12 + cr//4, 16 + cr//4), 
                'Constitution': (12 + cr//4, 16 + cr//4),
                'Default': (8 + cr//8, 12 + cr//8)
            }
            
            if isinstance(yaml_scaling, str) and yaml_scaling in expected_ranges:
                min_score, max_score = expected_ranges[yaml_scaling]
                if not (min_score <= python_score <= max_score):
                    ability_diffs[ability] = {
                        'python_score': python_score,
                        'yaml_scaling': yaml_scaling,
                        'expected_range': f"{min_score}-{max_score}"
                    }
        
        if ability_diffs:
            gaps['ability_score_mismatches'] = ability_diffs
        
        return gaps
    
    def _analyze_complex_features(self, template_class, settings) -> Dict[str, Any]:
        """Analyze complex features that are hard to capture in YAML."""
        complex_gaps = []
        
        # Check if template uses CR-dependent logic
        import inspect
        source = inspect.getsource(template_class.generate_stats)
        
        if 'if cr >=' in source or 'if stats.cr >=' in source:
            complex_gaps.append("Uses CR-dependent conditional logic")
        
        if 'rng' in source or 'choose_' in source:
            complex_gaps.append("Uses random selection")
        
        if 'species' in source and 'HumanSpecies' in source:
            complex_gaps.append("Has species-dependent behavior")
        
        if 'settings.hp_multiplier *' in source:
            complex_gaps.append("Uses dynamic HP multiplier calculations")
        
        if 'grant_spellcasting' in source:
            complex_gaps.append("Grants spellcasting abilities")
        
        if 'with_set_attacks' in source or 'multiattack' in source:
            complex_gaps.append("Has complex attack count logic")
        
        return complex_gaps

    def analyze_all_templates(self) -> Dict[str, Any]:
        """Analyze all available templates and provide summary."""
        templates_to_test = [
            ("foe_foundry.creatures.berserker", "BerserkerTemplate", "berserker", "berserker.yml"),
            ("foe_foundry.creatures.assassin", "AssassinTemplate", "assassin", "assassin.yml"),
            ("foe_foundry.creatures.knight", "KnightTemplate", "knight", "knight.yml"),
            ("foe_foundry.creatures.goblin", "GoblinTemplate", "goblin", "goblin.yml"),
            ("foe_foundry.creatures.mage", "MageTemplate", "mage", "mage.yml"),
            ("foe_foundry.creatures.lich", "LichTemplate", "lich", "lich.yml"),
            ("foe_foundry.creatures.priest", "PriestTemplate", "priest", "priest.yml"),
            ("foe_foundry.creatures.scout", "ScoutTemplate", "scout", "scout.yml"),
        ]
        
        all_results = {}
        summary = {
            'total_templates': len(templates_to_test),
            'successful_analyses': 0,
            'common_gaps': {},
            'complex_features': {}
        }
        
        for module_name, template_name, monster_key, yaml_file in templates_to_test:
            try:
                # Import the template
                module = __import__(module_name, fromlist=[template_name])
                template_class = getattr(module, template_name)
                
                yaml_path = Path(f"/home/runner/work/foe_foundry/foe_foundry/foe_foundry/statblocks/{yaml_file}")
                
                if not yaml_path.exists():
                    all_results[template_name] = {"error": f"YAML file not found: {yaml_file}"}
                    continue
                
                # Analyze gaps
                gaps = self.analyze_template_gaps(template_class, yaml_path, monster_key)
                all_results[template_name] = gaps
                
                if 'error' not in gaps:
                    summary['successful_analyses'] += 1
                    
                    # Track common gap types
                    for gap_type, gap_data in gaps.items():
                        if gap_type not in summary['common_gaps']:
                            summary['common_gaps'][gap_type] = 0
                        if gap_data:  # Non-empty gaps
                            summary['common_gaps'][gap_type] += 1
                    
                    # Track complex features
                    complex_features = gaps.get('complex', [])
                    for feature in complex_features:
                        if feature not in summary['complex_features']:
                            summary['complex_features'][feature] = 0
                        summary['complex_features'][feature] += 1
                
            except Exception as e:
                all_results[template_name] = {"error": str(e)}
        
        return {
            'summary': summary,
            'detailed_results': all_results
        }


if __name__ == "__main__":
    analyzer = YAMLPythonComparison()
    results = analyzer.analyze_all_templates()
    
    print("=== YAML vs Python Template Analysis ===\n")
    
    summary = results['summary']
    print(f"Templates analyzed: {summary['successful_analyses']}/{summary['total_templates']}")
    print()
    
    print("Common gap types (number of templates affected):")
    for gap_type, count in summary['common_gaps'].items():
        print(f"  {gap_type}: {count}")
    print()
    
    print("Complex features detected (number of templates):")
    for feature, count in summary['complex_features'].items():
        print(f"  {feature}: {count}")
    print()
    
    print("Detailed results:")
    for template_name, gaps in results['detailed_results'].items():
        print(f"\n{template_name}:")
        if 'error' in gaps:
            print(f"  ERROR: {gaps['error']}")
        else:
            for gap_type, gap_data in gaps.items():
                if gap_data:
                    print(f"  {gap_type}: {len(gap_data) if isinstance(gap_data, (dict, list)) else 'present'}")