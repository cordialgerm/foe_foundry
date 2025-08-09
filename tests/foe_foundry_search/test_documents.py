"""Unit tests for foe_foundry_search.documents module.

These tests work with the actual data files in the repository to ensure
the document loading functionality works correctly with real data.
"""

from pathlib import Path

from foe_foundry import CreatureType, DamageType, MonsterRole
from foe_foundry_search.documents import (
    MonsterDocument,
    MonsterDocumentMeta,
    iter_monster_doc_metas,
    iter_monster_docs,
    load_monster_doc_metas,
    load_monster_docs,
)
from foe_foundry_search.documents.load import (
    _cleanup_damage_types,
    _cleanup_role,
    _cleanup_subtypes,
)


class TestMonsterDocument:
    """Test MonsterDocument class."""

    def test_monster_document_creation(self):
        """Test creating a MonsterDocument instance."""
        path = Path("/test/path/aboleth_description.txt")
        monster_key = "aboleth"
        text = "A fearsome aberration that lives in dark waters."

        doc = MonsterDocument(path=path, monster_key=monster_key, text=text)

        assert doc.path == path
        assert doc.monster_key == monster_key
        assert doc.text == text

    def test_monster_document_with_special_characters(self):
        """Test MonsterDocument with special characters in text."""
        path = Path("/test/path/troll_description.txt")
        monster_key = "troll"
        text = (
            "A large, regenerating creature with claws & fangs. It's quite dangerous!"
        )

        doc = MonsterDocument(path=path, monster_key=monster_key, text=text)

        assert doc.monster_key == monster_key
        assert "claws & fangs" in doc.text
        assert "It's quite dangerous!" in doc.text


class TestMonsterDocumentMeta:
    """Test MonsterDocumentMeta class."""

    def test_monster_document_meta_creation(self):
        """Test creating a MonsterDocumentMeta instance with minimal required fields."""
        meta = MonsterDocumentMeta(
            key="aboleth",
            name="Aboleth",
            size="Large",
            srd=True,
            path=Path("/test/aboleth.json"),
            creature_type=CreatureType.Aberration,
            creature_subtypes=[],
            damage_types=[DamageType.Psychic],
            alignment="lawful evil",
            cr="10",
            ac=17,
            hp=135,
            movement="10 ft., swim 40 ft.",
            role="Controller",
            tags=["aquatic", "telepathic"],
            adjectives=["ancient", "malevolent"],
            description="A powerful aberration",
            memorable="Its tentacles and psychic powers",
            goals="Dominate lesser creatures",
            relations="Commands fish and aquatic life",
            environment="Underground lakes and seas",
            strengths="Psychic abilities and aquatic mobility",
            weaknesses="Vulnerable when out of water",
            attacks="Tentacle slam, mucus cloud",
            most_powerful_ability="Enslave ability",
            additional_information=["Legendary creature", "Can create illusions"],
            senses="Darkvision 120 ft.",
            skills="History +12, Perception +10",
            spellcasting="None",
            test_queries=["What is an aboleth?", "How do aboleths fight?"],
        )

        assert meta.key == "aboleth"
        assert meta.name == "Aboleth"
        assert meta.creature_type == CreatureType.Aberration
        assert DamageType.Psychic in meta.damage_types
        assert meta.cr == "10"

    def test_cr_numeric_fraction(self):
        """Test cr_numeric property with fractional CR."""
        meta = MonsterDocumentMeta(
            key="kobold",
            name="Kobold",
            size="Small",
            srd=True,
            path=Path("/test/kobold.json"),
            creature_type=CreatureType.Humanoid,
            creature_subtypes=["kobold"],
            damage_types=[],
            alignment="lawful evil",
            cr="1/4",
            ac=12,
            hp=5,
            movement="30 ft.",
            role=None,
            tags=[],
            adjectives=[],
            description="Small draconic humanoid",
            memorable="Pack tactics",
            goals="Serve dragons",
            relations="Works in groups",
            environment="Caves and underground",
            strengths="Numbers and traps",
            weaknesses="Low individual power",
            attacks="Dagger, sling",
            most_powerful_ability="Pack Tactics",
            additional_information=[],
            senses=None,
            skills=None,
            spellcasting=None,
            test_queries=[],
        )

        assert meta.cr_numeric == 0.25

    def test_cr_numeric_whole_number(self):
        """Test cr_numeric property with whole number CR."""
        meta = MonsterDocumentMeta(
            key="dragon",
            name="Ancient Red Dragon",
            size="Gargantuan",
            srd=True,
            path=Path("/test/dragon.json"),
            creature_type=CreatureType.Dragon,
            creature_subtypes=[],
            damage_types=[DamageType.Fire],
            alignment="chaotic evil",
            cr="24",
            ac=22,
            hp=546,
            movement="40 ft., climb 40 ft., fly 80 ft.",
            role="Solo",
            tags=[],
            adjectives=[],
            description="Massive red dragon",
            memorable="Devastating fire breath",
            goals="Hoard treasure",
            relations="Rules over lesser creatures",
            environment="Volcanic mountains",
            strengths="Immense power and magic",
            weaknesses="Arrogance",
            attacks="Bite, claw, fire breath",
            most_powerful_ability="Fire Breath",
            additional_information=[],
            senses=None,
            skills=None,
            spellcasting=None,
            test_queries=[],
        )

        assert meta.cr_numeric == 24.0


