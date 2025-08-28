from foe_foundry.attack_template import AttackTemplate
from foe_foundry.creatures._data import GenerationSettings
from foe_foundry.creatures.species import AllSpecies, CreatureSpecies
from foe_foundry.environs import EnvironmentAffinity
from foe_foundry.powers import PowerSelection
from foe_foundry.statblocks import BaseStatblock

from ._template import Monster, MonsterTemplate, MonsterVariant
from .zombie.powers import LoadoutZombie


class YamlMonsterTemplate(MonsterTemplate):
    def __init__(self, yaml_data: dict):
        # Store yaml_data for use in methods
        self.yaml_data = yaml_data

        template_data = yaml_data["template"]

        # Extract required fields
        name = template_data["name"]

        # Parse variants from yaml_data
        variants = parse_variants_from_template_yaml(template_data)

        # Parse species from yaml_data
        species = parse_species_from_template_yaml(template_data)

        # Parse environments from yaml_data
        environments = parse_environments_from_template_yaml(template_data)

        # Parse sentient flag
        is_sentient_species = template_data.get("is_sentient_species", False)

        # Call parent constructor with parsed data
        super().__init__(
            name=name,
            tag_line="TODO LATER",
            description="TODO LATER",
            treasure=["TODO LATER"],
            variants=variants,
            species=species,
            environments=environments,
            is_sentient_species=is_sentient_species,
        )

    def generate_stats(
        self, settings: GenerationSettings
    ) -> tuple[BaseStatblock, list[AttackTemplate]]:
        stats = parse_statblock_from_yaml(self.yaml_data)
        attacks = parse_attacks_from_yaml(self.yaml_data)
        return stats, attacks

    def choose_powers(self, settings: GenerationSettings) -> PowerSelection:
        # TODO Later
        # This is just a placeholder for now to make the class valid
        # We will fix this later
        return PowerSelection(
            loadouts=LoadoutZombie,
        )


def parse_statblock_from_yaml(yaml_data: dict) -> BaseStatblock:
    # TODO NOW
    pass


def parse_attacks_from_yaml(yaml_data: dict) -> list[AttackTemplate]:
    # TODO NOW
    pass


def parse_species_from_template_yaml(template_data: dict) -> list[CreatureSpecies]:
    species_option = template_data.get("species", None)
    if species_option == "all":
        return AllSpecies
    else:
        return []


def parse_variants_from_template_yaml(template_data: dict) -> list[MonsterVariant]:
    variants = []
    monsters: list[dict] = template_data["monsters"]
    for monster_data in monsters:
        name = monster_data["name"]
        cr = monster_data["cr"]
        is_legendary = monster_data.get("is_legendary", False)

        monster = Monster(
            name=name,
            cr=cr,
            is_legendary=is_legendary,
            srd_creatures=None,  # TODO LATER
            other_creatures=None,  # TODO LATER
        )

        variant = MonsterVariant(name=name, description=name, monsters=[monster])
        variants.append(variant)

    return variants


def parse_environments_from_template_yaml(
    template_data: dict,
) -> list[EnvironmentAffinity]:
    environments_data = template_data.get("environments", None)
    # TODO NOW
