"""
Example usage of the Solar PV LLM AI Vector Store

This script demonstrates:
1. How to use the VectorStoreHandler directly
2. Common operations: ingest, search, filter, delete, stats
3. Best practices for Solar PV document management

Note: Requires .env file with valid API keys
"""

from src.vector_store.handler import VectorStoreHandler
from src.logging.logger import get_logger

logger = get_logger(__name__)


def example_document_ingestion():
    """Example: Ingest Solar PV documents"""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Document Ingestion")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Prepare documents with Solar PV metadata
    documents = [
        {
            "text": (
                "The thermal cycling test (MQT 11) in IEC 61215 subjects PV modules "
                "to 200 thermal cycles between -40°C and +85°C to assess thermal "
                "stress resistance."
            ),
            "metadata": {
                "standards": "IEC 61215",
                "clauses": ["MQT 11"],
                "test_type": "reliability",
                "category": "thermal_testing",
                "source": "IEC 61215 Documentation"
            }
        },
        {
            "text": (
                "Hot spot endurance testing (MST 09) in IEC 61730 evaluates the "
                "module's ability to withstand heating effects from reverse current "
                "in shaded cells to ensure no fire hazard occurs."
            ),
            "metadata": {
                "standards": "IEC 61730",
                "clauses": ["MST 09"],
                "test_type": "safety",
                "category": "electrical_safety",
                "source": "IEC 61730 Documentation"
            }
        }
    ]

    # Ingest documents
    result = handler.ingest_documents(
        documents=documents,
        namespace="examples"
    )

    print(f"\n✓ Ingested {result['documents_ingested']} documents")
    print(f"  Namespace: {result['namespace']}")
    print(f"  Batches: {result['batches_processed']}")


def example_basic_search():
    """Example: Basic similarity search"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Basic Similarity Search")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Perform basic search
    query = "What are the temperature cycling requirements?"
    results = handler.search(
        query=query,
        top_k=3,
        namespace="examples"
    )

    print(f"\nQuery: {query}")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  Score: {result['score']:.4f}")
        print(f"  Standard: {result['metadata'].get('standards')}")
        print(f"  Test Type: {result['metadata'].get('test_type')}")
        print(f"  Snippet: {result['metadata'].get('text_snippet', '')[:80]}...")
        print()


def example_filtered_search():
    """Example: Search with Solar PV filters"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Filtered Search")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Search with standard and test type filters
    query = "safety testing procedures"
    results = handler.search_with_filters(
        query=query,
        top_k=5,
        standards="IEC 61730",  # Only IEC 61730 standard
        test_type="safety",      # Only safety tests
        namespace="examples"
    )

    print(f"\nQuery: {query}")
    print(f"Filters: standards='IEC 61730', test_type='safety'")
    print(f"Found {len(results)} results:\n")

    for i, result in enumerate(results, 1):
        print(f"Result {i}:")
        print(f"  ID: {result['id']}")
        print(f"  Score: {result['score']:.4f}")
        print(f"  Standard: {result['metadata'].get('standards')}")
        print(f"  Clauses: {result['metadata'].get('clauses')}")
        print()


def example_index_stats():
    """Example: Get index statistics"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Index Statistics")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Get stats for namespace
    result = handler.get_stats(namespace="examples")

    stats = result['stats']
    print(f"\nIndex Statistics:")
    print(f"  Total Vectors: {stats['total_vector_count']}")
    print(f"  Dimension: {stats['dimension']}")
    print(f"  Index Fullness: {stats['index_fullness']:.2%}")
    print(f"\nNamespace Breakdown:")
    for ns, ns_stats in stats.get('namespaces', {}).items():
        print(f"  {ns}: {ns_stats['vector_count']} vectors")


def example_advanced_filtering():
    """Example: Advanced filtering with multiple criteria"""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Advanced Multi-Filter Search")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Search with multiple filters
    query = "module testing under stress"
    results = handler.search_with_filters(
        query=query,
        top_k=10,
        standards="IEC 61215",
        clauses=["MQT 11", "MQT 12"],  # Multiple clauses
        test_type="reliability",
        namespace="examples"
    )

    print(f"\nQuery: {query}")
    print(f"Filters:")
    print(f"  - standards: IEC 61215")
    print(f"  - clauses: MQT 11, MQT 12")
    print(f"  - test_type: reliability")
    print(f"\nFound {len(results)} results")


def example_delete_operations():
    """Example: Delete vectors"""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Delete Operations")
    print("=" * 80)

    handler = VectorStoreHandler()

    # Delete by filter
    result = handler.delete_documents(
        filters={"test_type": "safety"},
        namespace="examples"
    )

    print(f"\nDeletion completed:")
    print(f"  {result['deletion_info']}")

    # Get stats after deletion
    stats_result = handler.get_stats(namespace="examples")
    print(f"\nRemaining vectors: {stats_result['stats']['total_vector_count']}")


def main():
    """Run all examples"""
    print("\n" + "=" * 80)
    print("Solar PV LLM AI - Vector Store Usage Examples")
    print("=" * 80)

    try:
        example_document_ingestion()
        example_basic_search()
        example_filtered_search()
        example_index_stats()
        example_advanced_filtering()

        # Uncomment to test deletion (will remove vectors!)
        # example_delete_operations()

        print("\n" + "=" * 80)
        print("All examples completed successfully! ✓")
        print("=" * 80)
        print("\nNext steps:")
        print("1. Check the API docs at http://localhost:8000/docs")
        print("2. Run the QA test suite: python tests/test_vector_store.py")
        print("3. Review VECTOR_STORE_INTEGRATION.md for detailed documentation")
        print()

    except Exception as e:
        logger.error(f"Example failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print("\nMake sure:")
        print("1. .env file is configured with valid API keys")
        print("2. Pinecone and OpenAI services are accessible")
        print("3. Dependencies are installed: pip install -r requirements.txt")


if __name__ == "__main__":
    main()