class TestActualDataLoading:
    """Test loading with actual data files (integration tests)."""

    def test_load_real_documents(self):
        """Test loading actual document files from the filesystem."""
        documents = load_monster_docs()

        # Should have a significant number of documents
        assert len(documents) >= 100, (
            f"Expected at least 100 documents, got {len(documents)}"
        )

        # All should be MonsterDocument instances
        for doc in documents.values():
            assert isinstance(doc, MonsterDocument)
            assert doc.monster_key
            assert doc.text
            assert doc.path.exists()

    def test_load_real_document_metas(self):
        """Test loading actual metadata files from the filesystem."""
        metas = load_monster_doc_metas()

        # Should have a significant number of metadata entries
        assert len(metas) >= 100, (
            f"Expected at least 100 metadata entries, got {len(metas)}"
        )

        # All should be MonsterDocumentMeta instances
        for meta in metas.values():
            assert isinstance(meta, MonsterDocumentMeta)
            assert meta.name
            assert meta.key
            assert meta.creature_type
            assert meta.path.exists()

    def test_iter_real_documents(self):
        """Test iterating over actual documents."""
        documents = list(iter_monster_docs())

        # Should have documents
        assert len(documents) >= 100

        # Check a sample of documents
        sample_size = min(20, len(documents))
        for doc in documents[:sample_size]:
            assert isinstance(doc, MonsterDocument)
            assert doc.monster_key
            assert len(doc.text) > 0
            assert doc.path.suffix == ".txt"

            # Verify the text is meaningful
            assert len(doc.text.strip()) > 10  # Should have substantial content

    def test_iter_real_document_metas(self):
        """Test iterating over actual metadata."""
        metas = list(iter_monster_doc_metas())

        # Should have metadata
        assert len(metas) >= 100

        # Check a sample of metadata
        sample_size = min(20, len(metas))
        for meta in metas[:sample_size]:
            assert isinstance(meta, MonsterDocumentMeta)
            assert meta.name
            assert meta.key
            assert meta.creature_type in CreatureType
            assert meta.cr_numeric >= 0
            assert meta.path.suffix == ".json"

    def test_document_cache_consistency(self):
        """Test that cached loading returns the same results."""
        # Load twice
        docs1 = load_monster_docs()
        docs2 = load_monster_docs()

        # Should be the same object (cached)
        assert docs1 is docs2

        # Same for metas
        metas1 = load_monster_doc_metas()
        metas2 = load_monster_doc_metas()

        assert metas1 is metas2

    def test_key_consistency(self):
        """Test that document keys are consistent between docs and metas."""
        docs = load_monster_docs()
        metas = load_monster_doc_metas()

        # Check that keys have consistent monster_key/key values
        for key in list(docs.keys())[:20]:  # Check first 20 for speed
            assert docs[key].monster_key == key

        for key in list(metas.keys())[:20]:  # Check first 20 for speed
            assert metas[key].key == key

    def test_document_content_quality(self):
        """Test that documents have meaningful content."""
        documents = list(iter_monster_docs())

        # Test a sample of documents
        sample_size = min(25, len(documents))
        for doc in documents[:sample_size]:
            # Content should be substantial
            assert len(doc.text) > 50, f"Document {doc.monster_key} has very short text"

            # Should contain alphabetic characters (not just symbols)
            assert any(c.isalpha() for c in doc.text), (
                f"Document {doc.monster_key} has no alphabetic characters"
            )

            # Verify the key extraction worked correctly
            expected_suffixes = [
                "_additional_info",
                "_background",
                "_description",
                "_skills",
            ]
            filename_stem = doc.path.stem
            assert any(
                filename_stem.endswith(suffix) for suffix in expected_suffixes
            ), (
                f"Document {doc.monster_key} filename {filename_stem} doesn't end with expected suffix"
            )

    def test_metadata_content_quality(self):
        """Test that metadata has meaningful content."""
        metas = list(iter_monster_doc_metas())

        # Test a sample of metadata
        sample_size = min(25, len(metas))
        for meta in metas[:sample_size]:
            # Basic required fields
            assert len(meta.name) > 0
            assert len(meta.key) > 0
            assert meta.hp > 0
            assert meta.ac > 0

            # CR should be valid
            cr_numeric = meta.cr_numeric
            assert 0 <= cr_numeric <= 30, (
                f"CR {cr_numeric} for {meta.name} is out of expected range"
            )

            # Creature type should be valid
            assert isinstance(meta.creature_type, CreatureType)

            # Size should be a valid D&D size
            valid_sizes = {"tiny", "small", "medium", "large", "huge", "gargantuan"}
            assert meta.size.lower() in valid_sizes, (
                f"Invalid size '{meta.size}' for {meta.name}"
            )

    def test_specific_known_monsters(self):
        """Test loading of specific well-known monsters."""
        metas = load_monster_doc_metas()

        # Test if we can find some common D&D monsters
        # Note: We don't know exactly which monsters are in the dataset,
        # but we can test the structure if any are found
        if "aboleth" in metas:
            aboleth = metas["aboleth"]
            assert aboleth.name == "Aboleth"
            assert aboleth.creature_type == CreatureType.Aberration

        if "troll" in metas:
            troll = metas["troll"]
            assert "troll" in troll.name.lower()

        # Just verify we have some monsters with different creature types
        creature_types_found = {
            meta.creature_type for meta in list(metas.values())[:50]
        }
        assert len(creature_types_found) >= 3, (
            "Should have monsters of multiple creature types"
        )


