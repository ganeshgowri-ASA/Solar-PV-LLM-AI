"""
Basic usage example for RAG engine.

This example demonstrates:
1. Creating documents
2. Initializing the RAG pipeline
3. Adding documents
4. Querying with different retrieval methods
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
from src.rag_engine.utils.data_models import Document
from config.rag_config import RAGConfig, RetrievalConfig, VectorStoreConfig


def create_sample_documents():
    """Create sample documents about solar PV systems."""
    return [
        Document(
            id="doc1",
            content=(
                "Solar photovoltaic (PV) panels convert sunlight directly into "
                "electricity using semiconductor materials. The most common type "
                "uses silicon-based cells that create an electric field when "
                "exposed to light."
            ),
            metadata={
                "source": "solar_basics.pdf",
                "page": 1,
                "topic": "fundamentals",
                "date": "2024-01-15"
            }
        ),
        Document(
            id="doc2",
            content=(
                "The efficiency of solar panels typically ranges from 15% to 22% "
                "for residential applications. Premium monocrystalline panels can "
                "achieve efficiency rates above 22%, while polycrystalline panels "
                "usually range from 15% to 17%."
            ),
            metadata={
                "source": "efficiency_guide.pdf",
                "page": 3,
                "topic": "performance"
            }
        ),
        Document(
            id="doc3",
            content=(
                "Solar panel installation requires proper roof orientation, ideally "
                "facing south in the northern hemisphere with minimal shading. The "
                "optimal tilt angle depends on latitude and seasonal considerations."
            ),
            metadata={
                "source": "installation_manual.pdf",
                "page": 5,
                "topic": "installation"
            }
        ),
        Document(
            id="doc4",
            content=(
                "Inverters are critical components that convert DC electricity from "
                "solar panels into AC electricity for home use. String inverters, "
                "microinverters, and power optimizers each have distinct advantages."
            ),
            metadata={
                "source": "components.pdf",
                "page": 2,
                "topic": "equipment"
            }
        ),
        Document(
            id="doc5",
            content=(
                "Solar energy systems can significantly reduce electricity bills, "
                "lower carbon footprint, and increase property value. Many regions "
                "offer tax incentives and rebates for solar installations."
            ),
            metadata={
                "source": "benefits.pdf",
                "page": 1,
                "topic": "economics"
            }
        ),
    ]


def main():
    """Run basic RAG pipeline example."""
    print("=" * 80)
    print("RAG Engine - Basic Usage Example")
    print("=" * 80)

    # 1. Create configuration
    print("\n1. Initializing RAG pipeline...")
    config = RAGConfig(
        retrieval=RetrievalConfig(
            top_k=10,
            top_k_rerank=3,
            hybrid_alpha=0.5,  # Equal weight to vector and BM25
            use_hyde=False
        ),
        vector_store=VectorStoreConfig(
            store_type="chromadb",
            store_path=Path("./data/vector_store_example"),
            collection_name="solar_pv_docs"
        )
    )

    # Initialize pipeline
    pipeline = RAGPipeline(config=config)
    print("   ✓ Pipeline initialized")

    # 2. Add documents
    print("\n2. Adding sample documents...")
    documents = create_sample_documents()
    pipeline.add_documents(documents)
    print(f"   ✓ Added {len(documents)} documents")

    # 3. Get pipeline statistics
    print("\n3. Pipeline Statistics:")
    stats = pipeline.get_stats()
    print(f"   - Vector store documents: {stats['vector_store']['document_count']}")
    print(f"   - BM25 documents: {stats['bm25']['document_count']}")
    print(f"   - Embedding model: {stats['vector_store']['embedding_model']}")

    # 4. Example queries
    queries = [
        "How efficient are solar panels?",
        "What is the best way to install solar panels?",
        "What are the benefits of solar energy?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\n{'-' * 80}")
        print(f"Query {i}: {query}")
        print('-' * 80)

        # Vector retrieval
        print("\n   A. Vector Retrieval:")
        results = pipeline.retrieve(
            query=query,
            top_k=2,
            retrieval_method="vector",
            use_reranker=False
        )
        for j, result in enumerate(results, 1):
            print(f"      [{j}] Score: {result.score:.4f}")
            print(f"          {result.document.content[:100]}...")
            print(f"          (Source: {result.document.metadata.get('source', 'unknown')})")

        # BM25 retrieval
        print("\n   B. BM25 Retrieval:")
        results = pipeline.retrieve(
            query=query,
            top_k=2,
            retrieval_method="bm25",
            use_reranker=False
        )
        for j, result in enumerate(results, 1):
            print(f"      [{j}] Score: {result.score:.4f}")
            print(f"          {result.document.content[:100]}...")
            print(f"          (Source: {result.document.metadata.get('source', 'unknown')})")

        # Hybrid retrieval
        print("\n   C. Hybrid Retrieval (RRF):")
        results = pipeline.retrieve(
            query=query,
            top_k=2,
            retrieval_method="hybrid",
            use_reranker=False
        )
        for j, result in enumerate(results, 1):
            print(f"      [{j}] Score: {result.score:.4f}")
            print(f"          {result.document.content[:100]}...")
            print(f"          (Source: {result.document.metadata.get('source', 'unknown')})")

    # 5. Create formatted context
    print(f"\n{'-' * 80}")
    print("Creating RAG Context")
    print('-' * 80)

    test_query = "How do solar panels work and what is their efficiency?"
    context = pipeline.create_context(
        query=test_query,
        top_k=3,
        retrieval_method="hybrid",
        use_reranker=False
    )

    print(f"\nQuery: {context.query}")
    print(f"\nRetrieved {len(context.retrieved_docs)} documents:")
    print("\nFormatted Context:")
    print(context.context_text)

    print("\n" + "=" * 80)
    print("Example completed successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()
