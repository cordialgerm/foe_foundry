# YAML Parsing PRD

Your task is to complete the `YamlMonsterTemplate` in `_yaml_template.py`. This class provides a much cleaner and more extensible implementation of the `MonsterTemplate` compared to the imperative code-based approach of existing templates defined in `creatures/<monster>/<monster>.py`

## History

Previously, we went through all of the templtes in `creatures/<monster>/<monster>.py` and translated them them to `creatures/templates/<monster>.yml` and created a nice declarative YAML syntax for these templates.

A previous agent also created parsing logic to translate these YAML templates, but the logic is messy. We need to clean this implementation up. You can see the previous implementation in OLD_yaml_parser.py

The previous agent also wrote some unit tests that at the time claimed the parsing was accurate, but those tests were messy. We're going to clean that up as well.

## High Level Goals

- Create a well-defined schema for these YAML templates and ensure all the existing templates follow the schema
- Create well-defined and unit-tested parsing / translation methods that take individual pieces of the YAML format and translate it to the corresponding python objects that are needed to build out the `BaseStatblock`


## Detailed Tasks

1. Create a YAML schema that works for all power templates.
  - Store that in /foe_foundry/creatures/templates
  - Create a well-structured helper method in /foe_foundry/creatures/templates/schema.py that validates YAML against the schema
  - Create pytest tests in /tests/foe_foundry/templates/test_yaml_schema.py that verify each template passes the schema. Use pytest fixtures to parametrize the test so it checks each template in the templates folder
2. Create a series of helper functions that parse or translate from the YAML format, as defined in `creatures/templates/<monster>.yml`
  - tests should live in /tests/foe_foundry/templates/test_yaml_helpers.py and test each parsing method on multiple example yaml chunks
  - helper methods shuld live in _yaml_template.py and be well-constructed and clean
  - You can be inspired by logic in OLD_yaml_parser.py, but that code is messy. If you use that code, clean it up and modularize it into tested, pure functions
3. Finish the implementation of YamlMonster, using the clean unit-tested pure-function parsing helpers
4. Create a comparison integration test in /tests/foe_foundry/templates/test_yaml_templates.py
  - should be parametrized test that compares the python imperative implementation to the YAML implementation
  - it runs on every template in `foe_foundry.creatures.AllTemplates`
  - it finds the corresponding YAML template for that python template and constructs a `YamlMonsterTemplate`
  - test should call `generate_all()` and iterate through each `StatsBeingGenerated` from the two templates
  - test should compare the `StatsBeingGenerated` and assert they are all exactly equivalent
  - create a standalone helper method to compare that a given `StatsBeingGenerated` is equivalent to another


## Relevant Notes

- You can read `/foe_foundry/creatures/templates/prompt_python_template.md` to learn more about the approach of representing the python classes as markdown files
- You can update these instructions via the SCRATCHPAD below. Record new ideas, thoughts, or challenges that will help subsequent turns of a coding agent understand the progress and challenges youve encountered

## SCRATCHPAD

TODO - additional notes go here


