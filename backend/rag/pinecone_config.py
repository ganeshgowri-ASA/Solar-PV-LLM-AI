"""
Pinecone Vector Database Configuration
Configures connection to Pinecone for Solar PV knowledge base.

Index: pv-expert-knowledge
Environment: us-west-2
Embedding Model: llama-text-embed-v2
"""

import os
from dataclasses import dataclass
from typing import Optional

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not required if env vars are set directly


@dataclass
class PineconeConfig:
    """
    Pinecone configuration for Solar PV knowledge base.

    Attributes:
        api_key: Pinecone API key from environment
        index_name: Name of the Pinecone index
        environment: Pinecone environment/region
        namespace: Default namespace for operations
        embedding_model: Model used for embeddings
        rerank_model: Model used for reranking results
    """
    api_key: str
    index_name: str = "pv-expert-knowledge"
    environment: str = "us-west-2"
    namespace: str = "solar_pv_docs"
    embedding_model: str = "llama-text-embed-v2"
    rerank_model: str = "bge-reranker-v2-m3"

    # Field mapping for integrated embeddings
    field_map: dict = None

    def __post_init__(self):
        if self.field_map is None:
            self.field_map = {"text": "content"}

    @classmethod
    def from_env(cls) -> "PineconeConfig":
        """
        Create configuration from environment variables.

        Environment variables:
            PINECONE_API_KEY: Required API key
            PINECONE_INDEX: Index name (default: pv-expert-knowledge)
            PINECONE_ENVIRONMENT: Environment (default: us-west-2)
            PINECONE_NAMESPACE: Default namespace (default: solar_pv_docs)
        """
        api_key = os.getenv("PINECONE_API_KEY")
        if not api_key:
            raise ValueError(
                "PINECONE_API_KEY environment variable is required. "
                "Set it in your .env file or environment."
            )

        return cls(
            api_key=api_key,
            index_name=os.getenv("PINECONE_INDEX", "pv-expert-knowledge"),
            environment=os.getenv("PINECONE_ENVIRONMENT", "us-west-2"),
            namespace=os.getenv("PINECONE_NAMESPACE", "solar_pv_docs"),
        )

    def get_cli_create_command(self) -> str:
        """
        Generate CLI command to create the index.

        Returns:
            Shell command string for index creation
        """
        return (
            f"pc index create "
            f"-n {self.index_name} "
            f"-m cosine "
            f"-c aws "
            f"-r {self.environment} "
            f"--model {self.embedding_model} "
            f"--field_map text={self.field_map.get('text', 'content')}"
        )


# Namespace constants for different content types
class Namespaces:
    """Predefined namespaces for Solar PV content organization"""
    DOCS = "solar_pv_docs"
    RESEARCH = "solar_pv_research"
    FAQ = "solar_pv_faq"
    TUTORIALS = "solar_pv_tutorials"
    STANDARDS = "solar_pv_standards"

    @classmethod
    def get_user_namespace(cls, user_id: str) -> str:
        """Generate namespace for user-specific content"""
        return f"user_{user_id}"

    @classmethod
    def get_session_namespace(cls, session_id: str) -> str:
        """Generate namespace for session-specific content"""
        return f"session_{session_id}"


# Metadata field constraints
METADATA_FIELDS = {
    "category": ["fundamentals", "technology", "installation", "maintenance", "standards", "design"],
    "difficulty": ["beginner", "intermediate", "expert", "advanced"],
    "topic": [
        "pv_cells", "efficiency", "inverters", "mounting", "wiring",
        "safety", "grid_connection", "storage", "monitoring", "maintenance"
    ],
    "standard_type": ["IEC", "IEEE", "UL", "NEC", "ASTM", "ISO"]
}

# Batch limits as per Pinecone requirements
BATCH_LIMITS = {
    "text_records": 96,  # Max records per batch for text
    "vector_records": 1000,  # Max records per batch for vectors
    "max_batch_size_mb": 2  # Max batch size in MB
}

# Consistency wait time (seconds after upsert before search)
CONSISTENCY_WAIT_SECONDS = 10


# Singleton config instance
_config_instance: Optional[PineconeConfig] = None


def get_pinecone_config() -> PineconeConfig:
    """
    Get or create Pinecone configuration singleton.

    Returns:
        PineconeConfig instance

    Raises:
        ValueError: If PINECONE_API_KEY is not set
    """
    global _config_instance
    if _config_instance is None:
        _config_instance = PineconeConfig.from_env()
    return _config_instance