class TestCleanupFunctions:
    """Test the utility cleanup functions."""

    def test_cleanup_role(self):
        """Test role cleanup function."""
        # Test None/empty cases
        assert _cleanup_role(None) is None
        assert _cleanup_role("none") is None
        assert _cleanup_role("UNKNOWN") is None
        assert _cleanup_role("null") is None

        # Test support mapping
        assert _cleanup_role("support") == MonsterRole.Support
        assert _cleanup_role("supporter") == MonsterRole.Support

        # Test controller mappings
        assert _cleanup_role("hindering enemy") == MonsterRole.Controller
        assert _cleanup_role("disruptor") == MonsterRole.Controller
        assert _cleanup_role("manipulator") == MonsterRole.Controller

        # Test direct parsing for valid roles
        assert _cleanup_role("artillery") == MonsterRole.Artillery
        assert _cleanup_role("controller") == MonsterRole.Controller

    def test_cleanup_damage_types(self):
        """Test damage type cleanup function."""
        # Test None case
        assert _cleanup_damage_types(None) == []

        # Test string input with valid damage types (using lowercase as they appear in enum)
        result = _cleanup_damage_types("fire, cold, lightning")
        assert DamageType.Fire in result
        assert DamageType.Cold in result
        assert DamageType.Lightning in result

        # Test list input
        result = _cleanup_damage_types(["fire", "psychic"])
        assert DamageType.Fire in result
        assert DamageType.Psychic in result

        # Test filtering of invalid types
        result = _cleanup_damage_types(["fire", "none", "unknown", "psychic"])
        assert DamageType.Fire in result
        assert DamageType.Psychic in result
        assert len(result) == 2  # Should filter out "none" and "unknown"

    def test_cleanup_subtypes(self):
        """Test subtype cleanup function."""
        # Test None case
        assert _cleanup_subtypes(None) is None

        # Test string input
        result = _cleanup_subtypes("kobold, draconic, small")
        assert result == ["kobold", "draconic", "small"]

        # Test list input
        result = _cleanup_subtypes(["elf", "noble"])
        assert result == ["elf", "noble"]

        # Test trimming whitespace
        result = _cleanup_subtypes("  human  ,  fighter  ")
        assert result == ["human", "fighter"]


