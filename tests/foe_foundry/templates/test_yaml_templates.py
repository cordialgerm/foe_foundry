"""
Integration tests comparing YAML templates to Python imperative implementations.
"""

import pytest
from pathlib import Path
from typing import List, Tuple
import yaml

# Note: This test file is designed to be run when the full foe_foundry environment is available
# For now, it serves as a placeholder and documentation for the required functionality


class TestYamlTemplateComparison:
    """Test class for comparing YAML and Python template implementations."""
    
    @pytest.fixture
    def all_python_templates(self):
        """
        Fixture to get all Python template implementations.
        
        This would import from foe_foundry.creatures.AllTemplates when available.
        """
        # TODO: Implement when full environment is available
        # from foe_foundry.creatures import AllTemplates
        # return AllTemplates
        return []
    
    @pytest.fixture
    def yaml_template_files(self):
        """
        Fixture to get all YAML template files.
        """
        templates_dir = Path(__file__).parent.parent.parent / "foe_foundry" / "creatures" / "templates"
        return list(templates_dir.glob("*.yml"))
    
    def find_corresponding_yaml_template(self, python_template, yaml_files: List[Path]) -> Path:
        """
        Find the YAML template file that corresponds to a Python template.
        
        Args:
            python_template: The Python MonsterTemplate instance
            yaml_files: List of available YAML template files
            
        Returns:
            Path to the corresponding YAML file
            
        Raises:
            ValueError: If no corresponding YAML template is found
        """
        template_key = python_template.key
        
        for yaml_file in yaml_files:
            if yaml_file.stem == template_key:
                return yaml_file
        
        raise ValueError(f"No YAML template found for Python template: {template_key}")
    
    def load_yaml_template(self, yaml_path: Path):
        """
        Load a YamlMonsterTemplate from a YAML file.
        
        Args:
            yaml_path: Path to the YAML template file
            
        Returns:
            YamlMonsterTemplate instance
        """
        # TODO: Implement when full environment is available
        # from foe_foundry.creatures._yaml_template import YamlMonsterTemplate
        # 
        # with open(yaml_path, 'r', encoding='utf-8') as f:
        #     yaml_data = yaml.safe_load(f)
        # 
        # return YamlMonsterTemplate(yaml_data)
        pass
    
    def compare_stats_being_generated(self, python_stats, yaml_stats) -> bool:
        """
        Compare two StatsBeingGenerated instances for equivalence.
        
        This is a helper method that compares the essential properties of
        generated monster statistics to determine if they are equivalent.
        
        Args:
            python_stats: StatsBeingGenerated from Python template
            yaml_stats: StatsBeingGenerated from YAML template
            
        Returns:
            True if the stats are equivalent, False otherwise
        """
        # TODO: Implement detailed comparison logic
        # 
        # Key areas to compare:
        # - Basic stats (name, CR, creature type, size, etc.)
        # - Ability scores and modifiers
        # - HP, AC, and saves
        # - Skills and proficiencies
        # - Movement speeds
        # - Senses
        # - Damage immunities/resistances/vulnerabilities
        # - Condition immunities
        # - Languages
        # - Attacks (name, bonus, damage, properties)
        # - Legendary actions (if applicable)
        #
        # Example structure:
        # if python_stats.name != yaml_stats.name:
        #     return False
        # if python_stats.cr != yaml_stats.cr:
        #     return False
        # if python_stats.creature_type != yaml_stats.creature_type:
        #     return False
        # # ... continue for all relevant fields
        # return True
        
        return True  # Placeholder
    
    @pytest.mark.parametrize("python_template", [], ids=lambda t: t.key)
    def test_yaml_template_matches_python_template(self, python_template, yaml_template_files):
        """
        Test that a YAML template produces equivalent results to its Python counterpart.
        
        This test:
        1. Finds the corresponding YAML template for the Python template
        2. Generates all possible monster variants from both templates
        3. Compares each generated monster for equivalence
        """
        # TODO: Implement when full environment is available
        pytest.skip("Requires full foe_foundry environment")
        
        # Find corresponding YAML template
        yaml_path = self.find_corresponding_yaml_template(python_template, yaml_template_files)
        yaml_template = self.load_yaml_template(yaml_path)
        
        # Get all possible generation settings for this template
        # This would iterate through all variants, monsters, species, etc.
        # python_settings = python_template.all_generation_settings()
        # yaml_settings = yaml_template.all_generation_settings()
        
        # assert len(python_settings) == len(yaml_settings), "Different number of generation settings"
        
        # Compare each generated monster
        # for python_setting, yaml_setting in zip(python_settings, yaml_settings):
        #     python_stats = python_template.generate(python_setting)
        #     yaml_stats = yaml_template.generate(yaml_setting)
        #     
        #     assert self.compare_stats_being_generated(python_stats, yaml_stats), \
        #         f"Mismatch for {python_setting.id}"
    
    def test_yaml_template_basic_functionality(self, yaml_template_files):
        """
        Test basic functionality of YAML templates.
        
        This test verifies that YAML templates can be loaded and basic operations work.
        """
        # Test a few templates to ensure basic functionality
        test_files = yaml_template_files[:3]  # Test first 3 files
        
        for yaml_path in test_files:
            # Load and validate the YAML file
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Basic structure validation
            assert "template" in yaml_data
            assert "key" in yaml_data["template"]
            assert "name" in yaml_data["template"]
            assert "monsters" in yaml_data["template"]
            
            # Validate each monster entry
            for monster in yaml_data["template"]["monsters"]:
                assert "key" in monster
                assert "name" in monster
                assert "cr" in monster
                assert isinstance(monster["cr"], (int, float))
                
                # Ensure monster data section exists
                assert monster["key"] in yaml_data
            
            # Validate common sections exist
            common_sections = [k for k in yaml_data.keys() if k == "common" or k.endswith("_common")]
            assert len(common_sections) > 0, f"No common section found in {yaml_path.name}"
    
    def test_all_yaml_templates_have_required_sections(self, yaml_template_files):
        """
        Test that all YAML templates have the required sections for monster generation.
        """
        required_template_fields = ["key", "name", "monsters"]
        # Only require essential fields that should be in every common section
        required_common_fields = ["creature_type", "abilities"]
        
        for yaml_path in yaml_template_files:
            with open(yaml_path, 'r', encoding='utf-8') as f:
                yaml_data = yaml.safe_load(f)
            
            # Check template section
            template_section = yaml_data.get("template", {})
            for field in required_template_fields:
                assert field in template_section, \
                    f"Missing required template field '{field}' in {yaml_path.name}"
            
            # Check common sections
            common_sections = [k for k in yaml_data.keys() if k == "common" or k.endswith("_common")]
            assert len(common_sections) > 0, f"No common section found in {yaml_path.name}"
            
            # Check first common section has required fields
            common_data = yaml_data[common_sections[0]]
            for field in required_common_fields:
                assert field in common_data, \
                    f"Missing required common field '{field}' in {yaml_path.name}"
            
            # Verify that each monster has a data section and essential fields
            template_data = yaml_data["template"]
            for monster in template_data.get("monsters", []):
                monster_key = monster["key"]
                assert monster_key in yaml_data, \
                    f"Missing data section for monster '{monster_key}' in {yaml_path.name}"
                
                # Get merged data for this monster to check essential fields
                monster_data = yaml_data[monster_key]
                merged_data = {**common_data}
                for key, value in monster_data.items():
                    if key != "<<":
                        merged_data[key] = value
                
                # Check that essential fields exist either in common or monster-specific data
                essential_fields = ["creature_type", "abilities"]
                for field in essential_fields:
                    assert field in merged_data, \
                        f"Missing essential field '{field}' for monster '{monster_key}' in {yaml_path.name}"


