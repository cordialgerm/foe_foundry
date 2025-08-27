"""
Integration tests comparing YAML template parser with original MonsterTemplate implementations.
"""
import pytest
from pathlib import Path
from typing import Dict, Any, List, Tuple

from foe_foundry.statblocks.yaml_parser import parse_yaml_template
from foe_foundry.statblocks.base import BaseStatblock
from foe_foundry.attack_template import AttackTemplate
from foe_foundry.creatures._data import GenerationSettings, rng_factory


class TestYAMLTemplateIntegration:
    """Integration tests for YAML template parser."""
    
    def get_original_template_stats(self, template_class, monster_key: str) -> Tuple[BaseStatblock, List[AttackTemplate]]:
        """Get stats from original MonsterTemplate implementation."""
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
    
    def get_yaml_template_stats(self, yaml_path: Path, monster_key: str) -> Tuple[BaseStatblock, List[AttackTemplate]]:
        """Get stats from YAML template parser."""
        return parse_yaml_template(yaml_path, monster_key)
    
    def compare_base_statblocks(self, original: BaseStatblock, yaml_parsed: BaseStatblock) -> Dict[str, Any]:
        """Compare two BaseStatblock objects and return differences."""
        differences = {}
        
        # Compare basic attributes
        attrs_to_compare = [
            'name', 'cr', 'creature_type', 'size', 'creature_class',
            'damage_multiplier', 'primary_damage_type', 'secondary_damage_type',
            'is_legendary'
        ]
        
        for attr in attrs_to_compare:
            orig_val = getattr(original, attr, None)
            yaml_val = getattr(yaml_parsed, attr, None)
            
            if orig_val != yaml_val:
                differences[attr] = {
                    'original': orig_val,
                    'yaml': yaml_val
                }
        
        # Compare languages (may be in different order)
        orig_langs = set(original.languages) if original.languages else set()
        yaml_langs = set(yaml_parsed.languages) if yaml_parsed.languages else set()
        if orig_langs != yaml_langs:
            differences['languages'] = {
                'original': list(orig_langs),
                'yaml': list(yaml_langs)
            }
        
        return differences
    
    def compare_attack_templates(self, original: List[AttackTemplate], yaml_parsed: List[AttackTemplate]) -> Dict[str, Any]:
        """Compare attack template lists and return differences."""
        differences = {}
        
        if len(original) != len(yaml_parsed):
            differences['count'] = {
                'original': len(original),
                'yaml': len(yaml_parsed)
            }
        
        # Compare attack names
        orig_names = [att.attack_name for att in original]
        yaml_names = [att.attack_name for att in yaml_parsed] if yaml_parsed else []
        
        if orig_names != yaml_names:
            differences['attack_names'] = {
                'original': orig_names,
                'yaml': yaml_names
            }
        
        return differences
    
    def test_berserker_template_comparison(self):
        """Test berserker template: original vs YAML."""
        from foe_foundry.creatures.berserker import BerserkerTemplate
        
        yaml_path = Path("/home/runner/work/foe_foundry/foe_foundry/foe_foundry/statblocks/berserker.yml")
        monster_key = "berserker"
        
        # Get stats from both sources
        orig_stats, orig_attacks = self.get_original_template_stats(BerserkerTemplate, monster_key)
        yaml_stats, yaml_attacks = self.get_yaml_template_stats(yaml_path, monster_key)
        
        # Compare
        stat_diffs = self.compare_base_statblocks(orig_stats, yaml_stats)
        attack_diffs = self.compare_attack_templates(orig_attacks, yaml_attacks)
        
        print(f"Berserker comparison:")
        print(f"  Stat differences: {stat_diffs}")
        print(f"  Attack differences: {attack_diffs}")
        
        # Basic assertions
        assert orig_stats.name == yaml_stats.name
        assert orig_stats.cr == yaml_stats.cr
        
    def test_assassin_template_comparison(self):
        """Test assassin template: original vs YAML."""
        from foe_foundry.creatures.assassin import AssassinTemplate
        
        yaml_path = Path("/home/runner/work/foe_foundry/foe_foundry/foe_foundry/statblocks/assassin.yml")
        monster_key = "assassin"
        
        # Get stats from both sources
        orig_stats, orig_attacks = self.get_original_template_stats(AssassinTemplate, monster_key)
        yaml_stats, yaml_attacks = self.get_yaml_template_stats(yaml_path, monster_key)
        
        # Compare
        stat_diffs = self.compare_base_statblocks(orig_stats, yaml_stats)
        attack_diffs = self.compare_attack_templates(orig_attacks, yaml_attacks)
        
        print(f"Assassin comparison:")
        print(f"  Stat differences: {stat_diffs}")
        print(f"  Attack differences: {attack_diffs}")
        
    def test_multiple_templates_summary(self):
        """Test multiple templates and provide a summary of gaps."""
        templates_to_test = [
            ("foe_foundry.creatures.berserker", "BerserkerTemplate", "berserker", "berserker.yml"),
            ("foe_foundry.creatures.assassin", "AssassinTemplate", "assassin", "assassin.yml"),
            ("foe_foundry.creatures.knight", "KnightTemplate", "knight", "knight.yml"),
            ("foe_foundry.creatures.goblin", "GoblinTemplate", "goblin", "goblin.yml"),
        ]
        
        all_differences = {}
        
        for module_name, template_name, monster_key, yaml_file in templates_to_test:
            try:
                # Import the template
                module = __import__(module_name, fromlist=[template_name])
                template_class = getattr(module, template_name)
                
                yaml_path = Path(f"/home/runner/work/foe_foundry/foe_foundry/foe_foundry/statblocks/{yaml_file}")
                
                # Get stats from both sources
                orig_stats, orig_attacks = self.get_original_template_stats(template_class, monster_key)
                yaml_stats, yaml_attacks = self.get_yaml_template_stats(yaml_path, monster_key)
                
                # Compare
                stat_diffs = self.compare_base_statblocks(orig_stats, yaml_stats)
                attack_diffs = self.compare_attack_templates(orig_attacks, yaml_attacks)
                
                all_differences[template_name] = {
                    'stat_differences': stat_diffs,
                    'attack_differences': attack_diffs
                }
                
            except Exception as e:
                all_differences[template_name] = {
                    'error': str(e)
                }
        
        print("Summary of all template differences:")
        for template, diffs in all_differences.items():
            print(f"\n{template}:")
            if 'error' in diffs:
                print(f"  ERROR: {diffs['error']}")
            else:
                print(f"  Stat differences: {len(diffs['stat_differences'])} fields")
                print(f"  Attack differences: {len(diffs['attack_differences'])} fields")
                if diffs['stat_differences']:
                    print(f"    Stat issues: {list(diffs['stat_differences'].keys())}")
                if diffs['attack_differences']:
                    print(f"    Attack issues: {list(diffs['attack_differences'].keys())}")


if __name__ == "__main__":
    test = TestYAMLTemplateIntegration()
    test.test_multiple_templates_summary()