class TestDocumentValidation:
    """Test validation of loaded documents and metadata."""

    def test_all_documents_have_required_fields(self):
        """Test that all loaded documents have required fields."""
        documents = load_monster_docs()

        # Test a reasonable sample
        sample_keys = list(documents.keys())[:25]
        for key in sample_keys:
            doc = documents[key]
            assert doc.path is not None
            assert doc.monster_key is not None
            assert doc.text is not None
            assert len(doc.text) > 0
            assert doc.monster_key == key

    def test_all_metas_have_required_fields(self):
        """Test that all loaded metadata have required fields."""
        metas = load_monster_doc_metas()

        # Test a reasonable sample
        sample_keys = list(metas.keys())[:25]
        for key in sample_keys:
            meta = metas[key]
            assert meta.name is not None
            assert meta.key is not None
            assert meta.creature_type is not None
            assert meta.cr is not None
            assert meta.hp > 0
            assert meta.ac > 0
            assert meta.key == key
            assert isinstance(meta.creature_type, CreatureType)

    def test_damage_types_are_valid(self):
        """Test that all damage types in metadata are valid."""
        metas = load_monster_doc_metas()

        # Test a sample
        sample_metas = list(metas.values())[:25]
        for meta in sample_metas:
            for damage_type in meta.damage_types:
                assert isinstance(damage_type, DamageType)

    def test_cr_values_are_valid(self):
        """Test that CR values are valid and can be converted to numeric."""
        metas = load_monster_doc_metas()

        # Test a sample
        sample_metas = list(metas.values())[:25]
        for meta in sample_metas:
            # Should be able to get numeric CR without error
            cr_numeric = meta.cr_numeric
            assert isinstance(cr_numeric, float)
            assert cr_numeric >= 0
            assert cr_numeric <= 30  # Reasonable upper bound for D&D CRs

    def test_data_counts_meet_expectations(self):
        """Test that we have the expected amount of data."""
        documents = load_monster_docs()
        metas = load_monster_doc_metas()

        # Based on our testing, we should have:
        # - Over 300 document files (we actually have 322)
        # - Over 2000 metadata files (we actually have 2204)
        assert len(documents) >= 300, (
            f"Expected at least 300 documents, got {len(documents)}"
        )
        assert len(metas) >= 2000, (
            f"Expected at least 2000 metadata entries, got {len(metas)}"
        )

        # The document count should be significantly lower than metadata count
        # since each monster has multiple document types but one metadata entry
        assert len(metas) > len(documents) * 3, (
            f"Expected more metadata entries than documents, got {len(metas)} vs {len(documents)}"
        )