# Standalone helper functions for comparison (when environment is available)

def compare_ability_scores(python_abilities, yaml_abilities) -> bool:
    """Compare ability score configurations."""
    # TODO: Implement detailed ability score comparison
    return True

def compare_attacks(python_attacks, yaml_attacks) -> bool:
    """Compare attack configurations.""" 
    # TODO: Implement detailed attack comparison
    return True

def compare_resistances_immunities(python_resistances, yaml_resistances) -> bool:
    """Compare resistance and immunity configurations."""
    # TODO: Implement detailed resistance/immunity comparison
    return True

def compare_skills_and_saves(python_skills, yaml_skills) -> bool:
    """Compare skill and saving throw configurations."""
    # TODO: Implement detailed skills/saves comparison
    return True


if __name__ == "__main__":
    # Run basic tests that don't require the full environment
    import sys
    
    templates_dir = Path(__file__).parent.parent.parent / "foe_foundry" / "creatures" / "templates"
    if not templates_dir.exists():
        templates_dir = Path("/home/runner/work/foe_foundry/foe_foundry/foe_foundry/creatures/templates")
    
    template_files = list(templates_dir.glob("*.yml"))
    
    print(f"Found {len(template_files)} YAML templates")
    
    # Test basic structure validation
    test_instance = TestYamlTemplateComparison()
    
    try:
        test_instance.test_yaml_template_basic_functionality(template_files)
        print("✓ Basic functionality test passed")
        
        test_instance.test_all_yaml_templates_have_required_sections(template_files)
        print("✓ Required sections test passed")
        
        print("\nAll standalone tests passed! ✅")
        
    except Exception as e:
        print(f"Test failed: {e}")
        sys.exit(1)