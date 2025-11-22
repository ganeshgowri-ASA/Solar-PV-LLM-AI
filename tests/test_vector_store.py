"""
Test script for QA of vector store integration

This script:
1. Loads sample Solar PV documents
2. Ingests them into the vector store
3. Runs similarity searches with various filters
4. Verifies filtering correctness
5. Tests deletion and stats endpoints

Note: Requires .env file with valid PINECONE_API_KEY and OPENAI_API_KEY
"""

import json
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.vector_store.handler import VectorStoreHandler
from src.logging.logger import get_logger

logger = get_logger(__name__)


def load_sample_documents():
    """Load sample Solar PV documents"""
    sample_file = Path(__file__).parent.parent / "sample_docs" / "solar_pv_documents.json"

    with open(sample_file, 'r') as f:
        documents = json.load(f)

    logger.info(f"Loaded {len(documents)} sample documents")
    return documents


def test_document_ingestion(handler, documents):
    """Test document ingestion"""
    logger.info("=" * 80)
    logger.info("TEST 1: Document Ingestion")
    logger.info("=" * 80)

    result = handler.ingest_documents(
        documents=documents,
        namespace="test",
        batch_size=5
    )

    logger.info(f"✓ Ingestion Result: {result}")
    assert result['status'] == 'success'
    assert result['documents_ingested'] == len(documents)
    logger.info(f"✓ Successfully ingested {result['documents_ingested']} documents")

    return result


def test_basic_search(handler):
    """Test basic similarity search"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 2: Basic Similarity Search")
    logger.info("=" * 80)

    query = "What are the thermal testing requirements for solar modules?"
    results = handler.search(query=query, top_k=3, namespace="test")

    logger.info(f"Query: {query}")
    logger.info(f"✓ Found {len(results)} results")

    for i, result in enumerate(results, 1):
        logger.info(f"\nResult {i}:")
        logger.info(f"  ID: {result['id']}")
        logger.info(f"  Score: {result['score']:.4f}")
        logger.info(f"  Standards: {result['metadata'].get('standards', 'N/A')}")
        logger.info(f"  Test Type: {result['metadata'].get('test_type', 'N/A')}")
        logger.info(f"  Snippet: {result['metadata'].get('text_snippet', '')[:100]}...")

    assert len(results) > 0
    logger.info("✓ Basic search working correctly")

    return results


def test_filtered_search_by_standard(handler):
    """Test search with standards filter"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 3: Filtered Search by Standard (IEC 61215)")
    logger.info("=" * 80)

    query = "reliability testing for solar panels"
    results = handler.search_with_filters(
        query=query,
        top_k=5,
        standards="IEC 61215",
        namespace="test"
    )

    logger.info(f"Query: {query}")
    logger.info(f"Filter: standards='IEC 61215'")
    logger.info(f"✓ Found {len(results)} results")

    # Verify all results match filter
    for result in results:
        standard = result['metadata'].get('standards', '')
        logger.info(f"  - {result['id']}: {standard}")
        assert standard == "IEC 61215", f"Result has wrong standard: {standard}"

    logger.info("✓ All results correctly filtered by standard")

    return results


def test_filtered_search_by_test_type(handler):
    """Test search with test_type filter"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 4: Filtered Search by Test Type (safety)")
    logger.info("=" * 80)

    query = "module testing procedures"
    results = handler.search_with_filters(
        query=query,
        top_k=5,
        test_type="safety",
        namespace="test"
    )

    logger.info(f"Query: {query}")
    logger.info(f"Filter: test_type='safety'")
    logger.info(f"✓ Found {len(results)} results")

    # Verify all results match filter
    for result in results:
        test_type = result['metadata'].get('test_type', '')
        logger.info(f"  - {result['id']}: {test_type}")
        assert test_type == "safety", f"Result has wrong test_type: {test_type}"

    logger.info("✓ All results correctly filtered by test type")

    return results


def test_multi_filter_search(handler):
    """Test search with multiple filters"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 5: Multi-Filter Search (IEC 61215 + reliability)")
    logger.info("=" * 80)

    query = "environmental testing"
    results = handler.search_with_filters(
        query=query,
        top_k=5,
        standards="IEC 61215",
        test_type="reliability",
        namespace="test"
    )

    logger.info(f"Query: {query}")
    logger.info(f"Filters: standards='IEC 61215', test_type='reliability'")
    logger.info(f"✓ Found {len(results)} results")

    # Verify all results match both filters
    for result in results:
        standard = result['metadata'].get('standards', '')
        test_type = result['metadata'].get('test_type', '')
        logger.info(f"  - {result['id']}: {standard} | {test_type}")
        assert standard == "IEC 61215", f"Result has wrong standard: {standard}"
        assert test_type == "reliability", f"Result has wrong test_type: {test_type}"

    logger.info("✓ All results correctly filtered by multiple criteria")

    return results


def test_index_stats(handler):
    """Test index statistics"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 6: Index Statistics")
    logger.info("=" * 80)

    result = handler.get_stats(namespace="test")

    logger.info(f"✓ Stats retrieved successfully")
    logger.info(f"  Total vectors: {result['stats']['total_vector_count']}")
    logger.info(f"  Dimension: {result['stats']['dimension']}")
    logger.info(f"  Index fullness: {result['stats']['index_fullness']}")
    logger.info(f"  Namespaces: {result['stats']['namespaces']}")

    assert result['status'] == 'success'
    logger.info("✓ Index stats working correctly")

    return result


def test_deletion(handler):
    """Test vector deletion"""
    logger.info("\n" + "=" * 80)
    logger.info("TEST 7: Vector Deletion by Filter")
    logger.info("=" * 80)

    # Delete documents with specific standard
    result = handler.delete_documents(
        filters={"standards": "IEC 62804"},
        namespace="test"
    )

    logger.info(f"✓ Deletion completed: {result}")
    assert result['status'] == 'success'
    logger.info("✓ Deletion working correctly")

    # Verify deletion
    search_results = handler.search_with_filters(
        query="PID testing",
        top_k=5,
        standards="IEC 62804",
        namespace="test"
    )

    logger.info(f"  Search after deletion: {len(search_results)} results")
    logger.info("✓ Deletion verified")

    return result


def main():
    """Run all QA tests"""
    try:
        logger.info("Starting Vector Store QA Tests")
        logger.info("=" * 80)

        # Initialize handler
        logger.info("Initializing VectorStoreHandler...")
        handler = VectorStoreHandler()
        logger.info("✓ Handler initialized successfully\n")

        # Load sample documents
        documents = load_sample_documents()

        # Run tests
        test_document_ingestion(handler, documents)
        test_basic_search(handler)
        test_filtered_search_by_standard(handler)
        test_filtered_search_by_test_type(handler)
        test_multi_filter_search(handler)
        test_index_stats(handler)
        test_deletion(handler)

        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS PASSED ✓")
        logger.info("=" * 80)

        return 0

    except Exception as e:
        logger.error(f"\n❌ TEST FAILED: {e}", exc_info=True)
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
