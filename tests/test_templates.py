import pytest

from foe_foundry.creatures import (
    GenerationSettings,
    MonsterTemplate,
    all_templates_and_settings,
)


def _ids(t: MonsterTemplate) -> str:
    return t.key


def _ids2(obj: tuple[MonsterTemplate, GenerationSettings]) -> str:
    template, settings = obj
    return f"{template.key}/{settings.id}"


@pytest.mark.parametrize(
    "template_and_setting", all_templates_and_settings(), ids=_ids2
)
def test_all_statblocks(
    template_and_setting: tuple[MonsterTemplate, GenerationSettings],
):
    template, settings = template_and_setting
    stats = template.generate(settings).finalize()
    assert stats is not None
