"""
Advanced usage example for RAG engine.

This example demonstrates:
1. Using HyDE for query enhancement
2. Re-ranking with cross-encoder
3. Custom configuration
4. Advanced retrieval options
"""

import sys
from pathlib import Path
import os

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.rag_engine.pipeline.rag_pipeline import RAGPipeline
from src.rag_engine.utils.data_models import Document
from src.rag_engine.embeddings.hyde import HyDE
from src.rag_engine.reranking.reranker import CrossEncoderReranker
from config.rag_config import RAGConfig, RetrievalConfig, VectorStoreConfig, RerankerConfig, HyDEConfig


def create_extended_documents():
    """Create extended set of documents about solar PV systems."""
    return [
        Document(
            id="doc1",
            content=(
                "Monocrystalline solar panels are made from a single crystal structure, "
                "offering higher efficiency (20-22%) and better performance in low light "
                "conditions. They have a distinctive black appearance and are more "
                "expensive than polycrystalline alternatives."
            ),
            metadata={"source": "panel_types.pdf", "topic": "technology", "year": 2024}
        ),
        Document(
            id="doc2",
            content=(
                "Polycrystalline solar panels are manufactured from multiple silicon "
                "crystals melted together. They typically achieve 15-17% efficiency, "
                "have a blue appearance, and are more affordable. They perform slightly "
                "less efficiently in high temperatures."
            ),
            metadata={"source": "panel_types.pdf", "topic": "technology", "year": 2024}
        ),
        Document(
            id="doc3",
            content=(
                "Thin-film solar panels use layers of photovoltaic material deposited "
                "on a substrate. While they have lower efficiency (10-12%), they are "
                "flexible, lightweight, and perform better in high temperatures and "
                "partial shading conditions."
            ),
            metadata={"source": "panel_types.pdf", "topic": "technology", "year": 2024}
        ),
        Document(
            id="doc4",
            content=(
                "Maximum Power Point Tracking (MPPT) is a technique used by solar "
                "inverters to maximize power output. MPPT continuously adjusts the "
                "electrical operating point to extract maximum available power from "
                "solar panels under varying conditions."
            ),
            metadata={"source": "inverter_tech.pdf", "topic": "equipment", "year": 2024}
        ),
        Document(
            id="doc5",
            content=(
                "Battery storage systems for solar installations typically use lithium-ion "
                "technology. Popular options include Tesla Powerwall, LG Chem RESU, and "
                "Enphase batteries. Storage capacity ranges from 5 kWh to 20+ kWh for "
                "residential systems."
            ),
            metadata={"source": "energy_storage.pdf", "topic": "storage", "year": 2024}
        ),
        Document(
            id="doc6",
            content=(
                "Net metering allows solar system owners to send excess electricity to "
                "the grid in exchange for credits. These credits offset electricity drawn "
                "from the grid at night or during low production periods, significantly "
                "improving ROI."
            ),
            metadata={"source": "grid_integration.pdf", "topic": "economics", "year": 2024}
        ),
        Document(
            id="doc7",
            content=(
                "Solar panel degradation is typically 0.5-1% per year. Quality panels "
                "often come with 25-year performance warranties guaranteeing 80-85% of "
                "original output after 25 years. Regular maintenance and cleaning can "
                "minimize degradation."
            ),
            metadata={"source": "maintenance.pdf", "topic": "performance", "year": 2024}
        ),
        Document(
            id="doc8",
            content=(
                "The levelized cost of energy (LCOE) for solar PV has decreased by over "
                "90% since 2010. In many regions, new solar installations are now cheaper "
                "than fossil fuel alternatives, making solar the most cost-effective "
                "energy source."
            ),
            metadata={"source": "economics.pdf", "topic": "economics", "year": 2024}
        ),
    ]


def example_with_hyde():
    """Example using HyDE for query enhancement."""
    print("\n" + "=" * 80)
    print("Example 1: Using HyDE (Hypothetical Document Embeddings)")
    print("=" * 80)

    # Note: This requires OPENAI_API_KEY environment variable
    if not os.getenv("OPENAI_API_KEY"):
        print("⚠ Skipping HyDE example (OPENAI_API_KEY not set)")
        return

    config = RAGConfig(
        retrieval=RetrievalConfig(top_k=5, top_k_rerank=3),
        vector_store=VectorStoreConfig(
            store_type="chromadb",
            store_path=Path("./data/vector_store_advanced"),
        ),
        hyde=HyDEConfig(
            enabled=True,
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            llm_model="gpt-3.5-turbo"
        )
    )

    pipeline = RAGPipeline(config=config)
    documents = create_extended_documents()
    pipeline.add_documents(documents)

    query = "cost effectiveness of solar"

    print(f"\nOriginal Query: {query}")

    # Without HyDE
    print("\n1. Standard Retrieval:")
    results_standard = pipeline.retrieve(
        query=query,
        top_k=3,
        retrieval_method="hybrid",
        use_hyde=False,
        use_reranker=False
    )
    for i, result in enumerate(results_standard, 1):
        print(f"   [{i}] {result.document.content[:80]}...")

    # With HyDE
    print("\n2. With HyDE Enhancement:")
    results_hyde = pipeline.retrieve(
        query=query,
        top_k=3,
        retrieval_method="hybrid",
        use_hyde=True,
        use_reranker=False
    )
    for i, result in enumerate(results_hyde, 1):
        print(f"   [{i}] {result.document.content[:80]}...")


