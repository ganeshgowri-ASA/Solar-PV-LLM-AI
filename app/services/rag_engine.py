"""
RAG (Retrieval Augmented Generation) Engine.
Handles document retrieval from vector database.
"""
import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
from loguru import logger

from app.core.config import settings
from app.models.schemas import Citation


class RAGEngine:
    """
    RAG Engine for document retrieval and context augmentation.
    Uses ChromaDB for vector storage and sentence-transformers for embeddings.
    """

    def __init__(self):
        """Initialize RAG engine with vector database."""
        self.embedding_model = None
        self.chroma_client = None
        self.collection = None
        self._initialize()

    def _initialize(self):
        """Initialize vector database and embedding model."""
        try:
            # Initialize embedding model
            logger.info("Loading embedding model...")
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Embedding model loaded successfully")

            # Initialize ChromaDB
            persist_dir = Path(settings.CHROMA_PERSIST_DIRECTORY)
            persist_dir.mkdir(parents=True, exist_ok=True)

            logger.info(f"Initializing ChromaDB at {persist_dir}")
            self.chroma_client = chromadb.Client(Settings(
                persist_directory=str(persist_dir),
                anonymized_telemetry=False
            ))

            # Get or create collection
            try:
                self.collection = self.chroma_client.get_collection(
                    name=settings.CHROMA_COLLECTION_NAME
                )
                logger.info(f"Loaded existing collection: {settings.CHROMA_COLLECTION_NAME}")
            except:
                self.collection = self.chroma_client.create_collection(
                    name=settings.CHROMA_COLLECTION_NAME,
                    metadata={"description": "Solar PV documents and knowledge base"}
                )
                logger.info(f"Created new collection: {settings.CHROMA_COLLECTION_NAME}")

        except Exception as e:
            logger.error(f"Failed to initialize RAG engine: {e}")
            raise

    def generate_embedding(self, text: str) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Input text

        Returns:
            Embedding vector
        """
        embedding = self.embedding_model.encode(text, convert_to_tensor=False)
        return embedding.tolist()

    def retrieve_context(
        self,
        query: str,
        max_results: int = None
    ) -> List[Citation]:
        """
        Retrieve relevant context from vector database.

        Args:
            query: Search query
            max_results: Maximum number of results to return

        Returns:
            List of citations with relevant context
        """
        if max_results is None:
            max_results = settings.MAX_RETRIEVAL_RESULTS

        try:
            # Generate query embedding
            query_embedding = self.generate_embedding(query)

            # Query vector database
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=max_results,
                include=["documents", "metadatas", "distances"]
            )

            # Convert to citations
            citations = []
            if results and results['documents'] and len(results['documents']) > 0:
                for i, (doc, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Convert distance to similarity score (0-1)
                    # Lower distance = higher similarity
                    relevance_score = max(0, 1 - (distance / 2))

                    citation = Citation(
                        source=metadata.get('source', 'Unknown'),
                        page=metadata.get('page'),
                        chunk_id=metadata.get('chunk_id', f'chunk_{i}'),
                        relevance_score=round(relevance_score, 3),
                        text_snippet=doc[:500] if len(doc) > 500 else doc
                    )
                    citations.append(citation)

            logger.info(f"Retrieved {len(citations)} relevant documents for query")
            return citations

        except Exception as e:
            logger.error(f"Error retrieving context: {e}")
            return []

    def add_documents(
        self,
        documents: List[str],
        metadatas: List[Dict[str, Any]],
        ids: List[str]
    ) -> bool:
        """
        Add documents to vector database.

        Args:
            documents: List of document texts
            metadatas: List of metadata dicts
            ids: List of unique document IDs

        Returns:
            Success status
        """
        try:
            # Generate embeddings
            embeddings = [self.generate_embedding(doc) for doc in documents]

            # Add to collection
            self.collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids,
                embeddings=embeddings
            )

            logger.info(f"Added {len(documents)} documents to vector database")
            return True

        except Exception as e:
            logger.error(f"Error adding documents: {e}")
            return False

    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get statistics about the vector database collection.

        Returns:
            Collection statistics
        """
        try:
            count = self.collection.count()
            return {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "document_count": count,
                "status": "healthy"
            }
        except Exception as e:
            logger.error(f"Error getting collection stats: {e}")
            return {
                "collection_name": settings.CHROMA_COLLECTION_NAME,
                "document_count": 0,
                "status": "error",
                "error": str(e)
            }


# Global RAG engine instance
rag_engine = RAGEngine()
