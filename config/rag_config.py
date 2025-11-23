"""Configuration settings for RAG engine."""
from typing import Literal, Optional
from pydantic import BaseModel, Field
from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()


class RetrievalConfig(BaseModel):
    """Configuration for retrieval components."""

    top_k: int = Field(default=10, description="Number of documents to retrieve")
    top_k_rerank: int = Field(default=5, description="Number of documents after re-ranking")
    hybrid_alpha: float = Field(default=0.5, ge=0.0, le=1.0,
                                description="Weight for semantic search (1-alpha for BM25)")
    use_hyde: bool = Field(default=False, description="Enable HyDE technique")


class VectorStoreConfig(BaseModel):
    """Configuration for vector store."""

    store_type: Literal["chromadb", "faiss"] = Field(default="chromadb")
    store_path: Path = Field(default=Path("./data/vector_store"))
    embedding_model: str = Field(default="sentence-transformers/all-MiniLM-L6-v2")
    collection_name: str = Field(default="solar_pv_docs")


class RerankerConfig(BaseModel):
    """Configuration for re-ranking."""

    reranker_type: Literal["cohere", "cross-encoder", "none"] = Field(default="cohere")
    cohere_api_key: Optional[str] = Field(default=None)
    cross_encoder_model: str = Field(default="cross-encoder/ms-marco-MiniLM-L-6-v2")


class HyDEConfig(BaseModel):
    """Configuration for HyDE (Hypothetical Document Embeddings)."""

    enabled: bool = Field(default=False)
    llm_model: str = Field(default="gpt-3.5-turbo")
    prompt_template: str = Field(
        default="Write a detailed passage that would answer the following question: {query}"
    )
    openai_api_key: Optional[str] = Field(default=None)


class RAGConfig(BaseModel):
    """Main RAG engine configuration."""

    retrieval: RetrievalConfig = Field(default_factory=RetrievalConfig)
    vector_store: VectorStoreConfig = Field(default_factory=VectorStoreConfig)
    reranker: RerankerConfig = Field(default_factory=RerankerConfig)
    hyde: HyDEConfig = Field(default_factory=HyDEConfig)

    @classmethod
    def from_env(cls) -> "RAGConfig":
        """Create configuration from environment variables."""
        return cls(
            retrieval=RetrievalConfig(
                top_k=int(os.getenv("TOP_K_RETRIEVAL", "10")),
                top_k_rerank=int(os.getenv("TOP_K_RERANK", "5")),
                hybrid_alpha=float(os.getenv("HYBRID_ALPHA", "0.5")),
                use_hyde=os.getenv("USE_HYDE", "false").lower() == "true",
            ),
            vector_store=VectorStoreConfig(
                store_type=os.getenv("VECTOR_STORE_TYPE", "chromadb"),
                store_path=Path(os.getenv("VECTOR_STORE_PATH", "./data/vector_store")),
                embedding_model=os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2"),
            ),
            reranker=RerankerConfig(
                reranker_type=os.getenv("RERANKER_TYPE", "cohere"),
                cohere_api_key=os.getenv("COHERE_API_KEY"),
                cross_encoder_model=os.getenv("CROSS_ENCODER_MODEL", "cross-encoder/ms-marco-MiniLM-L-6-v2"),
            ),
            hyde=HyDEConfig(
                enabled=os.getenv("USE_HYDE", "false").lower() == "true",
                openai_api_key=os.getenv("OPENAI_API_KEY"),
            ),
        )
