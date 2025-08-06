from foe_foundry.creatures.orc.orc import OrcTemplate
from foe_foundry.creatures.priest.priest import PriestTemplate, PriestVariant
from foe_foundry.creatures.species import OrcSpecies
from foe_foundry.creatures.wight import WightTemplate
from foe_foundry_data.monsters import MonsterModel


def test_monster_model():
    for variant, monster, species, stats in WightTemplate.generate_all():
        model = MonsterModel.from_monster(
            stats=stats.finalize(),
            template=WightTemplate,
            variant=variant,
            monster=monster,
            species=species,
            base_url="https://128.0.0.1:8080",
        )
        assert len(model.images) > 0
        assert model.template_html is not None
        assert model.encounter_html is not None
        assert model.overview_html is not None
        assert len(model.loadouts) > 0


def test_monster_model_with_species():
    stats = PriestTemplate.generate_monster(
        variant=PriestVariant, monster=PriestVariant.monsters[0], species=OrcSpecies
    ).finalize()

    assert stats.name == "Orc Acolyte"
    assert stats.name == f"Orc {PriestVariant.monsters[0].name}"


def test_orc_has_image():
    assert OrcTemplate.primary_image_url is not None
