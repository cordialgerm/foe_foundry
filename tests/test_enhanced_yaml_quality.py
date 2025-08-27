"""
Enhanced YAML template quality validation tests.
Checks for specific improvements made in manual Python-to-YAML translation.
"""
import yaml
from pathlib import Path
import pytest


class TestEnhancedYAMLQuality:
    """Test specific quality improvements in YAML templates."""
    
    @pytest.fixture
    def statblocks_dir(self):
        """Get the statblocks directory."""
        return Path(__file__).parent.parent / "foe_foundry" / "statblocks"
    
    def load_yaml_template(self, statblocks_dir: Path, template_name: str):
        """Load a YAML template file."""
        yaml_path = statblocks_dir / f"{template_name}.yml"
        with open(yaml_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f)
    
    def test_knight_conditional_logic_resolution(self, statblocks_dir):
        """Test knight template CR-dependent logic resolution."""
        data = self.load_yaml_template(statblocks_dir, "knight")
        
        # Check that CHA scaling includes the tuple format [Medium, 2]
        assert data['common']['abilities']['CHA'] == ['Medium', 2], \
            "Knight should have CHA: [Medium, 2] scaling from Python code"
        
        # Check HP multiplier for high CR monsters
        questing_knight = data['questing-knight']
        assert questing_knight['hp_multiplier'] == 1.1, \
            "Questing Knight (CR 12) should have 1.1 HP multiplier from cr >= 12 condition"
        
        paragon_knight = data['paragon-knight']
        assert paragon_knight['hp_multiplier'] == 1.1, \
            "Paragon Knight (CR 16) should have 1.1 HP multiplier from cr >= 12 condition"
        
        # Check weapon display names based on CR
        assert data['knight']['attacks']['main']['base'] == 'Greatsword'
        assert 'display_name' not in data['knight']['attacks']['main'], \
            "Basic Knight should not have display_name (no CR threshold met)"
        
        assert data['knight-of-the-realm']['attacks']['main']['display_name'] == 'Blessed Blade', \
            "Knight of the Realm (CR 6) should get Blessed Blade from cr >= 6 condition"
        
        assert data['questing-knight']['attacks']['main']['display_name'] == 'Oathbound Blade', \
            "Questing Knight (CR 12) should get Oathbound Blade from cr >= 12 condition"
    
    def test_berserker_secondary_damage_progression(self, statblocks_dir):
        """Test berserker secondary damage type progression by CR."""
        data = self.load_yaml_template(statblocks_dir, "berserker")
        
        # Basic berserker (CR 2) should have no secondary damage (cr < 4)
        assert data['common']['attacks']['main']['secondary_damage_type'] is None, \
            "Basic berserker attacks should have no secondary damage (CR < 4)"
        
        # Veteran and higher should have elemental damage list (cr >= 4)
        veteran = data['berserker-veteran']
        expected_elements = ["Fire", "Cold", "Lightning", "Acid", "Poison"]
        assert veteran['attacks']['main']['secondary_damage_type'] == expected_elements, \
            "Berserker Veteran should have elemental damage types from cr >= 4 condition"
        
        # Check saves progression - only CR >= 4 get saves
        assert data['common']['saves'] == [], \
            "Basic berserker should have no saves"
        assert set(veteran['saves']) == {'STR', 'CON'}, \
            "Berserker Veteran should have STR and CON saves from cr >= 4 condition"
    
    def test_assassin_attack_structure(self, statblocks_dir):
        """Test assassin attack structure and skill progression."""
        data = self.load_yaml_template(statblocks_dir, "assassin")
        
        # Check that set_attacks is properly structured
        assert data['common']['attacks']['set_attacks'] == 2, \
            "Assassin should have set_attacks: 2 from multiattack logic"
        
        # Check secondary attack is present
        assert 'secondary' in data['common']['attacks'], \
            "Assassin should have secondary HandCrossbow attack"
        assert data['common']['attacks']['secondary']['base'] == 'HandCrossbow', \
            "Assassin secondary attack should be HandCrossbow"
        
        # Check that contract-killer has different attack count
        contract_killer = data['contract-killer']
        assert contract_killer['attacks']['set_attacks'] == 1, \
            "Contract Killer should have set_attacks: 1 from cr <= 4 condition"
        
        # Check expertise only for CR >= 6 (assassin and assassin-legend, not contract-killer)
        assert data['common']['skills']['expertise'] == [], \
            "Basic common should have no expertise"
        assert 'expertise' not in data['contract-killer'].get('skills', {}), \
            "Contract Killer should not have expertise (CR < 6)"
        assert 'Stealth' in data['assassin']['skills']['expertise'], \
            "Assassin should have Stealth expertise from cr >= 6 condition"
    
    def test_goblin_complete_reconstruction(self, statblocks_dir):
        """Test goblin template complete reconstruction from broken state."""
        data = self.load_yaml_template(statblocks_dir, "goblin")
        
        # Check all CRs are properly filled
        monsters = {m['key']: m['cr'] for m in data['template']['monsters']}
        assert monsters['goblin-lickspittle'] == 0.125, "Goblin Lickspittle should have CR 1/8"
        assert monsters['goblin'] == 0.25, "Goblin should have CR 1/4"
        assert monsters['goblin-brute'] == 0.5, "Goblin Brute should have CR 1/2"
        
        # Check environments are populated (was empty before)
        assert len(data['template']['environments']) > 0, \
            "Goblin should have environment mappings"
        native_envs = [env for env in data['template']['environments'] if env['affinity'] == 'native']
        assert len(native_envs) >= 2, \
            "Goblin should have multiple native environments"
        
        # Check creature types are not null
        assert data['common']['creature_type'] == 'Humanoid', \
            "Goblin should have Humanoid creature type (was null)"
        assert 'Fey' in data['common']['additional_creature_types'], \
            "Goblin should have Fey as additional creature type"
        
        # Check roles are not null
        assert data['common']['roles']['primary'] == 'Skirmisher', \
            "Goblin should have Skirmisher primary role (was null)"
        
        # Check variant-specific differences
        brute = data['goblin-brute']
        assert brute['roles']['primary'] == 'Soldier', \
            "Goblin Brute should have different primary role"
        assert brute['abilities']['STR'] == 'Primary', \
            "Goblin Brute should have STR Primary scaling"
        
        shaman = data['goblin-shaman']
        assert shaman['roles']['primary'] == 'Controller', \
            "Goblin Shaman should have Controller role"
        assert shaman['abilities']['INT'] == 'Primary', \
            "Goblin Shaman should have INT Primary scaling"
    
    def test_environment_mapping_accuracy(self, statblocks_dir):
        """Test that environment mappings are complete and accurate."""
        # Test several templates for environment completeness
        templates_to_check = ['knight', 'assassin', 'berserker', 'goblin']
        
        for template_name in templates_to_check:
            data = self.load_yaml_template(statblocks_dir, template_name)
            environments = data['template']['environments']
            
            assert len(environments) > 0, \
                f"{template_name} should have environment mappings"
            
            # Check all environments have required fields
            for env in environments:
                assert 'affinity' in env, \
                    f"{template_name} environment should have affinity"
                assert env['affinity'] in ['native', 'common', 'uncommon', 'rare'], \
                    f"{template_name} should have valid affinity values"
                
                # Should have at least one dimension
                dimensions = [k for k in env.keys() if k != 'affinity']
                assert len(dimensions) >= 1, \
                    f"{template_name} environment should have at least one dimension"
    
    def test_ability_score_tuple_formatting(self, statblocks_dir):
        """Test that ability score scaling properly represents tuple formats."""
        # Check several templates for proper tuple representation
        test_cases = [
            ('knight', 'CHA', ['Medium', 2]),
            ('berserker', 'DEX', ['Medium', 2]),
            ('berserker', 'CON', ['Constitution', 2]),
            ('assassin', 'INT', ['Medium', 0.5]),
            ('assassin', 'WIS', ['Medium', 1]),
        ]
        
        for template_name, ability, expected_value in test_cases:
            data = self.load_yaml_template(statblocks_dir, template_name)
            actual_value = data['common']['abilities'][ability]
            assert actual_value == expected_value, \
                f"{template_name} {ability} should be {expected_value}, got {actual_value}"
    
    def test_yaml_structure_validity(self, statblocks_dir):
        """Test that YAML files have valid structure without syntax errors."""
        template_names = ['knight', 'berserker', 'assassin', 'goblin', 'bandit', 'balor']
        
        for template_name in template_names:
            try:
                data = self.load_yaml_template(statblocks_dir, template_name)
                
                # Check basic structure
                assert 'template' in data, f"{template_name} should have template section"
                assert 'common' in data, f"{template_name} should have common anchor"
                
                # Check no !!set syntax errors
                yaml_content = (statblocks_dir / f"{template_name}.yml").read_text()
                assert '!!set' not in yaml_content, \
                    f"{template_name} should not have !!set syntax errors"
                
                # Check template monsters all have valid CRs
                for monster in data['template']['monsters']:
                    assert monster['cr'] is not None, \
                        f"{template_name} monster {monster['key']} should have valid CR"
                
            except yaml.YAMLError as e:
                pytest.fail(f"{template_name}.yml has YAML syntax errors: {e}")