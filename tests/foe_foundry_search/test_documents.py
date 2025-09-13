"""Tests for foe_foundry_search.documents module."""

from foe_foundry_search.documents.load import iter_documents


class TestDocuments:
    """Test class for document loading functionality."""

    def test_iter_documents_count(self):
        """Test that iter_documents() returns more than 100 documents."""
        # Count the total number of documents
        document_count = sum(1 for _ in iter_documents())

        # Assert that we have more than 100 documents
        assert (
            document_count > 100
        ), f"Expected more than 100 documents, but got {document_count}"

        # Print the actual count for debugging purposes
        print(f"Total documents found: {document_count}")

    def test_iter_documents_not_empty(self):
        """Test that iter_documents() returns at least one document."""
        documents = list(iter_documents())
        assert len(documents) > 0, "Expected at least one document"

    def test_iter_documents_yields_valid_documents(self):
        """Test that iter_documents() yields valid Document objects."""
        documents = list(iter_documents())

        # Check that we have documents
        assert len(documents) > 0, "Expected at least one document"

        # Check the first document has required attributes
        first_doc = documents[0]
        assert hasattr(first_doc, "doc_id"), "Document should have doc_id attribute"
        assert hasattr(first_doc, "doc_type"), "Document should have doc_type attribute"
        assert hasattr(first_doc, "name"), "Document should have name attribute"
        assert hasattr(first_doc, "content"), "Document should have content attribute"

        # Check that doc_id is not empty
        assert first_doc.doc_id, "Document doc_id should not be empty"
        assert first_doc.name, "Document name should not be empty"
        assert first_doc.content, "Document content should not be empty"
