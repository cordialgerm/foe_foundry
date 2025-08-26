import textwrap

from foe_foundry.utils.yaml import extract_yaml_block_from_text


def test_basic_yaml():
    text = """monster_name: Magma Elemental\nmonster_type: elemental"""
    result = extract_yaml_block_from_text(text)
    assert result["monster_name"] == "Magma Elemental"
    assert result["monster_type"] == "elemental"


def test_colon_in_value():
    text = """monster_fantasy: Born where magma and stone fuse: volcanic vents, forge-rites, or earthshaping rituals."""
    result = extract_yaml_block_from_text(text)
    assert "magma and stone fuse" in result["monster_fantasy"]
    assert ":" in result["monster_fantasy"]


def test_double_quote_in_value():
    text = textwrap.dedent("""
    ```yaml
    monster_quote: He said, "Burn!"
    ```
    """)
    result = extract_yaml_block_from_text(text)
    assert result["monster_quote"] == 'He said, "Burn!"'


def test_yaml_block_with_code_fence():
    text = """```yaml\nmonster_name: Magma Elemental\nmonster_type: elemental\n```"""
    result = extract_yaml_block_from_text(text)
    assert result["monster_name"] == "Magma Elemental"
    assert result["monster_type"] == "elemental"


def test_multiline_value():
    text = """monster_description: |\n  This monster is made of magma.\n  It is very hot."""
    result = extract_yaml_block_from_text(text)
    assert "very hot" in result["monster_description"]


def test_list_value():
    text = """monster_abilities:\n  - Eruptive strikes\n  - Resilience"""
    result = extract_yaml_block_from_text(text)
    assert isinstance(result["monster_abilities"], list)
    assert "Eruptive strikes" in result["monster_abilities"]


def test_error_handling():
    text = "monster_name Magma Elemental"  # missing colon
    result = extract_yaml_block_from_text(text)
    assert text == result
