from foe_foundry.creatures.wight import WightTemplate
from foe_foundry_data.monsters import MonsterModel


def test_monster_model():
    for stats in WightTemplate.generate_all():
        model = MonsterModel.from_monster(
            stats=stats.finalize(),
            template=WightTemplate,
            base_url="https://128.0.0.1:8080",
        )
        assert len(model.images) > 0
        assert model.template_html is not None