def example_with_reranking():
    """Example using cross-encoder re-ranking."""
    print("\n" + "=" * 80)
    print("Example 2: Using Cross-Encoder Re-ranking")
    print("=" * 80)

    config = RAGConfig(
        retrieval=RetrievalConfig(top_k=8, top_k_rerank=3),
        vector_store=VectorStoreConfig(
            store_type="chromadb",
            store_path=Path("./data/vector_store_advanced"),
        ),
        reranker=RerankerConfig(
            reranker_type="cross-encoder",
            cross_encoder_model="cross-encoder/ms-marco-MiniLM-L-6-v2"
        )
    )

    # Initialize with cross-encoder reranker
    reranker = CrossEncoderReranker(model_name=config.reranker.cross_encoder_model)
    pipeline = RAGPipeline(config=config, reranker=reranker)

    documents = create_extended_documents()
    pipeline.add_documents(documents)

    query = "What type of solar panel is most efficient?"

    print(f"\nQuery: {query}")

    # Without re-ranking
    print("\n1. Before Re-ranking (top 8 from hybrid retrieval):")
    results_before = pipeline.retrieve(
        query=query,
        top_k=8,
        retrieval_method="hybrid",
        use_reranker=False
    )
    for i, result in enumerate(results_before[:5], 1):
        print(f"   [{i}] Score: {result.score:.4f}")
        print(f"       {result.document.content[:80]}...")

    # With re-ranking
    print("\n2. After Cross-Encoder Re-ranking (top 3):")
    results_after = pipeline.retrieve(
        query=query,
        top_k=8,
        retrieval_method="hybrid",
        use_reranker=True
    )
    for i, result in enumerate(results_after, 1):
        print(f"   [{i}] Score: {result.score:.4f}")
        print(f"       {result.document.content[:80]}...")


def example_comparison():
    """Compare different retrieval strategies."""
    print("\n" + "=" * 80)
    print("Example 3: Comparing Retrieval Strategies")
    print("=" * 80)

    config = RAGConfig(
        retrieval=RetrievalConfig(top_k=5),
        vector_store=VectorStoreConfig(
            store_type="chromadb",
            store_path=Path("./data/vector_store_advanced"),
        )
    )

    pipeline = RAGPipeline(config=config)
    documents = create_extended_documents()
    pipeline.add_documents(documents)

    query = "battery storage for solar systems"

    print(f"\nQuery: {query}\n")

    strategies = [
        ("Vector Only", "vector", 0.5),
        ("BM25 Only", "bm25", 0.5),
        ("Hybrid (α=0.3)", "hybrid", 0.3),  # Favor BM25
        ("Hybrid (α=0.5)", "hybrid", 0.5),  # Equal weight
        ("Hybrid (α=0.7)", "hybrid", 0.7),  # Favor vector
    ]

    for name, method, alpha in strategies:
        print(f"{name}:")

        # Update alpha if using hybrid
        if method == "hybrid":
            pipeline.hybrid_retriever.alpha = alpha

        results = pipeline.retrieve(
            query=query,
            top_k=3,
            retrieval_method=method,
            use_reranker=False
        )

        for i, result in enumerate(results, 1):
            print(f"   [{i}] Score: {result.score:.4f}")
            print(f"       {result.document.content[:70]}...")
        print()


def main():
    """Run advanced examples."""
    print("=" * 80)
    print("RAG Engine - Advanced Usage Examples")
    print("=" * 80)

    # Example 1: HyDE (requires OpenAI API key)
    example_with_hyde()

    # Example 2: Cross-encoder re-ranking
    example_with_reranking()

    # Example 3: Strategy comparison
    example_comparison()

    print("\n" + "=" * 80)
    print("Advanced examples completed!")
    print("=" * 80)


if __name__ == "__main__":
    main()
